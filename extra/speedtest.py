from io import BytesIO
from controllers.base import Args, onCommand, Context
from pyrogram import Client
from pyrogram.types import Message
from PIL import Image
from speedtest import Speedtest, ShareResultsConnectFailure, ShareResultsSubmitFailure
from utils.utils import convertBytes, threadingExec
from utils import logger

import aiohttp 
s = aiohttp.ClientSession()

@onCommand("speedtest", minVer="1.0.0", help="speedtest <id|list?>: 服务器测速")
async def handler(args: Args, client: Client, msg: Message, ctx: Context):
    test = Speedtest()
    await msg.edit("获取伺服器中...")
    
    # 获取测速服务器
    try:
        appointed = args.getInt(0)
        if appointed > 0:
            test.get_servers(servers=[appointed])
        else:
            # test.get_best_server()
            test.get_closest_servers()
    except Exception as e:
        logger.error(f"Speedtest Error: {str(e)}")
        await msg.edit("测速中断，无法获取测速服务器")
        return
    
    if args.get(0) == "list":
        srv = []
        for distance in test.servers:
            for server in test.servers[distance]:
                cc = server["cc"]
                sponsor = server["sponsor"]
                id = "%5s" % (server["id"])
                srv.append(f"- `{cc}` | `{id}` | `{sponsor}`")
        await msg.edit("最近的服务器列表:\n\n" + "\n".join(srv), "md")
        return
    
    # 开始测速
    try:
        await msg.edit("下行测速中...")
        await threadingExec(test.download)
        await msg.edit("上行测速中...")
        await threadingExec(test.upload)
        await msg.edit("生成图片中...")
        test.results.share()
    except (ShareResultsConnectFailure, ShareResultsSubmitFailure, RuntimeError) as e:
        await msg.edit("测速中断，在测速的过程中发生错误")
        return
    
    # 处理信息
    try:
        result = test.results.dict()
        des = (
            f"**Speedtest** \n"
            f"Server: `{result['server']['name']} - "
            f"{result['server']['cc']}` \n"
            f"Sponsor: `{result['server']['sponsor']}` \n"
            f"Upload: `{convertBytes(result['upload'])}` \n"
            f"Download: `{convertBytes(result['download'])}` \n"
            f"Latency: `{result['ping']}` \n"
            f"Timestamp: `{result['timestamp']}`"
        )

        # 处理图片
        data = await s.get(result['share'])
        content = await data.read()
        with BytesIO() as buffer:
            img = Image.open(BytesIO(content))
            img = img.crop((17, 11, 727, 389))
            img.save(buffer, format="PNG")
            reply = None
            if msg.reply_to_message:
                reply = msg.reply_to_message_id
            await client.send_photo(msg.chat.id, buffer, caption=des, parse_mode='md', reply_to_message_id=reply)
        # await client.send_photo(msg.chat.id, result['share'], caption=des, parse_mode='md')
    except:
        await msg.edit("测速中断，无法生成测速报告")
        return

    await msg.delete()
