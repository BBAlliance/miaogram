import asyncio
from utils.config import addPluginWhiteList, getConfig, VERSION
from controllers.base import Args, onCommand, Context, loadedPlugins, reloadExternalPlugin
from pyrogram import Client
from pyrogram.types import Message

@onCommand("enable", help="enable <plugin>: 启用一个插件", version=VERSION)
async def handler(args: Args, client: Client, msg: Message, ctx: Context):
    pluginName = args.get(0)
    prefix = getConfig("prefix", "")

    if not pluginName:
        await msg.edit(f'请传入插件名作为参数，您可以通过 `{prefix}reload scan` 来查看你的插件列表 ~', "md")
        return
    
    if pluginName in loadedPlugins:
        await msg.edit('该插件已经启用，无需再次启用 ~', "md")
        return

    status = await reloadExternalPlugin(pluginName)
    if status:
        addPluginWhiteList(pluginName)
        prefix = getConfig("prefix", "")
        loadedPlugins.add(pluginName)
        await msg.edit_text(f"🚩 启用成功，您可以运行 `{prefix}help {pluginName}` 来查看插件运行帮助 ~")
    else:
        await msg.edit_text(f"装载插件时发生问题，请确认插件代码无误或插件版本匹配 ~")
    
    await asyncio.sleep(10)
    await msg.delete()
    