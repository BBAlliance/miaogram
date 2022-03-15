from .base import Args, onCommand
from pyrogram import Client
from pyrogram.types import Message
from os import path
from utils import utils
from PIL import Image

@onCommand("pic", help="pic: 回复下载静态图片")
async def handler(_: Args, client: Client, message: Message):
    re = message.reply_to_message
    
    if not re:
        await message.edit(f"请回复一则消息")
    elif not re.sticker:
        await message.edit(f"请回复一个表情")
    else:
        await message.edit(f"处理中...")
        fname = re.sticker.file_name
        f = await client.download_media(re, file_name=path.join("data/downloads", utils.randStr() + fname))
        
        im = Image.open(f).convert("RGB")
        f += ".png"
        im.save(f, "png")
        await client.send_document(message.chat.id, f)
        await message.delete()
