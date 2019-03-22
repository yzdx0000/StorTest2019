# -*- coding:utf-8 _*-
# Author:wangxiang
# Date  :2018-8-6
"""
测试内容:元数据对象损坏后写该对象

步骤:
1、在节点A创建LUN1
2、将逻辑卷映射至主机1上LUN1
3、在主机1上运行vdbench -f min-seq-w-1l.conf -jn；
4、业务完成或将一个日志节点的一个共享盘拔出；
5、在主机1上运行vdbench -f min-seq-w-1l.conf -jn；
6、插回故障盘开始修复，主机端执行vdbench -f min-seq-w-1l.conf -jro校验数据一致性
7、数据修复完成后，比较内部数据一致性

检查项:
1、步骤4、业务执行完成后，系统处于待机状态，拔掉一块日志硬盘不触发修复，系统上报磁盘异常告警；
2、步骤5、系统写到坏数据，触发修复，开始修复数据；
3、步骤6、数据校验一致。
4、步骤7、修复完成后，内部数据校验一致
"""
# testlink case: 1000-33214
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
"""获取指定节点数据盘和共享盘"""
share_disk, data_disk = env_manage_repair_test.Reliable_osan.get_share_monopoly_disk_ids(s_ip=node_ip1, node_id=node_id)
disk_ids = []
for share_disk in share_disk:
    disk_phy_id = env_manage_repair_test.Reliable_osan.get_physicalid_by_name(node_ip1, share_disk)
    disk_ids.append(disk_phy_id)
disk_phy_id = random.choice(disk_ids)  # 磁盘物理id
disk_name = env_manage_repair_test.Reliable_osan.get_name_by_physicalid(node_ip1, disk_phy_id)  # 磁盘名字
disk_uuid = env_manage_repair_test.com_disk.get_disk_uuid_by_name(node_id=node_id, disk_name=disk_name)  # 磁盘uuid
disk_id = env_manage_repair_test.Reliable_osan.get_diskid_by_name(s_ip=node_ip1, node_id=node_id,
                                                                  disk_name=disk_name)  # 集群中的磁盘id
stor_id_block = env_manage_repair_test.Lun_osan.get_storage__type_id(s_ip=node_ip1, type="SHARED")


def iscsi_login():
    global min_seq_w
    global min_seq_r
    login.login()

    # 修改vdbench配置文件的参数值
    #seekpct = 0  # 随机
    rdpct1 = 0  # 读写比例(0是全写)
    rdpct2 = 100
    xfersize1 = cp("vdbench", "unmix_xfersize1")
    lun1 = env_manage_repair_test.Lun_osan.ls_scsi_dev(client_ip1)
    min_seq_w = env_manage_repair_test.co2_osan.gen_vdb_xml(max_range=cp("vdbench", "range"),
                                                            maxdata=cp("vdbench", "maxdata"), lun=lun1,
                                                            xfersize=xfersize1, seekpct=cp("vdbench", "seekpct"),
                                                            rdpct=rdpct1, thread=cp("vdbench", "threads"))
    min_seq_r = env_manage_repair_test.co2_osan.gen_vdb_xml(max_range=cp("vdbench", "range"),
                                                            maxdata=cp("vdbench", "maxdata"), lun=lun1,
                                                            xfersize=xfersize1, seekpct=cp("vdbench", "seekpct"),
                                                            rdpct=rdpct2, thread=cp("vdbench", "threads"))


def disk_error(arg):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    env_manage_repair_test.Reliable_osan.remove_disk(node_ip=node_ip1, disk_id=disk_phy_id, disk_usage="SHARED")


def run_vdb(arg=1):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=min_seq_r, jn_jro='jro', output=node_ip1)


def case():
    log.info("step1:生成vdbench配置文件，主机端登录 ...")
    iscsi_login()
    log.info("step2:在主机1上运行vdbench -f min-seq-w-1l.conf -jn ...")
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=min_seq_w, jn_jro='jn', output=node_ip1)
    log.info("step3:业务完成后将一个日志节点的一个共享盘拔出...")
    disk_error(1)

    log.info(
        "step4:在主机1上运行vdbench -f min-seq-w-1l.conf -jn,插回故障盘开始修复,主机端执行vdbench -f min-seq-write.conf -jro校验数据一致性 ...")
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=min_seq_r, output=node_ip1,whether_change_xml="N")
    env_manage_repair_test.Reliable_osan.insert_disk(node_ip=node_ip1, disk_id=disk_phy_id, disk_usage="SHARED")
    # env_manage_repair_test.com_disk.remove_disks(disk_id)
    # env_manage_repair_test.Reliable_osan.add_disks(s_ip=node_ip1, node_ids=node_id, uuid=disk_uuid, usage="SHARED",
    #                                                storage_id=stor_id_block)
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=min_seq_w, output=node_ip1,jn_jro='jro')
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
