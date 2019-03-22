#!/usr/bin/python
#-*-coding:utf-8 -*
"""
:Date: 2018-09-15
:Author: wuyq
:Description:
1、在节点A上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
3、在主机1上运行vdbench -f mix-R-Align.conf -jn；在主机2上运行vdbench -f mix-R.conf;
4、在步骤3中的业务运行过程中，制造节点B和节点C的oJNL进程异常；
5、节点A接管节点B和节点C日志并重建成功后，恢复节点B和节点C；
6、待系统正常后，断开节点A业务网；
7、节点A数据修复完成，在主机1上执行vdbench -f mix-R-Align.conf -jro比较一致性；
:Changerlog:
"""
# testlink case: 1000-32898
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

conf_file = common2.CONF_FILE    #配置文件路径
osan = common2.oSan()
reliable = breakdown.Os_Reliable()
disk = breakdown.disk()
node = common.Node()

file_name = os.path.basename(__file__)
file_name = file_name[:-3]                      # 获取本脚本名，去掉.py后缀
error.rel_check_before_run(file_name, free_jnl_num=0, jnl_rep=2, node_num=3, data_rep=2)
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

# 从所有服务节点中选取服务节点A和非日志节点B

io_node_list = error.get_io_node_id()
# 判断业务节点数量是否大于2
if len(io_node_list) < 3:
    log.error("Error,the Business Node Number is less than 3!!! %s" % io_node_list)
    os._exit(-110)
fault_node_id_A = random.choice(io_node_list)
io_node_list.remove(fault_node_id_A)
fault_node_id_B = random.choice(io_node_list)
io_node_list.remove(fault_node_id_B)
fault_node_id_C = random.choice(io_node_list)
fault_node_ip_A = node.get_node_ip_by_id(fault_node_id_A)
fault_node_ip_B = node.get_node_ip_by_id(fault_node_id_B)
fault_node_ip_C = node.get_node_ip_by_id(fault_node_id_C)

# 获取非日志节点的业务网卡
fault_eth_list_A = error.get_io_eth(fault_node_id_A)

def up_down():
    log.info("故障点:业务日志节点B与C的oPara进程故障,业务日志节点A的所有业务网故障")
    time.sleep(100)
    log.info("Step4:在步骤3中的业务运行过程中，将业务日志节点B与C的oPara进程故障,节点:%s,%s" % (fault_node_ip_B, fault_node_ip_C))
    log.info("Step4:将故障节点oPara进程杀死,节点:%s." % (fault_node_ip_B))
    ReliableTest.run_kill_process(fault_node_ip_B, 'oPara')
    log.info("Step4:将故障节点oPara进程杀死,节点:%s." % (fault_node_ip_C))
    ReliableTest.run_kill_process(fault_node_ip_C, 'oPara')
    time.sleep(60)
    log.info("Step5:检查故障节点oPara进程状态 : %s." % (fault_node_ip_B))
    reliable.check_process_stat(fault_node_ip_B, 'oPara')
    log.info("Step5:检查故障节点oPara进程状态 : %s." % (fault_node_ip_B))
    reliable.check_process_stat(fault_node_ip_B, 'oPara')
    time.sleep(60)
    log.info("Step6:等待故障上报后，将业务日志节点A业务网络故障,节点:%s" % (fault_node_ip_A))
    thread_list_A= []
    for io_eth in fault_eth_list_A:
        thread_list_A.append(threading.Thread(target=reliable.network_test, args=(fault_node_ip_A, io_eth, 'down')))
    for thread in thread_list_A:
        thread.start()
    for thread in thread_list_A:
        thread.join()
    time.sleep(100)
    log.info("Step5:将所有故障节点业务网恢复,节点:%s,%s" % (fault_node_ip_A, fault_node_ip_B))
    for io_eth in fault_eth_list_A:
        reliable.network_test(fault_node_ip_A, io_eth, 'up')

def vdb_jn():
    log.info("Step3:在主机1上运行vdbench -f mix-R-Align.conf -jn.")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jn",time=1200)
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
