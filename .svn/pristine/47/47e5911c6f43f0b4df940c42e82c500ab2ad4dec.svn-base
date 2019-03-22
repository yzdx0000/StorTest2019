# -*- coding:utf-8 _*-
# Author:wangxiang
# Date  :2018-8-9
"""
测试内容:副本下，主动删除一个节点时，oStor进程故障
步骤:
1、在节点A上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
3、在主机1上运行vdbench -f mix-R-Align.conf -jn；在主机2上运行vdbench -f mix-R.conf;
4、业务过程中手动删除一个节点后立即杀掉节点oStor进程
5、数据重建，主机端执行vdbench -f mix-R-Align.conf -jro;校验数据一致性
6、数据重建完成后，比较内部数据一致性。

检查项:
1、步骤4，手动删除成功，业务正常，数据重建启动，oStor进程被拉起
2、步骤5，数据校验一致
3、步骤6、重建完成后，内部数据校验一致。
"""
# testlink case: 1000-33330
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


def iscsi_login():
    global mix_R_Align
    global mix_R
    login.login()

    # 修改vdbench配置文件的参数值
    #seekpct = 0  # 随机
    rdpct1 = 0  # 读写比例(0是全写)
    rdpct2 = 50
    xfersize1 = cp("vdbench", "mix_xfersize1")
    offset = '2048'
    lun1 = env_manage_repair_test.Lun_osan.ls_scsi_dev(client_ip1)
    lun2 = env_manage_repair_test.Lun_osan.ls_scsi_dev(client_ip2)
    mix_R_Align = env_manage_repair_test.co2_osan.gen_vdb_xml(lun=lun1, xfersize=xfersize1, seekpct=cp("vdbench", "seekpct"),
                                                              rdpct=rdpct2)
    mix_R = env_manage_repair_test.co2_osan.gen_vdb_xml(lun=lun2, xfersize=xfersize1, seekpct=cp("vdbench", "seekpct"), rdpct=rdpct2,
                                                        offset=offset)


def os_reboot(arg=1):
    '''节点重启'''
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    env_manage_repair_test.Reliable_osan.poweroff_os(node_ip2, "init 6")  # 虚拟机方式，使用power off命令重启
    # ReliableTest.run_down_node(IPMI_ip) #物理机，使用IPMI方式关机


def os_up(nums=None):
    # ReliableTest.run_up_vir_node(esxi_ip=esxi_ip, u_name="root", pw="parastor;123", vm_id=nums)
    for i in range(600):
        cmd = ("nc -z %s 22 >& /dev/null" % (node_ip1))
        (res, final) = commands.getstatusoutput(cmd)
        if res == 0:
            break
        if i == 60:
            print ("waiting up %s s" % i)
            # ReliableTest.run_up_vir_node(esxi_ip=esxi_ip, u_name="root", pw="parastor;123", vm_id=nums)
        elif i == 120:
            print ("waiting up %s s" % i)
            # ReliableTest.run_up_vir_node(esxi_ip=esxi_ip, u_name="root", pw="parastor;123", vm_id=nums)
        elif i == 599:
            print "os is not up"
            os._exit(1)
        time.sleep(1)


def disk_error(arg=1):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    global disk_ids
    node_id = env_manage_repair_test.com_node.get_node_id_by_ip(node_ip1)
    share_disk, data_disk = env_manage_repair_test.Reliable_osan.get_share_monopoly_disk_ids(s_ip=node_ip1, node_id=node_id)
    disk_ids = []
    for share_disk in share_disk:
        disk_id = env_manage_repair_test.Reliable_osan.get_diskid_by_name(node_ip1, 1, share_disk)
        disk_ids.append(disk_id)
    log.info(disk_ids)
    env_manage_repair_test.Reliable_osan.remove_disk(node_ip=node_ip1, disk_id=disk_ids[0], disk_usage="SHARE")


def node_error(arg=1):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    node_id2 = env_manage_repair_test.com_node.get_node_id_by_ip(node_ip2)
    env_manage_repair_test.Lun_osan.remove_node(node_ip1, node_id2)


def run_vdb1(arg=0):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=mix_R_Align, jn_jro='jn', output=node_ip1)


def run_vdb2(arg=0):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip2, vdb_xml=mix_R, output=node_ip1)


def network_error():
    env_manage_repair_test.Reliable_osan.network_test(node_ip2, cp('create_subnet', 'network_interface'), 'down')


def os_up(nums=None):
    # ReliableTest.run_up_vir_node(esxi_ip=esxi_ip, u_name="root", pw="parastor;123", vm_id=nums)
    for i in range(600):
        cmd = ("nc -z %s 22 >& /dev/null" % (node_ip1))
        (res, final) = commands.getstatusoutput(cmd)
        if res == 0:
            break
        if i == 60:
            print ("waiting up %s s" % i)
            # ReliableTest.run_up_vir_node(esxi_ip=esxi_ip, u_name="root", pw="parastor;123", vm_id=nums)
        elif i == 120:
            print ("waiting up %s s" % i)
            # ReliableTest.run_up_vir_node(esxi_ip=esxi_ip, u_name="root", pw="parastor;123", vm_id=nums)
        elif i == 599:
            print "os is not up"
            os._exit(1)
        time.sleep(1)


def os_down(arg=1):
    '''节点关机'''
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    env_manage_repair_test.Reliable_osan.poweroff_os(node_ip2, "init 0")  # 虚拟机方式，使用power off命令关机
    # ReliableTest.run_down_node(IPMI_ip) #物理机，使用IPMI方式关机


def case():
    log.info("step1:生成vdbench配置文件，主机端登录 ...")
    iscsi_login()
    log.info(
        "step2:在主机1上运行vdbench -f mix-R-Align.conf -jn；在主机2上运行vdbench -f mix-R.conf,业务过程中手动删除一个节点后立即杀掉节点oStor进程...")
    decorator_func.multi_threads(run_vdb1, run_vdb2, node_error)
    ReliableTest.run_kill_process(node_ip1, 'oStor')  # 将oStor进程故障

    log.info("step3:数据重建，主机端执行vdbench -f mix-R-Align.conf -jro;校验数据一致性 ...")
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=mix_R_Align, jn_jro='jro',
                                            output=node_ip1)
    log.info("step4:恢复故障的目标盘，数据重建和修复完成后，比较内部元数据一致性 ...")
    env_manage_repair_test.break_down.check_bad_obj()


def main():
    env_manage_repair_test.rel_check_before_run(filename=file_name)  # 环境检测和准备

    case()  # 用例步骤

    env_manage_repair_test.clean()  # 环境清理

    os._exit(-110)


if __name__ == '__main__':
    common.case_main(main)  # 主函数执行入口
