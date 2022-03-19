from controllers.base import Args, onCommand, Context, call
from pyrogram import Client
from pyrogram.types import Message

PIP="httpie"

@onCommand("http", minVer="1.4.0", help="http <cmd>: 执行 httpie 指令", version="1.0.0")
async def handler(args: Args, client: Client, msg: Message, ctx: Context):
    args.insert(0, "http")
    _, err = await call("controllers.sh.handler", args, client, msg, ctx)
    if err:
        await msg.edit(f"执行发生意外: {err}")
    