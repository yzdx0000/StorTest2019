# -*- coding:utf-8 _*-
"""
测试内容:元数据盘分组中同时故障（元数据副本-1）个元数据盘同时故障，部分超时内恢复

步骤:
1、在节点A创建LUN1
2、将逻辑卷映射至主机1上LUN1
3、在主机1上运行vdbench -f min-seq-w-1l.conf -jn；
4、业务完成或将一个共享池内共享盘拔出副本数-1个；
5、等待1个小时后启动被动重建，被动重建开始后将共享盘插回；
6、恢复插回的共享盘，主机端执行vdbench -f min-seq-w-1l.conf -jro校验数据一致性
7、修复完成后，比较内部数据一致性

检查项:
1、步骤4、业务执行完成后，系统处于待机状态，拔掉日志硬盘不触发修复，系统上报磁盘异常告警；
2、步骤5、达到超时时间后共享盘开始重建，重建过程中插入磁盘，系统识别磁盘且能上线使用；
3、步骤6、数据校验一致。
4、步骤7，内部数据校验一致

"""

# testlink case: 1000-33228
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
# import error

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
client_ip1 = env_manage_repair_test.client_ips[0]
esxi_ip = env_manage_repair_test.Esxi_ips
nodeid1 = env_manage_repair_test.com_node.get_node_id_by_ip(node_ip1)
nodeid2 = env_manage_repair_test.com_node.get_node_id_by_ip(node_ip2)

"""获取指定节点数据盘和共享盘"""
share_disk, data_disk = env_manage_repair_test.Reliable_osan.get_share_monopoly_disk_ids(node_ip1, nodeid1)
disk_ids1 = []
for share_disk in share_disk:
    disk_phy_id = env_manage_repair_test.Reliable_osan.get_physicalid_by_name(node_ip1, share_disk)
    disk_ids1.append(disk_phy_id)
disk_phy_id1 = random.choice(disk_ids1)  # 磁盘物理id
disk_name1 = env_manage_repair_test.Reliable_osan.get_name_by_physicalid(node_ip1, disk_phy_id1)  # 磁盘名字
disk_uuid1 = env_manage_repair_test.com_disk.get_disk_uuid_by_name(nodeid1, disk_name1)  # 磁盘uuid
disk_id1 = env_manage_repair_test.Reliable_osan.get_diskid_by_name(node_ip1, nodeid1, disk_name1)  # 集群中的磁盘id

share_disk, data_disk = env_manage_repair_test.Reliable_osan.get_share_monopoly_disk_ids(node_ip2, nodeid2)
disk_ids2 = []
for share_disk in share_disk:
    disk_phy_id = env_manage_repair_test.Reliable_osan.get_physicalid_by_name(node_ip2, share_disk)
    disk_ids2.append(disk_phy_id)
disk_phy_id2 = random.choice(disk_ids2)  # 磁盘物理id
disk_name2 = env_manage_repair_test.Reliable_osan.get_name_by_physicalid(node_ip2, disk_phy_id2)  # 磁盘名字
disk_uuid2 = env_manage_repair_test.com_disk.get_disk_uuid_by_name(nodeid2, disk_name2)  # 磁盘uuid
disk_id2 = env_manage_repair_test.Reliable_osan.get_diskid_by_name(node_ip2, nodeid2, disk_name2)  # 集群中的磁盘id
stor_id_block = env_manage_repair_test.Lun_osan.get_storage__type_id(s_ip=node_ip1, type="SHARED")


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
                                                            rdpct=rdpct1)
    min_seq_r = env_manage_repair_test.co2_osan.gen_vdb_xml(lun=lun1, xfersize=xfersize1, seekpct=cp("vdbench", "seekpct"),
                                                            rdpct=rdpct2)


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
    env_manage_repair_test.Reliable_osan.remove_disk(node_ip=node_ip1, disk_id=disk_phy_id1, disk_usage="SHARED")
    env_manage_repair_test.Reliable_osan.remove_disk(node_ip=node_ip2, disk_id=disk_phy_id2, disk_usage="SHARED")


def disk_insert(arg=0):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    env_manage_repair_test.Reliable_osan.check_disk_state(node_ip=node_ip1,
                                                          disk_uuid=disk_uuid1,
                                                          disk_state="DISK_STATE_ZOMBIE")  # 检测磁盘状态，若为ZOMBIE，认为重建完成
    env_manage_repair_test.Reliable_osan.check_disk_state(node_ip=node_ip2,
                                                          disk_uuid=disk_uuid2,
                                                          disk_state="DISK_STATE_ZOMBIE")  # 检测磁盘状态，若为ZOMBIE，认为重建完成
    env_manage_repair_test.Reliable_osan.insert_disk(node_ip=node_ip1, disk_id=disk_phy_id1, disk_usage="SHARED")
    env_manage_repair_test.Reliable_osan.insert_disk(node_ip=node_ip2, disk_id=disk_phy_id2, disk_usage="SHARED")

    env_manage_repair_test.com_disk.remove_disks(disk_ids=disk_id1)
    env_manage_repair_test.com_disk.remove_disks(disk_ids=disk_id2)

    env_manage_repair_test.Reliable_osan.add_disks(s_ip=node_ip1, node_ids=nodeid1, uuid=disk_uuid1, usage="SHARED",
                                                   storage_id=stor_id_block)
    env_manage_repair_test.Reliable_osan.add_disks(s_ip=node_ip2, node_ids=nodeid2, uuid=disk_uuid2, usage="SHARED",
                                                   storage_id=stor_id_block)


def case():
    log.info("生成vdbench配置文件，主机端登录 ...")
    iscsi_login()
    log.info("在主机1对lun1上运行vdbench -f min-seq-w-1l.conf -jn ...")
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=min_seq_w, jn_jro='jn', output=node_ip1)
    log.info("业务完成后将一个共享池内共享盘拔出副本数-1个")
    disk_error()
    log.info("等待超时后，触发被动重建,被动重建开始后将共享盘插回...")
    env_manage_repair_test.Reliable_osan.run_down_disk_wait(node_ip1, int(cp("timeout", "disk_timeout")))
    time.sleep(int(cp("timeout", "disk_timeout"))/int(cp('timeout', 'unit_time')) + 20)
    disk_insert()

    log.info(
        "恢复插回的共享盘，主机端执行vdbench -f min-seq-write.conf -jro校验数据一致性")
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=min_seq_w, output=node_ip1)
    log.info("数据修复完成后，比较内部数据一致性 ...")
    env_manage_repair_test.break_down.check_bad_obj()
    env_manage_repair_test.Reliable_osan.compare_data()


def main():
    env_manage_repair_test.rel_check_before_run(filename=file_name)  # 环境检测和准备

    case()  # 用例步骤

    common.ckeck_system()  # 检查系统core

    env_manage_repair_test.clean()  # 环境清理


if __name__ == '__main__':
    common.case_main(main)  # 主函数执行入口
