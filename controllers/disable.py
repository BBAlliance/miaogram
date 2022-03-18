import asyncio
from utils.config import VERSION, delPluginWhiteList, getConfig
from controllers.base import Args, deregister, onCommand, Context, loadedPlugins
from pyrogram import Client
from pyrogram.types import Message

from utils.utils import existExtraFile

@onCommand("disable", help="disable <plugin>: 禁用一个插件", version=VERSION)
async def handler(args: Args, client: Client, msg: Message, ctx: Context):
    pluginName = args.get(0)
    prefix = getConfig("prefix", "")

    if not pluginName:
        await msg.edit(f'请传入插件名作为参数，您可以通过 `{prefix}reload scan` 来查看你的插件列表 ~', "md")
        return
    
    if pluginName not in loadedPlugins:
        await msg.edit('该插件未被启用，无需再次禁用 ~', "md")
        return
    loadedPlugins.remove(pluginName)

    delPluginWhiteList(pluginName)

    deregister(f"extra.{pluginName}")
    deregister(f"data.{pluginName}")

    await msg.edit_text(f"🚩 禁用 `{pluginName}` 成功 ~")
    
    await asyncio.sleep(10)
    await msg.delete()
    