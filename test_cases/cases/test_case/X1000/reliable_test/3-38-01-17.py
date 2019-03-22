# -*- coding:utf-8 _*-
# Author:wangxiang
# Date  :2019-02-20
"""
1、 每节点创建100条thick和thin混合LUN，共创建300条LUN，其中LUN1-LUN100对应对齐 大小块混合读写，LUN101-LUN200为非对齐 大小块混合读写；且指定100条LUN使用和该LUN不同节点target做映射
2、使用2个主机，主机1映射LUN1-LUN100，主机2映射LUN101-LUN200；
3、在主机1上运行vdbench -f mix-S-Align.conf -jn；在主机2上运行vdbench -f mix-S.conf;
4、在步骤3中的业务运行过程中，将一个业务节点的所有业务网故障；
5、5分钟后，步骤4上的VIP接收节点的业务网再次故障
6、主机1上业务完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性；
7、比较存储内部数据一致性
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
import error

import env_manage_repair_test
import env_manage_lun_manage
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

disk = breakdown.disk()
osan = common2.oSan()

log.info("获取故障节点的所有业务网")
fault_node_id1 = env_manage_repair_test.break_down.get_node_id_by_ip(n_ip=node_ip1)

io_eth_list1, a_extra1 = error.get_ioip_info(node_id=fault_node_id1)
log.info(io_eth_list1)
fault_eth_list1 = error.get_data_eth(fault_node_id1)
log.info(fault_eth_list1)

fault_node_id2 = env_manage_repair_test.break_down.get_node_id_by_ip(n_ip=node_ip2)

io_eth_list2, a_extra2 = error.get_ioip_info(node_id=fault_node_id2)
log.info(io_eth_list2)

fault_eth_list2 = error.get_data_eth(fault_node_id2)
log.info(fault_eth_list2)

fault_node_id3 = env_manage_repair_test.break_down.get_node_id_by_ip(n_ip=node_ip3)

io_eth_list3, a_extra3 = error.get_ioip_info(node_id=fault_node_id3)
log.info(io_eth_list3)

fault_eth_list3 = error.get_data_eth(fault_node_id2)
log.info(fault_eth_list3)

"""获取指定节点数据盘和共享盘"""
share_disk, data_disk = env_manage_repair_test.Reliable_osan.get_share_monopoly_disk_ids(s_ip=node_ip1, node_id=node_id)
disk_ids = []
L = []
for share_disk in share_disk:
    disk_phy_id = env_manage_repair_test.Reliable_osan.get_physicalid_by_name(node_ip1, share_disk)
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
for share_disk in share_disk:
    disk_phy_id = env_manage_repair_test.Reliable_osan.get_physicalid_by_name(node_ip2, share_disk)
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
for share_disk in share_disk:
    disk_phy_id = env_manage_repair_test.Reliable_osan.get_physicalid_by_name(node_ip3, share_disk)
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
stor_id_block = env_manage_repair_test.Lun_osan.get_storage__type_id(s_ip=node_ip1, type="SHARED")


def iscsi_login():
    global mix_R_Align
    global mix_R
    login.login()

    # 修改vdbench配置文件的参数值
    lun1 = env_manage_repair_test.Lun_osan.ls_scsi_dev(client_ip1)
    lun2 = env_manage_repair_test.Lun_osan.ls_scsi_dev(client_ip2)
    mix_R_Align = env_manage_repair_test.co2_osan.gen_vdb_xml(max_range=cp("vdbench", "range"),
                                                              maxdata=cp("vdbench", "maxdata"),
                                                              thread=cp("vdbench", "threads"), lun=lun1,
                                                              xfersize=cp("vdbench", "unmix_xfersize1"),
                                                              seekpct=cp("vdbench", "seekpct"),
                                                              rdpct=cp("vdbench", "rdpct1"))
    mix_R = env_manage_repair_test.co2_osan.gen_vdb_xml(max_range=cp("vdbench", "range"),
                                                        maxdata=cp("vdbench", "maxdata"),
                                                        thread=cp("vdbench", "threads"), lun=lun2,
                                                        xfersize=cp("vdbench", "mix_xfersize1"),
                                                        seekpct=cp("vdbench", "seekpct"),
                                                        rdpct=cp("vdbench", "rdpct2"),
                                                        offset=int(cp("vdbench", "offset")))


def disk_error(arg=1):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    env_manage_repair_test.Reliable_osan.remove_disk(node_ip=node_ip1, disk_id=L[0].split(",")[0], disk_usage="SHARED")

    env_manage_repair_test.Reliable_osan.remove_disk(node_ip=node_ip1, disk_id=L2[0].split(",")[0], disk_usage="SHARED")

    time.sleep(300)

    env_manage_repair_test.Reliable_osan.insert_disk(node_ip=node_ip1, disk_id=L[0].split(",")[0], disk_usage="SHARED")

    env_manage_repair_test.Reliable_osan.insert_disk(node_ip=node_ip1, disk_id=L2[0].split(",")[0], disk_usage="SHARED")


def network_error(arg=1):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    time.sleep(50)
    # 数据重建时(执行disk_error后开始重建)，重建目标节点数据网故障
    for i in io_eth_list1:
        env_manage_repair_test.Reliable_osan.network_test(s_ip=node_ip1,
                                                          net_name=i,
                                                          net_stat="down")


def network_error2(arg=1):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    time.sleep(350)
    env_manage_repair_test.Reliable_osan.net_flash_test(node_ip1, fault_eth_list1)


def network_error3(arg=1):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    time.sleep(350)
    env_manage_repair_test.Reliable_osan.net_flash_test(node_ip2, fault_eth_list2)


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


def lun_map():
    node_ids_list = env_manage_lun_manage.osan.get_nodes(node_ip1)
    node_ids = ",".join('%s' % id for id in node_ids_list)

    exe_id = env_manage_lun_manage.Reliable_osan.get_node_id_by_ip(node_ip2)

    targets = env_manage_lun_manage.osan.gen_dict_mul(s_ip=node_ip2, command="get_targets", arg1="nodeId",
                                                      arg2="id",
                                                      arg3="targets", target=exe_id)

    node_id1 = env_manage_lun_manage.Reliable_osan.get_node_id_by_ip(node_ip1)
    luns1 = env_manage_lun_manage.osan.get_luns_by_node_id(node_id=node_id1)

    node_id2 = env_manage_lun_manage.Reliable_osan.get_node_id_by_ip(node_ip2)
    luns3 = env_manage_lun_manage.osan.get_luns_by_node_id(node_id=node_id2)
    hostgroup_ids = env_manage_lun_manage.osan.get_host_groups(s_ip=node_ip1)
    for lun in luns1:
        env_manage_lun_manage.osan.lun_map_by_target(node_ip1, lun_ids=lun, target_id=targets[0],
                                                     hp_id=hostgroup_ids[0])
    for lun in luns3:
        env_manage_lun_manage.osan.map_lun(s_ip=node_ip1, lun_ids=lun, hg_id=hostgroup_ids[1])


def case():
    env_manage_lun_manage.lun_map_by_target()
    iscsi_login()
    decorator_func.multi_threads(run_vdb1, run_vdb2, disk_error)

    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=mix_R_Align, jn_jro='jro',
                                            output=node_ip1)
    log.info("数据修复完成系统恢复正常后，比较内部数据一致 ...")

    env_manage_repair_test.break_down.check_bad_obj()
    env_manage_repair_test.Reliable_osan.compare_data()


def main():
    common2.oSan().check_vip_balance(need_judge=1)
    error.rel_check_before_run(file_name, jnl_rep=3, node_num=3)
    env_manage_lun_manage.revert_env()
    case()
    env_manage_repair_test.xstor_init()
    common2.oSan().check_vip_balance(need_judge=1, need_wait=1)
    decorator_func.pass_flag()


if __name__ == '__main__':
    common.case_main(main)  # 主函数执行入口