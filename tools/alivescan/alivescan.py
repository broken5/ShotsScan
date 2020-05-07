from gevent import monkey, pool; monkey.patch_all(thread=False, select=False)
import random
import chardet
import urllib3
import time
import requests
from tools.alivescan import config
from bs4 import BeautifulSoup
from tools.oneforall.config import logger
import threading
urllib3.disable_warnings()
LOCK = threading.RLock()


class WebAliveScan:
    def __init__(self, subdomain):
        self.subdomain = subdomain
        self.data = []

    def gen_url_by_port(self, domain, port):
        protocols = ['http://', 'https://']
        if port == 80:
            url = f'http://{domain}'
            return url
        elif port == 443:
            url = f'https://{domain}'
            return url
        else:
            for protocol in protocols:
                url = f'{protocol}{domain}:{port}'
                return url

    def gen_url_list(self, domain_list):
        # 获取端口
        ports = config.ports.get('default')
        # 生成URL
        url_list = []
        for domain in domain_list:
            domain = domain.strip()
            logger.log('INFOR', f'开始扫描:[{domain}]')
            if ':' in domain:
                domain, port = domain.split(':')
                url_list.append(self.gen_url_by_port(domain, int(port)))
                continue
            for port in ports:
                url_list.append(self.gen_url_by_port(domain, port))
        return url_list

    def sizeHuman(self, num):
        base = 1024
        for x in ['B ', 'KB', 'MB', 'GB']:
            if base > num > -base:
                return "%3.0f%s" % (num, x)
            num /= base
        return "%3.0f %s" % (num, 'TB')

    def request(self, url):
        try:
            r = requests.get(url, timeout=config.timeout, headers=self.get_headers(), verify=config.verify_ssl,
                             allow_redirects=config.allow_redirects)
            text = r.content.decode(encoding=chardet.detect(r.content)['encoding'])
            title = self.get_title(text).strip().replace('\r', '').replace('\n', '')
            banner = self.get_banner(r.headers)
            size = self.sizeHuman(len(r.text))
            status = r.status_code
            subdomain = (url.split('//')[-1]).split(':')[0]
            if status in config.ignore_status_code:
                return
            result = {'url': r.url, 'title': title, 'status': status, 'size': size, 'fingerprint': banner}
            self.data.append(result)
            logger.log('INFOR', f'AliveWeb:[{url}]')

            return r, text
        except Exception as e:
            # print(e)
            return e

    def get_headers(self):
        """
        生成伪造请求头
        """
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/68.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) '
            'Gecko/20100101 Firefox/68.0',
            'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/68.0']
        ua = random.choice(user_agents)
        headers = {
            'Accept': 'text/html,application/xhtml+xml,'
                      'application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Referer': 'https://www.google.com/',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': ua,
        }
        return headers

    def get_title(self, markup):
        """
        获取标题
        :param markup: html标签
        :return: 标题
        """
        soup = BeautifulSoup(markup, 'lxml')
        title = soup.title
        if title:
            return title.text

        h1 = soup.h1
        if h1:
            return h1.text

        h2 = soup.h2
        if h2:
            return h2.text

        h3 = soup.h3
        if h2:
            return h3.text

        desc = soup.find('meta', attrs={'name': 'description'})
        if desc:
            return desc['content']

        word = soup.find('meta', attrs={'name': 'keywords'})
        if word:
            return word['content']

        text = soup.text
        if len(text) <= 200:
            return text
        return ''

    def get_banner(self, headers):
        banner = str({'Server': headers.get('Server'),
                      'Via': headers.get('Via'),
                      'X-Powered-By': headers.get('X-Powered-By')})
        return banner

    def run(self):
        logger.log('INFOR', f'WebAlive探测进程启动:WebAliveScan')
        domain_list = [self.subdomain]
        url_list = self.gen_url_list(domain_list)
        gevent_pool = pool.Pool(config.threads)
        while url_list:
            for task in [
                gevent_pool.spawn(self.request, url_list.pop())
                for i in range(len(url_list[:config.threads]))
            ]:
                task.join()


if __name__ == '__main__':
    app = WebAliveScan('www.baidu.com')
    app.run()