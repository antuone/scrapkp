# -*- coding: utf-8 -*-
import sqlite3

# Соединяемся с БД медиатеки
CONN = sqlite3.connect('/home/antuone/.kodi/userdata/Database/MyVideos108.db')
C = CONN.cursor()
SQL = "SELECT REPLACE(REPLACE(art_urls,'<thumb>',''),'</thumb>','') FROM actor WHERE art_urls LIKE '%actor%'"
C.execute(SQL)

for row in C.fetchall():
    print row[0]

# SQL = "UPDATE actor SET art_urls=REPLACE(art_urls,'actor/','actor_big/')"
# C.execute(SQL)
# SQL = "UPDATE art SET url=REPLACE(url,'actor/','actor_big/')"
# C.execute(SQL)
# CONN.commit()
# C.close()

# CONN = sqlite3.connect('/home/antuone/.kodi/userdata/Database/Textures13.db')
# C = CONN.cursor()
# SQL = "UPDATE texture SET url=REPLACE(url,'actor/','actor_big/')"
# C.execute(SQL)
# CONN.commit()
# C.close()
