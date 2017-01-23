# -*- coding: utf-8 -*-
'''
    Скребок кинопоиска
'''
import requests
from bs4 import BeautifulSoup

ID = 45336

URL_STUDIO = 'https://plus.kinopoisk.ru/film/45336/details/?tabId=info'
HEADERS = {
'Host': 'plus.kinopoisk.ru',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Accept-Language': 'en-US,en;q=0.5',
'Accept-Encoding': 'gzip, deflate, br',
'X-Requested-With': 'XMLHttpRequest',
'Referer': 'https://plus.kinopoisk.ru/film/43213/details/',
'DNT': '1',
'Connection': 'keep-alive'}

# SOUP = BeautifulSoup(requests.get(URL_STUDIO, headers=HEADERS).text, "lxml")
# print(SOUP.prettify())

# print(requests.get(URL_STUDIO, headers=HEADERS).text)

JSON = requests.get(URL_STUDIO, headers=HEADERS).json()

print(JSON)









