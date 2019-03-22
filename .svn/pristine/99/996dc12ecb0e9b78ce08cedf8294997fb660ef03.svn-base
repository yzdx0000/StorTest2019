# -*- coding:utf-8 _*-
"""
测试内容:数据修改写时，同磁盘组多块数据盘故障，超时内恢复

步骤:
1、在节点A创建lun1-lun6
2、将逻辑卷映射至主机1上lun1-lun6
3、在主机1上运行vdbench -f min-seq-write.conf -jn；
4、在步骤3业务进行过程中，将同磁盘组多块数据盘故障；
5、立即触发数据修复，超时内插回拔出的数据盘
6、数据修复过程中，主机端执行vdbench -f min-seq-write.conf -jro校验数据一致性
7、数据修复完成后，比较内部数据一致性

检查项:
1、步骤4、拔掉多块数据盘，业务不受影响，系统上报磁盘异常信息；
2、步骤5、持续修改写数据，故障盘超时后触发数据修复；
3、步骤6、修复过程中，内外部数据校验一致；
4,、步骤7、修复完成后，内部数据校验一致。

"""

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
import prepare_clean
import env_manage_extend_test
import decorator_func
from get_config import config_parser as cp

"""初始化日志和变量"""
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)  # 初始化日志文件

node_ip1 = env_manage_extend_test.deploy_ips[0]
node_ip2 = env_manage_extend_test.deploy_ips[1]
node_ip3 = env_manage_extend_test.deploy_ips[2]
client_ip1 = env_manage_extend_test.client_ips[0]
client_ip2 = env_manage_extend_test.client_ips[1]
esxi_ip = env_manage_extend_test.Esxi_ips
node_id = env_manage_extend_test.com_node.get_node_id_by_ip(node_ip1)
node_id2 = env_manage_extend_test.com_node.get_node_id_by_ip(node_ip2)

"""获取指定节点数据盘和共享盘"""
share_disk, data_disk = env_manage_extend_test.Reliable_osan.get_share_monopoly_disk_ids(s_ip=node_ip1, node_id=node_id)
disk_ids = []
for data_disk in data_disk:
    disk_phy_id = env_manage_extend_test.Reliable_osan.get_physicalid_by_name(node_ip1, data_disk)
    disk_ids.append(disk_phy_id)
disk_phy_id = disk_ids[0]  # 磁盘物理id1
disk_phy_id2 = disk_ids[1]  # 磁盘物理id1
disk_name = env_manage_extend_test.Reliable_osan.get_name_by_physicalid(node_ip1, disk_phy_id)  # 磁盘名字
disk_uuid = env_manage_extend_test.com_disk.get_disk_uuid_by_name(node_id=node_id, disk_name=disk_name)  # 磁盘uuid
disk_id = env_manage_extend_test.Reliable_osan.get_diskid_by_name(s_ip=node_ip1, node_id=node_id,
                                                                  disk_name=disk_name)  # 集群中的磁盘id
disk_name2 = env_manage_extend_test.Reliable_osan.get_name_by_physicalid(node_ip1, disk_phy_id2)  # 磁盘名字
disk_uuid2 = env_manage_extend_test.com_disk.get_disk_uuid_by_name(node_id=node_id, disk_name=disk_name2)  # 磁盘uuid
disk_id2 = env_manage_extend_test.Reliable_osan.get_diskid_by_name(s_ip=node_ip1, node_id=node_id,
                                                                   disk_name=disk_name2)  # 集群中的磁盘id
stor_id_block = env_manage_extend_test.Lun_osan.get_storage__type_id(s_ip=node_ip1)
share_disk, data_disk = env_manage_extend_test.Reliable_osan.get_share_monopoly_disk_ids(s_ip=node_ip2,
                                                                                         node_id=node_id2)
share_disk3, data_disk3 = env_manage_extend_test.Reliable_osan.get_share_monopoly_disk_ids(s_ip=node_ip2,
                                                                                           node_id=node_id2)
disk_ids3 = []
for data_disk3 in data_disk3:
    disk_phy_id = env_manage_extend_test.Reliable_osan.get_physicalid_by_name(node_ip2, data_disk3)
    disk_ids3.append(disk_phy_id)
