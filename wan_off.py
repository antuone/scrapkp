# -*- coding: utf-8 -*-
'''
    Исследование выключения интернета у роутера
'''
import requests

URL = 'http://192.168.0.50/index.cgi?v2=y&rq=1&res_config_id0=1&res_config_action0=3&res_json0=y&res_data_type0=json&res_struct_size0=36&res_pos0=0&res_buf0={%22eth1%22:{%22enable%22:true,%22max_count%22:3,%22mtu%22:1500,%22port%22:%22WAN%22,%22type%22:%22ethernet%22,%22is_wan%22:true,%22services%22:{%22eth1_2%22:{%22contag%22:2,%22firewall%22:true,%22rip%22:false,%22apn%22:%22%22,%22username%22:%22v41788632%22,%22level%22:3,%22mtu%22:1492,%22iface%22:%22ppp0%22,%22dns_prim%22:%22212.33.225.212%22,%22ppp_ip_ext%22:false,%22dial_num%22:%22%22,%22enable%22:false,%22password%22:%22w5cgn95fccA%22,%22gwif%22:true,%22metric%22:50,%22encrypt%22:%220%22,%22igmp%22:true,%22nat%22:true,%22type%22:%22ppp%22,%22auto%22:false,%22ppp_state%22:5,%22keep_alive%22:{%22interval%22:30,%22fails%22:3},%22servicename%22:%22domru.ru%22,%22is_wan%22:true,%22static_ip%22:%22%22,%22auth%22:%220%22,%22contype%22:%22pppoe%22,%22mask%22:%22255.255.255.255%22,%22noauth%22:false,%22name%22:%22pppoe_WAN_1%22,%22extra_options%22:%22%22,%22dns_sec%22:%225.3.3.3%22,%22ifname%22:%22eth1_2%22,%22ppp_debug%22:false,%22pppoe_pass_through%22:false,%22ping_respond%22:true,%22unit%22:0,%22l2_iface%22:%22eth1%22,%22ip%22:%2246.146.140.248%22,%22gateway%22:%2210.95.255.126%22,%22ismyiface%22:true,%22connection_status%22:%22Connected%22}},%22ifname%22:%22eth1%22,%22ismyiface%22:true}}&proxy=y&_=1484814367261'
HEADERS = {
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
requests.get(URL, headers=HEADERS)
