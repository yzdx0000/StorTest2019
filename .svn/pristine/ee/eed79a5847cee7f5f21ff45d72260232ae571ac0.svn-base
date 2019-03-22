# -*- coding:utf-8 _*-
# Author:wangxiang
# Date  :2018-8-7
"""
测试内容:副本下，主动删除一个节点触发修复后，大小块混合读写
步骤:
1、在节点A创建lun1-lun6
2、将逻辑卷映射至主机1上lun1-lun6
3、在主机1上运行vdbench -f min-seq-write.conf -jn；
4、业务完成前，将一个节点删除；
5、删除开始后，在主机1上运行vdbench -f mix-S-Align.conf -jn；
6、业务执行完成后，主机端执行 vdbench -f mix-S-Align.conf -jro校验数据一致性
7、数据重建完成后，比较内部数据一致性。

检查项:
1、步骤4、节点开始删除后，立即执行重建；
2、步骤5、节点状态显示重建状态
3、步骤6、业务正常，比较数据一致
4、步骤7、重构完成后，内部数据比较一致。
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
nodeids = env_manage_repair_test.Lun_osan.get_nodes(node_ip1)


def iscsi_login():
    global mix_seq_w
    global mix_seq_r
    global min_seq_w
    login.login()

    # 修改vdbench配置文件的参数值
    #seekpct = 0  # 随机
    rdpct1 = 0  # 读写比例(0是全写)
    rdpct2 = 100
    xfersize1 = cp("vdbench", "mix_xfersize1")
    xfersize2 = cp("vdbench", "unmix_xfersize1")
    lun1 = env_manage_repair_test.Lun_osan.ls_scsi_dev(client_ip1)
    mix_seq_w = env_manage_repair_test.co2_osan.gen_vdb_xml(lun=lun1, xfersize=xfersize1, seekpct=cp("vdbench", "seekpct"), rdpct=rdpct1)
    min_seq_w = env_manage_repair_test.co2_osan.gen_vdb_xml(lun=lun1, xfersize=xfersize2, seekpct=cp("vdbench", "seekpct"), rdpct=rdpct1)
    mix_seq_r = env_manage_repair_test.co2_osan.gen_vdb_xml(lun=lun1, xfersize=xfersize1, seekpct=cp("vdbench", "seekpct"), rdpct=rdpct2)


def node_error(arg=1):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    env_manage_repair_test.Lun_osan.remove_node(node_ip1, nodeids[-1])


def run_vdb1(arg=0):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=min_seq_w, jn_jro='jn', output=node_ip1)


def case():
    log.info("step1:生成vdbench配置文件，主机端登录 ...")
    iscsi_login()
    log.info("step2:在主机1上运行vdbench -f min-seq-w-1l.conf -jn,业务完成前，将一个存储节点删除 ...")
    decorator_func.multi_threads(node_error, run_vdb1)
    log.info("step3:删除开始后，在主机1上运行vdbench -f mix-S-Align.conf -jn")
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=mix_seq_w, jn_jro='jn', output=node_ip1)
    log.info("step4:主机端执行vdbench -f min-seq-write.conf -jro校验数据一致性 ...")
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=mix_seq_r, jn_jro='jro',
                                            output=node_ip1)
    log.info("数据修复完成后，比较内部数据一致性 ...")
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=min_seq_w, jn_jro='jro',
                                            output=node_ip1)
    env_manage_repair_test.break_down.check_bad_obj()
    env_manage_repair_test.Reliable_osan.compare_data()


def main():
    env_manage_repair_test.rel_check_before_run(filename=file_name)  # 环境检测和准备

    case()  # 用例步骤

    common.ckeck_system()  # 检查系统core

    env_manage_repair_test.main()  # 删除节点，重装系统


if __name__ == '__main__':
    common.case_main(main)  # 主函数执行入口
