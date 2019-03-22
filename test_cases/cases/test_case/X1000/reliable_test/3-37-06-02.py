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
import Queue
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

q = Queue.Queue(10)
node_ip1 = env_manage_repair_test.jnl_ips[0]
node_ip2 = env_manage_repair_test.jnl_ips[1]
node_ip3 = env_manage_repair_test.jnl_ips[2]
client_ip1 = env_manage_repair_test.client_ips[0]
client_ip2 = env_manage_repair_test.client_ips[1]
esxi_ip = env_manage_repair_test.Esxi_ips
node_id = env_manage_repair_test.Reliable_osan.get_node_id_by_ip(node_ip1)
node_id2 = env_manage_repair_test.Reliable_osan.get_node_id_by_ip(node_ip2)

log.info("获取故障节点的所有业务网")
fault_node_id1 = env_manage_repair_test.break_down.get_node_id_by_ip(n_ip=node_ip1)

io_eth_list1, a_extra1 = error.get_ioip_info(node_id=fault_node_id1)
log.info(io_eth_list1)

fault_node_id2 = env_manage_repair_test.break_down.get_node_id_by_ip(n_ip=node_ip2)

io_eth_list2, a_extra2 = error.get_ioip_info(node_id=fault_node_id2)
log.info(io_eth_list2)

"""获取指定节点数据盘和共享盘"""
share_disk, data_disk = env_manage_repair_test.Reliable_osan.get_share_monopoly_disk_ids(s_ip=node_ip1, node_id=node_id)
disk_ids = []
for share_disk in share_disk:
    disk_phy_id = env_manage_repair_test.Reliable_osan.get_physicalid_by_name(node_ip1, share_disk)
    disk_ids.append(disk_phy_id)
disk_phy_id1 = disk_ids[0]  # 磁盘物理id1
disk_phy_id2 = disk_ids[1]  # 磁盘物理id1
disk_name = env_manage_repair_test.Reliable_osan.get_name_by_physicalid(node_ip1, disk_phy_id1)  # 磁盘名字
disk_uuid = env_manage_repair_test.com_disk.get_disk_uuid_by_name(node_id=node_id, disk_name=disk_name)  # 磁盘uuid
disk_id = env_manage_repair_test.Reliable_osan.get_diskid_by_name(s_ip=node_ip1, node_id=node_id,
                                                                  disk_name=disk_name)  # 集群中的磁盘id
disk_name2 = env_manage_repair_test.Reliable_osan.get_name_by_physicalid(node_ip1, disk_phy_id2)  # 磁盘名字
disk_uuid2 = env_manage_repair_test.com_disk.get_disk_uuid_by_name(node_id=node_id, disk_name=disk_name2)  # 磁盘uuid
disk_id2 = env_manage_repair_test.Reliable_osan.get_diskid_by_name(s_ip=node_ip1, node_id=node_id,
                                                                   disk_name=disk_name2)  # 集群中的磁盘id
stor_id_block = env_manage_repair_test.Lun_osan.get_storage__type_id(s_ip=node_ip1, type="SHARED")
share_disk, data_disk = env_manage_repair_test.Reliable_osan.get_share_monopoly_disk_ids(s_ip=node_ip2,
                                                                                         node_id=node_id2)
disk_ids3 = []
for data_disk in data_disk:
    disk_phy_id = env_manage_repair_test.Reliable_osan.get_physicalid_by_name(node_ip2, data_disk)
    disk_ids3.append(disk_phy_id)
disk_phy_id3 = disk_ids3[1]  # 磁盘物理id1
disk_name3 = env_manage_repair_test.Reliable_osan.get_name_by_physicalid(node_ip2, disk_phy_id3)  # 磁盘名字
disk_uuid3 = env_manage_repair_test.com_disk.get_disk_uuid_by_name(node_id=node_id2, disk_name=disk_name3)  # 磁盘uuid
disk_id3 = env_manage_repair_test.Reliable_osan.get_diskid_by_name(s_ip=node_ip2, node_id=node_id2,
                                                                   disk_name=disk_name3)  # 集群中的磁盘id


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
    time.sleep(10)
    env_manage_repair_test.Reliable_osan.remove_disk(node_ip=node_ip1, disk_id=disk_phy_id1, disk_usage="SHARED")
    env_manage_repair_test.Reliable_osan.remove_disk(node_ip=node_ip1, disk_id=disk_phy_id2, disk_usage="SHARED")
    env_manage_repair_test.Reliable_osan.run_down_disk_wait(node_ip1, int(cp('timeout', 'disk_timeout')))  # 设置磁盘修复超时时间
    time.sleep(int(cp('timeout', 'disk_timeout')) / int(cp('timeout', 'unit_time')) + 30)


