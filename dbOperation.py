import mysql.connector as cn

insert_API_info = r'insert into api_info (api_name,description,category,submitted) values (%s,%s,%s,%s)'
insert_comment = r'insert into comment (api_id,user_name,comment,post_time) values (%s,%s,%s,%s)'

def get_connect():
    connect = cn.connect(host='localhost',user='pweb',password='123456',database = 'pweb',port='3306',charset='utf8')
    return connect

def insert_into_API_info(params):
    '''[insert into API_info table]
    
    Arguments:
        params {a list of tupe} -- the data to be inserted into API_info
    '''
    if not isinstance(params,list):
        params = [params]
    cnn = get_connect()
    api_ids = []
    try:
        cursor = cnn.cursor()
        for param in params:
            cursor.execute(insert_API_info,param)
            api_ids.append(cursor.lastrowid)
        # cursor.executemany(insert_API_info,params)
        # print(cursor.lastrowid)
        cnn.commit()
    except Exception as e:
        print(repr(e))
        raise
    finally:
        cursor.close()
        cnn.close()   
    return api_ids     
    
def insert_into_comment(params):
    '''insert into comment table
    
    Arguments:
        params {list of tuples } -- 
    '''
    cnn = get_connect()
    try:
        cursor = cnn.cursor() 
        cursor.executemany(insert_comment,params)
        cnn.commit()
    except Exception as e:
        print(repr(e))
        raise
    finally:
        cursor.close()
        cnn.close()


if __name__ == '__main__':
    ids = insert_into_API_info([
        ('test','test','test','test'),
        ('test2','test2','test2','test2')
    ])
    print(ids)


