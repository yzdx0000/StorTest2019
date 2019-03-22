# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-9

'''
测试内容: oSan进程反复异常中删除lun
测试步骤：
1）创建节点池，创建存储池，配置访问区，开启SAN协议，
2）制造oSan进程反复故障，在故障期间删除LUN
检查项：
1）访问区配置成功
2）逻辑卷成功删除
'''

# testlink case: 1000-33707
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


def setup():
    '''获取业务节点IP和非业务节点IP'''
    global node_ip1
    global node_ip2
    global client_ip1
    node_ip1 = env_manage.get_inter_ids()[0]  # 业务节点IP
    node_ip2 = env_manage.get_inter_ids()[1]  # 业务节点IP
    client_ip1 = env_manage.client_ips[0]


def run_kill():
    for i in range(3):
        kill_ip = random.choice(env_manage.deploy_ips)
        log.info("node %s will kill osan process" % (kill_ip))
        ReliableTest.run_kill_process(kill_ip, "oSan")
        time.sleep(20)


def create_luns():
    for i in range(10):
        lun_name = "LUN" + str(i)
        env_manage.create_lun(ips=node_ip1, name=lun_name)


def check_lun():
    num = env_manage.get_option(s_ip=node_ip1, command="get_luns")
    decorator_func.judge_target(num, 10)


def case():
    log.info("step:1.创建逻辑卷")
    create_luns()
    log.info("step:2.删除逻辑卷时kill oSan 进程")
    threads = []
    t1 = threading.Thread(target=run_kill)
    threads.append(t1)
    t2 = threading.Thread(target=env_manage.clean_lun, args=(node_ip1,))
    threads.append(t2)
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def main():
    env_manage.clean_test_env()
    setup()
    case()
    log.info("step:3.检查测试环境")
    env_manage.com_lh.get_os_status(node_ip1)
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)