def network_error(arg=1):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    decorator_func.timer(50, 25, log_interval=0)
    vip_pool_id = env_manage_lun_manage.osan.get_vip_pool_ids(node_ip1)[0]
    fault_vips1 = env_manage_lun_manage.osan.get_vips_by_node_dict(s_ip=node_ip1, vip_pool_id=vip_pool_id)
    log.info(fault_vips1)
    for i in io_eth_list1:
        env_manage_repair_test.Reliable_osan.network_test(s_ip=node_ip1,
                                                          net_name=i,
                                                          net_stat="down")

    decorator_func.timer(90, 25, log_interval=0)
    fault_vips2 = env_manage_lun_manage.osan.get_vips_by_node_dict(vip_pool_id=vip_pool_id)
    log.info(fault_vips2)

    for k2, v2 in fault_vips2[0].items():
        for k1, v1 in fault_vips1.items():
            if k2 == k1:
                global target_ip
                target_ip = v2
                log.info(target_ip)
                break
    q.put(item=target_ip)
    q.put(item=target_ip)


def network_error2(arg=1):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    decorator_func.timer(250, 25, log_interval=0)

    target_ip = q.get()
    fault_node_id2 = env_manage_repair_test.break_down.get_node_id_by_ip(n_ip=target_ip)

    fault_eth_list2 = error.get_data_eth(fault_node_id2)
    log.info(fault_eth_list2)

    env_manage_repair_test.Reliable_osan.net_flash_test(target_ip, fault_eth_list2)


def os_error(arg=3):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    decorator_func.timer(250, 25, log_interval=0)

    target_ip = q.get()
    for s_ip in env_manage_repair_test.jnl_ips:
        if s_ip != node_ip1 and s_ip != target_ip:
            target_ip = s_ip

    log.info("获取机器类型，若为虚拟机则获取vm_id")
    type_info = env_manage_repair_test.get_os_type(target_ip)
    vm_ids = None
    if type_info != "phy":
        vm_ids = env_manage_repair_test.Reliable_osan.vm_id(esxi_ip=esxi_ip, u_name=cp("esxi", "esxi_user"),
                                                            pw=cp("esxi", "esxi_passwd"),
                                                            node_ip=target_ip)
    else:
        vm_ids = ReliableTest.get_ipmi_ip(target_ip)

    env_manage_repair_test.down_node(target_ip, type_info,"init 6")  # 下电
    env_manage_repair_test.Reliable_osan.get_os_status(target_ip)  # 检测重启后机器状态，是否已开机


def os_error2(arg=3):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    decorator_func.timer(250, 25, log_interval=0)

    log.info("获取机器类型，若为虚拟机则获取vm_id")
    type_info = env_manage_repair_test.get_os_type(node_ip1)
    vm_ids = None
    if type_info != "phy":
        vm_ids = env_manage_repair_test.Reliable_osan.vm_id(esxi_ip=esxi_ip, u_name=cp("esxi", "esxi_user"),
                                                            pw=cp("esxi", "esxi_passwd"),
                                                            node_ip=node_ip1)
    else:
        vm_ids = ReliableTest.get_ipmi_ip(node_ip1)

    env_manage_repair_test.down_node(node_ip1, type_info)  # 下电

    decorator_func.timer(180, 20)

    env_manage_repair_test.up_node(node_info=vm_ids, type_info=type_info)  # 上电
    env_manage_repair_test.Reliable_osan.get_os_status(node_ip1)  # 检测重启后机器状态，是否已开机


def run_vdb1(arg=0):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=mix_R_Align, jn_jro='jn', output=node_ip1)


def run_vdb2(arg=0):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip2, vdb_xml=mix_R, output=node_ip1)


def case():
    iscsi_login()
    decorator_func.multi_threads(run_vdb1, run_vdb2, network_error, network_error2, os_error)
    for i in io_eth_list1:
        env_manage_repair_test.Reliable_osan.network_test(s_ip=node_ip1,
                                                          net_name=i,
                                                          net_stat="up")

    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=mix_R_Align, jn_jro='jro',
                                            output=node_ip1)
    log.info("数据修复完成系统恢复正常后，比较内部数据一致 ...")

    env_manage_repair_test.break_down.check_bad_obj()
    env_manage_repair_test.Reliable_osan.compare_data()


def main():
    common2.oSan().check_vip_balance()
    error.rel_check_before_run(file_name, jnl_rep=3, node_num=5)
    env_manage_lun_manage.revert_env()
    case()
    common2.oSan().check_vip_balance(need_wait=1)
    decorator_func.pass_flag()


if __name__ == '__main__':
    common.case_main(main)  # 主函数执行入口
