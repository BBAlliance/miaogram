from os.path import basename
from utils.config import reloadConfig, VERSION
from utils.utils import listFiles, removeExt
from .base import Args, onCommand, reloadPlugins, Context, loadedPlugins
from pyrogram import Client
from pyrogram.types import Message

@onCommand("reload", help="reload <scan?>: 重载配置和所有插件", version=VERSION)
async def handler(args: Args, client: Client, message: Message, ctx: Context):
    arg = args.get(0)
    if arg == "scan":
        loaded = loadedPlugins.copy()
        enabled = []
        disabled = []

        addons = [removeExt(basename(f)) for f in listFiles("extra/*.py") + listFiles("data/*.py")]
        addons = [f for f in addons if not f.startswith("__")]
        for plugin in addons:
            if plugin in loaded:
                enabled.append(plugin)
            else:
                disabled.append(plugin)
        
        enabled = '\n'.join(enabled)
        disabled = '\n'.join(disabled)

        if enabled:
            enabled = f"\n\n**已启用的插件:**\n`{enabled}`"
        if disabled:
            disabled = f"\n\n**已禁用的插件**:\n`{disabled}`"

        await message.edit(f"🐛 扫描到的插件有:{enabled}{disabled}", 'md')
    else:
        await message.edit("重载中...", 'md')
        reloadConfig()
        success, failure = await reloadPlugins()
        success = "\n".join(success)
        failure = "\n".join(failure)

        if success:
            success = f"\n\n**已加载:**\n`{success}`"
        if failure:
            failure = f"\n\n**失败插件**:\n`{failure}`"
        await message.edit(f"🐛 重载插件列表完成:{success}{failure}", 'md')
