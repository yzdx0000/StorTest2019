# -*- coding:utf-8 _*-
"""
测试内容:数据修改写时，全部节点数据网故障，10分钟内恢复

步骤:
1、在节点A创建lun1-lun6
2、将逻辑卷映射至主机1上lun1-lun6
3、在主机1上运行vdbench -f min-seq-write.conf -jn；
4、将存储系统所有数据网断开，10分钟后恢复数据网；
5、检查恢复后系统时候正常
6、主机端执行vdbench -f min-seq-write.conf -jro校验数据一致性
7、数据修复完成后，比较内部数据一致性

检查项:
1、步骤5，检查系统，网络恢复后系统恢复正常
3、步骤6、修复过程中，内外部数据校验一致；
4,、步骤7、修复完成后，内部数据校验一致
"""

# testlink case: 1000-33212
import os, sys
import utils_path
import common2
import common
import Lun_managerTest
import log
import get_config
import threading
import login
import time
import commands
import random
import breakdown
import ReliableTest
import error

import env_manage_repair_test
import decorator_func
from get_config import config_parser as cp

"""初始化日志和全局变量"""
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)  # 初始化日志文件

log.info("---------------全局初始化操作-----------------")
node_ip1 = env_manage_repair_test.deploy_ips[0]
node_ip2 = env_manage_repair_test.deploy_ips[1]
node_ip3 = env_manage_repair_test.deploy_ips[2]
client_ip1 = env_manage_repair_test.client_ips[0]
esxi_ip = env_manage_repair_test.Esxi_ips

node_id1 = env_manage_repair_test.break_down.get_node_id_by_ip(n_ip=node_ip1)
node_id2 = env_manage_repair_test.break_down.get_node_id_by_ip(n_ip=node_ip2)
node_id3 = env_manage_repair_test.break_down.get_node_id_by_ip(n_ip=node_ip3)

fault_eth_list1 = error.get_data_eth(node_id1)
fault_eth_list2 = error.get_data_eth(node_id2)
fault_eth_list3 = error.get_data_eth(node_id3)

# vm_ids = env_manage_repair_test.Reliable_osan.vm_id(esxi_ip=esxi_ip, u_name=cp("esxi", "esxi_user"),
#                                                     pw=cp("esxi", "esxi_passwd"),
#                                                     node_ip=node_ip1)

"""计算集群中所有lun大小之和,因为主机只映射了一半的lun，根据此值设置vdbench  maxdata的值是实际lun大小的2倍"""
lun_ids = env_manage_repair_test.Lun_osan.get_lun(node_ip1)
total_lun_size = 0.0
for lun_id in lun_ids:
    total_lun_size = total_lun_size + (env_manage_repair_test.Lun_osan.get_option_single(s_ip=node_ip1,
                                                                                         command='get_luns', ids="ids",
                                                                                         indexname="luns",
                                                                                         argv2="total_bytes",
                                                                                         argv1=lun_id)) / 1024 / 1024
print total_lun_size
vdbench_lun_size = "{}G".format(round(total_lun_size / 1024, 2))
log.info("将vdbench的maxdata值设置为集群主机映射lun总大小的2倍，为{}".format(vdbench_lun_size))

"""获取指定节点数据盘和共享盘"""
share_disk, data_disk = env_manage_repair_test.Reliable_osan.get_share_monopoly_disk_ids(s_ip=node_ip1, node_id=1)
disk_ids = []
for share_disk in share_disk:
    disk_id = env_manage_repair_test.Reliable_osan.get_physicalid_by_name(node_ip1, share_disk)
    disk_ids.append(disk_id)

"""随机获取故障节点ip"""
failnode_ip = random.choice(env_manage_repair_test.deploy_ips)


def iscsi_login():
    global lun1_min_seq_w
    global lun2_min_seq_w
    global min_seq_w
    global min_seq_r
    login.login()

    # 修改vdbench配置文件的参数值
    #seekpct = 0  # 随机
    rdpct1 = 0  # 读写比例(0是全写)
    rdpct2 = 100
    xfersize1 = cp("vdbench", "unmix_xfersize1")
    lun1 = env_manage_repair_test.Lun_osan.ls_scsi_dev(client_ip1)
    min_seq_w = env_manage_repair_test.co2_osan.gen_vdb_xml(lun=lun1, xfersize=xfersize1, seekpct=cp("vdbench", "seekpct"),
                                                            rdpct=rdpct1, maxdata=vdbench_lun_size)
    min_seq_r = env_manage_repair_test.co2_osan.gen_vdb_xml(lun=lun1, xfersize=xfersize1, seekpct=cp("vdbench", "seekpct"),
                                                            rdpct=rdpct2, maxdata=vdbench_lun_size)


