# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-11-20

'''
有LUN映射时更新VIP
测试步骤：
1、创建节点池
2、创建存储池
3、创建访问区
4、创建SVIP，填写zone id，svip name，IP地址，掩码，网关，网卡名称，提交后可成功创建
5、创建VIP，填写 SVIP id，域名，IP地址，协议类型，配置方法，负载均衡类型并启动iSCSI
6、创建LUN和LUN映射，使LUN只关联到部分VIP上
7、修改VIP地址池中无LUN映射的VIP
8、创建LUN，使LUN能分配到修改的VIP上；
9、主机端使用SVIP登录修改的VIP并扫描对应的LUN
检查项：
1、节点池创建成功
2、存储池创建成功
3、访问区创建成功
4、成功创建SVIP
5、创建VIP成功
6、LUN创建成功，只关联到部分VIP
7、修改VIP成功
8、新增LUN分配到修改VIP上
9、主机端扫描登录新VIP成功

'''
# testlink case: 1000-34182

import os
import time
import random
import xml
import json
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
from get_config import config_parser as cp

'''初始化'''
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log


def setup():
    '''获取业务节点IP和非业务节点IP'''
    global node_ip1
    global node_ip2
    global client_ip1
    node_ip1 = env_manage.deploy_ips[0]  # 业务节点IP
    node_ip2 = env_manage.deploy_ips[1]  # 非业务节点IP
    client_ip1 = env_manage.client_ips[0]


def get_vip():
    lun_xml = os.getcwd() + '/test_config.xml'
    svip2 = xml.dom.minidom.parse(lun_xml)
    svip2_info = svip2.getElementsByTagName('vips')[0]
    svips_infos = svip2_info.getElementsByTagName('vip')
    vips_list = []
    for svip in svips_infos:
        ip = svip.getElementsByTagName('ip')[0].firstChild.nodeValue
        vips_list.append(ip)
    return vips_list


def create_luns():
    for i in range(3):
        lun_name = "LUN" + str(i)
        env_manage.create_lun(node_ip1, lun_name)


def create_luns2():
    for i in range(3, 10):
        lun_name = "LUN" + str(i)
        env_manage.create_lun(node_ip1, lun_name)


def update_vip(n_vip):
    log.info("修改（删除）没有lun的vip")
    vip_pool_id = env_manage.osan.get_vip_pool_ids(s_ip=node_ip1)
    map_vip = env_manage.com_lh.get_map_vip(node_ip1)
    new_vip = map_vip.extend(n_vip)
    env_manage.osan.update_vip_address_pool(vip_id=vip_pool_id[0], s_ip=node_ip1, vip_addresses=new_vip)


def create_iscsi_login(ips, cli_ips):
    # node_id = com_lh.get_node_id_by_ip(ips)
    svip = env_manage.com2_osan.get_svip(ips)
    env_manage.osan.discover_scsi_list(client_ip=cli_ips, svip=svip[0])  # 进行一下discovery，真正的tag从xstor中拿
    target_list = env_manage.osan.get_map_target(ips)
    map_vip = env_manage.com_lh.get_map_vip(node_ip1)
    new_target_list = []
    for iqn in target_list:
        iqn = iqn.encode("utf-8")
        lun_map_vip = iqn.split("target.")[-1]
        if lun_map_vip in map_vip:
            continue
        else:
            new_target_list.append(iqn)
        log.info("Get Info:\nSvip list:%s \nTarget list:%s" % (svip, new_target_list))
        for tag in new_target_list:
            log.info("主机发现存储target：%s,主机 %s 将进行SCSI登录" % (tag, cli_ips))
            env_manage.osan.iscsi_login(client_ip=cli_ips, iqn=tag)


def case():
    vip2 = get_vip()[1]
    log.info("创建lun")
    create_luns()
    log.info("创建lun map")
    env_manage.create_lun_map()
    log.info("iscsi 登录")
    env_manage.create_iscsi_login()
    log.info("扫描iscsi设备")
    env_manage.com2_osan.ls_scsi_dev(client_ip1)
    log.info("退出登录")
    env_manage.com2_osan.iscsi_logout_all(client_ip1)
    log.info("删除lun map")
    env_manage.clean_lun_map(node_ip1)
    log.info("修改vip")
    update_vip(vip2)
    log.info("创建lun")
    create_luns2()
    log.info("创建lun map")
    env_manage.create_lun_map()
    log.info("iscsi登录")
    env_manage.create_iscsi_login()
    log.info("再次扫描iscsi设备")
    scsi_ids = env_manage.com2_osan.ls_scsi_dev(client_ip1)
    if len(scsi_ids) == 10:
        log.info("all lun login to host")
    else:
        log.error("have lun lose")
        os._exit(1)


def main():
    env_manage.clean_test_env()
    setup()
    case()
    log.info("step:6.检查清理测试环境")
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == '__main__':
    env_manage.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    common.case_main(main)