# -*-coding:utf-8 -*
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

####################################################################################
#
# Author: chenjy1
# Date 20181218
# @summary：
#    复制域变化节点rep服务跟随变化
# @steps:
#    1、复制域修改节点，rep服务和命令查看rep的nodeid进行相应的改变
#
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
REP_ABS_PATH = os.path.join(rep_common.REP_PATH, FILE_NAME)  # /mnt/volume1/snap/snap_13_0_0_0
NEED_CLUSTER_LIST = [rep_common.MASTER]


def get_orep_nodeid_lst(run_cluster=rep_common.MASTER):
    log.info('wait 60s')
    time.sleep(60)
    rc, stdout = common.get_services(run_cluster=run_cluster, print_flag=True)
    common.judge_rc(rc, 0, 'get_services failed')
    pscli_info = common.json_loads(stdout)
    id_lst = []
    flag = False
    for node in pscli_info['result']['nodes']:
        for service in node['services']:
            if service['service_type'] == 'oRep':
                if service['inTimeStatus'] == 'SERV_STATE_OK' \
                        or service['inTimeStatus'] == 'SERV_STATE_READY':
                    flag = True
        if flag is True:
            id_lst.append(node['node_id'])
        flag = False
    return id_lst


def check_rep_area(idlst, run_cluster=rep_common.MASTER):

    rc, pscli_info = rep_common.get_rep_area()
    common.judge_rc(rc, 0, 'get_rep_area failed')
    get_id_lst = pscli_info['result']['node_ids']

    tmplst = [x for x in get_id_lst if x in idlst]
    diff_lst = [y for y in (get_id_lst + idlst) if y not in tmplst]
    log.info(diff_lst)
    if diff_lst != []:
        common.except_exit('expect nodeid  not equal to get_rep_area')

    #rc, stdout = common.get_services(print_flag=False, run_cluster=rep_common.SLAVE)
    #common.judge_rc(rc, 0, 'get_services failed')
    #pscli_info = common.json_loads(stdout)

    real_lst = get_orep_nodeid_lst(run_cluster=run_cluster)
    log.info(real_lst)
    common.judge_rc(real_lst, idlst, 'services not equal')

    return


def case():
    log.info('case begin')
    rc, id_lst = rep_common.get_node_id_lst()
    common.judge_rc(rc, 0, 'get_node_id_lst failed')
    choose_node_id = random.choice(id_lst)
    nodeid_str = rep_common.convert_lst_to_str(id_lst)

    rc, slave_id_lst = rep_common.get_node_id_lst(run_cluster=rep_common.SLAVE)
    common.judge_rc(rc, 0, 'get_node_id_lst failed')
    slave_id_str = rep_common.convert_lst_to_str(slave_id_lst)

    part_id_lst = id_lst[:-1]
    left_id = id_lst[-1]
    choose_node_id_in_part_lst = random.choice(part_id_lst)
    part_id_str = rep_common.convert_lst_to_str(part_id_lst)

    log.info('复制域修改节点，rep服务和命令查看rep的nodeid进行相应的改变')
    '''先加入部分节点'''
    rc, pscli_info = rep_common.enable_rep_server(node_ids=part_id_str)
    common.judge_rc(rc, 0, 'enable_rep_server failed')
    check_rep_area(part_id_lst)
    '''在删除一个节点'''
    rc, pscli_info = rep_common.disable_rep_server(node_ids=choose_node_id_in_part_lst)
    common.judge_rc(rc, 0, 'disable_rep_server failed')
    part_id_lst.remove(choose_node_id_in_part_lst)
    check_rep_area(part_id_lst)
    part_id_lst.append(choose_node_id_in_part_lst)
    '''加入另一个节点'''
    rc, pscli_info = rep_common.enable_rep_server(node_ids=left_id)
    common.judge_rc(rc, 0, 'enable_rep_server failed')
    part_id_lst.remove(choose_node_id_in_part_lst)
    part_id_lst.append(left_id)
    check_rep_area(part_id_lst)

    """删除所选参数即有域内也有域外"""
    rc, pscli_info = rep_common.disable_rep_server(node_ids=nodeid_str)
    common.judge_rc(rc, 0, 'disable_rep_server failed')
    check_rep_area([])

    log.info('双端所有节点（需>=3）加入复制域')
    rc, pscli_info = rep_common.enable_rep_server(node_ids=nodeid_str)
    common.judge_rc(rc, 0, 'enable_rep_server failed')
    check_rep_area(id_lst)
    log.info('复制域逐个删除节点')  # todo 开发实现今后会有变化
    for id in id_lst:
        rc, pscli_info = rep_common.disable_rep_server(node_ids=id)
        common.judge_rc(rc, 0, 'disable_rep_server failed')
        id_lst.remove(id)
        check_rep_area(id_lst)

    return


def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

