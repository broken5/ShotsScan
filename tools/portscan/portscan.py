import shodan
import requests
import nmap
import time
from tools.portscan import config
from tools.oneforall.config import logger
from base64 import b64encode


class PortScan:
    def __init__(self, ip):
        self.ip = ip
        self.shodan = self.init_shodan()
        self.fofa = self.init_fofa()
        self.data = []

    def shodan_scan(self):
        if not self.shodan:
            return []
        logger.log('INFOR', f'开始Shodan端口扫描 - [{self.ip}]')
        if self.shodan:
            try:
                result = self.shodan.host(self.ip)
                data = result['data']
                port_list = []
                for i in data:
                    port = i.get('port', '0')
                    if port:
                        port_list.append(port)
                logger.log('INFOR', f'Shodan端口扫描完成 - [{self.ip}] {port_list}')
                return port_list
            except Exception as e:
                logger.log('ALERT', f'Shodan查询[{self.ip}]失败:{e}')
                return []

    def init_shodan(self):
        api = shodan.Shodan(config.shodan_api)
        try:
            api.info()
            return api
        except Exception as e:
            logger.log('ALERT', f'shodan api异常:{e}')
            return None

    def fofa_scan(self):
        if not self.fofa:
            return []
        logger.log('INFOR', f'开始Fofa端口扫描 - [{self.ip}]')
        query = f'ip="{self.ip}"'
        qbase64 = b64encode(query.encode()).decode()
        try:
            url = self.fofa + f'&qbase64={qbase64}'
            r = requests.get(url)
            result = r.json()
            if result['error']:
                logger.log('ALERT', f'fofa接口错误:{result["error"]}')
                return []
            else:
                port_list = list(set([int(i[2]) for i in result['results']]))
                logger.log('INFOR', f'Fofa端口扫描完成 - [{self.ip}] {port_list}')
                return port_list
        except Exception as e:
            logger.log('ALERT', f'fofa连接异常:{e}')
            return []

    def init_fofa(self):
        try:
            url = f'https://fofa.so/api/v1/info/my?email={config.fofa_email}&key={config.fofa_key}'
            r = requests.get(url)
            r.json()
            return f'https://fofa.so/api/v1/search/all?email={config.fofa_email}&key={config.fofa_key}'
        except Exception as e:
            logger.log('ALERT', f'fofa连接异常:{e}')
            return None

    def nmap_scan(self, port_list):
        logger.log('INFOR', f'nmap - [{self.ip}]开始扫描')
        try:
            nm = nmap.PortScanner(nmap_search_path=config.nmap_search_path)
        except Exception as e:
            logger.log('ERROR', f'nmap程序未找到:{e}')
            return None
        ports = ','.join([str(tmp) for tmp in port_list])
        nm.scan(hosts=self.ip, ports=ports, arguments='-Pn -T 4 -sV --version-intensity=3')
        try:
            port_list = nm[self.ip]['tcp'].keys()
        except Exception as e:
            logger.log('ERROR', f'nmap扫描端口异常{e}')
            return None
        else:
            port_dict = {}
            for port in port_list:
                if nm[self.ip].has_tcp(port):
                    port_info = nm[self.ip]['tcp'][port]
                    state = port_info.get('state', 'no')
                    if state == 'open':
                        name = port_info.get('name', '')
                        product = port_info.get('product', '')
                        version = port_info.get('version', '')
                        port_dict[port] = {'ip': self.ip, 'port': port, 'name': name, 'product': product, 'version': version}
                        logger.log('INFOR', f'nmap扫描:{self.ip}:{port} {name} {product} {version}')
            logger.log('INFOR', f'nmap[{self.ip}]扫描完成')
            return port_dict

    def run(self):
        time.sleep(1)
        shodan_result = self.shodan_scan()
        fofa_result = self.fofa_scan()
        port_list = set(shodan_result + fofa_result)
        if port_list:
            port_results = self.nmap_scan(port_list)
            self.data = port_results
        else:
            self.data = []


if __name__ == '__main__':
    portscan = PortScan('39.108.3.16')
    portscan.run()
    print(portscan.data)
