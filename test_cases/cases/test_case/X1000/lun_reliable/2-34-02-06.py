# -*-coding:utf-8 -*-
# !/usr/bin/python

'''
测试步骤：
1）配置访问区，将逻辑卷映射主机
2）制造磁盘池异常，使逻辑卷不能正常工作。
3）主机端扫描磁盘，无异常
4）主机端重启，无异常
5）测试windows/linux系统
检查项：
卷异常不会导致主机异常
'''

# testlink case: 1000-34001
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


def del_lun_map(m_id):
    log.info("在节点 %s 删除LUN MAP 映射 %s" % (node_ip1, m_id))
    env_manage.osan.delete_lun_map(s_ip=node_ip1, map_id=m_id)


def run_case():
    time.sleep(30)
    env_manage.create_lun(name="LUN2")
    map_id = env_manage.create_lun_map()
    log.info("step:2.节点重启")
    os_type = env_manage.get_os_type(node_ip2)
    env_manage.down_node(node_ip2, os_type, "init 6")  # 节点关机
    log.info("step:3.删除一个lun map")
    # map_id = env_manage.com_lh.get_map_by_lun(node_ip1, lun_id)
    del_lun_map(map_id[0])
    log.info("step:4.检查节点运行状态，检查服务恢复情况。")
    env_manage.com_lh.get_os_status(node_ip2)


def case():
    log.info("step:1.创建逻辑卷,创建lun map")
    env_manage.create_lun(name="LUN1")
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
    log.info("step:5.清理检查测试环境")
    env_manage.clean_lun_map()
    env_manage.clean_lun()
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)
