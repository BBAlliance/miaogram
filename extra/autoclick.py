from controllers.base import Args, onCommand, onMessage, Context
from pyrogram import Client
from pyrogram.types import Message
from utils import logger, config

import aiohttp
import asyncio

KVKey = '@autoclick.text'
toggler = config.readKey(KVKey)
s = aiohttp.ClientSession()

@onMessage(minVer="1.0.0")
async def msgHandler(client: Client, msg: Message, ctx: Context):
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

@onCommand("autoclick", minVer="1.0.0", help="autoclick <btnName>: 自动按按钮")
async def handler(args: Args, client: Client, msg: Message, ctx: Context):
    global toggler
    pattern = args.get(0)
    if not pattern:
        await msg.edit(f"当前正在监听 {toggler}～")
    elif pattern == '-':
        await msg.edit(f"关闭监听 {toggler}～")
        toggler = ""
        ctx.set(KVKey, toggler)
    else:
        toggler = pattern
        await msg.edit(f"开始监听 {toggler}～")
        ctx.set(KVKey, toggler)
    
    await asyncio.sleep(3)
    await msg.delete()
