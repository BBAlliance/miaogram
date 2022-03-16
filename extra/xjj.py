from utils.utils import getVendor, randPick
from controllers.base import Args, onCommand
from pyrogram import Client
from pyrogram.types import Message
import aiohttp 
from random import randint
from io import BytesIO

s = aiohttp.ClientSession()
localLibrary = getVendor("xjj.txt").strip().split()

def getLink():
    r = randint(0, 1)
    if r == 0:
        return randPick(localLibrary)
    else:
        return "https://se.jiba.xyz/xiuren.php"

async def getCosplay():
    for _ in range(3):
        try:
            img = await s.get(getLink())
            if img.status == 200:
                content = await img.read()
                return BytesIO(content)
        except:
            continue
    return None

@onCommand("xjj", minVer="1.0.0", help="xjj: 来一张小姐姐")
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
