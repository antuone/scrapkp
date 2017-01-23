# -*- coding: utf-8 -*-
'''
    скребок списка фильмов
'''
import sqlite3
from threading import Thread
import requests

HEADERS = {
    'Host': 'plus.kinopoisk.ru',
    'User-Agent':
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://plus.kinopoisk.ru/catalogue/?advanced=1&what=фильм',
    'DNT': '1',
    'Connection': 'keep-alive'
}
GENRE = ['', 'комедия', 'фэнтези', 'анимационный', 'фантастика', 'ужасы', 'триллер', 'мелодрама',
         'аниме', 'исторический', 'драма', 'детектив', 'боевик']
GENRE = '&genres=' + GENRE[4]
WHAT = ['', 'фильм', 'сериал']
WHAT = '&what=' + WHAT[2]
URL = 'https://plus.kinopoisk.ru/catalogue/?advanced=1&chunkOnly=1&page=%d%s%s'
SQL = "INSERT INTO list_id (id, type) VALUES (?,?)"
STOP = [False]
def rocket(position, step, number):
    ''' Ракета '''
    if STOP[0]:
        return 0

    response = requests.get(URL % (position + 1, '', ''), headers=HEADERS)
    if response.ok:
        json = response.json()
    else:
        STOP[0] = True
        print(str(response) + str(response.url))
        return 0

    if len(json['state']['movies']) < 12:
        STOP[0] = True
    # Соединяемся с БД медиатеки
    conn = sqlite3.connect('/mnt/ram/MyVideos108.db')
    cursor = conn.cursor()
    # Добавляем список ID
    for _id in json['state']['movies']:
        _type = json['state']['movies'][_id]['type']
        try:
            cursor.execute(SQL, (_id, _type))
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    if json['hasMore'] is True:
        print('Поток %d - Страница обработана - %s' % (number, position))
        Thread(target=rocket, args=(position + step, step, number)).start()
    else:
        cursor.execute('SELECT count(id) from list_id')
        count = cursor.fetchone()[0]
        print('Поток %d - Последняя страница %s - Количество идентификаторов %d' %
              (number, position, count))
        STOP[0] = True
        return 0
    conn.close()

K = 9
for i in range(K):
    Thread(target=rocket, args=(i, K, i)).start()
