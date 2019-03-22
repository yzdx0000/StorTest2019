# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-6
'''
测试内容:节点异常情况下创建逻辑卷
测试步骤：
1）创建逻辑卷创建完成后映射至主机
2）将日志组一台非业务节点关机
3）检查逻辑卷状态
4）将逻辑卷重新映射至主机，对逻辑卷进行读写
检查项：
1）逻辑卷状态显示正常
2）可正常读写

'''

# testlink case: 1000-33622
import os
import time
import random
import commands
import utils_path
import log
import common
import ReliableTest
import prepare_x1000
import env_manage
import decorator_func

'''初始化'''
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log


def setup():
    '''获取业务节点IP和非业务节点IP'''
    global node_ip1
    global node_ip2
    global client_ip1
    node_ip1 = env_manage.get_inter_ids()[0]  # 业务节点IP
    node_ip2 = env_manage.get_inter_ids()[-1]  # 非业务节点IP
    client_ip1 = env_manage.client_ips[0]


def vdb_test(run_ip):
    log.info("从主机 %s 获取scsi 设备" % (run_ip))
    lun_name = env_manage.osan.ls_scsi_dev(client_ip=run_ip)
    if len(lun_name) > 10:
        lun_name = lun_name[:10]
    vdb_file = env_manage.com2_osan.gen_vdb_xml(lun=lun_name[:10], xfersize="4k", rdpct="50")
    log.info("vdbench 进行读写业务")
    env_manage.com2_osan.run_vdb(client_ip=run_ip, vdb_xml=vdb_file, output=node_ip1, jn_jro="jn", time=300)
    env_manage.com2_osan.run_vdb(client_ip=run_ip, vdb_xml=vdb_file, output=node_ip1, jn_jro="jro")
    log.info("vdbench run test finished")


def case():
    log.info("******************* case start **********************")
    log.info("step:1.创建逻辑卷")
    env_manage.create_luns()
    log.info("step:2.创建lun map")
    env_manage.create_lun_map(ips=node_ip1)
    log.info("step:3.ISCSI 登录")
    env_manage.create_iscsi_login()
    log.info("step:4.节点关机")
    os_type = env_manage.get_os_type(node_ip2)
    info = env_manage.down_node(node_ip2, os_type, "init 0")
    log.info("step:5.运行vdbench，收集测试结果")
    vdb_test(client_ip1)
    log.info("step:6.%s 节点开机 节点类型%s,节点ID or IPMI IP: %s" % (node_ip2, os_type, info))
    env_manage.up_node(info, os_type)
    log.info("step:7.检查节点运行状态，检查服务恢复情况。")
    env_manage.com_lh.get_os_status(node_ip2)
    # env_manage.com_bd_disk.multi_check_part_lun_uniform_by_ip()  # 校验一致性
    log.info("******************* case end ************************")


def main():
    log.info("step: checking the test environment")
    env_manage.clean_test_env()
    log.info("step: initialize node ip")
    setup()
    case()
    log.info("step:8.清理测试环境")
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)
