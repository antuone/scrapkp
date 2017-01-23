# -*- coding: utf-8 -*-
import os
import requests

FOLDER = 'futuron'

SETS = [679491, 679492, 679498, 679499, 679500, 679501, 685283,
        685308, 695388, 695393, 883189, 930891, 931014, 931090,
        931497, 931516, 931539, 931566, 1032568, 1033580, 1033597,
        1036441, 1036505, 1042576, 1526186, 1587597, 1661590]

GENRES = [121622, 121623, 121624, 121625, 121626, 121627, 121628,
          121629, 121630, 121632, 121633, 121634, 121635, 121636,
          121637, 121638, 121639, 121640, 121641, 121642, 121643,
          121644, 121645, 121646]

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
            "rangeSize":1}}}

# Создаем папку если ее нет
try:
    os.mkdir(FOLDER)
except OSError:
    pass


# Запрашиваем и получаем фильмы
URL = 'http://futuron.name/futuron/catalog/data/items'

def create_files(json):
    ''' создает файлы '''
    response = requests.post(URL, json=json).json()
    if 'data' in response:
        films = response["data"]["sections"][0]["items"]
    else:
        return
    # Перебор всех фильмов и создание файлов
    for film in films:
        if 'rusName' in film:
            name = film['rusName']
        elif 'engName' in film:
            name = film['engName']
        else:
            continue

        if 'releaseYear' in film:
            name += '.' + str(film['releaseYear'])

        name += '.mkv'
        name = name.replace('/', ' ')

        try:
            open(FOLDER + '/' + name, 'w').close()
        except IOError:
            print u'Ошибка в имени файла: ' + name

for _set in SETS:
    JSON['sections']['FILMS']['sets'] = [_set]
    create_files(JSON)

JSON['sections']['FILMS']['sets'] = []
for genre in GENRES:
    JSON['sections']['FILMS']['genres'] = [genre]
    create_files(JSON)

