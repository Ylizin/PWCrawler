import asyncio 
from pyppeteer import launch
from asyncio import run


class Crawler:
    def __init__(self,browser=None):
        if browser:
            self.browser = browser

    async def init_browser(self):
            self.browser = await launch(args = ['--no-sandbox','--proxy-server=socks5://172.22.96.1:1081'])

    async def make_page(self,page=None):
        if page:
            self.page = page
        else:
            self.page = await self.browser.newPage()
        return self.page
    
    async def goto_url(self,url,page=None):
        if not page:
            await self.page.goto(url)
        else:
            await page.goto(url)
    
    async def evaluate(self,func,*params):
        res = await self.page.evaluate(func,*params)
        return res
    
    async def get_elem(self, selector:str, page =None)->str:
        if page:
            return await page.querySelector(selector)
        return await self.page.querySelector(selector)
    

if __name__ == '__main__':
    # 应该添加一个生产消费系统，然后通过channel进行通信，将出现exc的信息返回并等待重新尝试
    # 同时还需要处理争端，在dict中加锁，以防一个key被同时写入
    URL_PAT ='https://en.wikipedia.org/wiki/{}'
    import pickle 
    words2para = pickle.load(open('./explan','rb'))
    words = pickle.load(open('./dict','rb'))
    async def test():
        c = Crawler()
        await c.init_browser()
        async def request_page(word):
            print(word)
            # make new page
            page = await c.make_page()
            await page.goto(URL_PAT.format(word))
            ele = await c.get_elem('#mw-content-text > div')
            p = await ele.querySelectorAllEval('p','''nodes=>{
                for(idx in nodes){
                    n = nodes[idx]
                    if(n.className=="")
                        {
                            return n.innerText
                        }
                    }    
                    }''')
            print(p)
            await page.close()
            if p and len(p.strip().split())<20 and ('refer' in p or 'this message may be' in p):
                words2para[word] = ""
            else:
                words2para[word] = p

        # res = await asyncio.gather(*[request_page(w) for w in words],return_exceptions=True)

        # 上面的写法请求得太快了，机器好像没顶住，加载不出来，不知道有没有wiki ban ip的问题
        # 这里直接串行了qaq
        for word in words.values():
            if word in words2para:
                continue
            try:
                await request_page(word)
            except Exception as e:
                print(e)
                continue
            pickle.dump(words2para,open('explan','wb'))
            await asyncio.sleep(5)

        await c.browser.close()
    run(test())