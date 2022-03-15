from .base import Args, onCommand, onMessage
from pyrogram import Client
from pyrogram.types import Message
from utils import logger

import aiohttp
import asyncio

toggler = ""
s = aiohttp.ClientSession()

@onMessage()
async def msgHandler(client: Client, msg: Message):
    global toggler
    try:
        if toggler and msg.reply_markup and msg.reply_markup.inline_keyboard:
            kbd = msg.reply_markup.inline_keyboard
            for lines in kbd:
                for btn in lines:
                    if btn and btn.text.find(toggler) != -1:
                        logger.info(f"AutoClick | Matched {toggler} btn={btn.text} chat={msg.chat.id} msgid={msg.message_id}")
                        await client.request_callback_answer(msg.chat.id, msg.message_id, btn.callback_data)
    except:
        pass

@onCommand("autoclick", help="autoclick <btnName>: 自动按按钮")
async def handler(args: Args, client: Client, msg: Message):
    global toggler
    pattern = args.get(0)
    if not pattern and not toggler:
        await msg.edit("错误的用法，请发送：`!autoclick <pattern>`", "md")
    elif not pattern:
        await msg.edit(f"关闭监听 {toggler}～")
        toggler = ""
    else:
        toggler = pattern
        await msg.edit(f"开始监听 {toggler}～")
    
    await asyncio.sleep(3)
    await msg.delete()
