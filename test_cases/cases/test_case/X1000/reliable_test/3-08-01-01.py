#!/usr/bin/python
#-*-coding:utf-8 -*
"""
:Date: 2018-09-10
:Author: wuyq
:Description:
1、在节点A（los节点）中创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
2、使用2个主机与节点A建立iscsi连接，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
3、在主机1上运行vdbench -f mix-S-Align.conf -jn；在主机2上运行vdbench -f mix-S.conf;
4、在步骤3中的业务运行过程中，将节点A一个数据网和业务网断开；
5、检查主机业务运行状态
6、主机1上业务完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性；
7、主机2上执行vdbench -f mix-s-Align.conf -jro比较一致性；
:Changerlog:
"""
# testlink case: 1000-32708
import os
import sys
import commands
import threading
import random
import time
import utils_path
import common2
import common
import log
import get_config
import ReliableTest
import login
import error
import breakdown

conf_file = common2.CONF_FILE    # 配置文件路径
osan = common2.oSan()
reliable = breakdown.Os_Reliable()
disk = breakdown.disk()
node = common.Node()

file_name = os.path.basename(__file__)
file_name = file_name[:-3]                      # 获取本脚本名，去掉.py后缀
error.rel_check_before_run(file_name, free_jnl_num=1, jnl_rep=3, node_num=4)
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

# 选择数据网卡和业务网卡
fault_vip = random.choice(vip)
fault_io_ip = osan.get_node_by_vip(fault_vip)
fault_io_id = node.get_node_id_by_ip(fault_io_ip)

data_eth_list = error.get_data_eth(fault_io_id)
io_eth_list = error.get_io_eth(fault_io_id)
data_eth_name = random.choice(data_eth_list)
io_eth_name = random.choice(io_eth_list)


def up_down():
    log.info("故障点:一个业务节点的一个业务网卡和一个数据网卡")
    time.sleep(100)
    log.info("Step4:在步骤3中的业务运行过程中，将节点一个数据网和业务网断开,业务节点:%s" % (fault_io_ip))
    log.info("将故障节点数据网的网卡故障,网卡：%s" % (data_eth_name))
    log.info("将故障节点业务网的网卡故障,网卡：%s" % (io_eth_name))
    thread_list = []
    thread_list.append(threading.Thread(target=reliable.network_test, args=(fault_io_ip, data_eth_name, 'down')))
    thread_list.append(threading.Thread(target=reliable.network_test, args=(fault_io_ip, io_eth_name, 'down')))
    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()
    time.sleep(100)
    log.info("Step5:将故障节点数据网的网卡恢复,网卡:%s" % data_eth_name)
    reliable.network_test(fault_io_ip, data_eth_name, 'up')
    log.info("Step5:将故障节点业务网的网卡恢复,网卡:%s" % io_eth_name)
    reliable.network_test(fault_io_ip, io_eth_name, 'up')

    log.info("Step7:数据修复完成系统恢复正常后，比较内部数据一致性")
    reliable.compare_data()

def vdb_jn():
    log.info("Step3:在主机1上运行vdbench -f mix-R-Align.conf -jn.")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0],jn_jro="jn",time=1200)
    log.info("Step6:主机1上业务完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jro")

    disk.multi_check_part_lun_uniform_by_ip()


def vdb_run():
    log.info("Step3:在主机2上运行vdbench -f mix-R.conf.")
    osan.run_vdb(client_ips[1], mix_R, output=deploy_ips[0],time=1200)

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
    for ip in vip:
        for cli in client_ips:
            pass
            #osan.iscsi_logout(cli,vip=ip)
def main():
    case()
if __name__ == '__main__':
    main()
