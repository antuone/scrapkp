# -*- coding: utf-8 -*-
'''
    скребок списка фильмов
'''
import sys
import sqlite3
import requests
PAGE = sys.argv[1]
HEADERS = {
    'Host': 'plus.kinopoisk.ru',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0',
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
_PAGE = '&page=' + PAGE
URL = 'https://plus.kinopoisk.ru/catalogue/?advanced=1&chunkOnly=1%s%s%s'
URL = URL % ('', GENRE, _PAGE)
# Соединяемся с БД медиатеки
CONN = sqlite3.connect('/mnt/ram/MyVideos108.db')
C = CONN.cursor()
RESPONSE = requests.get(URL, headers=HEADERS)
if RESPONSE.ok:
    JSON = RESPONSE.json()
else:
    print(RESPONSE)
    exit(0)

# Добавляем список ID
SQL = "INSERT INTO list_id (id, type) VALUES (?,?)"
for i in JSON['state']['movies']:
    _type = JSON['state']['movies'][i]['type']
    try:
        C.execute(SQL, (i, _type))
    except sqlite3.IntegrityError:
        pass
CONN.commit()



if JSON['hasMore'] == True:
    print('Страница обработана - %s' % PAGE)
else:
    C.execute('SELECT count(id) from list_id')
    COUNT = C.fetchone()[0]
    print('Последняя старница - %s' % PAGE + 'Количество идентификаторов %d' % COUNT)
    print('#')
    print('  Нажмите пожалуйста CTRL + C')
    print('#')

CONN.close()
