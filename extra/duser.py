import asyncio
from controllers.base import Args, onCommand, Context
from pyrogram import Client
from pyrogram.types import Message

@onCommand("duser", minVer="1.4.0", help="duser: 删除用户群内所有信息", allowAnonymous=True, version="1.0.0")
async def handler(_: Args, client: Client, message: Message, ctx: Context):
    id = 0
    if message.reply_to_message:
        if message.reply_to_message.from_user:
            id = message.reply_to_message.from_user.id
        elif message.reply_to_message.sender_chat:
            id = message.reply_to_message.sender_chat.id
    
    willDelete = message
    if id:
        if await client.delete_user_history(message.chat.id, id):
            willDelete = await client.send_message(message.chat.id, f"TA 的消息已经被全部清空啦")
        else:
            await message.edit(f"清空失败，您可能没有权限哦")
    else:
        await message.edit(f"无法获取 TA 的信息，请回复一则正确的消息")
    
    await asyncio.sleep(5)
    await willDelete.delete()
