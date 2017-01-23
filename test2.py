# -*- coding: utf-8 -*-
'''
    Вывод 404 ошибки кинопоиска
'''
import requests
ID = '1'
URL = 'http://kparser.pp.ua/json/film/%s/' % ID
RESPONSE = requests.get(URL)

print(RESPONSE.ok)

exit(0)

if RESPONSE.content == 404:
    print('404')
    exit(0)

# print(KPARSER)
