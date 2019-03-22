# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-10
'''
测试内容：添加vip过程中将oPmgr故障
测试步骤：
1）配置节点池，配置存储池
2）配置访问区
3）添加VIP池，添加过程中将oPmgr故障，从进程接管业务，添加成功
检查项：
1）节点池，存储池创建成功
2）访问区创建成功
3）VIP池添加成功
'''

# testlink case: 1000-33966
import os
import time
import threading
import utils_path
import log
import common
import ReliableTest
import env_manage
import access_env
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


def run_kill_thread():
    rc = env_manage.com_lh.get_cmd_status(node_ip1, cmd_name="add_vip_address_pool")
    if rc == 0:
        orole_ip = env_manage.com_lh.get_master_oRole(node_ip1)
        env_manage.com_lh.kill_thread(s_ip=orole_ip, p_name="oRole", t_name="pmgr")
        return
    elif rc == 1:
        log.error("Not find CMD ,timeout will exit")
        os._exit(1)


def case():
    log.info("step:1.创建访问区，创建svip")
    env_manage.create_access()
    env_manage.create_subnet()
    log.info("step:2.创建vip过程中kill pmgr")
    threads = []
    t1 = threading.Thread(target=run_kill_thread)
    threads.append(t1)
    t2 = threading.Thread(target=env_manage.create_vip)
    threads.append(t2)
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def main():
    access_env.check_env()
    setup()
    case()
    log.info("step:3.检查清理测试环境")
    env_manage.clean_vip_address_pool()
    env_manage.clean_subnet()
    env_manage.clean_access_zone()
    access_env.check_env()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)