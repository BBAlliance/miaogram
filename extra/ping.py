import time
from controllers.base import Args, onCommand, Context
from pyrogram import Client
from pyrogram.types import Message

@onCommand("ping", minVer="1.0.0", help="ping: 检查到 DC 的延迟")
async def handler(_: Args, client: Client, message: Message, ctx: Context):
    t = time.time()
    await message.edit("> Pong!")
    t = (time.time() - t) * 1000
    t = "{:.2f}".format(t)
    dc = message.chat.dc_id

    await message.edit(f"> Pong! 群聊 DC: {dc}, 用时 {t} ms")
    