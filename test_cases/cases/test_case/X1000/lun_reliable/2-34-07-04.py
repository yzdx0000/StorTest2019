# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-15

'''
测试内容: oJmgs进程异常解除映射
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

# testlink case: 1000-34023
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


def run_kill(master_ip):
    ReliableTest.run_kill_process(node_ip=master_ip, process="oJmgs")


def del_lun_map(id):
    map_id = env_manage.com_lh.get_map_by_lun(node_ip1, id)
    log.info("在节点 %s 删除LUN MAP 映射 %s" % (node_ip1, map_id))
    env_manage.osan.delete_lun_map(s_ip=node_ip1, map_id=map_id)


def run_case():
    ojmgs_id, ojmgs_ip = env_manage.com_lh.oJmgs_master_id()
    time.sleep(60)
    lun_id = env_manage.create_lun(node_ip1, "LUN2")
    env_manage.create_lun_map()
    log.info("step:1.删除lun map过程中kill进程")
    threads = []
    t1 = threading.Thread(target=del_lun_map, args=(lun_id,))
    threads.append(t1)
    t2 = threading.Thread(target=run_kill, args=(ojmgs_ip,))
    threads.append(t2)
    for i in threads:
        i.start()
    for i in threads:
        i.join()


def case():
    log.info("step:1.创建逻辑卷，创建lun map")
    env_manage.create_lun(node_ip1, "LUN1")
    threads = []
    threads.append(threading.Thread(target=env_manage.vdb_test))
    threads.append(threading.Thread(target=run_case))
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def main():
    env_manage.clean_test_env()
    setup()
    case()
    log.info("step:3.检查清理测试环境")
    env_manage.com_lh.get_os_status(node_ip1)
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)