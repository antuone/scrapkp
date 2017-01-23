# -*- coding: utf-8 -*-
# TEXT = u'Золотой ключ'

# def format_str(str, lenght=25):
#     k = len(str)
#     if k < lenght:
#         i = lenght - k
#         while i > 0:
#             str = ' ' + str
#             i = i - 1
#     str += ' : '
#     str = str.encode('utf-8')
#     return str

# print format_str(TEXT) + "Красивый"


# for key in FILM:
#     if isinstance(FILM[key], dict):
#         for key2 in FILM[key]:
#             if isinstance(FILM[key][key2], dict):
#                 for key3 in FILM[key][key2]:
#                     print fstr(key + ' ' + key2 + '(%s)' % key3) + FILM[key][key2][key3]
#             else:
#                 print fstr(key2 + '(%s)' % key) + FILM[key][key2]
#     else:
#         print fstr(key) + str(FILM[key])
import os
# Создаем папку если ее нет
try:
    os.mkdir('strm')
except OSError:
    pass
print os.path.abspath('strm')
