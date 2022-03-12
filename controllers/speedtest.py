from io import BytesIO
from .base import Args, onCommand
from pyrogram import Client
from pyrogram.types import Message
from requests import get
from PIL import Image
from speedtest import Speedtest, ShareResultsConnectFailure, ShareResultsSubmitFailure
from utils.utils import convertBytes, threadingExec

@onCommand("!speedtest")
async def handler(args: Args, client: Client, msg: Message):
    test = Speedtest()
    await msg.edit("获取伺服器中...")
    
    # 获取测速服务器
    try:
        appointed = args.getInt(0)
        if appointed > 0:
            test.get_servers(servers=appointed)
        else:
            # test.get_best_server()
            test.get_closest_servers()
    except:
        await msg.edit("测速中断，无法获取测速服务器")
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
        data = get(result['share']).content
        with BytesIO() as buffer:
            img = Image.open(BytesIO(data))
            img = img.crop((17, 11, 727, 389))
            img.save(buffer, format="PNG")
            await client.send_photo(msg.chat.id, buffer, caption=des, parse_mode='md')
        # await client.send_photo(msg.chat.id, result['share'], caption=des, parse_mode='md')
    except:
        await msg.edit("测速中断，无法生成测速报告")
        return

    await msg.delete()
