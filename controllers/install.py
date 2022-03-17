import asyncio
from os import unlink
from os.path import basename
from utils.config import getConfig
from utils.logger import error, info
from utils.utils import getDataFile, randStr, removeExt, setDataFile
from controllers.base import Args, onCommand, Context
from pyrogram import Client
from pyrogram.types import Message
from os.path import join

import aiohttp

proxy = {}
s = aiohttp.ClientSession()

@onCommand("install", help="install <url>: 回复一个文件或者发送链接来装一个库")
async def handler(args: Args, client: Client, msg: Message, ctx: Context):
    m = await msg.edit_text('获取中...')
    url = args.getAll()
    text = ""
    pluginName = ""
    if msg.reply_to_message:
        doc = msg.reply_to_message.document
        if doc and (doc.file_name.endswith(".py") or doc.file_name.endswith(".txt")):
            fname = randStr() + ".py"
            fpath = await client.download_media(msg.reply_to_message, file_name=join("data/downloads", fname))
            pluginName = doc.file_name
            text = getDataFile(f"downloads/{fname}")
            unlink(fpath)
        else:
            await msg.edit_text('回复的文件格式错误，请务必回复一个 .py 文档 ~')
            return
    elif url:
        try:
            request = await s.get(url)
            pluginName = basename(url).split("?")[0]
            text = await request.text('utf-8')
        except Exception as e:
            error(f"Download Plugin Error | url: {url} err: {e}")
            await msg.edit_text('无法下载文件或文件格式有误，请检查 ~')
            return
    
    # 检查文件
    if not pluginName or text.find("controllers.base") < 0 or text.find("async def") < 0 or text.find("@on") < 0:
        error(f"Download Plugin Error | cannot parse the file")
        await msg.edit_text('无法解析文件，请检查文件内容 ~')
        return
    
    # 写入文件
    if not pluginName.endswith(".py"):
        pluginName = removeExt(pluginName) + ".py"
    setDataFile(pluginName, text)

    prefix = getConfig("prefix", "")
    await msg.edit_text(f"🚩 安装成功，您可以运行 `{prefix}reload` 来加载插件 ~")

    await asyncio.sleep(3)
    await msg.delete()