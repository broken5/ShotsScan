# ShotsScan

### 注意事项

1. `Shots`只负责发布扫描任务与数据展示，`ShotsScan`只负责扫描，所以需要正确配置`config.py`中的`key`与`website`确保`ShotsScan`能接收到任务
2. `ShotsScan`中的调用的扫描工具都在`tools`目录下，如果要修改工具扫描配置，需要去对应的目录下修改
3. `PortScan`需要单独配置`Fofa密钥`与`Shodan密钥`的，否则不能正常扫描
4. `ShotsScan`和`Shots`如果搭建在不同的服务器上，确保两台服务器之间网络延迟不要过高，否则会有丢包现象
5. 每次记得更新后记得pip install -r requirements.txt
