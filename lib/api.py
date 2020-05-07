import requests
import config
import json
import geoip2.database
import ipdb
import ipaddress
import socket
import time
from pathlib import Path


def get(target):
    url = ''
    data = {}
    if target == 'ip':
        url = config.get_ip_url
    elif target == 'domain':
        url = config.get_domain_url
    elif target == 'subdomain':
        url = config.get_subdomain_url
    if url:
        url = url + f'?key={config.key}'
        try:
            r = requests.post(url, timeout=3)
            data = r.json()
            if data['code'] == 1:
                return data
            elif data['code'] == 0:
                return data
        except Exception as e:
            data['code'] = 0
            data['msg'] = e
        return data


def put_alive(alive_data):
    try:
        url = config.put_alive_url + f'?key={config.key}'
        # print(json.dumps(alive_data))
        r = requests.post(url, data=json.dumps(alive_data))
        return r.json()
    except Exception as e:
        return e


def put_port(port_data):
    try:
        url = config.put_port_url + f'?key={config.key}'
        # print(json.dumps(port_data))
        r = requests.post(url, data=json.dumps(port_data))
        # print(r.text)
        return r.json()
    except Exception as e:
        return e


def put_subdomain(domain_data):
    try:
        n = 100
        subdomain_list = domain_data['data']
        for i in [subdomain_list[i:i + n] for i in range(0, len(subdomain_list), n)]:
            url = config.put_subdomain_url + f'?key={config.key}'
            domain_data['data'] = i
            r = requests.post(url, data=json.dumps(domain_data))
            time.sleep(1)
    except Exception as e:
        return e


def get_ip_info(ip, subdomian=''):
    ip_info = {'is_cdn': False, 'is_private': False, 'city': ''}
    try:
        if ip == '' and subdomian:
            addr = socket.getaddrinfo(subdomian, 'http')
            ip = addr[0][4][0]
            ip_info['ip'] = ip
        try:
            city_info = config.ip_db.find_map(ip, 'CN')
            if city_info['region_name'] == city_info['city_name']:
                ip_info['city'] = city_info['country_name'] + city_info['region_name'] + city_info['isp_domain']
            else:
                ip_info['city'] = city_info['country_name'] + city_info['region_name'] + city_info['city_name'] +\
                                  city_info['isp_domain']
        except Exception as e:
            ip_info['city'] = ''
        if ipaddress.ip_address(ip).is_private:
            ip_info['is_private'] = True
            return ip_info
        for cdn in config.cdn_list:
            if ipaddress.ip_address(ip) in ipaddress.ip_network(cdn):
                ip_info['is_cdn'] = True

        response = config.geo_reader.asn(ip)
        for i in config.ASNS:
            if response.autonomous_system_number == int(i):
                ip_info['is_cdn'] = True
        return ip_info
    except Exception as e:
        return str(e)


def update_ip_to_domain(ip_info):
    try:
        url = config.update_domain_url + f'?key={config.key}'
        r = requests.post(url, data=json.dumps(ip_info))
        return r.json()
    except Exception as e:
        return e


if __name__ == '__main__':
    print(get_ip_info('123.123.123.412'))
