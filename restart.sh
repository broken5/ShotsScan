ps -aux |grep alivescan.py  | awk '{print$2}'|  xargs kill -9 2>/dev/null
ps -aux |grep portscan.py   | awk '{print$2}'|  xargs kill -9 2>/dev/null
ps -aux |grep subdomain.py  | awk '{print$2}'|  xargs kill -9 2>/dev/null
nohup python3 subdomain.py  > logs/subdomain.log  2>&1  &
nohup python3 portscan.py   > logs/portscan.log   2>&1  &
nohup python3 alivescan.py  > logs/alivescan.log  2>&1  &