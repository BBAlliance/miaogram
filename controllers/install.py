import asyncio
from os import unlink
from os.path import basename
from utils.config import addPluginWhiteList, getConfig, VERSION
from utils.logger import error
from utils.utils import delDataFile, getTempFile, randStr, removeExt, setDataFile
from controllers.base import Args, onCommand, Context, reloadExternalPlugin, loadedPlugins
from pyrogram import Client
from pyrogram.types import Message
from os.path import join

import aiohttp

proxy = {}
s = aiohttp.ClientSession()

@onCommand("install", help="install <url>: 回复一个文件或者发送链接来装一个库", allowAnonymous=True, version=VERSION)
async def handler(args: Args, client: Client, msg: Message, ctx: Context):
    await msg.edit_text('获取中...')
    url = args.getAll()
    text = ""
    pluginName = ""
    if msg.reply_to_message:
        doc = msg.reply_to_message.document
        if doc and (doc.file_name.endswith(".py") or doc.file_name.endswith(".txt")):
            fname = randStr() + ".py"
            fpath = await client.download_media(msg.reply_to_message, file_name=join("tmp/downloads", fname))
            pluginName = removeExt(doc.file_name)
            text = getTempFile(f"downloads/{fname}")
            unlink(fpath)
        else:
            await msg.edit_text('回复的文件格式错误，请务必回复一个 .py 文档 ~')
            return
    elif url:
        try:
            request = await s.get(url)
            pluginName = removeExt(basename(url).split("?")[0])
            text = await request.text('utf-8')
        except Exception as e:
            error(f"Download Plugin Error | url: {url} err: {e}")
            await msg.edit_text('无法下载文件或文件格式有误，请检查 ~')
            return
    
    # 检查插件名
    if pluginName.find(".") > -1 or pluginName.find(" ") > -1:
        await msg.edit_text('插件文件命名有误，请确认插件除了后缀外不能有额外的空格和点 ~')
        return
    
    # 检查文件
    if not pluginName or text.find("controllers.base") < 0 or text.find("async def") < 0 or text.find("@on") < 0:
        error(f"Download Plugin Error | cannot parse the file")
        await msg.edit_text('无法解析文件，请检查文件内容 ~')
        return
    
    # 写入文件
    pluginFileName = pluginName + ".py"
    setDataFile(pluginFileName, text)

    # 重载插件
    status = await reloadExternalPlugin(pluginName)
    if status:
        addPluginWhiteList(pluginName)
        loadedPlugins.add(pluginName)
        prefix = getConfig("prefix", "")
        await msg.edit_text(f"🚩 安装成功，您可以运行 `{prefix}help {pluginName}` 来查看插件运行帮助 ~")
    else:
        delDataFile(pluginFileName)
        await msg.edit_text(f"装载插件时发生问题，请确认插件代码无误或插件版本匹配 ~")
    
    await asyncio.sleep(10)
    await msg.delete()