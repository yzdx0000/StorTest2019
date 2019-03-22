# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-9

'''
测试内容:SVIP和VIP在不同一节点上能被扫描LUN
测试步骤：
1）创建存储池和访问分区，业务子网和对应的SVIP和VIP地址池，并创建2条LUN，LUN1和LUN2对应的VIP1和VIP2分别在节点1和节点2上，SVIP在节点1上
2）创建主机组，添加主机，并将主机组映射到LUN2
3）在主机端使用SVIP登录主机映射的LUN
检查项：
1）使用SVIP登录扫描LUN2成功，不能扫描到LUN1

'''

# testlink case: 1000-33878
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


def network_test():
    vip_list = env_manage.com2_osan.get_vip_address_pools(node_ip1)[0]
    vips = env_manage.com2_osan.analysis_vip(vip_list)
    vip_node = env_manage.com2_osan.get_node_by_vip(vips[0])
    subnet_eth = env_manage.com_lh.get_vip_eth_name(vip_node)
    env_manage.com_lh.net_flash_test(vip_node, subnet_eth)


def case():
    log.info("step:1.创建逻辑卷")
    env_manage.create_lun(node_ip1, "LUN1")
    env_manage.create_lun(node_ip1, "LUN2")
    log.info("step:2.创建lun map")
    env_manage.create_lun_map()
    log.info("step:3.网卡闪断")
    network_test()
    env_manage.create_iscsi_login(client_ip1)
    nums = check_disk()
    lun_ids = env_manage.osan.get_lun()
    if nums == len(lun_ids):
        log.info("step:4.lun数量符合预期")
        return
    else:
        log.info("have disk lost")
        log.info("get lun ids: %s" % (len(lun_ids)) )
        log.info("get scsi device :%s " % (nums))
        exit(1)


def main():
    env_manage.clean_test_env()
    setup()
    case()
    log.info("step:5.检查清理测试环境")
    env_manage.osan.iscsi_logout_all(client_ip1)
    env_manage.clean_lun_map()
    env_manage.clean_lun()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)
