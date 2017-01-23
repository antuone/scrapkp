# -*- coding: utf-8 -*-
'''
    Скребок кинопоиска
'''
import os
import sys
import sqlite3
import time
import requests
import threading
from bs4 import BeautifulSoup

def echo(_str):
    ''' печатает строку '''
    print(_str)

URL_WAN_ON  = 'http://192.168.0.50/index.cgi?v2=y&rq=1&res_config_id0=1&res_config_action0=3&res_json0=y&res_data_type0=json&res_struct_size0=36&res_pos0=0&res_buf0={%22eth1%22:{%22enable%22:true,%22max_count%22:3,%22mtu%22:1500,%22port%22:%22WAN%22,%22type%22:%22ethernet%22,%22is_wan%22:true,%22services%22:{%22eth1_2%22:{%22rip%22:false,%22contag%22:2,%22firewall%22:true,%22level%22:3,%22apn%22:%22%22,%22username%22:%22v41788632%22,%22mtu%22:1492,%22iface%22:%22ppp0%22,%22dns_prim%22:%22212.33.225.212%22,%22ppp_ip_ext%22:false,%22dial_num%22:%22%22,%22password%22:%22w5cgn95fccA%22,%22enable%22:true,%22gwif%22:true,%22nat%22:true,%22igmp%22:true,%22metric%22:50,%22encrypt%22:%220%22,%22type%22:%22ppp%22,%22servicename%22:%22domru.ru%22,%22ppp_state%22:5,%22keep_alive%22:{%22interval%22:30,%22fails%22:3},%22auto%22:false,%22is_wan%22:true,%22auth%22:%220%22,%22static_ip%22:%22%22,%22contype%22:%22pppoe%22,%22noauth%22:false,%22mask%22:%22255.255.255.255%22,%22name%22:%22pppoe_WAN_1%22,%22extra_options%22:%22%22,%22ifname%22:%22eth1_2%22,%22dns_sec%22:%225.3.3.3%22,%22ppp_debug%22:false,%22pppoe_pass_through%22:false,%22ping_respond%22:true,%22unit%22:0,%22l2_iface%22:%22eth1%22,%22ip%22:%2246.147.58.54%22,%22gateway%22:%2210.95.255.254%22,%22ismyiface%22:true,%22connection_status%22:%22Disconnected%22}},%22ifname%22:%22eth1%22,%22ismyiface%22:true}}&proxy=y&_=1484814367259'
URL_WAN_OFF = 'http://192.168.0.50/index.cgi?v2=y&rq=1&res_config_id0=1&res_config_action0=3&res_json0=y&res_data_type0=json&res_struct_size0=36&res_pos0=0&res_buf0={%22eth1%22:{%22enable%22:true,%22max_count%22:3,%22mtu%22:1500,%22port%22:%22WAN%22,%22type%22:%22ethernet%22,%22is_wan%22:true,%22services%22:{%22eth1_2%22:{%22contag%22:2,%22firewall%22:true,%22rip%22:false,%22apn%22:%22%22,%22username%22:%22v41788632%22,%22level%22:3,%22mtu%22:1492,%22iface%22:%22ppp0%22,%22dns_prim%22:%22212.33.225.212%22,%22ppp_ip_ext%22:false,%22dial_num%22:%22%22,%22enable%22:false,%22password%22:%22w5cgn95fccA%22,%22gwif%22:true,%22metric%22:50,%22encrypt%22:%220%22,%22igmp%22:true,%22nat%22:true,%22type%22:%22ppp%22,%22auto%22:false,%22ppp_state%22:5,%22keep_alive%22:{%22interval%22:30,%22fails%22:3},%22servicename%22:%22domru.ru%22,%22is_wan%22:true,%22static_ip%22:%22%22,%22auth%22:%220%22,%22contype%22:%22pppoe%22,%22mask%22:%22255.255.255.255%22,%22noauth%22:false,%22name%22:%22pppoe_WAN_1%22,%22extra_options%22:%22%22,%22dns_sec%22:%225.3.3.3%22,%22ifname%22:%22eth1_2%22,%22ppp_debug%22:false,%22pppoe_pass_through%22:false,%22ping_respond%22:true,%22unit%22:0,%22l2_iface%22:%22eth1%22,%22ip%22:%2246.146.140.248%22,%22gateway%22:%2210.95.255.126%22,%22ismyiface%22:true,%22connection_status%22:%22Connected%22}},%22ifname%22:%22eth1%22,%22ismyiface%22:true}}&proxy=y&_=1484814367261'

HEADERS_WAN = {
    'Host': '192.168.0.50',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'http://192.168.0.50/index.cgi',
    'Cookie': 'user_ip=192.168.0.87; cookie_lang=rus; url_hash=network%2Fwan; lan_ip=192.168.0.50; client_login=admin; client_password=LIST78!%4038pps%3D',
    'DNT': '1',
    'Connection': 'keep-alive'
}

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

