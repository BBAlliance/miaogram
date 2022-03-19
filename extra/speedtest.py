from io import BytesIO
import json
from controllers.base import Args, onCommand, Context
from pyrogram import Client
from pyrogram.types import Message
from PIL import Image
from utils.utils import TempDir, convertBytes, execute, existTempFile
from utils import logger
import platform
from os.path import join

import aiohttp 
s = aiohttp.ClientSession()

longHelp = """**使用方法：**
`1.` 直接运行 `speedtest` 指令以用最近的服务器进行测速
`2.` 加上服务器 id 例如 `speedtest 12345` 进行制定服务器测速
`3.` 使用 `speedtest list` 来列出附近的服务器

⚠️ 当前版本只支持 Linux x86_64 以及 aarch64 架构
"""

async def install() -> str:
    if not existTempFile("speedtest"):
        arch = platform.uname().machine
        if arch in ["x86_64", "aarch64"]:
            url = f"https://install.speedtest.net/app/cli/ookla-speedtest-1.1.1-linux-{arch}.tgz"
            await execute(f"""/bin/bash -c 'wget -qO- "{url}" | tar zx -C {TempDir} speedtest'""")
            if existTempFile("speedtest"):
                return ""
            return "下载时发生错误，请重试"
        else:
            return f"不支持该系统架构: {arch}"
    return ""

@onCommand("speedtest", minVer="1.3.0", help="speedtest <id|list?>: 服务器测速", version="1.0.2", longHelp=longHelp)
async def handler(args: Args, client: Client, msg: Message, ctx: Context):
    await msg.edit("运行中...")
    installMsg = await install()
    if installMsg:
        await msg.edit(installMsg)
        return

    target = join(TempDir, "speedtest") + " --accept-license --accept-gdpr -f json"
    if args.get(0) == "list":
        target += " -L"
        try:
            result = await execute(target, False)
            result = json.loads(result)["servers"]
            srv = []
            for server in result:
                location = server["location"]
                sponsor = server["name"]
                id = "%5d" % (server["id"])
                srv.append(f"- `{id}` | `{location}` | `{sponsor}`")
            await msg.edit("最近的服务器列表:\n\n" + "\n".join(srv), "md")
        except:
            await msg.edit("无法获取最近的服务器...")
        return

    appointed = args.getInt(0)
    if appointed > 0:
        target += f" -s {appointed}"

    try:
        result = await execute(target, False)
        result = json.loads(result)
        des = (
            f"**Speedtest** \n"
            f"Server: `{result['server']['name']} - "
            f"{result['server']['location']}` \n"
            f"Host: `{result['server']['host']}` \n"
            f"Upload: `{convertBytes(result['upload']['bandwidth'] * 8)}` \n"
            f"Download: `{convertBytes(result['download']['bandwidth'] * 8)}` \n"
            f"Latency: `{result['ping']['latency']}` \n"
            f"Jitter: `{result['ping']['jitter']}` \n"
            f"Timestamp: `{result['timestamp']}`"
        )

        # 开始处理图片
        try:
            data = await s.get(f"{result['result']['url']}.png")
            content = await data.read()
            with BytesIO() as buffer:
                img = Image.open(BytesIO(content))
                img = img.crop((17, 11, 727, 389))
                img.save(buffer, format="PNG")
                reply = None
                if msg.reply_to_message:
                    reply = msg.reply_to_message_id
                await client.send_photo(msg.chat.id, buffer, caption=des, parse_mode='md', reply_to_message_id=reply)
        except:
            logger.info(result)
            await msg.edit(des, 'md')
            return
    except Exception as e:
        logger.error(f"Speedtest Error | message: {e}")
        await msg.edit("测速中断，无法生成测速报告")
        return

    await msg.delete()