disk_phy_id3 = disk_ids3[0]


def iscsi_login():
    global mix_R_Align
    global mix_R
    login.login()

    # 修改vdbench配置文件的参数值
    seekpct = 0  # 随机
    rdpct1 = 0  # 读写比例(0是全写)
    rdpct2 = 50
    xfersize1 = cp("vdbench", "mix_xfersize1")
    lun1 = env_manage_extend_test.Lun_osan.ls_scsi_dev(client_ip1)
    lun2 = env_manage_extend_test.Lun_osan.ls_scsi_dev(client_ip2)
    mix_R_Align = env_manage_extend_test.co2_osan.gen_vdb_xml(max_range=cp("vdbench", "range"),
                                                              maxdata=cp("vdbench", "maxdata"),
                                                              thread=cp("vdbench", "threads"), lun=lun1,
                                                              xfersize=xfersize1, seekpct=seekpct,
                                                              rdpct=rdpct2)
    mix_R = env_manage_extend_test.co2_osan.gen_vdb_xml(max_range=cp("vdbench", "range"),
                                                        maxdata=cp("vdbench", "maxdata"),
                                                        thread=cp("vdbench", "threads"), lun=lun2, xfersize=xfersize1,
                                                        seekpct=seekpct,
                                                        rdpct=rdpct2, offset=int(cp("vdbench", "offset")))


def run_vdb1(arg=0):
    log.info('Run task %s (%s)...' % (arg, os.getpid()))
    env_manage_extend_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=mix_R_Align, jn_jro='jn', output=node_ip1)


def run_vdb2(arg=0):
    log.info('Run task %s (%s)...' % (arg, os.getpid()))
    env_manage_extend_test.co2_osan.run_vdb(client_ip=client_ip2, vdb_xml=mix_R, output=node_ip1)


def disk_error(arg=0):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    decorator_func.timer(int(cp("wait_time", "remove_disk")))
    log.info(disk_ids)
    env_manage_extend_test.com_disk.remove_disks(disk_ids=disk_id)
    env_manage_extend_test.com_disk.remove_disks(disk_ids=disk_id2)


def disk_error1(arg=1):
    decorator_func.timer(int(cp("wait_time", "remove_disk")) + 10)
    env_manage_extend_test.Reliable_osan.remove_disk(node_ip=node_ip2, disk_id=disk_phy_id3, disk_usage="DATA")


def add_node(arg=3):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    decorator_func.timer(int(cp("wait_time", "remove_disk")))
    env_manage_extend_test.Lun_osan.add_nodes(node_ip1, cp("add_node_conf", "conf"))


def vdb_jn(confile, type):
    log.info("Run vdbench with jn.")
    env_manage_extend_test.co2_osan.run_vdb(client_ip1, confile, output=node_ip1, jn_jro=type)


def case():
    log.info("生成vdbench配置文件，主机端登录 ...")
    iscsi_login()
    log.info("在主机1上运行vdbench -f mix-R-Align.conf -jn；在主机2上运行vdbench -f mix-R.conf,"
             "在步骤3中的业务运行过程中，向节点池中加入新节点，日志盘配置成共享盘，数据盘配置成数据盘，将数据盘加入到存储池中，存储节点启动均衡； ...")
    decorator_func.multi_threads(run_vdb1, run_vdb2, add_node)
    log.info("数据重建时，重建源数据盘拔掉,主机端执行vdbench -f mix-R-Align.conf -jro;校验数据一致性...")
    env_manage_extend_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=mix_R_Align, jn_jro='jro', output=node_ip1)
    log.info("插回拔掉的输盘后，数据重建和修复完成后，比较内部数据一致性 ...")
    env_manage_extend_test.Reliable_osan.compare_data()


def main():
    env_manage_extend_test.rel_check_before_run(filename=file_name)  # 环境检测和准备

    case()  # 用例步骤

    common.ckeck_system()  # 检查系统core

    env_manage_extend_test.clean()  # 环境清理


if __name__ == '__main__':
    common.case_main(main)  # 主函数执行入口
