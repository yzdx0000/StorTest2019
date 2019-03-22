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
import make_fault

####################################################################################
#
# Author: chenjy1
# Date 20181218
# @summary：
#    通道相关
# @steps:
#    1、相同的2个集群不支持创建多个通道（不同IP/反向）
#    2、对非管理网/数据网的ip创建通道
#    3、测试创建对于本集群的通道
#    4、使用某ip创建通道后，ifdown对端此ip或ifdown主端能ping通此ip的网卡
#    5、对多个集群创建多个通道
#
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
REP_ABS_PATH = os.path.join(rep_common.REP_PATH, FILE_NAME)                 # /mnt/volume1/snap/filename
FILE_MASTER_PATH = os.path.join(rep_common.MASTER_PAIR_PATH, FILE_NAME)     # /mnt/parastor/rep_test_dir/filename
FILE_SLAVE_PATH = os.path.join(rep_common.SLAVE_PAIR_PATH, FILE_NAME)       # /mnt/(slave)parastor/(slave)rep_test/filename
NEED_CLUSTER_LIST = [rep_common.MASTER, rep_common.SLAVE]
THREADS_NUMBER = 20


def get_all_ip(ctl_ip):
    ip_lst = []
    cmd = 'ip a |grep inet |grep -v inet6 |grep -v 127.0.0.1'
    rc, stdout = common.run_command(ctl_ip,cmd)
    common.judge_rc(rc, 0, 'cmd %s failed  ip:%s' % (cmd, ctl_ip))
    str_line = stdout.split('\n')[:-1]
    for line in str_line:
        ip_lst.append(line.strip().split(' ')[1].split('/')[0])
    return ip_lst


def get_other_ip(ip, run_cluster=rep_common.SLAVE):
    ob_node = common.Node()
    nodeid = ob_node.get_node_id_by_ip(ip)
    rc, stdout = common.get_nodes(ids=nodeid, run_cluster=run_cluster, print_flag=False)
    common.judge_rc(rc, 0, 'get_nodes failed')
    node_info = common.json_loads(stdout)
    for node in node_info['result']['nodes']:
        if ip == node['ctl_ips'][0]['ip_address']:
            iplst = get_all_ip(ip)
            for mechineip in iplst:
                if mechineip not in node['data_ips']:
                    return mechineip
    return ''


def get_dataip_by_ctlip(ctlip, run_cluster=rep_common.MASTER):
    dataip_lst = []
    ob_node = common.Node()
    nodeid = ob_node.get_node_id_by_ip(ctlip)
    rc, stdout = common.get_nodes(ids=nodeid, run_cluster=run_cluster, print_flag=False)
    common.judge_rc(rc, 0, 'get_nodes failed')
    node_info = common.json_loads(stdout)
    for node in node_info['result']['nodes']:
        for dataip in node['data_ips']:
            dataip_lst.append(dataip['ip_address'])
    return dataip_lst




def case():
    log.info('case begin')
    ob_node = common.Node()
    skip_flag = True
    node_with_otherip = ''
    other_ip = ''
    for ip in rep_common.SLAVE_NODE_LST:
        other_ip = get_other_ip(ip)
        if other_ip != '':
            skip_flag = False
            node_with_otherip = ip
            break
    if skip_flag:
        log.warn('没有节点拥有非管理网、非数据网的ip')
        sys.exit(-1)

    master_id_lst = []
    slave_id_lst = []

    rc, master_all_id_lst = rep_common.get_node_id_lst()
    common.judge_rc(rc, 0, 'get_node_id_lst failed')
    rc, slave_all_id_lst = rep_common.get_node_id_lst(run_cluster=rep_common.SLAVE)
    common.judge_rc(rc, 0, 'get_node_id_lst failed')

    if rep_common.REP_DOMAIN == rep_common.THREE:
        master_id_lst = master_all_id_lst[0:3]
        slave_id_lst = slave_all_id_lst[0:3]
    else:
        master_id_lst = master_all_id_lst
        slave_id_lst = slave_all_id_lst

    log.info('1>[主从]创建3节点复制域')
    master_nodeid_str = rep_common.convert_lst_to_str(master_id_lst)
    rc, pscli_info = rep_common.enable_rep_server(node_ids=master_nodeid_str)
    common.judge_rc(rc, 0, 'enable_rep_server failed')
    slave_nodeid_str = rep_common.convert_lst_to_str(slave_id_lst)
    rc, pscli_info = rep_common.enable_rep_server(node_ids=slave_nodeid_str, run_cluster=rep_common.SLAVE)
    common.judge_rc(rc, 0, 'enable_rep_server failed')

    if node_with_otherip not in slave_id_lst:
        slave_id_lst[-1] = node_with_otherip

    log.info('2>[主]测试创建对于本集群的通道')
    rc, stdout = rep_common.create_rep_channel(name=FILE_NAME, ip=rep_common.MASTER_NODE_LST[0])
    common.judge_rc_unequal(rc, 0, 'create_rep_channel failed')
    dataip =get_dataip_by_ctlip(ctlip=rep_common.MASTER_NODE_LST[0])
    rc, stdout = rep_common.create_rep_channel(name=FILE_NAME, ip=dataip)
    common.judge_rc_unequal(rc, 0, 'create_rep_channel failed')

    log.info('3>[主]正常创建通道')
    rc, create_channel_ip = rep_common.ip_for_create_channel(slave_id_lst, run_cluster=rep_common.SLAVE)
    common.judge_rc(rc, 0, 'ip_for_create_channel failed')
    rc, stdout = common.create_rep_channel(ip=create_channel_ip)
    common.judge_rc(rc, 0, 'create_rep_channel failed')

    rc, channelid = rep_common.get_channel_id_by_ip(ip=create_channel_ip)
    common.judge_rc(rc, 0, 'get_rep_channels failed')

    log.info('4>[主]使用某ip创建通道后，ifdown对端此ip或ifdown主端能ping通此ip的网卡')
    # todo 故障不支持

    log.info('4>相同的2个集群不支持创建多个通道（不同IP/反向）')
    '''反向'''
    rc, create_channel_ip = rep_common.ip_for_create_channel(master_id_lst, run_cluster=rep_common.MASTER)
    common.judge_rc(rc, 0, 'ip_for_create_channel failed')
    rc, stdout = common.create_rep_channel(ip=create_channel_ip,  run_cluster=rep_common.MASTER)
    common.judge_rc_unequal(rc, 0, 'create_rep_channel failed')
    '''不同ip'''
    tmp_ip = create_channel_ip
    create_channel_ip = ''
    while True:
        rc, create_channel_ip = rep_common.ip_for_create_channel(master_id_lst, run_cluster=rep_common.MASTER)
        common.judge_rc(rc, 0, 'ip_for_create_channel failed')
        if create_channel_ip != tmp_ip:
            break
    rc, stdout = common.create_rep_channel(ip=create_channel_ip, run_cluster=rep_common.MASTER)
    common.judge_rc_unequal(rc, 0, 'create_rep_channel failed')

    log.info('5> 支持对非管理网/数据网的ip创建通道')
    rc, stdout = common.create_rep_channel(ip=other_ip, run_cluster=rep_common.MASTER)
    common.judge_rc(rc, 0, 'create_rep_channel failed')

    return


def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
