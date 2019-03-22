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

# testlink case: 1000-33953
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
    global client_ip1
    node_ip1 = env_manage.get_inter_ids()[0]  # 业务节点IP
    node_ip2 = env_manage.get_inter_ids()[-1]  # 非业务节点IP
    client_ip1 = env_manage.client_ips[0]


def run_kill_process():
    ojmgs_node_id, master_ojmgs_ip = env_manage.com_lh.oJmgs_master_id()
    master_orole_ip = env_manage.com_lh.get_master_oRole(node_ip1)
    log.info("will kill %s oRole" % (master_orole_ip))
    ReliableTest.run_kill_process(node_ip=master_orole_ip, process="oRole")
    log.info("will kill %s oJmgs" % (master_orole_ip))
    ReliableTest.run_kill_process(node_ip=master_ojmgs_ip, process="oJmgs")
    return


def case():
    log.info("step:1.create lun")
    env_manage.create_luns(s_ip=node_ip1, nums=10)
    log.info("step:2.修改逻辑卷时查杀oRole和某个节点上的oSan进程")
    threads = []
    t1 = threading.Thread(target=run_kill_process)
    threads.append(t1)
    t2 = threading.Thread(target=env_manage.update_luns)
    threads.append(t2)
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def main():
    env_manage.clean_test_env()
    setup()
    case()
    log.info("step:3.清理检查测试环境")
    env_manage.clean_lun()
    env_manage.com_lh.get_os_status(node_ip1)
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == '__main__':
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)
