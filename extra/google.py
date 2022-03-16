from controllers.base import Args, onCommand
from pyrogram import Client
from pyrogram.types import Message

import requests
from pyquery import PyQuery
from urllib.parse import quote_plus, urlparse, parse_qs

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'
COOKIE = 'Accept-Language: en" -b "YSC=BiCUU3-5Gdk; CONSENT=YES+cb.20220301-11-p0.en+FX+700; GPS=1; VISITOR_INFO1_LIVE=4VwPMkB7W5A; PREF=tz=Asia.Shanghai; _gcl_au=1.1.1809531354.1646633279'

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

def search_page(query, language=None, num=None, start=0):
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
    # Add headers
    headers = {'user-agent': USER_AGENT, 'cookie': COOKIE}
    try:
        requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
        r = requests.get(url=url,
                            headers=headers,
                            allow_redirects=False,
                            verify=False,
                            timeout=30)
        if r.status_code != 200:
            return None
        content = r.content
        text = content.decode('utf-8')
        return text
    except:
        return None

def search(query, language=None, num=None, start=0):
    content = search_page(query, language, num, start)
    if not content:
        return None
    
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
    for i in search(query=text, language='zh', num=int(10)):
        try:
            title = i['text'][0:18].replace("`", "'") + '...'
            link = i['url']
            results += f"\n`{title}` | [详情]({link}) \n"
        except:
            await msg.edit("无法获取到有效信息...")
            return

    await msg.edit(f"**Google** | `{text}` | 🔍 \n{results}", reply_markup="md", disable_web_page_preview=True)