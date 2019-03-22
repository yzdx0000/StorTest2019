# -*-coding:utf-8 -*-
# !/usr/bin/python

'''
测试步骤：
1、创建节点池，创建存储池
2、创建访问区access1
3、将任意一个节点断电
4、创建访问区access2
检查项：
1）节点池、存储池创建成功
2）节点正常关闭
3）创建访问区成功

'''

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


def run_kill():
    # for i in range(3):
    master_orole_ip = env_manage.com_lh.get_master_oRole(node_ip1)
    env_manage.com_lh.pasue_thread(s_ip=master_orole_ip, p_name="oRole", t_name="pmgr")


def run_pasuse_process():
    master_orole_ip = env_manage.com_lh.oJmgs_master_id(node_ip1)
    env_manage.com_lh.run_process(p_ip=master_orole_ip, p_name="oRole")
    time.sleep(10)


def case():
    env_manage.create_lun(name="LUN1")
    env_manage.create_lun(name="LUN2")
    env_manage.create_lun_map(node_ip1)
    threads = []
    t1 = threading.Thread(target=env_manage.clean_lun_map, args=(node_ip1,))
    threads.append(t1)
    t2 = threading.Thread(target=run_kill)
    threads.append(t2)
    for i in threads:
        i.start()
    for i in threads:
        i.join()
    run_pasuse_process()


def main():
    env_manage.clean_test_env()
    setup()
    case()
    env_manage.clean_lun_map()
    env_manage.clean_lun()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)
