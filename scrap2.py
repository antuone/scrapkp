# -*- coding: utf-8 -*-
'''
    Скребок кинопоиска
'''
import os
import sys
import sqlite3
import requests
from bs4 import BeautifulSoup

def fstr(str1, lenght=10):
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

ID = sys.argv[1]
# print (fstr(ID) + 'В процессе')

# Соединяемся с БД медиатеки
CONN = sqlite3.connect('/mnt/ram/MyVideos108.db')
C = CONN.cursor()
# Проверяем есть ли такой фильм уже в медиатеке
C.execute("SELECT idMovie FROM movie WHERE idMovie=? LIMIT 1", (ID,))
if C.fetchone() != None:
    print(fstr(ID) + 'Такой фильм уже есть в медиатеке')
    exit(0)

HEADERS = {
    'Host': 'plus.kinopoisk.ru',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5','Accept-Encoding': 'gzip, deflate, br',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer':'https://plus.kinopoisk.ru/film/%s/details/' % ID,
    'DNT': '1','Connection': 'keep-alive'
}
HEADERS_0 = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0',
}

# Запрос json информации фильма с plus.kinopoisk.ru
URL = 'https://plus.kinopoisk.ru/film/%s/details/cast/' % ID
RESPONSE = requests.get(URL, headers=HEADERS)
if RESPONSE.ok:
    KINOPOISK = RESPONSE.json()
else:
    print(fstr(URL) + str(RESPONSE))
    exit(0)
#
URL = 'https://plus.kinopoisk.ru/film/%s/details/?tabId=info' % ID
RESPONSE = requests.get(URL, headers=HEADERS_0)
if RESPONSE.ok:
    KINOPOISK_INFO = RESPONSE.text
else:
    print(fstr(URL) + str(RESPONSE))
    exit(0)
#
URL = 'https://www.kinopoisk.ru/film/%s/studio/' % ID
RESPONSE = requests.get(URL, headers=HEADERS_0)
if RESPONSE.ok:
    KINOPOISK_INFO_OLD = RESPONSE.text
else:
    print(fstr(URL) + str(RESPONSE))
    exit(0)

FILM = {}
FILM['Название Фильма'] = KINOPOISK['state']['movies'][ID]['title']
FILM['Обложка'] = 'https:' + KINOPOISK['state']['movies'][ID]['image']['sources'][0]['srcset']['1x']
FILM['Постер'] = 'https://www.kinopoisk.ru/images/film_big/%s.jpg' % ID
FILM['Рейтинг'] = KINOPOISK['state']['movies'][ID]['ratingData']['rating']['rate']
CASTS = BeautifulSoup(KINOPOISK['content'], "lxml").body.contents
INFO = BeautifulSoup(KINOPOISK_INFO, "lxml")
FILM['Описание'] = INFO.find('div', {'class': 'kinoisland__content',
                                     'itemprop':'description'}).text
INFO = INFO.find('table', {'class':'film-info film-info_general film-info_main'}).contents

STUDIO_TAGS = BeautifulSoup(KINOPOISK_INFO_OLD, "lxml").find('table', {'border':'0', 'width':'80%'})
IS_STUDIO = False
if STUDIO_TAGS is not None:
    IS_STUDIO = True
    STUDIO_TAGS = STUDIO_TAGS.contents

# Студии
STUDIOS = []
STUDIOS_STRING = ''
if IS_STUDIO:
    for tag in STUDIO_TAGS:
        try:
            STUDIOS.append(tag.find('a').text)
        except AttributeError:
            pass
    STUDIOS_STRING = ', '.join(STUDIOS)


# Основная информация
for el in INFO:
    key = el.td.text
    value = el.td.nextSibling.text
    if key != 'Сборы' and key != 'Зрители':
        FILM[key] = value

# Съемочная группа
for div in CASTS:
    cast = div.div.text
    is_actor = False
    if cast == '':
        cast = 'Актёр'
        tags = div.find('div', {'class':'actors-table'}).contents
        is_actor = True
    else:
        tags = div.find('div', {'class':'paginated-list'}).contents
    FILM[cast] = {}
    for el in tags:
        if is_actor and el['class'][0] != 'actors-table__row':
            continue
        tag_info = el.find('div', {'class':'person__info'})
        if tag_info is None:
            continue
        person = tag_info.find('div', {'class':'person__info-name-wrap'}).a.text
        person_id = el.a['href'].split('/')[2]
        photo = 'https://st.kp.yandex.net/images/actor_iphone/iphone360_%s.jpg' % person_id
        FILM[cast][person] = {}
        FILM[cast][person]['Фото'] = photo
        for tag in tag_info.contents:
            if tag['class'][0] != 'person__info-name-wrap':
                FILM[cast][person][tag['class'][0]] = tag.text

