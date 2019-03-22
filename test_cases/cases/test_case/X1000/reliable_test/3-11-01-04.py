#!/usr/bin/python
#-*-coding:utf-8 -*
"""
:Date: 2019-03-15
:Author: wuyq
:Description:
1、在节点A上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
3、在主机1上运行vdbench -f mix-S-Align.conf -jn；在主机2上运行vdbench -f mix-S.conf;
4、在步骤3中的业务运行过程中，将所有业务节点网配置成bond，所有业务和数据网线交替故障恢复；
5、业务执行完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性；
6、节点A恢复后数据修复完成，比较存储内部数据一致性；"

:Changerlog:
"""
import os
import threading
import random
import time
import utils_path
import breakdown
import common2
import common
import log
import get_config
import login
import error

# 参数实例化
conf_file = common2.CONF_FILE
osan = common2.oSan()
reliable = breakdown.Os_Reliable()
disk = breakdown.disk()
node = common.Node()
# 初始化日志文件
file_name = os.path.basename(__file__)
file_name = file_name[:-3]
error.rel_check_before_run(file_name, jnl_rep=3, node_num=4, data_rep=3)
# 获取集群节点信息
deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
vip = login.login()

# 修改vdbench配置文件的参数值
mix_R_Align = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[0]),
                               xfersize="(4k,80,16k,20)",
                               seekpct=0,
                               rdpct=0)
mix_R = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[1]),
                         xfersize="(4k,80,16k,20)",
                         offset=2048,
                         seekpct=0,
                         rdpct=0)

# 获取带有VIP的集群业务节点
node_and_eths = {}
io_node_ids = reliable.get_business_nodes()
for io_node_id in io_node_ids:
    io_node_ip = node.get_node_ip_by_id(io_node_id)
    io_eth_list = error.get_io_eth(io_node_id)
    node_and_eths[io_node_ip] = io_eth_list

event1 = threading.Event()
event2 = threading.Event()

def up_down():
    time.sleep(100)
    log.info("Step2:在业务过程中,将所有的业务网卡配置为bond.")
    for io_node_ip in node_and_eths.keys():
        io_eth_list = node_and_eths[io_node_ip]
        reliable.bond_conf(io_node_ip, io_eth_list, 'bond0')

    time.sleep(100)
    log.info("Step3:在bond配置完成后,将所有业务节点的业务网交替故障.")
    for io_node_ip in node_and_eths.keys():
        time.sleep(30)
        log.info("将节点 %s 的业务网断开." % io_node_ip)
        for io_eth in node_and_eths[io_node_ip]:
            reliable.network_test(io_node_ip, io_eth, 'down')
        time.sleep(30)
        log.info("将节点 %s 的业务网恢复." % io_node_ip)
        for io_eth in node_and_eths[io_node_ip]:
            reliable.network_test(io_node_ip, io_eth, 'up')

    event1.wait()
    event2.wait()
    log.info("Step5:确定业务完成后,检查数据修复完成.")
    disk.check_bad_obj()
    log.info("Step6:将所有业务节点bond配置取消,恢复业务节点至初始状态.")
    for io_node_ip in node_and_eths.keys():
        io_eth_list = node_and_eths[io_node_ip]
        reliable.bond_conf(io_node_ip, io_eth_list, 'bond0', switch=0)

    log.info("Step7:检查集群内部数据一致性.")
    disk.multi_check_part_lun_uniform_by_ip()

def vdb_jn():
    log.info("Step1:在主机1上运行vdbench -f mix-R-Align.conf -jn.")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jn", time=1200)
    log.info("Step4:主机1上业务完成后，在主机1上执行vdbench -f mix-R-Align.conf -jro比较一致性.")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jro")
    event1.set()

def vdb_run():
    log.info("Step1:在主机2上运行vdbench -f mix-R.conf.")
    osan.run_vdb(client_ips[1], mix_R, output=deploy_ips[0], time=1200)
    event2.set()

def case():
    test_threads = []
    test_threads.append(threading.Thread(target=up_down))
    test_threads.append(threading.Thread(target=vdb_jn))
    test_threads.append(threading.Thread(target=vdb_run))
    for test_thread in test_threads:
        test_thread.start()
    for test_thread in test_threads:
        test_thread.join()
    for c_ip in client_ips:
        osan.vdb_check(c_ip=c_ip, time=100, oper="iops", output=deploy_ips[0])

if __name__ == '__main__':
    case()
