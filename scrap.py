# -*- coding: utf-8 -*-
'''
    Скребок кинопоиска
'''
import os
import sys
import sqlite3
import lib

ID = sys.argv[1]
print (lib.fstr(ID) + 'В процессе')


# Соединяемся с БД медиатеки
CONN = sqlite3.connect('/home/antuone/.kodi/userdata/Database/MyVideos108.db')
C = CONN.cursor()

# Проверяем есть ли такой фильм уже в медиатеке
C.execute("SELECT idMovie FROM movie WHERE idMovie=? LIMIT 1", (ID,))
if C.fetchone() != None:
    print(lib.fstr(ID) + 'Такой фильм уже есть в медиатеке')
    exit(0)

URL = 'https://plus.kinopoisk.ru/film/%s/details/' % ID
SOUP = lib.get_soup(URL)

TITLE = SOUP.find('title').text
if TITLE == 'Несуществующая страница — КиноПоиск+':
    print('%s - Несуществующая страница' % ID)
    exit(0)

URL_CAST = 'https://plus.kinopoisk.ru/film/%s/details/cast/' % ID
URL_STUDIO = 'https://www.kinopoisk.ru/film/%s/studio/' % ID

FILM = {}
FILM['Идентификатор'] = ID
FILM['Название Фильма'] = SOUP.find('h2', {'class': 'popup__heading'}).text
FILM['Обложка'] = SOUP.find('source', {'class': 'image__source',
                                       'media':'(min-width: 1340px)'})['srcset'].split(' ')[0]
FILM['Обложка'] = 'https:' + FILM['Обложка']

FILM['Постер'] = 'https://www.kinopoisk.ru/images/film_big/%s.jpg' % ID
FILM['Рейтинг'] = SOUP.find('div', {'class': 'rating-button__rating',
                                    'data-reactid':'3'}).text
FILM['Описание'] = SOUP.find('div', {'class': 'kinoisland__content',
                                     'itemprop':'description'}).text

INFO = SOUP.find('table', {'class': 'film-info film-info_general film-info_main'}).contents
CASTS = lib.get_soup(URL_CAST).find('div', {'class':'popup__content'}).contents
STUDIO_TAGS = lib.get_soup(URL_STUDIO).find('table', {'border':'0', 'width':'80%'})
if STUDIO_TAGS is None:
    IS_STUDIO = False
else:
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
    if key == 'Сборы':
        pass
        # FILM[key] = lib.get_revenues(el.td.nextSibling)
    elif key == 'Зрители':
        pass
        # FILM[key] = lib.get_viewers(el.td.nextSibling)
    else:
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
        tags = div.div.nextSibling.div.contents
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
IS_STUDIO = False
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
if 'Жанр' not in FILM:
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
# FILE_NAME = FILE_NAME.replace('/','')
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
SQL = '''INSERT INTO movie (idMovie,idFile,c00,c01,c03,c05,c06,c14,c15,c16,c18,c21,premiered)
VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)'''
C.execute(SQL, (ID, ID_FILE, FILM['Название Фильма'], FILM['Описание'],
                '"' + FILM['Слоган'] + '"', FILM['Рейтинг'], WRITERS,
                FILM['Жанр'], DIRECTORS, FILM['Оригинальное название'],
                STUDIOS_STRING, FILM['Страна'], FILM['Год производства']))

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

print (lib.fstr(ID) + 'Добавлен')