IS_DIRECTOR = False
IS_ACTOR = False
IS_GENRE = False
IS_COUNTRY = False

if 'Режиссёр' in FILM:
    IS_DIRECTOR = True
if 'Актёр' in FILM:
    IS_ACTOR = True
if 'Жанр' in FILM:
    IS_GENRE = True
if 'Страна' in FILM:
    IS_COUNTRY = True

if 'Сценарист' in FILM:
    WRITERS = ', '.join(FILM['Сценарист'])
else:
    WRITERS = ''
if IS_DIRECTOR:
    DIRECTORS = ', '.join(FILM['Режиссёр'])
else:
    DIRECTORS = ''
if 'Название Фильма' not in FILM:
    print('Нет названия фильма')
    exit(0)
if 'Описание' not in FILM:
    FILM['Описание'] = ''
if 'Слоган' not in FILM:
    FILM['Слоган'] = ''
if 'Рейтинг' not in FILM:
    FILM['Рейтинг'] = ''
if not IS_GENRE:
    FILM['Жанр'] = ''
if 'Оригинальное название' not in FILM:
    FILM['Оригинальное название'] = ''
if 'Страна' not in FILM:
    FILM['Страна'] = ''
if 'Год производства' not in FILM:
    FILM['Год производства'] = ''


# Добавляем режиссеров
if IS_DIRECTOR:
    SQL_DIRECTOR = "INSERT INTO director_link ('actor_id','media_id','media_type') VALUES (?,?,'movie')"
    SQL_DIRECTOR_VALUES = []
    for director in FILM['Режиссёр']:
        C.execute("SELECT actor_id FROM actor WHERE name=? LIMIT 1", (director,))
        id_director = C.fetchone()
        if id_director is None:
            C.execute("INSERT INTO actor ('name') VALUES (?)", (director,))
            CONN.commit()
            C.execute("SELECT last_insert_rowid()")
            id_director = C.fetchone()[0]
        else:
            id_director = id_director[0]
        # Собираем связи фильм с жанром
        SQL_DIRECTOR_VALUES.append((id_director, ID))


# Добавляем студии
if IS_STUDIO:
    SQL_STUDIO = "INSERT INTO studio_link ('studio_id','media_id','media_type') VALUES (?,?,'movie')"
    SQL_STUDIO_VALUES = []
    for studio in STUDIOS:
        C.execute("SELECT studio_id FROM studio WHERE name=? LIMIT 1", (studio,))
        id_studio = C.fetchone()
        if id_studio is None:
            C.execute("INSERT INTO studio ('name') VALUES (?)", (studio,))
            CONN.commit()
            C.execute("SELECT last_insert_rowid()")
            id_studio = C.fetchone()[0]
        else:
            id_studio = id_studio[0]
        # Собираем связи фильм с жанром
        SQL_STUDIO_VALUES.append((id_studio, ID))

# Добавляем актеров
if IS_ACTOR:
    SQL_ART = "INSERT INTO art ('media_id','media_type','type','url') VALUES(?,'actor','thumb',?)"
    SQL_ACTOR = '''INSERT INTO actor_link
    ('actor_id','media_id','media_type','role','cast_order') VALUES (?,?,'movie',?,?)'''
    SQL_ACTOR_VALUES = []
    I = 0
    for actor in FILM['Актёр']:
        C.execute("SELECT actor_id FROM actor WHERE name=? LIMIT 1", (actor,))
        id_actor = C.fetchone()
        if id_actor is None:
            C.execute("INSERT INTO actor ('name') VALUES (?)", (actor,))
            CONN.commit()
            C.execute("SELECT last_insert_rowid()")
            id_actor = C.fetchone()[0]
            C.execute(SQL_ART, (id_actor, FILM['Актёр'][actor]['Фото']))
            CONN.commit()
        else:
            id_actor = id_actor[0]

        if 'person__info-character-name' in FILM['Актёр'][actor]:
            role = FILM['Актёр'][actor]['person__info-character-name']
        else:
            role = ''
        # Собираем связи фильм с актером
        SQL_ACTOR_VALUES.append((id_actor, ID, role, I))
        I = I + 1

