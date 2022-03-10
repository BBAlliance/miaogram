import time
from .base import Args, onCommand
from pyrogram import Client
from pyrogram.types import Message

@onCommand("/!ping")
async def handler(_: Args, client: Client, message: Message):
    t = time.time()
    await message.edit("> Pong!")
    t = (time.time() - t) * 1000
    t = "{:.2f}".format(t)
    dc = message.chat.dc_id

    await message.edit(f"> Pong! 群聊 DC: {dc}, 用时 {t} ms")
    