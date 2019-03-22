# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-9

'''
测试内容:SVIP和VIP在同一节点上能被扫描LUN
测试步骤：
1）创建存储池和访问分区，业务子网和对应的SVIP和VIP地址池，并创建2条LUN，LUN1和LUN2对应的VIP1和VIP2分别在节点1和节点2上，SVIP在节点1上
2）创建主机组，添加主机，并将主机组映射到LUN1
3）在主机端使用SVIP登录主机映射的LUN
检查项：
1）使用SVIP登录扫描LUN1成功，不能扫描到LUN2

'''

# testlink case: 1000-33509
import os
import xml
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
import access_env
import decorator_func
 

'''初始化'''
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
# log.init(log_file_path, True)
current_path = os.path.dirname(os.path.abspath(__file__))


def setup():
    '''获取业务节点IP和非业务节点IP'''
    global node_ip1
    global node_ip2
    global node_ip3
    global new_node1
    global client_ip1
    node_ip1 = env_manage.deploy_ips[0]
    node_ip2 = env_manage.deploy_ips[1]
    node_ip3 = env_manage.deploy_ips[2]
    client_ip1 = env_manage.client_ips[0]
    new_node1 = env_manage.client_ips[1]


def check_disk(c_ip):
    log.info("from %s host to check scsi device in os" % (c_ip))
    disk_name = env_manage.osan.ls_scsi_dev(client_ip=c_ip)
    if disk_name is None:
        log.info("form %s find X1000 LUN failed.\nerror infor: %s " % (disk_name))
        exit(1)
    else:
        log.info("from %s find X1000 LUN %s" % (c_ip, disk_name))


def create_iscsi_login(ips, cli_ips, svip):
    env_manage.osan.discover_scsi_list(client_ip=cli_ips, svip=svip)  # 进行一下discovery，真正的tag从xstor中拿
    target_list = env_manage.osan.get_map_target(ips)
    log.info("Get Info:\nSvip list:%s \nTarget list:%s" % (svip, target_list))
    for tag in target_list:
        log.info("主机发现存储target：%s,主机 %s 将进行SCSI登录" % (tag, cli_ips))
        env_manage.osan.iscsi_login(client_ip=cli_ips, iqn=tag)


def case():
    svip1 = env_manage.svip[0]
    svip2 = env_manage.from_xml_get_svip2()[0]
    vip1 = env_manage.vips[0]
    vip2 = env_manage.from_xml_get_vip2()[0]
    az_id1 = env_manage.create_access(ips=node_ip1, node_ids="1,2,3", access_name="accesszone1")
    az_id2 = env_manage.create_access(ips=node_ip1, node_ids="4,5", access_name="accesszone2")
    log.info("step:2 create two SVIP")
    sub_id1 = env_manage.create_subnet(s_ip=node_ip1, svip=svip1, a_z_id=az_id1, access_name="sub1")
    sub_id2 = env_manage.create_subnet(s_ip=node_ip1, svip=svip2, a_z_id=az_id2, access_name="sub2")
    log.info("step:3.create two VIP pool send to SVIP")
    env_manage.create_vip(s_ip=node_ip1, subnet_id=sub_id1, vip_name="vip1.com", vip_pool=vip1)
    env_manage.create_vip(s_ip=node_ip1, subnet_id=sub_id2, vip_name="vip2.com", vip_pool=vip2)
    env_manage.enable_san()
    log.info("step:4.create host and initiator")
    env_manage.create_host_group()
    env_manage.create_host()
    env_manage.create_add_initiator()
    log.info("step:5 create lun assigned to access zone ")
    env_manage.create_lun(ips=node_ip1, name="LUN1", access_id=az_id1)
    env_manage.create_lun(ips=node_ip1, name="LUN2", access_id=az_id2)
    log.info("step:6.create lun map")
    env_manage.create_lun_map(node_ip1)
    log.info("step:7 iscsi login form host")
    create_iscsi_login(node_ip1, client_ip1, svip1)
    create_iscsi_login(node_ip1, client_ip1, svip2)
    log.info("step:8. check iscsi device in host")
    check_disk(client_ip1)
    log.info("step:9. iscsi logout for host")
    env_manage.osan.iscsi_logout_all(node_ip1)


def main():
    access_env.check_env()
    setup()
    case()
    log.info("The case finished!!!")


if __name__ == '__main__':
    # log.init(log_file_path, True)
    env_manage.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=5)
    common.case_main(main)
