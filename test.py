# -*- coding: utf-8 -*-
import sqlite3
import requests

SQL_GENRE = "INSERT INTO genre_link ('genre_id','media_id','media_type')"
SQL_GENRE += "VALUES ('%d','%d','movie')"

MONTHS = {
    u'января':1,
    u'февраля':2,
    u'марта':3,
    u'апреля':4,
    u'мая':5,
    u'июня':6,
    u'июля':7,
    u'августа':8,
    u'сентября':9,
    u'октября':10,
    u'ноября':11,
    u'декабря':12}

def value0(key, variable):
    '''Возвращает переменную если она существует'''
    if key in variable and len(variable[key]) > 0:
        return variable[key][0]
    else:
        return ''

# json для запроса фильмов с футурона
JSON_FUTURON = {
    "selection":"",
    "type":"FILMS",
    "text":"",
    "countries":[],
    "years":[],
    "rate":0,
    "sections":{
        "FILMS":{
            "name":"",
            "season":"",
            "director":"",
            "actor":"",
            "studio":"",
            "translations":[],
            "sndquality":[],
            "sets":[],
            "genres":[],
            "offset":10,
            "rangeSize":100}}}

# Запрашиваем и получаем фильмы
URL_FUTURON = 'http://futuron.name/futuron/catalog/data/items'
FILMS_FUTURON = requests.post(URL_FUTURON, json=JSON_FUTURON).json()["data"]["sections"][0]["items"]

# Соединяемся с БД медиатеки
CONN = sqlite3.connect('Database/MyVideos108.db')
C = CONN.cursor()
URL_PLUGIN = 'plugin://plugin.video.giraffe.seasonvar/'

# Перебор всех фильмов и запись их в медиатеку
for film_futuron in FILMS_FUTURON:
    # Запрашиваем ссылку на фильм в футуроне
    url = 'http://futuron.name/futuron/catalog/data/item/files?id=' + str(film_futuron["id"])
    video = requests.post(url).json()["data"][0]["mp4Url"]

    # Запрашиваем список фильмов с "кинопоиска" подходящих по названию с футурона
    url = 'http://kparser.pp.ua/json/search/' + film_futuron["rusName"]
    films_kparser = requests.get(url).json()["result"]

    # Если в этом списке найден атрибут ["most_wanted"] == 1
    # Тогда продолжаем и останавливаем перебор чтобы остановится на этом фильме
    for film_kparser in films_kparser:
        if film_kparser["most_wanted"] == 1:
            break
    if film_kparser["most_wanted"] == 0:
        continue

    # запрашиваем с "кинопоиска" данные об фильме
    url = 'http://kparser.pp.ua/json/film/' + film_kparser["id"]
    film = requests.get(url).json()

    print film_kparser["id"]


    # Проверяем есть ли такой фильм уже в медиатеке
    # Если есть переходим к следующиму фильму
    C.execute("SELECT idMovie FROM movie WHERE c00='%s' LIMIT 1" % film["name"][0])
    if C.fetchone() != None:
        print u'Такой фильм уже есть в медиатеке: ' + film['name'][0]
        continue

    # Проверяем есть ли path в таблице
    # Если нет, то добавляем
    C.execute("SELECT idPath FROM path WHERE strPath='%s' LIMIT 1" % URL_PLUGIN)
    id_path = C.fetchone()
    if id_path is None:
        C.execute("INSERT INTO path ('strPath') VALUES ('%s')" % URL_PLUGIN)
        CONN.commit()
        C.execute("SELECT last_insert_rowid()")
        id_path = C.fetchone()[0]
    else:
        id_path = id_path[0]

    # Добавляем ссылку фильма
    C.execute("INSERT INTO files ('idPath','strFilename') VALUES ('%d','%s')" % (
        id_path, "plugin://plugin.video.giraffe.seasonvar/?action=play&url=" + video)
             )
    CONN.commit()
    C.execute("SELECT last_insert_rowid()")
    id_file = C.fetchone()[0]

    # Формируем список скриншотов который пойдет в список фанарта
    fanarts = '<fanart>'
    for fanart in film_futuron['screenshotsURL']:
        fanarts += "<thumb>%s</thumb>" % fanart
    fanarts += '</fanart>'

    # Проверяем и форматируем данные
    studio = value0('company', film)
    premiered = value0('world_start', film)

    if premiered != "":
        premiered = premiered.split(' ')
        for month in MONTHS:
            if premiered[1] == month:
                premiered[1] = str(MONTHS[month])
                break
        premiered = premiered[2] + '-' + premiered[1] + '-' + premiered[0]
    else:
        premiered = str(film_futuron['releaseYear']) + '-1-1'

    # Добавляем фильм
    sql = "INSERT INTO movie ('idFile','c00','c01','c05','c06',"
    sql += "'c20','c14','c15','c18','c19','c21','c23','premiered')"
    sql += "VALUES ('%d','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"
    sql = sql % (
        id_file,
        film["name"][0],
        film["description"][0],
        film["aggregateRating"][0]["properties"]["ratingValue"][0],
        film["story_by"][0],
        fanarts,
        film["genre"][0],
        film["director"][0],
        studio,
        "plugin://plugin.video.youtube/?action=play_video&videoid="+film_futuron["youtubeId"],
        film["country"][0],
        id_path,
        premiered
    )
    C.execute(sql)

    # Коммитим чтобы дальше можно было узнать идентификатор
    CONN.commit()

    # Узнаем идентификатор фильма
    C.execute("SELECT last_insert_rowid()")
    id_media = C.fetchone()[0]

    # Добавляем обложку для фильма (poster)
    if film['image'][0] == 'https://st.kp.yandex.net/images/movies/poster_none.png':
        film['image'][0] = film_futuron['coverMaxiURL']

    poster = film["image"][0].replace('iphone', 'big').replace('big360_', '')

    sql = "INSERT INTO art ('media_id','media_type','type','url')"
    sql += "VALUES ('%d','movie','poster','%s')"
    sql = sql % (
        id_media,
        poster
    )
    C.execute(sql)

    background = value0('thumbnailUrl', film)
    if background == '':
        background = value0('screenshotsURL', film_futuron)

    # Добавляем фон (fanart)
    sql = "INSERT INTO art ('media_id','media_type','type','url')"
    sql += "VALUES ('%d','movie','fanart','%s')"
    sql = sql % (
        id_media,
        background
    )
    C.execute(sql)


    # Добавляем жанр если его нет
    film['genre'].pop(0)
    for genre in film['genre']:
        C.execute("SELECT genre_id FROM genre WHERE name='%s' LIMIT 1" % genre)
        id_genre = C.fetchone()
        if id_genre is None:
            C.execute("INSERT INTO genre ('name') VALUES ('%s')" % genre)
            CONN.commit()
            C.execute("SELECT last_insert_rowid()")
            id_genre = C.fetchone()[0]
        else:
            id_genre = id_genre[0]

        # Добавляем связь фильм с жанром
        sql = SQL_GENRE % (
            id_genre,
            id_media
        )
        C.execute(sql)

    # Коммитим
    CONN.commit()

C.close()
