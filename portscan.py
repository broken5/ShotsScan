from tools.portscan.portscan import PortScan
from lib.api import get, put_port, get_ip_info, update_ip_to_domain
from tools.oneforall.config import logger
import time
import datetime


def scan(ip, is_scan, subdomain):
    port_data = {'code': 0, 'reason': '', 'data': []}
    ip_info = {'is_cdn': False, 'is_private': False, 'ip': ip}
    try:
        if not ip:
            ip_info = get_ip_info('', subdomain)
            if isinstance(ip_info, dict):
                ip_info['domain'] = subdomain
                update_ip_to_domain(ip_info)
            else:
                raise Exception(str(ip_info))
        if (not is_scan) and (not ip_info['is_cdn']) and (not ip_info['is_private']):
            app = PortScan(ip_info['ip'])
            app.run()
            for i in app.data:
                ip_port_info = app.data.get(i)
                ip = ip_port_info['ip']
                port = ip_port_info['port']
                name = ip_port_info['name']
                product = ip_port_info['product']
                version = ip_port_info['version']
                port_data['data'].append(
                    {"ip": ip, "port": port, "service": name, "product": product, "version": version}
                )
            port_data['code'] = 1
        else:
            port_data['reason'] = '该IP端口数据已被录入'
    except Exception as e:
        port_data['code'] = 0
        port_data['reason'] = str(e)
    finally:
        return port_data


def run():
    while True:
        data = get('ip')
        if data['code'] == 0:
            logger.log('ERROR', data['msg'])
            time.sleep(30)
        else:
            ip = data['data'].get('ip')
            subdomain = data['data'].get('subdomain')
            is_scan = data['data'].get('is_scan')
            start = datetime.datetime.now()
            port_data = scan(ip, is_scan, subdomain)
            end = datetime.datetime.now()
            port_data['time'] = (end-start).seconds
            port_data['domain'] = subdomain
            put_port(port_data)


if __name__ == '__main__':
    run()
