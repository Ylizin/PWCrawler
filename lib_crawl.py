
new_id = '3F4BD63D7667A8DC0D1E1BDB45BB3B8D'
from enum import Enum

class WEEK(Enum):
    Mon = 0
    Tue = 1
    Wed = 2
    Thu = 3
    Fri = 4
    Sat = 5
    Sun = 6

def get_week_day():
    return WEEK(datetime.datetime.now().weekday())

def order():
    import time 
    from pyppeteer import page
    from wikiCrawler.crawler import Crawler
    if get_week_day()==WEEK.Thu:
        return

    c = Crawler()
    cookie = {'name':'JSESSIONID','value':'3F4BD63D7667A8DC0D1E1BDB45BB3B8D','url':'https://seat.lib.whu.edu.cn'}
    
    if new_id and new_id != 'no':
        cookie['value'] = new_id
    p = c.set_cookie(cookie=cookie)
    p = c.goto_url('https://seat.lib.whu.edu.cn/map#',page = p)
        
    loop = c.loop
    usually_seats = 'body > div:nth-child(4) > div.menu.fl > ul > li:nth-child(3) > a'
    loop.run_until_complete(p.click(usually_seats))
    date_sele = '#display_onDate'
    loop.run_until_complete(p.click(date_sele))
    date_sele2 = '#options_onDate > a'
    date_sele_func = '''
        (items)=>{
        items[items.length-1].click();
        }
        '''
    c.querySelectorAllEval(date_sele2,date_sele_func)
    
    seats_sele = '#seats > ul > li'
    seat_num = '027'
    find_027 ='''
        (items)=>{
        var stat = 0;
        for (var i =0; i <items.length;i++){
            if(items[i].innerText.indexOf('%s')>=0){
                idx = i;
                items[i].click();
                stat = 1;
                return stat;
                }
            }
        return stat;
        }
    '''%seat_num
        
    idx = 0
    while not idx:
        idx = int(c.querySelectorAllEval(seats_sele,find_027,p))
        print('seats sele waiting')
        time.sleep(1)
        
    start_time_sele = '#startTime > dl > ul > li a'
    end_time_sele = '#endTimeCotent > li a'
    start_time = '08:30'
    end_time = '22:30'
    set_time = '''
        (items)=>{
        stat = 0;
        for(var i = 0;i<items.length;i++){
            if(items[i].innerText.indexOf('%s')>=0){
                items[i].click();
                stat = 1;
                return stat;
                }
            }
        return stat;
        }
    '''
    set_start_time = set_time%start_time
    set_end_time = set_time%end_time
    idx = 0
    while not idx:
        idx = int(c.querySelectorAllEval(start_time_sele,set_start_time))
        print('start time sele waiting')
        time.sleep(1)
    
    idx = 0
    while not idx:
        idx = int(c.querySelectorAllEval(end_time_sele,set_end_time))
        print('end time sele waiting')
        time.sleep(1)
    
    confirm = '''
        (items)=>{
        items[0].click();
        }
        '''
    c.querySelectorAllEval('a.sureBtn',confirm)
    

if __name__ == '__main__':
    import schedule
    import time
    
    print(schedule.every().day.at('22:45:01').do(order))
    schedule.every().day.at('22:45:10').do(order)
    schedule.every().day.at('22:45:15').do(order)
    schedule.every().day.at('22:45:20').do(order)
    schedule.every().day.at('22:45:25').do(order)
    schedule.every().day.at('22:45:30').do(order)
    schedule.every().day.at('22:45:35').do(order)
    schedule.every().day.at('22:45:40').do(order)
    schedule.every().day.at('22:45:45').do(order)
    
    print('added ')
    import datetime
    while True:
        schedule.run_pending()
        print('waiting '+str(datetime.datetime.now()),flush=True)
        time.sleep(10)