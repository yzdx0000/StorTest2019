# -*- coding:utf-8 _*-
# Author:wangxiang
# Date  :2018-8-7
"""
测试内容:副本下，数据盘故障触发的数据修复开始前，oJob进程故障
步骤:
1、在节点A上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
3、在主机1上运行vdbench -f mix-R-Align.conf -jn；在主机2上运行vdbench -f mix-R.conf;
4、业务过程中将存储池磁盘拔出一块；
5、先将oJob进程故障，再插回被拔出的磁盘触发修复；
6、修复完成后在主机1上运行vdbench -f mix-R-Align.conf -jro;
7、数据修复完成系统恢复正常后，比较内部数据一致性。

检查项:
1、步骤4，将磁盘拔出，业务正常，系统上报磁盘故障信息
2、步骤5，插回拔出的磁盘，开始修复
3、步骤6、oStor进程故障后，可自动恢复，修复完成，数据校验一致
4、步骤7、数据修复完成后，内部数据校验一致
"""
# testlink case: 1000-33302
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
    global mix_R_Align
    global mix_R
    login.login()

    # 修改vdbench配置文件的参数值
    #seekpct = 0  # 随机
    rdpct1 = 0  # 读写比例(0是全写)
    rdpct2 = 50
    xfersize1 = cp("vdbench", "mix_xfersize1")
    lun1 = env_manage_repair_test.Lun_osan.ls_scsi_dev(client_ip1)
    lun2 = env_manage_repair_test.Lun_osan.ls_scsi_dev(client_ip2)
    mix_R_Align = env_manage_repair_test.co2_osan.gen_vdb_xml(max_range=cp("vdbench", "range"),
                                                              maxdata=cp("vdbench", "maxdata"),
                                                              thread=cp("vdbench", "threads"), lun=lun1,
                                                              xfersize=xfersize1, seekpct=cp("vdbench", "seekpct"),
                                                              rdpct=rdpct2)
    mix_R = env_manage_repair_test.co2_osan.gen_vdb_xml(max_range=cp("vdbench", "range"),
                                                        maxdata=cp("vdbench", "maxdata"),
                                                        thread=cp("vdbench", "threads"), lun=lun2, xfersize=xfersize1,
                                                        seekpct=cp("vdbench", "seekpct"),
                                                        rdpct=rdpct2, offset=int(cp("vdbench", "offset")))


def disk_error(arg=1):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    time.sleep(10)
    env_manage_repair_test.Reliable_osan.remove_disk(node_ip=node_ip1, disk_id=disk_phy_id, disk_usage="DATA")
    ReliableTest.run_kill_process(node_ip1, 'oJob')  # 将Job进程故障
    time.sleep(int(cp("wait_time", "interval_disk")))
    env_manage_repair_test.Reliable_osan.insert_disk(node_ip1, disk_id=disk_phy_id, disk_usage="DATA")


def run_vdb1(arg=0):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=mix_R_Align, jn_jro='jn', output=node_ip1)


def run_vdb2(arg=0):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip2, vdb_xml=mix_R, output=node_ip1)


def os_error(arg=3):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    time.sleep(int(cp("wait_time", "remove_disk")))
    type_info = env_manage_repair_test.get_os_type(node_ip3)
    env_manage_repair_test.down_node(node_ip3, type_info, "init 6")
    env_manage_repair_test.Reliable_osan.get_os_status(node_ip3)  # 检测重启后机器状态，是否已开机

    env_manage_repair_test.Reliable_osan.run_pause_process("oSan", node_ip1)  # 将源节点oStor进程故障


def case():
    log.info("step1:生成vdbench配置文件，主机端登录 ...")
    iscsi_login()
    log.info(
        "step2:在主机1上运行vdbench -f mix-R-Align.conf -jn；在主机2上运行vdbench -f mix-R.conf,业务过程中，业务过程中将存储池磁盘拔出一块 ...")
    decorator_func.multi_threads(run_vdb1, run_vdb2, disk_error)
    log.info("step3:插先将oJob进程故障，再插回被拔出的磁盘触发修复,主机端执行vdbench -f mix-R-Align.conf -jro;校验数据一致性 ...")
    env_manage_repair_test.break_down.check_bad_obj()
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=mix_R_Align, jn_jro='jro',
                                            output=node_ip1)
    log.info("数据修复完成系统恢复正常后，比较内部数据一致 ...")
    env_manage_repair_test.Reliable_osan.compare_data()


def main():
    env_manage_repair_test.rel_check_before_run(filename=file_name)  # 环境检测和准备

    case()  # 用例步骤

    common.ckeck_system()  # 检查系统core

    env_manage_repair_test.clean()  # 环境清理


if __name__ == '__main__':
    common.case_main(main)  # 主函数执行入口