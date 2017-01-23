# -*- coding: utf-8 -*-
import os
import requests

FOLDER = 'futuron'
FOLDER_SUB = 'comedy'

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
            "genres":["121642"],
            "offset":0,
            "rangeSize":1000}}}

# Запрашиваем и получаем фильмы
URL = 'http://futuron.name/futuron/catalog/data/items'
FILMS = requests.post(URL, json=JSON).json()["data"]["sections"][0]["items"]

# Создаем папку если ее нет
try:
    os.mkdir(FOLDER)
except OSError:
    pass
# Создаем подпапку
try:
    os.mkdir(FOLDER + '/' + FOLDER_SUB)
except OSError:
    pass

# Перебор всех фильмов и создание файлов
for film in FILMS:
    if 'rusName' in film:
        name = film['rusName']

    if 'engName' in film:
        name += ' ' + film['engName']

    name += ' ' + str(film['releaseYear'])
    name += '.mkv'

    name = name.replace('/', ' ')

    try:
        open(FOLDER + '/'+ FOLDER_SUB + '/' + name, 'w').close()
    except IOError:
        print u'Ошибка в имени файла: ' + name
