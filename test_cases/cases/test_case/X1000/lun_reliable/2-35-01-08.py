# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-9

'''
测试内容:SVIP和VIP在同一节点上能被扫描LUN
测试步骤：
1、创建存储池和访问分区，业务子网和对应的SVIP和VIP地址池（至少每个节点四个VIP），并创建2000条LUN，LUN1-LUN2000
2、创建主机组，添加主机，并将主机组映射到LUN1-LUN2000上
3、在主机端使用SVIP登录主机映射的LUN
检查项：
1、使用SVIP登录扫描2000条LUN成功

'''

# testlink case: 1000-33510
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
    node_ip2 = env_manage.get_inter_ids()[-1]  # 非业务节点IP
    client_ip1 = env_manage.client_ips[0]


def lun_map():
    lun_ids = env_manage.osan.get_lun(s_ip=node_ip1)
    host_group_id = env_manage.osan.get_host_groups(s_ip=node_ip1)
    env_manage.osan.map_lun(s_ip=node_ip1, lun_ids=lun_ids[0], hg_id=host_group_id[0])


def check_disk():
    disk_name = env_manage.osan.ls_scsi_dev(client_ip=client_ip1)
    if disk_name is None:
        log.info("find X1000 LUN failed")
        exit(1)
    else:
        disk_nums = len(disk_name)
        log.info("find X1000 LUN %s" % (disk_name))
        return disk_nums


def create_luns():
    for i in range(200):
        lun_name = "LUN" + str(i)
        env_manage.create_lun(node_ip1, lun_name)


def case():
    log.info("step:1.创建200个逻辑卷,创建lun map")
    create_luns()
    env_manage.create_lun_map()
    log.info("step:2.ISCSI 登录")
    env_manage.create_iscsi_login()
    nums = check_disk()
    lun_ids = env_manage.osan.get_lun()
    if nums == len(lun_ids):
        log.info("step:3.检查映射逻辑卷数量符合预期，ISCSI logout")
        env_manage.osan.iscsi_logout_all(client_ip1)
        return
    else:
        log.info("have disk lost")
        log.info("get lun ids: %s" % (len(lun_ids)))
        log.info("get scsi device :%s " % (nums))
        exit(1)


def main():
    env_manage.clean_test_env()
    setup()
    case()
    log.info("step:4.检查清理测试环境")
    env_manage.clean_lun_map()
    env_manage.clean_lun()
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == '__main__':
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)