def network_error(arg=1):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    for i in fault_eth_list1:
        env_manage_repair_test.Reliable_osan.network_test(s_ip=node_ip1,
                                                          net_name=i,
                                                          net_stat="down")
    for i in fault_eth_list2:
        env_manage_repair_test.Reliable_osan.network_test(s_ip=node_ip2,
                                                          net_name=i,
                                                          net_stat="down")
    for i in fault_eth_list3:
        env_manage_repair_test.Reliable_osan.network_test(s_ip=node_ip3,
                                                          net_name=i,
                                                          net_stat="down")

    time.sleep(600)

    for i in fault_eth_list1:
        env_manage_repair_test.Reliable_osan.network_test(s_ip=node_ip1,
                                                          net_name=i,
                                                          net_stat="up")
    for i in fault_eth_list2:
        env_manage_repair_test.Reliable_osan.network_test(s_ip=node_ip2,
                                                          net_name=i,
                                                          net_stat="up")
    for i in fault_eth_list3:
        env_manage_repair_test.Reliable_osan.network_test(s_ip=node_ip3,
                                                          net_name=i,
                                                          net_stat="up")


def os_down():
    '''节点关机'''
    ids = ReliableTest.run_down_vir_node(esxi_ip=esxi_ip, u_name=cp('esxi', 'esxi_user'), pw=cp('esxi', 'esxi_passwd'),
                                         node_ip=node_ip1)
    return ids
    # env_manage.com_lh.poweroff_os(test_ip,"init 0")   # 虚拟机方式，使用power off命令关机
    # ReliableTest.run_down_node(IPMI_ip) #物理机，使用IPMI方式关机


def run_vdb_w(arg=0):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=min_seq_w, jn_jro='jn', output=node_ip1)


def run_vdb_lun1_w(arg=0):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=lun1_min_seq_w, jn_jro='jn', output=node_ip1)


def run_vdb_lun2_w(arg=0):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=lun2_min_seq_w, jn_jro='jn', output=node_ip1)


def disk_error(arg=0):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    time.sleep(int(cp("wait_time", "remove_disk")))  # 执行vdbench期间，先等待时间再开始磁盘故障的操作
    log.info(disk_ids)
    env_manage_repair_test.Reliable_osan.remove_disk(node_ip=node_ip1, disk_id=disk_id[0], disk_usage="DATA")
    env_manage_repair_test.Reliable_osan.remove_disk(node_ip=node_ip1, disk_id=disk_id[1], disk_usage="DATA")


def vdb_jn(confile, type):
    log.info("Run vdbench with jn.")
    env_manage_repair_test.co2_osan.run_vdb(client_ip1, confile, output=node_ip1, jn_jro=type)


def case():
    log.info("生成vdbench配置文件，主机端登录 ...")
    iscsi_login()
    log.info("在主机1对lun1上运行vdbench -f min-seq-w-1l.conf -jn ...")
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=min_seq_w, jn_jro='jn', output=node_ip1)
    log.info("将存储系统所有数据网断开，10分钟后恢复数据网")
    network_error()
    env_manage_repair_test.rel_check_before_run(filename=file_name)  # 环境检测和准备
    log.info(
        "数据修复过程中，主机端执行vdbench -f min-seq-write.conf -jro校验数据一致性")
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=min_seq_w, jn_jro='jro', output=node_ip1)
    log.info("数据修复完成后，比较内部数据一致性 ...")
    env_manage_repair_test.Reliable_osan.compare_data()


def main():
    env_manage_repair_test.rel_check_before_run(filename=file_name)  # 环境检测和准备

    case()  # 用例步骤

    common.ckeck_system()  # 检查系统core

    env_manage_repair_test.clean()  # 环境清理


if __name__ == '__main__':
    common.case_main(main)  # 主函数执行入口
