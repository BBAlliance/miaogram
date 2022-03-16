from io import BytesIO
from controllers.base import Args, onCommand
from pyrogram import Client
from pyrogram.types import Message
from os import path, unlink
from utils import utils
from PIL import Image

@onCommand("pic", minVer="1.0.0", help="pic: 回复下载静态图片")
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

        with BytesIO() as buffer:
            img = Image.open(f).convert("RGB")
            img.save(buffer, format="PNG")
            await client.send_document(message.chat.id, buffer, file_name=utils.removeExt(fname) + ".png")
            img.close()
        
        unlink(f)
        await message.delete()
