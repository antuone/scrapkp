# -*- coding: utf-8 -*-
'''
    Формирует список несоскрабеных ID 
'''
import sqlite3
SQL = 'SELECT id FROM LIST_id WHERE id not in (SELECT idMovie FROM movie)'
# Соединяемся с БД медиатеки
conn = sqlite3.connect('/mnt/ram/MyVideos108.db')
cursor = conn.cursor()
# Добавляем список ID
cursor.execute(SQL)
rows = cursor.fetchall()
conn.close()

for row in rows:
    print(row[0])
