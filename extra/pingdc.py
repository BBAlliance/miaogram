from controllers.base import Args, onCommand, Context
from pyrogram import Client
from pyrogram.types import Message
from utils.utils import execute

DCs = {
    1: "149.154.175.50",
    2: "149.154.167.51",
    3: "149.154.175.100",
    4: "149.154.167.91",
    5: "91.108.56.130"
}

@onCommand("pingdc", minVer="1.0.0", help="pingdc: 测试到数据中心的延迟")
async def handler(_: Args, client: Client, message: Message, ctx: Context):
    data = []
    for dc in range(1, 6):
        result = await execute(f"ping -c 1 {DCs[dc]} | awk -F '/' " + "'END {print $5}'")
        data.append(result)
    await message.edit(
        f"`DC1`(🇺🇸 迈阿密): `{data[0]}ms`\n"
        f"`DC2`(🇳🇱 阿姆斯特丹): `{data[1]}ms`\n"
        f"`DC3`(🇺🇸 迈阿密): `{data[2]}ms`\n"
        f"`DC4`(🇳🇱 阿姆斯特丹): `{data[3]}ms`\n"
        f"`DC5`(🇸🇬 新加坡): `{data[4]}ms`"
    , "md")
