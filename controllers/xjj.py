from utils.utils import getVendor
from .base import Args, onCommand
from pyrogram import Client
from pyrogram.types import Message
import aiohttp 
from random import randint
from io import BytesIO

s = aiohttp.ClientSession()
libraries = [
    "https://api.vvhan.com/api/mobil.girl?type=json",
]
localLibrary = getVendor("xjj.txt").strip().split()

async def getCosplay():
    for _ in range(3):
        lib = localLibrary
        website = randint(0, len(lib)-1)
        try:
            img = await s.get(lib[website])
            if img.status == 200:
                # if website == 3:
                #     img = get(img.content)
                #     if img.status_code != 200:
                #         continue
                content = await img.read()
                return BytesIO(content)
        except:
            continue
    return None

@onCommand("!xjj")
async def handler(args: Args, client: Client, msg: Message):
    await msg.edit("获取中...")
    img = await getCosplay()
    if img:
        reply = None
        if msg.reply_to_message:
            reply = msg.reply_to_message_id
        await msg.delete()
        await client.send_photo(msg.chat.id, img, caption="小姐姐来啦～", reply_to_message_id=reply)
    else:
        await msg.edit("出错啦...")
