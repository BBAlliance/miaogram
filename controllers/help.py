from .base import Args, onCommand, modules
from pyrogram import Client
from pyrogram.types import Message
from utils.config import getConfig

@onCommand("help", minVer="1.0.0", help="help: 查看菜单")
async def handler(arg: Args, client: Client, message: Message):
    cmd = arg.get(0)
    if not cmd:
        output = "🌞 当前启用的指令有:\n"
        for k in modules:
            m = modules[k]
            if m.help:
                line = getConfig("prefix", "") + m.help
                output += "\n`" + line.replace("`", "'") + "`"
        await message.edit(f"{output}", 'md')
    else:
        picked = [modules[k] for k in modules if modules[k].command == cmd]
        if len(picked):
            m = picked[0]
            line = getConfig("prefix", "") + m.help
            output = f"🌛 `{cmd}`的帮助文档:\n"
            output += "\n`" + line.replace("`", "'") + "`"
            if m.longHelp:
                output += f"\n\n{m.longHelp.strip()}"
            await message.edit(f"{output}", 'md')
        else:
            await message.edit(f"找不到该模块哦 ～", 'md')
