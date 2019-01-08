import os
import requests
from bs4 import BeautifulSoup

PWBase = r'https://www.programmableweb.com'

APIUrl = PWBase + r'/' #+ r'api/' #+ 'musicdnsorg'
DirUrl = r'https://www.programmableweb.com/category/all/apis' # + '?page=729'


def get_api_comment(api_href,api_id):
    r = requests.get(PWBase + api_href +r'/comments')
    
    soup = BeautifulSoup(r.text,'html.parser')

    comments = soup.find('div',{'id':'comments'})

    author_dates = comments.find_all('div',{'class':'author-datetime'})
    comments = comments.find_all('div',{'class':'field-item even'})
    usernames = []
    dates = []
    for ad in author_dates:
        # print(ad.contents)
        username = ad.contents[1].string
        date = ad.contents[2].strip()

        usernames.append(username)
        dates.append(date)

    comments_content = []
    for comment in comments:
        comments_content.append(comment.text)
        # print(comment.get_text())
    insert_tuples = []
    for username,date,comment in zip(usernames,dates,comments_content):
        insert_tuples.append((api_id,username,comment,date))
    return insert_tuples

def get_dir_info():
    r = requests.get(DirUrl)
    soup = BeautifulSoup(r.text,'html.parser')

    pager = soup.find('li',{'class':'pager-next'})
    a = pager.find('a')
    return int(a.text)

def get_page_api_names(page):
    r = requests.get(DirUrl,params={'page':page})
    
    soup = BeautifulSoup(r.text,'html.parser')
    api_names = soup.find_all('td',{'class':'views-field views-field-title col-md-3'})
    api_submitted = soup.find_all('td',{'class':'views-field views-field-created'})
    names = []
    hrefs = []
    submitted = []
    for an,aps in zip(api_names,api_submitted):
      
        names.append(an.find('a').text)
        hrefs.append(an.find('a').attrs['href'])
        submitted.append(aps.text.strip())
    
    return list(zip(names,submitted,hrefs))

def get_api_info(api_url,api_name,submitted_time):
    r = requests.get(PWBase + api_url)
    soup = BeautifulSoup(r.text,'html.parser')
    description = soup.find('div',{'class':'api_description tabs-header_description'}).get_text().strip()
    tags = soup.find('div',{'class':'tags'}).find_all('a')
    tag_str = []
    for tag in tags:
        tag_str.append(tag.text)
    tag_str = ','.join(tag_str)
    return (api_name,description,tag_str,submitted_time)

if __name__ == '__main__':
    print(get_api_info('/api/google-maps','Google Maps','12.05.2005'))
