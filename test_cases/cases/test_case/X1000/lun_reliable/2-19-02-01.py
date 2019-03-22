# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-16
'''
测试内容:多进程异常情况下创建逻辑卷
测试步骤：
1）创建节点池，创建存储池，配置访问区，开启SAN协议，
2）创建逻辑卷过程中制造oJmgs+oSan进程故障
检查项：
1）访问区配置成功
2）逻辑卷成功创建
'''

# testlink case: 1000-33950
import os
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


def run_kill_process():
    rc = env_manage.com_lh.get_cmd_status(node_ip1, "create_lun")
    if rc == 0:
        master_orole_ip = env_manage.com_lh.get_master_oRole(node_ip1)
        ReliableTest.run_kill_process(node_ip=node_ip1, process="oSan")
        ReliableTest.run_kill_process(node_ip=master_orole_ip, process="oRole")
        return
    elif rc == 1:
        log.error("Not find CMD ,timeout will exit")
        os._exit(1)


def create_luns():
    for i in range(10):
        lun_name = "LUN" + str(i)
        env_manage.create_lun(node_ip1, lun_name)


def case():
    log.info("step:1.创建逻辑卷时查杀oRole和业务节点上的oSan进程")
    threads = []
    t1 = threading.Thread(target=run_kill_process)
    threads.append(t1)
    t2 = threading.Thread(target=create_luns)
    threads.append(t2)
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def main():
    env_manage.clean_test_env()
    setup()
    case()
    log.info("step:2.清理检查测试环境")
    env_manage.clean_lun()
    env_manage.com_lh.get_os_status(node_ip1)
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == '__main__':
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)
