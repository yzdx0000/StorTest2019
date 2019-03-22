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

# testlink case: 1000-33340
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

"""获取指定节点数据盘和共享盘"""
share_disk, data_disk = env_manage_repair_test.Reliable_osan.get_share_monopoly_disk_ids(s_ip=node_ip1, node_id=node_id)
disk_ids = []
for data_disk in data_disk:
    disk_phy_id = env_manage_repair_test.Reliable_osan.get_physicalid_by_name(node_ip1, data_disk)
    disk_ids.append(disk_phy_id)
disk_phy_id = disk_ids[0]  # 磁盘物理id1
disk_phy_id2 = disk_ids[1]  # 磁盘物理id1
disk_name = env_manage_repair_test.Reliable_osan.get_name_by_physicalid(node_ip1, disk_phy_id)  # 磁盘名字
disk_uuid = env_manage_repair_test.com_disk.get_disk_uuid_by_name(node_id=node_id, disk_name=disk_name)  # 磁盘uuid
disk_id = env_manage_repair_test.Reliable_osan.get_diskid_by_name(s_ip=node_ip1, node_id=node_id,
                                                                  disk_name=disk_name)  # 集群中的磁盘id
disk_name2 = env_manage_repair_test.Reliable_osan.get_name_by_physicalid(node_ip1, disk_phy_id2)  # 磁盘名字
disk_uuid2 = env_manage_repair_test.com_disk.get_disk_uuid_by_name(node_id=node_id, disk_name=disk_name2)  # 磁盘uuid
disk_id2 = env_manage_repair_test.Reliable_osan.get_diskid_by_name(s_ip=node_ip1, node_id=node_id,
                                                                   disk_name=disk_name2)  # 集群中的磁盘id
stor_id_block = env_manage_repair_test.Lun_osan.get_storage__type_id(s_ip=node_ip1)
share_disk, data_disk = env_manage_repair_test.Reliable_osan.get_share_monopoly_disk_ids(s_ip=node_ip2,
                                                                                         node_id=node_id2)
share_disk3, data_disk3 = env_manage_repair_test.Reliable_osan.get_share_monopoly_disk_ids(s_ip=node_ip2,
                                                                                           node_id=node_id2)
disk_ids3 = []
for data_disk3 in data_disk3:
    disk_phy_id = env_manage_repair_test.Reliable_osan.get_physicalid_by_name(node_ip2, data_disk3)
    disk_ids3.append(disk_phy_id)
disk_phy_id3 = disk_ids3[0]

"""计算集群中所有lun大小之和,因为主机只映射了一半的lun，根据此值设置vdbench  maxdata的值是实际lun大小的2倍"""
lun_ids = env_manage_repair_test.Lun_osan.get_lun(node_ip1)
total_lun_size = 0.0
for lun_id in lun_ids:
    total_lun_size = total_lun_size + (env_manage_repair_test.Lun_osan.get_option_single(s_ip=node_ip1,
                                                                                         command='get_luns', ids="ids",
                                                                                         indexname="luns",
                                                                                         argv2="total_bytes",
                                                                                         argv1=lun_id)) / 1024 / 1024

vdbench_lun_size = "{}G".format(round(total_lun_size / 1024, 2))
log.info("将vdbench的maxdata值设置为集群主机映射lun总大小的2倍，为{}".format(vdbench_lun_size))


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


def run_vdb1(arg=0):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=mix_R_Align, jn_jro='jn', output=node_ip1)


def run_vdb2(arg=0):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip2, vdb_xml=mix_R, output=node_ip1)


def disk_error(arg=0):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    decorator_func.timer(int(cp("wait_time", "remove_disk")))
    log.info(disk_ids)
    env_manage_repair_test.com_disk.remove_disks(disk_ids=disk_id)
    env_manage_repair_test.com_disk.remove_disks(disk_ids=disk_id2)


def disk_error1(arg=1):
    decorator_func.timer(int(cp("wait_time", "remove_disk")) + 10)
    env_manage_repair_test.Reliable_osan.remove_disk(node_ip=node_ip2, disk_id=disk_phy_id3, disk_usage="DATA")

    time.sleep(900)

    env_manage_repair_test.Reliable_osan.insert_disk(node_ip=node_ip2, disk_id=disk_phy_id3, disk_usage="DATA")


def vdb_jn(confile, type):
    log.info("Run vdbench with jn.")
    env_manage_repair_test.co2_osan.run_vdb(client_ip1, confile, output=node_ip1, jn_jro=type)


def case():
    log.info("生成vdbench配置文件，主机端登录 ...")
    iscsi_login()
    log.info("在主机1上运行vdbench -f mix-R-Align.conf -jn；在主机2上运行vdbench -f mix-R.conf,业务过程中手动删除二块数据盘 ...")
    decorator_func.multi_threads(run_vdb1, run_vdb2, disk_error, disk_error1)
    log.info("数据重建时，重建源数据盘拔掉,主机端执行vdbench -f mix-R-Align.conf -jro;校验数据一致性...")
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=mix_R_Align, jn_jro='jro', output=node_ip1)
    log.info("插回拔掉的输盘后，数据重建和修复完成后，比较内部数据一致性 ...")
    env_manage_repair_test.Reliable_osan.add_disks(s_ip=node_ip1, node_ids=node_id, uuid=disk_uuid, usage="DATA",
                                                   storage_id=stor_id_block)
    env_manage_repair_test.Reliable_osan.add_disks(s_ip=node_ip1, node_ids=node_id, uuid=disk_uuid2, usage="DATA",
                                                   storage_id=stor_id_block)
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=mix_R_Align, jn_jro='jro',
                                            output=node_ip1)
    env_manage_repair_test.break_down.check_bad_obj()
    env_manage_repair_test.Reliable_osan.compare_data()


def main():
    env_manage_repair_test.rel_check_before_run(filename=file_name)  # 环境检测和准备

    case()  # 用例步骤

    common.ckeck_system()  # 检查系统core

    env_manage_repair_test.clean()  # 环境清理


if __name__ == '__main__':
    common.case_main(main)  # 主函数执行入口
