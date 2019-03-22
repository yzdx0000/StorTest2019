# -*-coding:utf-8 -*-
# !/usr/bin/python

'''
测试步骤：
1、创建节点池，创建存储池，配置访问区，添加启动器
2、创建逻辑卷lun1，映射到主机host1
3、将任意一个节点断电
4、创建逻辑卷lun2，映射至主机host1
检查项：
卷异常不会导致主机异常
'''

# testlink case: 1000-33994
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


def lun_map(lun_id):
    host_group_id = env_manage.osan.get_host_groups(s_ip=node_ip1)
    env_manage.osan.map_lun(s_ip=node_ip1, lun_ids=lun_id, hg_id=host_group_id[0])


def ls_scsi_disk():
    lun_names = env_manage.osan.ls_scsi_dev(client_ip=client_ip1)
    log.info("get iscsi lun %s " % (lun_names))


def run_case():
    time.sleep(30)
    log.info("step:2.创建逻辑卷")
    lun_id2 = env_manage.create_lun(name="LUN2")
    log.info("step:3.节点关机")
    os_type = env_manage.get_os_type(node_ip2)
    info = env_manage.down_node(node_ip2, os_type, "init 0")  # 节点关机
    log.info("step:4.创建lun map，ISCSI 登录，扫描磁盘")
    lun_map(lun_id2)  # 创建映射
    env_manage.create_iscsi_login(client_ip1)
    ls_scsi_disk()
    log.info("step:5.%s 节点开机 节点类型%s,节点ID or IPMI IP: %s" % (node_ip2, os_type, info))
    env_manage.up_node(info, os_type)
    log.info("step:6.检查节点运行状态，检查服务恢复情况。")
    env_manage.com_lh.get_os_status(node_ip2)


def case():
    log.info("step:1.创建逻辑卷，创建lun map")
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
    log.info("step:7.清理检查测试环境")
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)