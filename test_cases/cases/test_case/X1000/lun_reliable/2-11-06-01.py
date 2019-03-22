# -*-coding:utf-8 -*-
# !/usr/bin/python

'''
测试步骤：
逻辑卷删除过程中将日志组业务节点正常重启
检查项：
逻辑卷删除成功
'''

# testlink case: 1000-33665
import os
import time
import random
import commands
import threading
import utils_path
import log
import common
import ReliableTest
import env_manage
import prepare_x1000
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


def os_down():
    rc = env_manage.com_lh.get_cmd_status(node_ip2, cmd_name="delete_lun")
    if rc == 0:
        type = env_manage.get_os_type(node_ip1)
        info = env_manage.down_node(node_ip1, type, "init 6")
        log.info("节点%s 即将reboot，节点类型 %s，节点ID or IPMI IP：%s " % (node_ip1, info, type))
        return
    elif rc == 1:
        log.error("Not find CMD ,timeout will exit")
        os._exit(1)


def case():
    log.info("step:1.创建逻辑卷")
    env_manage.create_lun()
    log.info("step:2.在删除lun时节点重启")
    threads = []
    t1 = threading.Thread(target=env_manage.clean_lun, args=(node_ip2,))
    threads.append(t1)
    t2 = threading.Thread(target=os_down)
    threads.append(t2)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    log.info("step:3.检查节点及服务运行状态")
    env_manage.com_lh.get_os_status(node_ip1)


def main():
    env_manage.clean_test_env()
    setup()
    case()
    log.info("step:4.检查节点及服务运行状态")
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)
