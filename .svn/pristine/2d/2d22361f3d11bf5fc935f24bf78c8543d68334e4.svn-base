# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-6

'''
测试内容:映射时异常
测试步骤：
1）创n个建逻辑卷
2）将n个逻辑卷映射至主机
3）在映射过程中将日志组业务节点关机
4）主机端检查逻辑卷个数
5）逻辑卷可正常使用
检查项：
1）逻辑卷创建成功
2）映射过程中关闭节点，映射不中断
3）逻辑卷全部映射至主机
4）逻辑卷可正常使用

'''

# testlink case: 1000-33634
import os
import time
import random
import commands
import threading
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

infos = []
os_types = []


def setup():
    '''获取业务节点IP和非业务节点IP'''
    global node_ip1
    global node_ip2
    global client_ip1
    node_ip1 = env_manage.get_inter_ids()[0]  # 业务节点IP
    node_ip2 = env_manage.get_inter_ids()[-1]  # 非业务节点IP
    client_ip1 = env_manage.client_ips[0]


def node_fault(down_ip):
    log.info("step:3. the node shut down")
    os_type = env_manage.get_os_type(down_ip)
    info = env_manage.down_node(down_ip, os_type, "init 0")
    os_types.append(os_type)
    infos.append(info)
    log.info("node down finished")


def case():
    log.info("******************* case start **********************")
    log.info("step:1.创建逻辑卷")
    env_manage.create_luns(s_ip=node_ip1, nums=10)
    log.info("step:3.创建lun map")
    threads = []
    threads.append(threading.Thread(target=node_fault, args=(node_ip1,)))
    threads.append(threading.Thread(target=env_manage.create_lun_map, args=(node_ip2,)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    log.info("step:5.检查lun map")
    lun_map_ids = env_manage.osan.get_lun_maps(node_ip2)
    lun_ids = env_manage.osan.get_lun()
    if len(lun_map_ids) == len(lun_ids):
        log.info("step:6.lun map数量正确 %s 节点开机 节点类型%s,节点ID or IPMI IP: %s" % (node_ip1, os_types[0], infos[0]))
        env_manage.up_node(infos[0], os_types[0])
        log.info("step:7.检查节点运行状态，检查服务恢复情况。")
        env_manage.com_lh.get_os_status(node_ip1)
    else:
        log.info("lun map test fail,get lun map %s " % (lun_map_ids))
        exit(1)
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
