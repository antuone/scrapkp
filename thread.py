# -*- coding: utf-8 -*-
'''
    Исследование многопоточности
'''
from threading import Thread

LIST_ID = [1, 2, 3, 4, 5, 6, 7, 8, 9]
STOP = [False]
def rocket():
    ''' Поток '''
    if STOP[0]:
        return 0
    _id = LIST_ID.pop()
    print(_id)
    if _id == 5:
        STOP[0] = True
    Thread(target=rocket).start()

# количество потоков
K = 3
for k in range(K):
    Thread(target=rocket).start()

