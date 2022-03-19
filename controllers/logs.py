from io import BytesIO

from utils.logger import getLogBank
from .base import Args, onCommand, Context
from pyrogram import Client
from pyrogram.types import Message

from utils.config import VERSION

@onCommand("logs", help="logs <lines>: 获取系统日志", allowAnonymous=True, version=VERSION)
async def handler(args: Args, client: Client, msg: Message, ctx: Context):
    lines = args.getInt(0)
    if lines <= 0:
        lines = 10
    
    lines = getLogBank(lines)
    logs = "".join(lines).strip()

    if logs:
        if len(logs) >= 4096:
            await msg.delete()
            await client.send_document(msg.chat.id, BytesIO(bytes(logs, encoding='utf-8')), parse_mode='md', file_name='execution.log')
        else:
            logs = logs.replace("`", "'")
            logs = f"**System Logs `({len(lines)})`:**\n\n`{logs}`"
            await msg.edit(f"{logs}")
    else:
        await msg.edit(f"`无结果返回`")
