# -*- coding: utf-8 -*-
'''
    Исследование скрипта:
        https://www.kinopoisk.ru/handler_trailer_popup.php
    Выдающего json  со списком трейлеров к фильмам
    Преимощество в нем в том что можно сразу запросить много фильмов
'''
import sqlite3
import threading
import time
import requests


URL = 'https://www.kinopoisk.ru/handler_trailer_popup.php'
HEADERS = {
    'Host': 'plus.kinopoisk.ru',
    'User-Agent':
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://www.kinopoisk.ru/top/navigator/m_act[genre]/6/order/rating/',
    'DNT': '1',
    'Connection': 'keep-alive'}
SQL = "INSERT INTO list_id (id, type) VALUES (?,?)"

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
def echo(_str):
    ''' печатает строку '''
    print(_str)

def get_ids(i):
    ''' возвращает строку с числами разделенных запяытой с промежутком 500 '''
    k = 500
    ids = []
    i = i * k
    j = i + k
    while i < j:
        ids.append(str(i+1))
        i = i + 1
    return ','.join(ids)

def rocket(position, step, number):
    ''' rocket jump '''

    data = {'ids':'%s' % get_ids(position)}
    try:
        response = requests.post(url=URL, data=data, timeout=3)
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
        threading.Thread(target=rocket, args=(position, step, number)).start()
        return 0

    json = response.json()
    # Соединяемся с БД медиатеки
    conn = sqlite3.connect('/mnt/ram/MyVideos108.db')
    cursor = conn.cursor()
    # Добавляем список ID
    for item in json['items']:
        _type = ''
        _id = item['fid']
        try:
            cursor.execute(SQL, (_id, _type))
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    COUNTER[0] = COUNTER[0] + 1
    threading.Thread(target=rocket, args=(position + step, step, number)).start()
    if len(json['items']) == 0:
        echo('Поток %d, Позиция %d не имеет фильмов, Счетчик %d' % (number, position, COUNTER[0]))
    else:
        echo('Поток %d, Позиция %d обработана, Счетчик %d' % (number, position, COUNTER[0]))

EVENT_PAUSE = threading.Event()
IS_WAN_SWITCH = [False]
COUNTER = [0]
PAUSE = []
K = 9
for i in range(K):
    threading.Thread(target=rocket, args=(i+300, K, i)).start()
    PAUSE.append(False)
