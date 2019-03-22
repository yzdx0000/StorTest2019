#!usr/bin/env python  
# -*- coding:utf-8 -*-  
""" 
:author: Liu he
:Description:
@file: env_init.py 
@time: 2019/03/16 
"""

import os
import utils_path
import log
import common
import common2
import breakdown
import get_config
import web_common
import breakdown
import xstor_web_com
import quota_common
import prepare_clean

# def setup():
#     '''初始化'''
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
current_path = os.path.dirname(os.path.abspath(__file__))
# import access_env
conf_file = get_config.CONFIG_FILE
deploy_ips = get_config.get_env_ip_info(conf_file)  # 获取集群IP列表
client_ips = get_config.get_allclient_ip()  # 获取客户端IP
new_ips = get_config.get_expand_ip_info()

# 类实例化
com_disk = common.Disk()
node = common.Node()
breakdown = breakdown.Os_Reliable()


def web_create_node_pool(driver, p_mode="replication", p_replica="3", p_stripe="3", node_parity="2"):
    node_pool = web_common.Node_Pool(driver)
    node_pool.create_node_pool(mode=p_mode, replica_num=p_replica, stripe_width=p_stripe, node_parity_num=node_parity)


def web_create_storage_pool(driver, s_name="pool1", type="BLOCK"):
    storaget_pool = web_common.Storage_Pool(driver)
    storaget_pool.create_storage_pool(name=s_name, service_type=type, disk_all=True)


def web_create_access_zone(driver, az_name="access_zone1", node_list=True):
    xstor_access_zone = xstor_web_com.AccessManage(driver)
    xstor_access_zone.create_access_zone(name=az_name, nodes_all=node_list, san=True)


def web_create_subnet(driver, s_ip=deploy_ips[0], az_name="access_zone1", sub_name="SVIP1", svip="20.1.1.111",
                      mask="255.255.255.0",
                      eth_name=['eth2'], ip_pool=["20.1.1.115-120"]):
    if az_name is None:
        az_name = breakdown.get_access_zone_node(s_ip)
    xstor_access_zone = xstor_web_com.AccessManage(driver)
    xstor_access_zone.create_subnet(access_zone_name=az_name, subnet_name=sub_name, svip=svip, mask=mask,
                                    eth_name_list=eth_name, domain_name="vip.com",
                                    ip_address_pool_list=ip_pool, protocol="ISCSI")


def web_create_host_group(driver, name):
    xstor_host_manage = xstor_web_com.HostManage(driver)
    xstor_host_manage.create_host_group(host_group_name=name)


def web_create_host(driver, host_name, list_num="2", type_os="LINUX"):
    xstor_host_manage = xstor_web_com.HostManage(driver)
    xstor_host_manage.create_host(host_name=host_name, list_num=list_num, type_os=type_os)  # 主机组列表从第二个开始


def web_update_host_group(driver, old_name, new_name):
    xstor_host_manage = xstor_web_com.HostManage(driver)
    xstor_host_manage.update_host_group(be_upname=old_name, new_name=new_name)


def web_clean_access_zone(driver, az_name="access_zone1"):
    xstor_access_zone = xstor_web_com.AccessManage(driver)
    xstor_access_zone.delete_access_zone(name=az_name)


def web_clean_host_group(driver, hg_name):
    xstor_host_manage = xstor_web_com.HostManage(driver)
    xstor_host_manage.delete_host_group(hg_name=hg_name)


def web_clean_host(driver, host_name):
    xstor_host_manage = xstor_web_com.HostManage(driver)
    xstor_host_manage.delete_host(host_name=host_name)


def main():
    driver = web_common.init_web_driver()  # 登录web
    # web_base = web_common.Web_Base(driver)  # 检查界面基础类
    # web_create_node_pool(driver)
    # web_create_storage_pool(driver)
    # web_create_access_zone(driver)
    # web_clean_access_zone(driver)
    # web_create_host_group(driver=driver, name="host_group1")
    # web_create_subnet(driver)
    # web_update_host_group(driver=driver, old_name="host_group1", new_name="hg1")
    # web_clean_host_group(driver=driver, hg_name="hg1")
    # web_create_host(driver=driver, host_name="host1")
    web_clean_host(driver, host_name="host1")
    web_common.quit_web_driver(driver)


if __name__ == '__main__':
    main()
