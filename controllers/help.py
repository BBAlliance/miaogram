from .base import Args, onCommand, pluginModules, Context
from pyrogram import Client
from pyrogram.types import Message
from utils.config import getConfig, VERSION

@onCommand("help", help="help: 查看菜单", allowAnonymous=True, version=VERSION)
async def handler(arg: Args, client: Client, message: Message, ctx: Context):
    cmd = arg.get(0)
    if not cmd:
        output = "🌞 当前启用的指令有:\n"
        for k in pluginModules:
            for f in pluginModules[k]:
                m = pluginModules[k][f]
                if m.help:
                    line = getConfig("prefix", "") + m.help
                    output += "\n`" + line.replace("`", "'") + "`"
        await message.edit(f"{output}", 'md')
    else:
        picked = None
        for k in pluginModules:
            for f in pluginModules[k]:
                if pluginModules[k][f].command == cmd and pluginModules[k][f].type == "command":
                    picked = pluginModules[k][f]
        if picked:
            line = getConfig("prefix", "") + picked.help
            output = f"🌛 `{cmd}`的帮助文档 (`{picked.version}`):\n"
            output += "\n`" + line.replace("`", "'") + "`"
            if picked.longHelp:
                output += f"\n\n{picked.longHelp.strip()}"
            await message.edit(f"{output}", 'md')
        else:
            await message.edit(f"找不到该模块哦 ～", 'md')
