import multiprocessing
import os
import time
from multiprocessing import Pool

from tqdm import tqdm

import Crawler
import dbOperation


def one_process(page):
    for name,submitted,href in Crawler.get_page_api_names(page):
        try:
            api_info = Crawler.get_api_info(href,name,submitted)
            insert_id = dbOperation.insert_into_API_info(api_info)[0]
            comment_info = Crawler.get_api_comment(href,insert_id)
            dbOperation.insert_into_comment(comment_info)
        except Exception as e:
            print(repr(e))
            print(name)
            print('\n')
            print(href)
            print('\n')
            #raise
            # return return will leave some condition unconsidered
        time.sleep(1)
    print('page:{0} finished.\n'.format(page))
    # one_process(page)

def main():
    p = Pool(int(os.cpu_count()/2+1))

    totalPages = Crawler.get_dir_info()
    print(totalPages)
    
    for i in range(totalPages):
        # one_process(i)
        p.apply_async(one_process,args=[i],error_callback = lambda e : print(repr(e)))
        
    p.close()
    p.join()

if __name__ == '__main__':
    main()
