#!/usr/bin/python
#-*-coding:utf-8 -*
"""
:Date: 2018-09-15
:Author: wuyq
1、在节点A上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
3、在主机1上运行vdbench -f mix-R-Align.conf -jn；在主机2上运行vdbench -f mix-R.conf;
4、在步骤3中的业务运行过程中，将节点A断开所有网络；
5、日志节点B在接管节点A日志过程中，将节点C数据网闪断；
6、业务完成后，在主机1上执行vdbench -f mix-R-Align.conf -jro比较一致性；
7、比较存储内部数据一致性。"

:Changerlog:
"""
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
osan.init_win_log(file_name)                    #初始化windows日志文件/g
reliable = breakdown.Os_Reliable()
disk = breakdown.disk()
node = common.Node()

file_name = os.path.basename(__file__)
file_name = file_name[:-3]                      # 获取本脚本名，去掉.py后缀
#log_file_path = log.get_log_path(file_name)     #获取日志目录，即test_cases/Log/Case_log
#log.init(log_file_path, True)                   #初始化日志文件
error.rel_check_before_run(file_name, jnl_rep=3, node_num=4)  # 运行前检查集群环境

# 获取集群节点信息
deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
vip = login.login()
# 修改vdbench配置文件的参数值
mix_R_win = osan.gen_win_vdb_conf(xfersize="(4k,80,16k,20)",
                                  seekpct=0,
                                  rdpct=0)
mix_R_Align = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[0]),
                               xfersize="(4k,80,16k,20)",
                               seekpct=0,
                               rdpct=0)
mix_R = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[1]),
                         xfersize="(4k,80,16k,20)",
                         offset=2048,
                         seekpct=0,
                         rdpct=0)

# 从所有服务节点中选出日志节点A
deploy_ls = deploy_ips[:]
los_id_list = disk.get_jnl_state()
los_ids = los_id_list.keys()
los_id = random.choice(los_ids)
los_node_id_A = los_id_list[los_id][0]
los_node_ip_A = node.get_node_ip_by_id(los_node_id_A)

fault_eth_list_A = error.get_data_eth(los_node_id_A)

def up_down():
    log.info("故障点:先将日志节点A下电,日志节点B接管日志业务后再将日志节点B的数据网断开")
    time.sleep(100)
    log.info("Step4:业务过程中,将日志节点A下电,日志节点A:%s" % los_node_ip_A)
    vm_id_A = error.down_node(los_node_ip_A)

    los_id_list = disk.get_jnl_state(los_node_ip_A)
    los_node_id_B = los_id_list[los_id][0]
    los_node_ip_B = disk.get_node_ip_by_id(los_node_ip_A, los_node_id_B)
    log.info("Step5:B节点接管A节点的日志业务后,将C节点的数据网闪断,日志节点B:%s" % los_node_ip_B)
    deploy_ls.remove(los_node_ip_A)
    deploy_ls.remove(los_node_ip_B)
    los_node_ip_C = random.choice(deploy_ls)
    los_node_id_C = disk.get_node_id_by_ip(los_node_ip_A, los_node_ip_C)
    fault_eth_list_C = error.get_data_eth(los_node_id_C)
    thread_list = []
    for eth_name in fault_eth_list_C:
        thread_list.append(threading.Thread(target=reliable.network_test, args=(los_node_ip_C, eth_name, 'down')))
    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()

    time.sleep(60)
    log.info("Step6:将下电的日志节点A重新上电,日志节点:%s" % los_node_ip_A)
    log.info("Step6:将日志节点A上电,日志节点:%s" % los_node_ip_A)
    error.up_node(vm_id_A)
    time.sleep(60)
    error.check_host(los_node_ip_A)  # 检测重启后机器状态，是否已开机

    time.sleep(60)
    log.info("Step7:将日志节点C的数据网恢复,日志节点:%s" % los_node_ip_B)
    thread_list = []
    for eth_name in fault_eth_list_C:
        thread_list.append(threading.Thread(target=reliable.network_test, args=(los_node_ip_C, eth_name, 'up')))
    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()

    log.info("Step8:数据修复完成系统恢复正常后,比较内部数据一致性")
    reliable.compare_data()

def vdb_jn():
    log.info("Step3:在主机1上运行vdbench -f mix-R-Align.conf -jn.")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jn",time=900)
    log.info("Step6:主机1上业务完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jro")

def vdb_run():
    log.info("Step3:在主机2上运行vdbench -f mix-R.conf.")
    osan.run_vdb(client_ips[1], mix_R, output=deploy_ips[0],time=1000)
def win_vdb_run():
    log.info("Step3:在windows主机上运行vdbench -f mix-R-win.conf.")
    osan.run_win_vdb(file_name, mix_R_win, jn_jro="jn", time=900)


def case():
    test_threads = []
    test_threads.append(threading.Thread(target=up_down))
    test_threads.append(threading.Thread(target=vdb_jn))
    test_threads.append(threading.Thread(target=vdb_run))
    test_threads.append(threading.Thread(target=win_vdb_run))
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

if __name__ == '__main__':
    case()
