from socket import timeout
from pyppeteer import launch
import asyncio

loop = asyncio.get_event_loop()
b = loop.run_until_complete(launch())
p1 = loop.run_until_complete(b.newPage())
p2 = loop.run_until_complete(b.newPage())
d = {1:p1,2:p2}
loop.run_until_complete(p1.goto('https://www.baidu.com'))
loop.run_until_complete(asyncio.wait_for(p2.goto('https://www.baidu.com',timeout=10,waitUntil='networkidle2'),timeout=1))
