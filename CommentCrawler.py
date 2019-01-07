import os
import requests
from bs4 import BeautifulSoup

PWBase = r'https://www.programmableweb.com'

APIUrl = PWBase + r'/' + 'api/'
r = requests.get(APIUrl + 'google-maps/comments')

soup = BeautifulSoup(r.text,'html.parser')

comments = soup.find('div',{'id':'comments'})
comments = comments.find_all('div',{'class':'field-item even'})

for i,comment in enumerate(comments):
    print(i)
    print(':\n')
    print(comment.text)
    print('\n')
