# -*- coding:utf-8 _*-
"""
测试内容:一个节点下电后写数据，超时内恢复

步骤:
1、在节点A创建lun1-lun6
2、将逻辑卷映射至主机1上lun1-lun6
3、在主机1对lun1上运行vdbench -f min-seq-w-1l.conf -jn；
4、业务过程中将存储一个节点关机；
5、在主机1对lun2上运行vdbench -f min-seq-w-1l.conf -jn（修改/dev/名称）；
6、在超时时间(24小时)内恢复，
7、在主机1上对lun1进行数据校验vdbench -f min-seq-w-1l.conf -jro校验数据一致性；
8、在主机1上对lun2进行数据校验vdbench -f min-seq-w-1l.conf -jro（修改/dev/名称）校验数据一致性。
9、数据修复完成后，比较内部数据一致性

检查项:
1、步骤4、业务完成后关闭一个节点，未达到超时时间数据不修复，系统上报节点异常告警；
2、步骤5、向一个新的空间写入新数据不触发数据修复
3、步骤7/8、数据比较一致

"""

# testlink case: 1000-33202
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

node_ip1 = env_manage_repair_test.deploy_ips[0]
node_ip2 = env_manage_repair_test.deploy_ips[1]
node_ip3 = env_manage_repair_test.deploy_ips[2]
client_ip1 = env_manage_repair_test.client_ips[0]
client_ip2 = env_manage_repair_test.client_ips[1]
esxi_ip = env_manage_repair_test.Esxi_ips

type_info = env_manage_repair_test.get_os_type(node_ip3)
vm_ids = None
if type_info != "phy":
    vm_ids = env_manage_repair_test.Reliable_osan.vm_id(esxi_ip=esxi_ip, u_name=cp("esxi", "esxi_user"),
                                                        pw=cp("esxi", "esxi_passwd"),
                                                        node_ip=node_ip3)
else:
    vm_ids = ReliableTest.get_ipmi_ip(node_ip3)


def os_error(arg=0):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    time.sleep(int(cp("wait_time", "remove_disk")))  # 执行vdbench期间，先等待时间再开始故障的操作

    env_manage_repair_test.down_node(node_ip3, type_info)
    time.sleep(100)

    env_manage_repair_test.up_node(node_info=vm_ids, type_info=type_info)
    env_manage_repair_test.Reliable_osan.get_os_status(node_ip3)  # 检测重启后机器状态，是否已开机


def iscsi_login():
    global lun1_min_seq_w
    global lun2_min_seq_w
    login.login()

    # 修改vdbench配置文件的参数值
    # seekpct = 0  # 随机
    rdpct1 = 0  # 读写比例(0是全写)
    rdpct2 = 100
    xfersize1 = cp("vdbench", "unmix_xfersize1")
    lun1 = env_manage_repair_test.Lun_osan.ls_scsi_dev(client_ip1)
    lun2 = env_manage_repair_test.Lun_osan.ls_scsi_dev(client_ip2)
    lun1_min_seq_w = env_manage_repair_test.co2_osan.gen_vdb_xml(max_range=cp("vdbench", "range"),
                                                                 maxdata=cp("vdbench", "maxdata"),
                                                                 thread=cp("vdbench", "threads"), lun=lun1,
                                                                 xfersize=xfersize1, seekpct=cp("vdbench", "seekpct"),
                                                                 rdpct=rdpct1)
    lun2_min_seq_w = env_manage_repair_test.co2_osan.gen_vdb_xml(max_range=cp("vdbench", "range"),
                                                                 maxdata=cp("vdbench", "maxdata"),
                                                                 thread=cp("vdbench", "threads"), lun=lun2,
                                                                 xfersize=xfersize1, seekpct=cp("vdbench", "seekpct"),
                                                                 rdpct=rdpct1)
    min_seq_r = env_manage_repair_test.Lun_osan.gen_vdb_xml(max_range=cp("vdbench", "range"),
                                                            maxdata=cp("vdbench", "maxdata"),
                                                            thread=cp("vdbench", "threads"), lun=lun1,
                                                            xfersize=xfersize1, seekpct=cp("vdbench", "seekpct"),
                                                            rdpct=rdpct2)


def run_vdb_lun1_w(arg=0):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=lun1_min_seq_w, jn_jro='jn', output=node_ip1)


def run_vdb_lun2_w(arg=0):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip2, vdb_xml=lun2_min_seq_w, jn_jro='jn', output=node_ip1)


def vdb_jn(confile, type):
    log.info("Run vdbench with jn.")
    env_manage_repair_test.co2_osan.run_vdb(client_ip1, confile, output=node_ip1, jn_jro=type)


def run_vdb_jro1(arg=1):
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=lun1_min_seq_w, jn_jro='jro', output=node_ip1)


def run_vdb_jro2(arg=1):
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip2, vdb_xml=lun2_min_seq_w, jn_jro='jro', output=node_ip1)


def case():
    log.info("生成vdbench配置文件，主机端登录 ...")
    iscsi_login()
    log.info("在主机1对lun1上运行vdbench -f min-seq-w-1l.conf -jn,业务过程中将存储一个节点关机 ...")
    decorator_func.multi_threads(run_vdb_lun1_w, os_error)
    log.info("在主机1对lun2上运行vdbench -f min-seq-w-1l.conf -jn（修改/dev/名称）,在超时时间(24小时)内恢复...")
    run_vdb_lun2_w()

    log.info(
        "在主机1上对lun1进行数据校验vdbench -f min-seq-w-1l.conf -jro校验数据一致性；在主机1上对lun2进行数据校验vdbench -f min-seq-w-1l.conf -jro（修改/dev/名称）校验数据一致性")
    decorator_func.multi_threads(run_vdb_jro1,run_vdb_jro2)
    log.info("数据修复完成后，比较内部数据一致性 ...")
    env_manage_repair_test.Reliable_osan.compare_data()


def main():
    env_manage_repair_test.rel_check_before_run(filename=file_name)  # 环境检测和准备

    case()  # 用例步骤

    common.ckeck_system()  # 检查系统core

    env_manage_repair_test.clean()  # 环境清理


if __name__ == '__main__':
    common.case_main(main)  # 主函数执行入口