# Добавляем жанр если его нет
if IS_GENRE:
    SQL_GENRE = "INSERT INTO genre_link ('genre_id','media_id','media_type') VALUES (?,?,'movie')"
    SQL_GENRE_VALUES = []
    GENRES = FILM['Жанр'].split(', ')
    for genre in GENRES:
        C.execute("SELECT genre_id FROM genre WHERE name=? LIMIT 1", (genre,))
        id_genre = C.fetchone()
        if id_genre is None:
            C.execute("INSERT INTO genre ('name') VALUES (?)", (genre,))
            CONN.commit()
            C.execute("SELECT last_insert_rowid()")
            id_genre = C.fetchone()[0]
        else:
            id_genre = id_genre[0]
        # Собираем связи фильм с жанром
        SQL_GENRE_VALUES.append((id_genre, ID))


# Добавляем страны если их нет
if IS_COUNTRY:
    SQL_COUNTRY = "INSERT INTO country_link ('country_id','media_id','media_type') VALUES (?,?,'movie')"
    SQL_COUNTRY_VALUES = []
    COUNTRIES = FILM['Страна'].split(', ')
    for country in COUNTRIES:
        C.execute("SELECT country_id FROM country WHERE name=? LIMIT 1", (country,))
        id_country = C.fetchone()
        if id_country is None:
            C.execute("INSERT INTO country ('name') VALUES (?)", (country,))
            CONN.commit()
            C.execute("SELECT last_insert_rowid()")
            id_country = C.fetchone()[0]
        else:
            id_country = id_country[0]
        # Собираем связи фильма с страной
        SQL_COUNTRY_VALUES.append((id_country, ID))


FOLDER = 'strm'
# Создаем папку если ее нет
try:
    os.mkdir(FOLDER)
except OSError:
    pass

FOLDER = os.path.abspath(FOLDER) + '/'

# Добавляем path если его нет
C.execute("SELECT idPath FROM path WHERE strPath=? LIMIT 1", (FOLDER,))
ID_PATH = C.fetchone()
if ID_PATH is None:
    C.execute("INSERT INTO path ('strPath') VALUES (?)", (FOLDER,))
    CONN.commit()
    C.execute("SELECT last_insert_rowid()")
    ID_PATH = C.fetchone()[0]
else:
    ID_PATH = ID_PATH[0]

# Добавляем file
SQL_FILES = "INSERT INTO files ('idPath','strFilename') VALUES (?,?)"
FILE_NAME = FILM['Название Фильма'] + ' (%s).strm' % FILM['Год производства']
FILE_NAME = FILE_NAME.replace('/','')
C.execute(SQL_FILES, (ID_PATH, FILE_NAME))
CONN.commit()
C.execute("SELECT last_insert_rowid()")
ID_FILE = C.fetchone()[0]

# Создаем файл
try:
    open(FOLDER + FILE_NAME, 'w').close()
except IOError:
    print('Ошибка в имени файла: ' + FILE_NAME)

# Добавляем связи
if IS_DIRECTOR:
    C.executemany(SQL_DIRECTOR, SQL_DIRECTOR_VALUES)
if IS_STUDIO:
    C.executemany(SQL_STUDIO, SQL_STUDIO_VALUES)
if IS_GENRE:
    C.executemany(SQL_GENRE, SQL_GENRE_VALUES)
if IS_COUNTRY:
    C.executemany(SQL_COUNTRY, SQL_COUNTRY_VALUES)
if IS_ACTOR:
    C.executemany(SQL_ACTOR, SQL_ACTOR_VALUES)

# Добавляем фильм
SQL = '''INSERT INTO movie
(idMovie,idFile,c00,c01,c03,c05,c06,c14,c15,c16,c18,c21,premiered,userrating)
VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''
C.execute(SQL, (ID, ID_FILE, FILM['Название Фильма'], FILM['Описание'],
                '"' + FILM['Слоган'] + '"', FILM['Рейтинг'], WRITERS,
                FILM['Жанр'], DIRECTORS, FILM['Оригинальное название'],
                STUDIOS_STRING, FILM['Страна'], FILM['Год производства'], FILM['Рейтинг']))

# Добавляем постер
SQL = "INSERT INTO art ('media_id','media_type','type','url')"
SQL += "VALUES (?,'movie','poster',?)"
C.execute(SQL, (ID, FILM['Постер']))

# Добавляем обложку
SQL = "INSERT INTO art ('media_id','media_type','type','url')"
SQL += "VALUES (?,'movie','fanart',?)"
C.execute(SQL, (ID, FILM['Обложка']))

# Коммитим
CONN.commit()
CONN.close()

print (fstr(ID) + 'Добавлен')
