from tools.oneforall import oneforall
from lib.api import get, put_subdomain, get_ip_info
from tools.oneforall.config import logger
import time
import datetime


def scan(domain):
    domain_data = {'code': 0, 'reason': '', 'data': []}
    try:
        app = oneforall.OneForAll(domain)
        app.run()
        for i in app.data:
            subdomain = i['subdomain']
            subdomain_ip = i['content']
            city = None
            is_private = False
            is_cdn = False
            if subdomain and subdomain_ip:
                subdomain_ip = subdomain_ip.split(',')[0]
                ip_info = get_ip_info(subdomain_ip)
                if isinstance(ip_info, dict):
                    city = ip_info['city']
                    is_private = ip_info['is_private']
                    is_cdn = ip_info['is_cdn']
            elif subdomain:
                pass
            else:
                continue
            domain_data['data'].append({
                'subdomain': subdomain,
                'subdomain_ip': subdomain_ip,
                'city': city,
                'is_private': is_private,
                'is_cdn': is_cdn
            })
        domain_data['code'] = 1
    except Exception as e:
        domain_data['code'] = 0
        domain_data['reason'] = str(e)
    finally:
        return domain_data


def run():
    while True:
        data = get('domain')
        if data['code'] == 0:
            logger.log('ERROR', data['msg'])
            time.sleep(30)
        else:
            domain = data['data']['domain']
            start = datetime.datetime.now()
            domain_data = scan(domain)
            end = datetime.datetime.now()
            domain_data['time'] = (end-start).seconds
            domain_data['domain'] = domain
            put_subdomain(domain_data)


if __name__ == '__main__':
    run()
