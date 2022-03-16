from controllers.base import Args, onCommand
from pyrogram import Client
from pyrogram.types import Message

from pyquery import PyQuery
from urllib.parse import quote_plus, urlparse, parse_qs
from utils.logger import error

import aiohttp

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'
COOKIES = {
    'CONSENT': 'YES+srp.gws-20220309-0-RC1.nl+FX+221',
    '1P_JAR': '2022-03-16-20',
    'DV': 'o4pAwEwV6rVBECjFbPp1FKDX1hFI-ZfyqnMyKQBBhwAAAMD4RF76uFSRDlYgAMzHDXoVCf4-sxUIAA',
}
HEADERS = {'user-agent': USER_AGENT}

s = aiohttp.ClientSession(cookies=COOKIES, headers=HEADERS)

DOMAIN = 'www.google.com'
URL_SEARCH = "https://{domain}/search?hl={language}&q={query}&btnG=Search&gbv=1"
URL_NUM = "https://{domain}/search?hl={language}&q={query}&btnG=Search&gbv=1&num={num}"
URL_NEXT = "https://{domain}/search?hl={language}&q={query}&btnG=Search&gbv=1&num={num}&start={start}"

def filter_link(link):
    try:
        o = urlparse(link, 'http')
        if o.netloc:
            return link
        if link.startswith('/url?'):
            link = parse_qs(o.query)['q'][0]
            o = urlparse(link, 'http')
            if o.netloc:
                return link
    except:
        return None

async def search_page(query, language=None, num=None, start=0):
    domain = DOMAIN
    if start > 0:
        url = URL_NEXT
        url = url.format(
            domain=domain, language=language, query=quote_plus(query), num=num, start=start)
    else:
        if num is None:
            url = URL_SEARCH
            url = url.format(
                domain=domain, language=language, query=quote_plus(query))
        else:
            url = URL_NUM
            url = url.format(
                domain=domain, language=language, query=quote_plus(query), num=num)
    if language is None:
        url = url.replace('hl=None&', '')
    try:
        r = await s.get(url, allow_redirects=False)
        if r.status != 200:
            error(f"Google Search Error | url: {url} redirecting: {r.headers.get('location')}")
            return None
        return await r.text('utf-8')
    except:
        return None

async def search(query, language=None, num=None, start=0):
    content = await search_page(query, language, num, start)
    if not content:
        return
    
    pq_content = PyQuery(content)
    for p in pq_content.items('a'):
        if p.attr('href').startswith('/url?q='):
            pa = p.parent()
            if pa.is_('div'):
                ppa = pa.parent()
                if ppa.attr('class') is not None:
                    
                    result = {}
                    result['title'] = p('h3').eq(0).text()
                    result['url_path'] = p('div').eq(1).text()
                    href = p.attr('href')
                    if href:
                        url = filter_link(href)
                        result['url'] = url
                    text = ppa('div').eq(0).text()
                    result['text'] = text
                    yield result

@onCommand("google", minVer="1.0.0", help="google: 你会用搜索吗")
async def handler(args: Args, client: Client, msg: Message):
    text = args.getAll()
    if not text and msg.reply_to_message:
        text = msg.reply_to_message.text
    
    if not text:
        await msg.edit("错误的使用方式，请回复一则消息或者加上你想搜索的关键词")
        return

    text = text.replace(' ', '+')
    await msg.edit('🔍 搜索中...')

    results = ""
    async for i in search(query=text, language='zh', num=int(10)):
        try:
            title = i['text'][0:18].replace("`", "'") + '...'
            link = i['url']
            results += f"\n`{title}` | [详情]({link}) \n"
        except:
            await msg.edit("无法获取到有效信息...")
            return

    await msg.edit(f"**Google** | `{text}` | 🔍 \n{results}", "md", disable_web_page_preview=True)
