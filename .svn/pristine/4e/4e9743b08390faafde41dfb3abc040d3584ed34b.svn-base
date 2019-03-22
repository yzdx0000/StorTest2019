# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import sys

import utils_path
import common
import snap_common
import log
import prepare_clean
import rep_common
import random
import get_config

####################################################################################
#
# Author: chenjy1
# Date 20181218
# @summary：
#    集群删除/添加域内某节点，查看复制域此节点消失/出现???
# @steps:
#    1、[主]创建复制域(节点数>=3随机)
#    2、[主]集群删除复制域内某节点
#    3、[主]查看复制域此节点消失
#    4、[主]集群添加某节点
#    5、[主]查看复制域列表不变
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
REP_ABS_PATH = os.path.join(rep_common.REP_PATH, FILE_NAME)             # /mnt/volume1/snap/snap_13_0_0_0
NEED_CLUSTER_LIST = [rep_common.MASTER]


def del_node(node_id):
    node = common.Node()
    rc, stdout = common.remove_node(node_id, remove_mode="AUTO_REBOOT")
    common.judge_rc(rc, 0, "remove node failed")
    return

def add_node(node_ip, node_pool_id, run_cluster=rep_common.MASTER):
    # 添加节点，以node_ip.xml命名的配置文件
    log.info("add node please waite...")
    config_file_path= os.path.join(get_config.config_path, "%s.xml" % node_ip)
    rc, stdout = common.add_nodes(config_file_path, run_cluster=run_cluster)
    common.judge_rc(rc, 0, "add node failed")

    # 扩容到到节点池
    rc, stdout = common.get_node_pools(id=node_pool_id, run_cluster=run_cluster)
    common.judge_rc(rc, 0, "get_node_pools failed")
    node_pool = common.json_loads(stdout)["result"]["node_pools"][0]

    rc, stdout = common.get_nodes(run_cluster=run_cluster)
    pscli_info = common.json_loads(stdout)
    nodes_info = pscli_info["result"]["nodes"]
    new_node_id = 0
    for node in nodes_info:
        for ctl_ips in node["ctl_ips"]:
            if ctl_ips["ip_address"] == node_ip:
                new_node_id = node["node_id"]

    node_ids_list = node_pool["node_ids"]
    node_ids_list.append(new_node_id)
    node_ids = ','.join(map(str, node_ids_list))  # 列表中不全是字符串会报错
    rc, stdout = common.update_node_pool(node_pool_id, node_pool["name"], node_ids, run_cluster=run_cluster)
    common.judge_rc(rc, 0, "update node pool failed")

    # 扩容到存储池
    rc, stdout = common.get_volumes(run_cluster=run_cluster)
    common.judge_rc(rc, 0, 'get_volumes failed')
    pscli_info = common.json_loads(stdout)
    volumename = ''
    if run_cluster == rep_common.MASTER:
        volumename= rep_common.MASTER_VOLUME_NAME
    elif run_cluster == rep_common.SLAVE:
        volumename = rep_common.SLAVE_VOLUME_NAME
    storage_pool_id = 0
    for volume in pscli_info['result']['volumes']:
        if volume['name'] == volumename:
             storage_pool_id = volume['storage_pool_id']

    rc, stdout = common.expand_storage_pool(storage_pool_id, node_pool_id)
    common.judge_rc(rc, 0, "expand storage pool failed")

    # 启动系统
    rc, stdout = common.startup()
    common.judge_rc(rc, 0, "start up sys failed")
    return


def prepare_node_xml(node_ip):
    node_xml = os.path.join(get_config.config_path, "%s.xml" % node_ip)
    cmd = 'ls %s' % node_xml
    rc, stdout = common.run_command_shot_time(cmd)
    if rc !=0:
        log.warn("cannnot find file %s ,case skipped" % node_xml)
        sys.exit(-1)
    node_xml = os.path.join(get_config.config_path, "%s.xml" % node_ip)
    for ip in rep_common.MASTER_NODE_LST:
        cmd = 'scp %s root@%s:%s' % (node_xml, ip, node_xml)
        rc, stdout = common.run_command_shot_time(cmd)
        common.judge_rc(rc, 0, cmd + 'failed')
    return


def wait_node_start(choose_node_ip):
    while True:
        flag = common.check_ping(choose_node_ip)
        if flag:
            log.info('node is working, wait 20s')
            time.sleep(20)
            break
        else:
            log.info('wait 60s for node restart')
            time.sleep(60)
    return

def case():
    log.info('1> 全节点加入复制域，至少4个节点')
    rc, id_lst = rep_common.get_node_id_lst()
    common.judge_rc(rc, 0, 'get_node_id_lst failed')
    id_lst = rep_common.convert_lst_to_str(id_lst)
    rc, pscli_info = rep_common.enable_rep_server(node_ids=id_lst)
    common.judge_rc(rc, 0, 'enable_rep_server failed')

    log.info('2> [主]删除某节点')
    choose_node_id = id_lst[-1]
    rc, stdout = common.get_nodes(ids=choose_node_id)
    common.judge_rc(rc, 0, 'get_nodes failed')
    pscli_info = common.json_loads(stdout)
    choose_node_ip = pscli_info['result']['nodes'][0]['ctl_ips'][0]['ip_address']
    choose_node_nodepoolid = pscli_info['result']['nodes'][0]['node_pool_id']
    prepare_node_xml(choose_node_ip)
    del_node(choose_node_id)

    log.info('wait 20s')
    time.sleep(20)

    rc, pscli_info = rep_common.get_rep_area()
    common.judge_rc(rc, 0, 'get_rep_area failed')
    oldid_lst = pscli_info['result']['node_ids']
    if int(choose_node_id) in pscli_info['result']['node_ids']:
        common.except_exit('nodeid:%s has been deleted, but get_rep_area can find this node' % choose_node_id)

    log.info('4> [主]集群添加某节点')
    add_node(choose_node_ip, choose_node_nodepoolid)

    log.info('5> [主]查看复制域列表不变')
    rc, pscli_info = rep_common.get_rep_area()
    common.judge_rc(rc, 0, 'get_rep_area failed')
    if int(choose_node_id) in pscli_info['result']['node_ids']:
        common.except_exit('nodeid:%s has been deleted, but get_rep_area can find this node' % choose_node_id)
    if oldid_lst != pscli_info['result']['node_ids']:
        common.except_exit('The replication domain changes before and after adding nodes ')

    return


def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, False, clusters=NEED_CLUSTER_LIST, node_num=4)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, False, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
