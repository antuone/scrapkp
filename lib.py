# -*- coding: utf-8 -*-
'''
    Скребок кинопоиска
'''
import requests
from bs4 import BeautifulSoup

def fstr(str1, lenght=25):
    '''
    Форматирует строку делая ее длиной равной length
    Доплняет в начале строки пробелы, а в конце двоеточие
    '''
    k = len(str1)
    if k < lenght:
        i = lenght - k
        while i > 0:
            str1 = ' ' + str1
            i = i - 1
    str1 += ' : '
    return str1

def get_revenues(revenues):
    '''
    Возвращает словарь сборов за фильм
    '''
    _revenues = {}
    for revenue in revenues:
        if revenue.span is None:
            _revenues['TOTAL'] = revenue.text.encode('utf-8')
        else:
            _revenues[revenue.span['title']] = revenue.text.encode('utf-8')
    return _revenues

def get_viewers(viewers):
    '''
    Возвращает словарь зрителей
    '''
    _viewers = {}
    i = 0
    length = len(viewers)
    while i < length:
        _viewers[viewers.contents[i]['title']] = viewers.contents[i+1].encode('utf-8')
        i += 2
    return _viewers

def get_soup(url):
    '''
        Возвращает суп - html разметки
    '''
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0)'
                             ' Gecko/20100101 Firefox/45.0'}
    # session = requests.Session()
    # response = session.get(url, headers=headers)
    # text = response.text
    # return BeautifulSoup(text, "lxml")
    return BeautifulSoup(requests.get(url, headers=headers).text, "lxml")
