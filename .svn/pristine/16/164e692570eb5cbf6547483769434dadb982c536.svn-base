# -*- coding:utf-8 _*-
# Author:wangxiang
# Date  :2018-8-7
"""
测试内容:一个节点数据网超时后恢复

步骤:
1、在节点A创建LUN1-LUN6
2、将逻辑卷映射至主机1上LUN1-LUN6
3、在主机1上运行vdbench -f min-seq-w-1l.conf -jn；
4、业务完成后一个节点数据网断开；
5、等待超时后，触发被动重建；
6、节点重建后将数据网恢复，将节点恢复到集群内；
7、恢复节点后，在主机1上运行vdbench -f min-seq-w-1l.conf -jro；
8、数据重建完成，比较内部数据一致性。

检查项:
1、步骤4、业务执行完成后，系统处于待机状态，拔掉一节点数据网不触发修复，系统上报磁盘异常告警；
2、步骤5、等待超时后触发重建，开始重建数据盘；
3、步骤6、超时后恢复节点数据网，该节点可重新加入到集群
4、步骤7、比较数据一致
5、步骤8，内部数据比较一致
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

fault_node_id = env_manage_repair_test.break_down.get_node_id_by_ip(n_ip=node_ip2)
fault_eth_list = error.get_data_eth(fault_node_id)
log.info(fault_eth_list)


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


def network_error1(arg=1):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    for i in fault_eth_list:
        env_manage_repair_test.Reliable_osan.network_test(s_ip=node_ip2,
                                                          net_name=i,
                                                          net_stat="down")


def network_up1(arg=1):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    for i in fault_eth_list:
        env_manage_repair_test.Reliable_osan.network_test(s_ip=node_ip2,
                                                          net_name=i,
                                                          net_stat="up")


def run_vdb(arg=1):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=min_seq_w, jn_jro='jn', output=node_ip1)


def case():
    log.info("step1:生成vdbench配置文件，主机端登录 ...")
    iscsi_login()
    log.info("step2:在主机1上运行vdbench -f min-seq-w-1l.conf -jn ...")
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=min_seq_w, jn_jro='jn', output=node_ip1)
    log.info("step3:业务完成后一个节点数据网断开...")
    network_error1()
    log.info("step4:等待超时后，触发被动重建；节点重建后将数据网恢复，将节点恢复到集群内(更改磁盘超时时间,以x1000.conf配置为准) ...")
    env_manage_repair_test.Reliable_osan.run_down_node_wait(s_ip=node_ip1,
                                                            timeout=int(cp('timeout', 'node_timeout')))  # 设置修复的超时时间

    time.sleep(int(cp('timeout', 'node_timeout'))/int(cp('timeout', 'unit_time')) + 20)  # 设置等待超时的时间
    network_up1()
    log.info("step5:恢复节点后，在主机1上运行vdbench -f min-seq-w-1l.conf -jro ...")

    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=min_seq_w, jn_jro='jro',
                                            output=node_ip1)
    log.info("重建完成后，比较内部数据一致性")
    env_manage_repair_test.break_down.check_bad_obj()
    env_manage_repair_test.Reliable_osan.compare_data()


def main():
    env_manage_repair_test.rel_check_before_run(filename=file_name)  # 环境检测和准备

    case()  # 用例步骤

    common.ckeck_system()  # 检查系统core

    env_manage_repair_test.clean()  # 环境清理


if __name__ == '__main__':
    common.case_main(main)  # 主函数执行入口
