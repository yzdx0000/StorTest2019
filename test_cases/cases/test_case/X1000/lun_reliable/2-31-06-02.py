# -*-coding:utf-8 -*-
# !/usr/bin/python

'''
测试步骤：
1）配置节点池，配置存储池
2）配置访问区
3）添加SVIP，VIP池
4）创建主机组，创建主机
5）创建 initiator
6）获取target过程中oPmgr异常

检查项：
1）节点池，存储池创建成功
2）访问区创建成功
3）SVIP、vip池配置成功
4）主机组创建成功，主机创建成功
5）启动器创建成功
6）Target成功获取

'''

# testlink case: 1000-33983
import os
import time
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
    global node_ip3
    global client_ip1
    node_ip1 = env_manage.deploy_ips[0]
    node_ip2 = env_manage.deploy_ips[1]
    node_ip3 = env_manage.deploy_ips[2]
    client_ip1 = env_manage.client_ips[0]


def run_kill():
    master_orole_ip = env_manage.com_lh.get_master_oRole(node_ip1)
    env_manage.com_lh.kill_thread(s_ip=master_orole_ip, p_name="oRole", t_name="pmgr")


def case():
    env_manage.create_luns(nums=10)
    env_manage.create_lun_map()
    threads = []
    t1 = threading.Thread(target=run_kill)
    threads.append(t1)
    t2 = threading.Thread(target=env_manage.create_iscsi_login, args=(client_ip1,))
    threads.append(t2)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    lun_name = env_manage.osan.ls_scsi_dev(client_ip=client_ip1)
    lun_ids = env_manage.osan.get_lun()
    if len(lun_name) == len(lun_ids):
        log.info("host get lun numbers right")
        env_manage.osan.iscsi_logout_all(client_ip1)
    else:
        log.error("check xstor disk is not equal 1 ,find disk is %s" % (len(lun_name)))
        env_manage.osan.iscsi_logout_all(client_ip1)
        exit(1)


def main():
    env_manage.clean_test_env()
    setup()
    case()
    env_manage.clean_lun_map()
    env_manage.clean_lun()
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)
