# -*-coding:utf-8 -*-
# !/usr/bin/python

'''
测试步骤：
1、创建节点池，创建存储池，配置访问区，添加启动器
2、创建逻辑卷lun1和lun2，映射至主机host1
3、将任意一个节点断电
4、解除lun1映射
检查项：
1）访问区配置成功
2）创建访问区成功
3）节点正常关闭
4）逻辑卷映射解除成功
'''

# testlink case: 1000-33995
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


def lun_map(lun_ids):
    '''获取lun Id，主机组Id，将逻辑卷映射至主机组'''
    # lun_id = env_manage.osan.get_lun(s_ip=node_ip1)
    host_group_id = env_manage.osan.get_host_groups(s_ip=node_ip1)
    map_id = env_manage.osan.map_lun(s_ip=node_ip1, lun_ids=lun_ids, hg_id=host_group_id[0])
    return map_id


def del_lun_map(m_id):
    log.info("在节点 %s 删除LUN MAP 映射 %s" % (node_ip1, m_id))
    env_manage.osan.delete_lun_map(s_ip=node_ip1, map_id=m_id)


def run_case():
    time.sleep(30)
    lun_id2 = env_manage.create_lun(name="LUN2")
    map_id = lun_map(lun_id2)
    log.info("step:2.节点下电")
    os_type = env_manage.get_os_type(node_ip2)
    info = env_manage.down_node(node_ip2, os_type, "init 0")  # 节点关机
    log.info("step:3.删除一个lun map")
    # map_id = env_manage.com_lh.get_map_by_lun(node_ip1, lun_id2)
    del_lun_map(map_id)
    log.info("step:4.%s 节点开机 节点类型%s,节点ID or IPMI IP: %s" % (node_ip2, os_type, info))
    env_manage.up_node(info, os_type)
    log.info("step:5.检查节点运行状态，检查服务恢复情况。")
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
    log.info("step:6.清理检查测试环境")
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)