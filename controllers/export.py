from io import BytesIO
from utils.config import getConfig, VERSION
from utils.utils import getDataFile, getExtraFile
from controllers.base import Args, onCommand, Context, loadedPlugins
from pyrogram import Client
from pyrogram.types import Message

@onCommand("export", help="export <plugin>: 导出并分享一个插件", allowAnonymous=True, version=VERSION)
async def handler(args: Args, client: Client, msg: Message, ctx: Context):
    pluginName = args.get(0)
    prefix = getConfig("prefix", "")

    if not pluginName:
        await msg.edit(f'请传入插件名作为参数，您可以通过 `{prefix}reload scan` 来查看你的插件列表 ~', "md")
        return
    
    if pluginName not in loadedPlugins:
        await msg.edit('该插件不在您已启用的插件列表中，请用 `{prefix}reload scan` 来查看你的插件列表 ~', "md")
        return

    await msg.edit('获取中...')
    text = getDataFile(f"{pluginName}.py") or getExtraFile(f"{pluginName}.py") or ""

    if not text:
        await msg.edit('无法获取插件内容，请确定它是否存在 ~', "md")
        return

    await client.send_document(msg.chat.id, BytesIO(bytes(text, encoding='utf-8')), file_name=f"{pluginName}.py")
    await msg.delete()
    