# -*- coding:utf-8 _*-
# Author:wangxiang
# Date  :2018-8-7
"""
测试内容:副本下，每副本对应的硬盘依次故障超时

步骤:
1、在节点A创建LUN1-LUN6
2、将逻辑卷映射至主机1上LUN1-LUN6
3、在主机1上运行vdbench -f min-seq-w-1l.conf -jn；
4、业务完成后将每副本对应硬盘依次故障超时；
5、等待超时后，触发被动重建；
6、数据重建完成后，比较内部数据一致性

检查项:
1、步骤4、业务执行完成后，系统处于待机状态，拔掉一块数据盘不触发修复，系统上报磁盘异常告警；
2、步骤5、等待超时后触发重建，开始重建数据盘；
3、步骤6，内部数据比较一致。
"""
import os
import sys
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

import env_manage_repair_test
import decorator_func
from get_config import config_parser as cp

"""初始化日志和变量"""
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)  # 初始化日志文件

node_ip1 = env_manage_repair_test.deploy_ips[0]
node_ip2 = env_manage_repair_test.deploy_ips[1]
node_ip3 = env_manage_repair_test.deploy_ips[2]
client_ip1 = env_manage_repair_test.client_ips[0]
client_ip2 = env_manage_repair_test.client_ips[1]
esxi_ip = env_manage_repair_test.Esxi_ips
node_id = env_manage_repair_test.com_node.get_node_id_by_ip(node_ip1)
node_id2 = env_manage_repair_test.com_node.get_node_id_by_ip(node_ip2)
node_id3 = env_manage_repair_test.com_node.get_node_id_by_ip(node_ip3)

"""获取指定节点数据盘和共享盘"""
share_disk, data_disk = env_manage_repair_test.Reliable_osan.get_share_monopoly_disk_ids(s_ip=node_ip1, node_id=node_id)
disk_ids = []
L = []
for data_disk in data_disk:
    disk_phy_id = env_manage_repair_test.Reliable_osan.get_physicalid_by_name(node_ip1, data_disk)
    disk_ids.append(disk_phy_id)
log.info(disk_ids)
for i in range(0, len(disk_ids)):
    disk_phy_id = disk_ids[i]  # 磁盘物理id
    disk_name = env_manage_repair_test.Reliable_osan.get_name_by_physicalid(node_ip1, disk_phy_id)  # 磁盘名字
    disk_uuid = env_manage_repair_test.com_disk.get_disk_uuid_by_name(node_id=node_id, disk_name=disk_name)  # 磁盘uuid
    disk_id = env_manage_repair_test.Reliable_osan.get_diskid_by_name(s_ip=node_ip1, node_id=node_id,
                                                                      disk_name=disk_name)  # 集群中的磁盘id
    L.append("{},{},{},{}".format(disk_phy_id, disk_name, disk_uuid, disk_id))
log.info(L)

share_disk, data_disk = env_manage_repair_test.Reliable_osan.get_share_monopoly_disk_ids(s_ip=node_ip2,
                                                                                         node_id=node_id2)
disk_ids2 = []
L2 = []
for data_disk in data_disk:
    disk_phy_id = env_manage_repair_test.Reliable_osan.get_physicalid_by_name(node_ip2, data_disk)
    disk_ids2.append(disk_phy_id)
log.info(disk_ids2)
for i in range(0, len(disk_ids2)):
    disk_phy_id2 = disk_ids2[i]  # 磁盘物理id
    disk_name2 = env_manage_repair_test.Reliable_osan.get_name_by_physicalid(node_ip2, disk_phy_id2)  # 磁盘名字
    disk_uuid2 = env_manage_repair_test.com_disk.get_disk_uuid_by_name(node_id=node_id2, disk_name=disk_name2)  # 磁盘uuid
    disk_id2 = env_manage_repair_test.Reliable_osan.get_diskid_by_name(s_ip=node_ip2, node_id=node_id2,
                                                                       disk_name=disk_name2)  # 集群中的磁盘id
    L2.append("{},{},{},{}".format(disk_phy_id2, disk_name2, disk_uuid2, disk_id2))
log.info(L2)

share_disk, data_disk = env_manage_repair_test.Reliable_osan.get_share_monopoly_disk_ids(s_ip=node_ip3,
                                                                                         node_id=node_id3)
disk_ids3 = []
L3 = []
for data_disk in data_disk:
    disk_phy_id = env_manage_repair_test.Reliable_osan.get_physicalid_by_name(node_ip3, data_disk)
    disk_ids3.append(disk_phy_id)
log.info(disk_ids3)
for i in range(0, len(disk_ids3)):
    disk_phy_id3 = disk_ids3[i]  # 磁盘物理id
    disk_name3 = env_manage_repair_test.Reliable_osan.get_name_by_physicalid(node_ip3, disk_phy_id3)  # 磁盘名字
    disk_uuid3 = env_manage_repair_test.com_disk.get_disk_uuid_by_name(node_id=node_id3, disk_name=disk_name3)  # 磁盘uuid
    disk_id3 = env_manage_repair_test.Reliable_osan.get_diskid_by_name(s_ip=node_ip3, node_id=node_id3,
                                                                       disk_name=disk_name3)  # 集群中的磁盘id
    L3.append("{},{},{},{}".format(disk_phy_id3, disk_name3, disk_uuid3, disk_id3))
log.info(L3)
stor_id_block = env_manage_repair_test.Lun_osan.get_storage__type_id(s_ip=node_ip1)