def rocket(ID, number):
    ''' rocket jump '''
    ID = str(ID)
    echo('Поток %d, Фильм %s в обработке' % (number, ID))
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
    try:
        URL = 'https://plus.kinopoisk.ru/film/%s/details/cast/' % ID
        RESPONSE1 = requests.get(URL, headers=HEADERS, timeout=3)
        URL = 'https://plus.kinopoisk.ru/film/%s/details/?tabId=info' % ID
        RESPONSE2 = requests.get(URL, headers=HEADERS_0, timeout=3)
        URL = 'https://www.kinopoisk.ru/film/%s/studio/' % ID
        RESPONSE3 = requests.get(URL, headers=HEADERS_0, timeout=3)
    except Exception:
        time.sleep(number)
        echo('Поток %d поймал исключение' % number)

        if IS_WAN_SWITCH[0] is True:
            echo('Поток %d встал на паузу' % number)
            PAUSE[number] = True
            EVENT_PAUSE.wait()
            EVENT_PAUSE.clear()
        else:
            IS_WAN_SWITCH[0] = True
            PAUSE[number] = True
            while True:
                echo('Поток %d ждет остальные потоки' % number)
                is_all_pause = True
                for pewq in PAUSE:
                    if pewq is False:
                        is_all_pause = False
                if is_all_pause is True:
                    echo('Поток %d ОТКЛЮЧАЕТ ИНТЕРНЕТ' % number)
                    requests.get(URL_WAN_OFF, headers=HEADERS_WAN)
                    time.sleep(20)
                    echo('Поток %d ВКЛЮЧАЕТ ИНТЕРНЕТ' % number)
                    requests.get(URL_WAN_ON, headers=HEADERS_WAN)
                    time.sleep(20)
                    echo('Поток %d ОТМЕНЯЕТ ПАУЗУ' % number)
                    IS_WAN_SWITCH[0] = False
                    for pqwe in PAUSE:
                        PAUSE[pqwe] = False
                    EVENT_PAUSE.set()
                    break
                else:
                    time.sleep(1)
        threading.Thread(target=rocket, args=(ID, number)).start()
        return 0

    if RESPONSE1.ok:
        KINOPOISK = RESPONSE1.json()
    else:
        print(fstr(URL) + str(RESPONSE1))
        exit(0)
    if RESPONSE2.ok:
        KINOPOISK_INFO = RESPONSE2.text
    else:
        print(fstr(URL) + str(RESPONSE2))
        exit(0)
    if RESPONSE3.ok:
        KINOPOISK_INFO_OLD = RESPONSE3.text
    else:
        print(fstr(URL) + str(RESPONSE3))
        exit(0)

    FILM = {}
    FILM['Название Фильма'] = KINOPOISK['state']['movies'][ID]['title']
    if KINOPOISK['state']['movies'][ID]['image'] is not None:
        for qwe in KINOPOISK['state']['movies'][ID]['image']['sources'][0]['srcset']:
            FILM['Обложка'] = qwe
            break
    FILM['Постер'] = 'https://www.kinopoisk.ru/images/film_big/%s.jpg' % ID
    if 'rating' in KINOPOISK['state']['movies'][ID]['ratingData']:
        FILM['Рейтинг'] = KINOPOISK['state']['movies'][ID]['ratingData']['rating']['rate']
    try:
        CASTS = BeautifulSoup(KINOPOISK['content'], "lxml").body.contents
    except AttributeError:
        CASTS = []
    INFO = BeautifulSoup(KINOPOISK_INFO, "lxml")
    DESRIPTION = INFO.find('div', {'class': 'kinoisland__content',
                                        'itemprop':'description'})
    if DESRIPTION is not None:
        FILM['Описание'] = DESRIPTION.text
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
    if 'Обложка' not in FILM:
        FILM['Обложка'] = ''
    # Соединяемся с БД медиатеки
    CONN = sqlite3.connect('/mnt/ram/MyVideos108.db')
    C = CONN.cursor()

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
        for item in SQL_DIRECTOR_VALUES:
            try:
                C.execute(SQL_DIRECTOR, (item[0], item[1]))
            except sqlite3.IntegrityError:
                pass
        # C.executemany(SQL_DIRECTOR, SQL_DIRECTOR_VALUES)
    if IS_STUDIO:
        for item in SQL_STUDIO_VALUES:
            try:
                C.execute(SQL_STUDIO, (item[0], item[1]))
            except sqlite3.IntegrityError:
                pass
        # C.executemany(SQL_STUDIO, SQL_STUDIO_VALUES)
    if IS_GENRE:
        for item in SQL_GENRE_VALUES:
            try:
                C.execute(SQL_GENRE, (item[0], item[1]))
            except sqlite3.IntegrityError:
                pass
        # C.executemany(SQL_GENRE, SQL_GENRE_VALUES)
    if IS_COUNTRY:
        for item in SQL_COUNTRY_VALUES:
            try:
                C.execute(SQL_COUNTRY, (item[0], item[1]))
            except sqlite3.IntegrityError:
                pass
        # C.executemany(SQL_COUNTRY, SQL_COUNTRY_VALUES)
    if IS_ACTOR:
        for item in SQL_ACTOR_VALUES:
            try:
                C.execute(SQL_ACTOR, (item[0], item[1], item[2], item[3]))
            except sqlite3.IntegrityError:
                pass
        # C.executemany(SQL_ACTOR, SQL_ACTOR_VALUES)

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

    COUNTER[0] = COUNTER[0] + 1
    echo('Поток %d, Фильм %s добавлен, Счетчик %d' % (number, ID, COUNTER[0]))
    if len(IDS) > 0:
        threading.Thread(target=rocket, args=(IDS.pop(0)[0], number)).start()

SQL = 'SELECT id FROM LIST_id WHERE id not in (SELECT idMovie FROM movie)'
# Соединяемся с БД медиатеки
conn = sqlite3.connect('/mnt/ram/MyVideos108.db')
cursor = conn.cursor()
# Добавляем список ID
cursor.execute(SQL)
IDS = cursor.fetchall()
conn.close()

EVENT_PAUSE = threading.Event()
IS_WAN_SWITCH = [False]
COUNTER = [0]
PAUSE = []
K = 7
for i in range(K):
    threading.Thread(target=rocket, args=(IDS.pop(0)[0], i)).start()
    PAUSE.append(False)
