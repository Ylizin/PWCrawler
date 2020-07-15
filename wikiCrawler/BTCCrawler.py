from crawler import Crawler
import asyncio
import datetime

URL= 'https://www.huobi.me/zh-cn/exchange/btc_usdt/'
# selector = '#__layout > section > section > div.content-top > div.right > div.r.trades-container > div > div > div.mod.order-books.cur > div.mod-body > dl > dd > div.now-price > dl'
selector ='#__layout > section > section > div.content-top > div.right > div.r.trades-container > div > div > div.mod.market-trades.global.cur > div.mod-body > dl > dd > p:first-child'
click_sel = '#__layout > section > section > div.content-top > div.right > div.r.trades-container > div > ul > li:nth-child(2)'
async def test():
    c = Crawler()
    await c.init_browser()
    page = await c.make_page()
    await page.goto(URL)
    await page.click(click_sel)
    await asyncio.sleep(5)
    async def request_page(p):
        ele = await c.get_elem(selector,p)
        res = await ele.querySelectorEval('span.time','(n)=>{return n.innerText}')
        return res

    for i in range(100):
        print(await request_page(page),datetime.datetime.now())
        await asyncio.sleep(2)
    await c.browser.close()
asyncio.run(test())