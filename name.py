# -*- coding: utf-8 -*-
# import sqlite3
import requests

URL = u'https://www.kinopoisk.ru/handler_popup_info.php?token=802250a34dbbf3e82e79a051a66433d9&type=name&id=377&rnd=0.31835925964665834'
HEADERS = {
    u'Host': u'www.kinopoisk.ru',
    u'User-Agent': u'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0',
    u'Accept': u'*/*',
    u'Accept-Language': u'en-US,en;q=0.5',
    u'Accept-Encoding': u'gzip, deflate, br',
    u'X-Requested-With': u'XMLHttpRequest',
    u'Referer': u'https://www.kinopoisk.ru/box/weekend/2016-12-23/type/rus/cur/RUB/view/all/',
    u'Cookie': u'last_visit=2017-01-08+20%3A28%3A52; mobile=no; my_perpages=%5B%5D; awfs=1; noflash=false; loc=win; _ym_uid=1483687893486247273; yandexuid=8299635981476775770; refresh_yandexuid=8299635981476775770; _ym_isad=1; PHPSESSID=b575cbc983bb4ea8809ec5088ba9a41c; yandex_gid=50; user_country=ru; _ym_visorc_22663942=b',
    u'DNT': u'1',
    u'Connection': u'keep-alive'}

PARAMS = {'type': 'name', 'id': '123'}

print requests.get(URL, params=PARAMS, headers=HEADERS).text
#json()['name']

# i = 90
# while i <= 95:
#     print requests.post(URL).json()['name']
#     i += 1
