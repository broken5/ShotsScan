from tools.alivescan.alivescan import WebAliveScan
from lib.api import get, put_alive
from tools.oneforall.config import logger
import time
import datetime


def scan(subdomain):
    alive_data = {'code': 0, 'reason': '', 'data': []}
    try:
        app = WebAliveScan(subdomain)
        app.run()
        for i in app.data:
            alive_data['data'].append(i)
        alive_data['code'] = 1
    except Exception as e:
        alive_data['code'] = 0
        alive_data['reason'] = str(e)
    finally:
        return alive_data


def run():
    while True:
        data = get('subdomain')
        if data['code'] == 0:
            logger.log('ERROR', data['msg'])
            time.sleep(30)
        else:
            subdomain = data['data'].get('subdomain')
            start = datetime.datetime.now()
            alive_data = scan(subdomain)
            end = datetime.datetime.now()
            alive_data['time'] = (end-start).seconds
            alive_data['domain'] = subdomain
            put_alive(alive_data)


if __name__ == '__main__':
    run()
