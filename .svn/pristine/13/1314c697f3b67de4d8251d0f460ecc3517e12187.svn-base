# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-9

'''
测试内容:异常后SVIP登录
测试步骤：
1）建LUN，创建主机组和对应的LUN映射
2）将其中一个子网SVIP1节点A关机
3）主机使用SVIP登录并扫描LUN
4）节点A上电恢复正常后，检查SVIP1情况

检查项：
2)主机能正确登录，并能扫描到所有LUN
3）节点A无SVIP1的IP

'''

# testlink case: 1000-33633
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
        disk_nums = len(disk_name)
        log.info("find X1000 scsi device ： %s" % (disk_nums))
        return disk_nums


def case():
    log.info("******************* case start **********************")
    log.info("step:1.创建逻辑卷")
    env_manage.create_luns(s_ip=node_ip1, nums=10)
    log.info("step:2.创建lun map")
    env_manage.create_lun_map()
    log.info("step:3.节点关机")
    type = env_manage.get_os_type(node_ip1)
    info = env_manage.down_node(node_ip1, type, "init 0")
    log.info("step:4.ISCSI 登录")
    env_manage.create_iscsi_login(client_ip1)
    log.info("step:5.主机检查硬盘数量")
    nums = check_disk()
    lun_ids = env_manage.osan.get_lun()
    if nums == len(lun_ids):
        log.info("step:6.lun数量正确，执行scsi logout")
        env_manage.osan.iscsi_logout_all(client_ip1)
        log.info("step:7.%s 节点开机 节点类型%s,节点ID or IPMI IP: %s" % (node_ip1, type, info))
        env_manage.up_node(info, type)
        log.info("step:8.检查节点运行状态，检查服务恢复情况。")
        env_manage.com_lh.get_os_status(node_ip1)
    else:
        log.info("have disk lost")
        log.info("get lun ids: %s" % (len(lun_ids)) )
        log.info("get scsi device :%s " % (nums))
        exit(1)
    log.info("******************* case end ************************")


def main():
    log.info("step: checking the test environment")
    env_manage.clean_test_env()
    log.info("step: initialize node ip")
    setup()
    case()
    log.info("step:9.清理测试环境")
    env_manage.clean_lun_map()
    env_manage.clean_lun()
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == '__main__':
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)
