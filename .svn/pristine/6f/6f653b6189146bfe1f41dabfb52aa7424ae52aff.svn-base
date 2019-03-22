# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2019-3-4

'''
测试内容:
测试步骤：
迁移时源节点数据网故障

检查项：


'''

import os
import time
import random
import xml
import commands
import threading
import datetime
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
current_path = os.path.dirname(os.path.abspath(__file__))

os_infos = []
os_types = []


def setup():
    '''获取业务节点IP和非业务节点IP'''
    global node_ip1
    global node_ip2
    global client_ip1
    node_ip1 = env_manage.deploy_ips[0]  # 业务节点IP
    node_ip2 = env_manage.deploy_ips[1]  # 非业务节点IP
    client_ip1 = env_manage.client_ips[0]


def get_new_node_tag_id(s_ip):
    for ip in s_ip:   # 获取一个新的带有target 节点ip
        vip_pool_id = env_manage.osan.get_vip_pool_ids(ip)
        vip_list = env_manage.osan.get_vips_by_node(s_ip=ip, vip_pool_id=vip_pool_id[0])
        if vip_list:
            log.info("get vip list:%s" % (vip_list))
            tg_node_ip = ip
            target_dict = env_manage.com_lh.get_targets_id_and_vip(s_ip=ip)   # 获取到target vip 和id组成的字典
            tag_id = target_dict[vip_list[0]]  # 使用vip 获取 一个target id
            log.info("step:6.get target :%s, form node :%s" % (tag_id, tg_node_ip))
            return tg_node_ip, tag_id
    os._exit(1)  # 如果剩余节点都没有vip，直接退出


def date_net_fault(s_ip, data_net):
    log.info("step:8.%s节点%s 网卡故障" % (s_ip, data_net))
    env_manage.down_network(s_ip, data_net)
    log.info("节点网卡关闭完成")
    return


def lun_map_case():
    log.info("step:2.创建逻辑卷")
    lun_id = env_manage.create_lun(ips=node_ip1)
    log.info("step:3.获取 lun 所在节点及los号")
    lun_los_id = env_manage.get_lun_default_los_id(lun_id)  # 获取lun 默认的los id
    lun_los_ip = env_manage.com_bd_disk.get_nodeip_by_losid(lun_los_id)  # lun los id 所在IP
    log.info("step:4.获取 lun 所在节点IP %s" % (lun_los_ip))
    env_manage.deploy_ips.remove(lun_los_ip)  # 移除lun 所在节点IP
    log.info("step:5.获取一个其他节点的target id 用来lun map")
    node_ip, target_id = get_new_node_tag_id(env_manage.deploy_ips)  # from IP
    log.info("step:7.创建lun map 过程中关闭lun los 源节点网卡")
    data_net = env_manage.com_lh.get_eth_name(s_ip=lun_los_ip)[1]
    threads = []
    threads.append(threading.Thread(target=env_manage.create_lun_map, args=(node_ip, lun_id, target_id)))
    threads.append(threading.Thread(target=date_net_fault, args=(lun_los_ip, data_net)))  # 源节点网卡
    for i in threads:
        i.start()
    for i in threads:
        i.join()
    log.info("step:9.%s 节点网卡 %s 恢复" % (lun_los_ip, data_net))
    env_manage.up_network(lun_los_ip, data_net)


def run_vdb():
    pass


def case():
    log.info("******************* case start **********************")
    log.info("step:1.运行vdbench过程中进行lun los迁移，且在迁移过程中将源节点数据网故障")
    threads = []
    threads.append(threading.Thread(target=run_vdb))
    threads.append(threading.Thread(target=lun_map_case))
    for i in threads:
        i.start()
    for i in threads:
        i.join()
    log.info("******************* case end ************************")


def main():
    log.info("init step: checking the test environment")
    env_manage.clean_test_env()
    log.info("init step: initialize node ip")
    setup()
    case()
    log.info("step:10.The test environment will be cleaned up")
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == '__main__':
    env_manage.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    # log.init(log_file_path, True)
    common.case_main(main)
