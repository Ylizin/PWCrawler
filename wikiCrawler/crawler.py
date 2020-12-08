import asyncio
from socket import timeout 
from pyppeteer import launch
from asyncio import run

from pyppeteer.network_manager import SecurityDetails
import time 
from pyppeteer.errors import PyppeteerError,TimeoutError
from collections import OrderedDict
import signal
# signal.signal(signal.SIGCLD, signal.SIG_IGN)
import os
class Crawler:
    def __init__(self,browser=None):
        self.loop = asyncio.get_event_loop()
        self.page_pool = OrderedDict()
        self.pool_size = 10
        if browser:
            self.browser = browser
        else:
            self.__init_browser()
        self.page = self.__make_page()
        
    def __init_browser(self):
        self.browser = self.loop.run_until_complete(launch(args = ['--no-sandbox']))

        # self.browser = self.loop.run_until_complete(launch(args = ['--no-sandbox','--proxy-server=socks5://127.0.0.1:1086']))
        # self.browser = self.loop.run_until_complete(asyncio.wait_for(launch(args = ['--no-sandbox','--proxy-server=socks5://192.168.31.254:1081']),timeout=10))

    def __make_page(self,page=None):
        if page:
            self.page = page
        else:
            self.page = self.loop.run_until_complete(asyncio.wait_for(self.browser.newPage(),timeout=10))
        return self.page
    
    def goto_url(self,url,page=None):
        if url in self.page_pool:
            return self.page_pool[url]

        page = self.__make_page()
        self.loop.run_until_complete(asyncio.wait_for(page.goto(url,wait_until = 'networkidle2',timeout = 10000),timeout=15))
        self.page_pool[url] = page
        self.page = page
        while len(self.page_pool)>self.pool_size:
            k,p = self.page_pool.popitem(last=False)
            self.loop.run_until_complete(asyncio.wait_for(p.close(),timeout=10))
        print("Current cached page size:{}".format(len(self.page_pool)))
        return page

    def evaluate(self,func,*params):
        res = self.loop.run_until_complete(asyncio.wait_for(self.page.evaluate(func,*params),timeout=10))
        return res
    
    def set_cookie(self,cookie,page = None):
        """
        set_cookie set cookie for a page

        Args:
            cookie (dict): dict of {'name':xxxx,'value':xxx}
        """
        if not page:
            if self.page:
                page = self.page
            else:
                page = self.__make_page()
                
        self.loop.run_until_complete(page.setCookie(cookie))
        return page
    
    def screenshot(self,page = None,path = r'./screen.png'):
        if not page:
            page = self.page
        self.loop.run_until_complete(self.page.screenshot(path = path ,fullPage = True))

    def querySelectorAllEval(self,sel,func,page=None):
        if not page:
            page = self.page
        return self.loop.run_until_complete(asyncio.wait_for(page.querySelectorAllEval(sel,func),timeout=10))
    
    def close_url(self,url):
        print('in close url '+url)
        if url not in self.page_pool:
            return
        else:
            p = self.page_pool[url]
            self.loop.run_until_complete(asyncio.wait_for(p.close(),timeout=10))
    
    def reopen(self):
        self.page_pool = OrderedDict()
        self.pool_size = 10
        self.close_browser()
        # self.loop.run_until_complete(asyncio.wait_for(self.browser.close(),timeout=10))
        self.__init_browser()

    def close_browser(self):
        pid = self.browser.process.pid
        pgid = os.getpgid(pid)
        os.kill(pid,signal.SIGKILL)
        time.sleep(1)

    def __del__(self):
        self.loop.run_until_complete(self.browser.close())
        # self.loop.close()

    # def get_elem(self, selector:str, page =None)->str:
    #     if page:
    #         return self.loop.run_until_complete(page.querySelector(selector))
    #     return self.loop.run_until_complete(self.page.querySelector(selector))

c = Crawler()

URL_PAT ='https://en.wikipedia.org/wiki/{}'
base_url = 'https://en.wikipedia.org'

SEL = '#mw-content-text > div > p'
Func_f = '''nodes=>{
                for(idx in nodes){
                    n = nodes[idx];
                    if(n.className=="")
                        {
                            return n.innerText;
                        }
                    }    
                    }'''


Disambiguation_sel = ".mw-normal-catlinks a[href]"
Disambiguation_f = """
nodes=>{
    s = '';
    for(idx in nodes){
        s+=(nodes[idx].innerText+' ');
    }
    return s;
}
"""

href_sel = "#mw-content-text > div >ul"
href_func = """
nodes=>{
    refs = [];
    
    for(idx in nodes){
        if (nodes.length>1&&idx>=nodes.length-1){
            break;
        }
        ul_node = nodes[idx].getElementsByTagName('a')
        for(var i =0;i<ul_node.length;++i){
            refs.push(ul_node[i].getAttribute('href'));
        }
    }
    return refs;
}
"""

def req(url=URL_PAT,selector=None,func = None,get_refs = True):
    print(url)
    time.sleep(10)
    # let the self.page goto url
    p = c.goto_url(url)

    # determine if is disambi
    cats = c.querySelectorAllEval(Disambiguation_sel,Disambiguation_f,p)
    if not cats:
        return 'no explanations'

    if "Disambiguation pages" in cats:
        disambi = True
    else:
        disambi = False

    if not disambi:
        p = c.querySelectorAllEval(SEL,Func_f,p)
        return [p]
    elif get_refs:
        refs= filter(lambda x: "disambiguation" not in x and x.startswith('/'),c.querySelectorAllEval(href_sel,href_func,p))
        return { link:req(url = base_url+link,get_refs=False) for link in refs}
    else:
        return ' '
        



if __name__ == '__main__':
    # 应该添加一个生产消费系统，然后通过channel进行通信，将出现exc的信息返回并等待重新尝试
    # 同时还需要处理争端，在dict中加锁，以防一个key被同时写入
    import pickle 
    words2para = pickle.load(open('./explan','rb'))
    # words2para = {}
    words = pickle.load(open('./tags','rb'))
    for w in words:
        if w not in words2para:
            try:
                print('a word {}'.format(w))
                words2para[w] = req(url = URL_PAT.format(w))
                pickle.dump(words2para,open('explan','wb'))
            except (PyppeteerError,TimeoutError,Exception) as e:
                print(e)
                c.reopen()

                

    # async def test():
    #     c = Crawler()
    #     await c.init_browser()
    #     async def request_page(word):
    #         print(word)
    #         # make new page
    #         page = await c.make_page()
    #         await page.goto(URL_PAT.format(word))
    #         ele = await c.get_elem(SEL)
    #         p = await ele.querySelectorAllEval('p',Func_f)
    #         print(p)
    #         await page.close()
    #         if p and len(p.strip().split())<20 and ('refer' in p or 'this message may be' in p):
    #             words2para[word] = ""
    #         else:
    #             words2para[word] = p

    #     # res = await asyncio.gather(*[request_page(w) for w in words],return_exceptions=True)

    #     # 上面的写法请求得太快了，机器好像没顶住，加载不出来，不知道有没有wiki ban ip的问题
    #     # 这里直接串行了qaq
    #     for word in words:
    #         if word in words2para:
    #             continue
    #         try:
    #             await request_page(word)
    #         except Exception as e:
    #             print(e)
    #             break
    #         pickle.dump(words2para,open('explan','wb'))
    #         await asyncio.sleep(5)

    #     await c.browser.close()
    # run(test())