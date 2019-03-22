# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-9

'''
测试内容:通过SVIP能扫描到所有节点LUN
测试步骤：
1）创建存储池和访问分区，业务子网和对应的SVIP和VIP地址池（至少每个节点一个VIP），并创建6条LUN，LUN1-LUN6
2）创建主机组，添加主机，并将主机组映射到LUN1-LUN6上
3）在主机端使用SVIP登录主机映射的LUN
检查项：
1）使用SVIP登录扫描6条LUN成功
'''

# testlink case: 1000-33505
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


def check_disk():
    disk_name = env_manage.osan.ls_scsi_dev(client_ip=client_ip1)
    if disk_name is None:
        log.info("find X1000 LUN failed")
        exit(1)
    else:
        disk_mums = len(disk_name)
        log.info("find X1000 LUN %s" % (disk_name))
        return disk_mums


def case():
    log.info("step:1.创建逻辑卷,创建lun map")
    env_manage.create_luns()
    env_manage.create_lun_map()
    log.info("step:2.ISCSI 登录")
    env_manage.create_iscsi_login()
    nums = check_disk()
    lun_ids = env_manage.osan.get_lun()
    if nums == len(lun_ids):
        log.info("step:3.检查映射逻辑卷符合预期,iscsi logout")
        env_manage.osan.iscsi_logout_all(client_ip1)
    else:
        log.info("have disk lost")
        log.info("get lun ids: %s" % (len(lun_ids)) )
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