def iscsi_login():
    global min_seq_w
    global min_seq_r
    login.login()

    # 修改vdbench配置文件的参数值
    #seekpct = 0  # 随机
    rdpct1 = 0  # 读写比例(0是全写)
    rdpct2 = 100
    xfersize1 = cp("vdbench", "mix_xfersize1")
    lun1 = env_manage_repair_test.Lun_osan.ls_scsi_dev(client_ip1)
    min_seq_w = env_manage_repair_test.co2_osan.gen_vdb_xml(max_range=cp("vdbench", "range"),
                                                            maxdata=cp("vdbench", "maxdata"),
                                                            thread=cp("vdbench", "threads"), lun=lun1,
                                                            xfersize=xfersize1, seekpct=cp("vdbench", "seekpct"), rdpct=rdpct1)
    min_seq_r = env_manage_repair_test.co2_osan.gen_vdb_xml(max_range=cp("vdbench", "range"),
                                                            maxdata=cp("vdbench", "maxdata"),
                                                            thread=cp("vdbench", "threads"), lun=lun1,
                                                            xfersize=xfersize1, seekpct=cp("vdbench", "seekpct"), rdpct=rdpct2)


def disk_error(arg=1):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    log.info(L)
    for l in L:
        env_manage_repair_test.Reliable_osan.remove_disk(node_ip=node_ip1, disk_id=l.split(",")[0], disk_usage="DATA")
    env_manage_repair_test.Reliable_osan.run_down_disk_wait(s_ip=node_ip1, timeout=int(cp('timeout', 'disk_timeout')))
    time.sleep(int(cp('timeout', 'disk_timeout')) /int(cp('timeout', 'unit_time'))+ 10)
    for l in L:
        env_manage_repair_test.Reliable_osan.check_disk_state(node_ip=node_ip1,
                                                              disk_uuid=l.split(",")[-2],
                                                              disk_state="DISK_STATE_ZOMBIE")  # 检测磁盘状态，若为ZOMBIE，认为重建完成
        env_manage_repair_test.com_disk.remove_disks(disk_ids=l.split(",")[-1])
        env_manage_repair_test.Reliable_osan.insert_disk(node_ip=node_ip1, disk_id=l.split(",")[0], disk_usage="DATA")
        env_manage_repair_test.Reliable_osan.add_disks(s_ip=node_ip1, node_ids=node_id, uuid=l.split(",")[-2],
                                                       usage="DATA",
                                                       storage_id=stor_id_block)

    for l in L2:
        env_manage_repair_test.Reliable_osan.remove_disk(node_ip=node_ip2, disk_id=l.split(",")[0],
                                                         disk_usage="DATA")
    time.sleep(int(cp('timeout', 'disk_timeout')) /int(cp('timeout', 'unit_time'))+ 10)
    for l in L2:
        env_manage_repair_test.Reliable_osan.check_disk_state(node_ip=node_ip2,
                                                              disk_uuid=l.split(",")[-2],
                                                              disk_state="DISK_STATE_ZOMBIE")  # 检测磁盘状态，若为ZOMBIE，认为重建完成
        env_manage_repair_test.com_disk.remove_disks(disk_ids=l.split(",")[-1])
        env_manage_repair_test.Reliable_osan.insert_disk(node_ip=node_ip2, disk_id=l.split(",")[0],
                                                         disk_usage="DATA")
        env_manage_repair_test.Reliable_osan.add_disks(s_ip=node_ip2, node_ids=node_id2, uuid=l.split(",")[-2],
                                                       usage="DATA",
                                                       storage_id=stor_id_block)
    for l in L3:
        env_manage_repair_test.Reliable_osan.remove_disk(node_ip=node_ip3, disk_id=l.split(",")[0], disk_usage="DATA")
    time.sleep(int(cp('timeout', 'disk_timeout')) /int(cp('timeout', 'unit_time'))+ 10)
    for l in L3:
        env_manage_repair_test.Reliable_osan.check_disk_state(node_ip=node_ip3,
                                                              disk_uuid=l.split(",")[-2],
                                                              disk_state="DISK_STATE_ZOMBIE")  # 检测磁盘状态，若为ZOMBIE，认为重建完成
        env_manage_repair_test.com_disk.remove_disks(disk_ids=l.split(",")[-1])
        env_manage_repair_test.Reliable_osan.insert_disk(node_ip=node_ip3, disk_id=l.split(",")[0], disk_usage="DATA")
        env_manage_repair_test.Reliable_osan.add_disks(s_ip=node_ip3, node_ids=node_id3, uuid=l.split(",")[-2],
                                                       usage="DATA",
                                                       storage_id=stor_id_block)


def run_vdb(arg=1):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=min_seq_w, jn_jro='jn', output=node_ip1)


def case():
    log.info("step1:生成vdbench配置文件，主机端登录 ...")
    iscsi_login()
    log.info("step2:在主机1上运行vdbench -f min-seq-w-1l.conf -jn ...")
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=min_seq_w, jn_jro='jn', output=node_ip1)
    log.info("step3:业务完成后将每副本对应硬盘依次故障超时...")
    disk_error()
    log.info("重建完成后，比较内部数据一致性")
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=min_seq_w, jn_jro='jro',
                                            output=node_ip1)
    env_manage_repair_test.break_down.check_bad_obj()
    env_manage_repair_test.Reliable_osan.compare_data()


def main():
    env_manage_repair_test.rel_check_before_run(filename=file_name)  # 环境检测和准备

    case()  # 用例步骤

    env_manage_repair_test.clean()  # 环境清理


if __name__ == '__main__':
    common.case_main(main)  # 主函数执行入口
