混合故障脚本

运行前的准备
由于脚本使用了openpyxl模块，所以需要安装一些python包
两种方式
一、如果是外网可以直接 pip install openpyxl
二、如果不能登录外网
	1、安装et_xmlfile-1.0.1.tar.gz （解压，python setup.py install）
	2、安装jdcal-1.0.1.tar.gz      （解压，python setup.py install）
	3、安装openpyxl-2.5.5.tar.gz   （解压，python setup.py install）

1、脚本是读取"case_list.xlsx"来获取要运行的故障类型
    case_list.xlsx:
	1>故障种类中绿色背景的是已经实现的。
	2>次数中是这个故障连续运行的次数，0就是不运行
	2>case_list中的故障1、2填写的编号和故障种类中一一对应。
	3>节点数量、节点冗余度、磁盘冗余度是这个用例所需要的最小的节点数量、节点冗余度、磁盘冗余度。
	4>时间间隔是故障1开始后等待多长时间运行故障2，形式可以写成时间段或者具体时间长度，比如：1-300或者60
	5>运行完，结果会填到运行结果中
	
2、脚本不能放在集群节点上。

3、脚本中vdbench的参数需要配置
	1>Vdb_Path是vdbench工具路径
	2>System_Ips是vdbench要运行的节点，可以写成一个节点或者元组多个ip，比如:"10.2.40.1"或者("10.2.40.1", "10.2.40.2")
	3>Anchor_Path是vdbench要写到的路径
	
4、参数-i指明一个集群节点

5、参数-c是配置后有core停止脚本