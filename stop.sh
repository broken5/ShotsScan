ps -aux |grep alivescan.py  | awk '{print$2}'|  xargs kill -9 2>/dev/null
ps -aux |grep portscan.py   | awk '{print$2}'|  xargs kill -9 2>/dev/null
ps -aux |grep subdomain.py  | awk '{print$2}'|  xargs kill -9 2>/dev/null