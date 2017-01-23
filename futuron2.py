# -*- coding: utf-8 -*-
import os
import requests

FOLDER_RUS = 'rus'
FOLDER_ENG = 'eng'

# json для запроса фильмов с футурона
JSON = {
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
            "offset":0,
            "rangeSize":1000}}}

# Запрашиваем и получаем фильмы
URL = 'http://futuron.name/futuron/catalog/data/items'
FILMS = requests.post(URL, json=JSON).json()["data"]["sections"][0]["items"]

# Создаем папку если ее нет
try:
    os.mkdir(FOLDER_RUS)
except OSError:
    pass

# Создаем папку если ее нет
try:
    os.mkdir(FOLDER_ENG)
except OSError:
    pass

# Перебор всех фильмов и создание файлов
for film in FILMS:
    if 'engName' in film:
        name = ' ' + film['engName']
        folder = FOLDER_ENG
    elif 'rusName' in film:
        name = film['rusName']
        folder = FOLDER_RUS
    else:
        continue

    name += ' ' + str(film['releaseYear'])
    name += '.mkv'

    name = name.replace('/', ' ')

    try:
        open(folder + '/' + name, 'w').close()
    except IOError:
        print u'Ошибка в имени файла: ' + name
