# -*- coding:utf-8 _*-
"""
测试内容:副本下，主动删除一个节点时，取消删除

步骤:
1、在节点A创建lun1-lun6
2、将逻辑卷映射至主机1上lun1-lun6
3、在主机1上运行vdbench -f min-seq-write.conf -jn；
4、业务过程中将一个节点删除；
5、删除开始后取消删除；
6、主机端执行vdbench -f min-seq-write.conf -jro校验数据一致性
7、节点恢复正常后，比较内部数据一致性。

检查项:
1、步骤4、拔掉多块数据盘，业务不受影响，系统上报磁盘异常信息；
2、步骤5、持续修改写数据，故障盘超时后触发数据修复；
3、步骤6、修复过程中，内外部数据校验一致；
4,、步骤7、修复完成后，内部数据校验一致。

"""

import os, sys
import utils_path
import common2
import signal
import subprocess
import shlex
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

"""初始化日志和变量"""
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)  # 初始化日志文件

node_ip1 = env_manage_repair_test.deploy_ips[0]
node_ip2 = env_manage_repair_test.deploy_ips[1]
client_ip1 = env_manage_repair_test.client_ips[0]
esxi_ip = env_manage_repair_test.Esxi_ips
node_id = env_manage_repair_test.com_node.get_node_id_by_ip(node_ip1)  # 随机选取一个节点

"""获取指定节点数据盘和共享盘"""
share_disk, data_disk = env_manage_repair_test.Reliable_osan.get_share_monopoly_disk_ids(s_ip=node_ip1, node_id=node_id)
disk_ids = []
for data_disk in data_disk:
    disk_phy_id = env_manage_repair_test.Reliable_osan.get_physicalid_by_name(node_ip1, data_disk)
    disk_ids.append(disk_phy_id)
disk_phy_id = random.choice(disk_ids)  # 磁盘物理id
disk_name = env_manage_repair_test.Reliable_osan.get_name_by_physicalid(node_ip1, disk_phy_id)  # 磁盘名字
disk_uuid = env_manage_repair_test.com_disk.get_disk_uuid_by_name(node_id=node_id, disk_name=disk_name)  # 磁盘uuid
disk_id = env_manage_repair_test.Reliable_osan.get_diskid_by_name(s_ip=node_ip1, node_id=node_id,
                                                                  disk_name=disk_name)  # 集群中的磁盘id
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


def run_vdb(arg=0):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=min_seq_w, jn_jro='jn', output=node_ip1)


def disk_error(arg=0):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    decorator_func.timer(int(cp("wait_time", "remove_disk")))
    env_manage_repair_test.com_disk.remove_disks(disk_ids=disk_id)


def node_error(arg=0):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    decorator_func.timer(int(cp("wait_time", "remove_disk")))
    env_manage_repair_test.Lun_osan.remove_node(s_ip=node_ip2, node_id=node_id)


def cancel_node_error():
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    decorator_func.timer(int(cp("wait_time", "remove_disk")) + 20)
    env_manage_repair_test.Lun_osan.cancel_remove_node(s_ip=node_ip2, node_id=node_id)


def vdb_jn(confile, type):
    log.info("Run vdbench with jn.")
    env_manage_repair_test.co2_osan.run_vdb(client_ip1, confile, output=node_ip1, jn_jro=type)


def case():
    log.info("生成vdbench配置文件，主机端登录 ...")
    iscsi_login()
    log.info("在主机1上运行vdbench -f min-seq-write.conf -jn；业务过程中将一个节点删除； ...")
    decorator_func.multi_threads(node_error, run_vdb, cancel_node_error)
    log.info("删除开始后取消删除；主机端执行vdbench -f mix-R-Align.conf -jro;校验数据一致性...")
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=min_seq_r, jn_jro='jro', output=node_ip1)
    log.info("节点恢复正常后，比较内部数据一致性 ...")
    env_manage_repair_test.break_down.check_bad_obj()
    env_manage_repair_test.Reliable_osan.compare_data()


def main():
    env_manage_repair_test.rel_check_before_run(filename=file_name)  # 环境检测和准备

    case()  # 用例步骤

    common.ckeck_system()  # 检查系统core

    env_manage_repair_test.clean()  # 环境清理


if __name__ == '__main__':
    common.case_main(main)  # 主函数执行入口