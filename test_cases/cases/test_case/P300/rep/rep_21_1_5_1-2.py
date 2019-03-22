# -*-coding:utf-8 -*
import os
import time

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
#    复制域参数测试
# @steps:
#    1、复制域添加不存在的节点id
#    2、创建复制域，参数非,分割、非数字
#    3、正常创建3节点复制域
#    4、删除不存在的节点id
#    5、删除复制域，参数非,分割、非数字
#    6、清除环境
#
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
REP_ABS_PATH = os.path.join(rep_common.REP_PATH, FILE_NAME)             # /mnt/volume1/snap/snap_13_0_0_0
NEED_CLUSTER_LIST = [rep_common.MASTER, rep_common.SLAVE]

def generate_noexist_idstr(real_id_lst):
    large_lst = range(100, 200)
    for id in real_id_lst:
        if id in large_lst:
            large_lst.remove(id)
    ids = random.choice(large_lst)
    number_lst = range(3, 90)
    failid_number = random.choice(number_lst)
    no_exist_ids = rep_common.convert_lst_to_str(large_lst[0:failid_number])
    return no_exist_ids

def case():
    log.info('case begin')
    log.info('1>复制域添加不存在的节点id')
    rc, real_id_lst = rep_common.get_node_id_lst(run_cluster=rep_common.MASTER)
    common.judge_rc(rc, 0, 'get_node_id_lst failed')
    no_exist_ids = generate_noexist_idstr(real_id_lst)
    rc, stdout = rep_common.enable_rep_server(no_exist_ids)
    common.judge_rc_unequal(rc, 0, 'enable_rep_server Successful!')

    log.info('2>创建复制域，参数非,分隔，非数字')
    wrong_symbol = "~@#%^*-=+?"
    for i in wrong_symbol:
        wrong_symbol_ids = rep_common.convert_lst_to_str_by_other_symbol(real_id_lst, i)
        rc, stdout = rep_common.enable_rep_server(wrong_symbol_ids)
        common.judge_rc_unequal(rc, 0, 'enable_rep_server Successful!')
    """
    letter_id_lst = []
    letter_ids = rep_common.convert_lst_to_str_by_other_symbol(real_id_lst, i)
    rc, stdout = rep_common.enable_rep_server(wrong_symbol_ids)
    common.judge_rc_unequal(rc, 0, 'enable_rep_server Successful!')
    """

    log.info('3>正常创建3节点复制域')
    ids = rep_common.convert_lst_to_str(real_id_lst)
    rc, stdout = rep_common.enable_rep_server(node_ids=ids)
    common.judge_rc(rc, 0, 'enable_rep_server failed!')

    log.info('4>删除不存在的节点id')
    ids = rep_common.convert_lst_to_str(real_id_lst)
    no_exist_ids = generate_noexist_idstr(real_id_lst)
    rc, stdout = rep_common.disable_rep_server(no_exist_ids)
    common.judge_rc_unequal(rc, 0, 'disable_rep_server Successful!')

    log.info('5>删除参数非,分隔，非数字')
    wrong_symbol = "~@#%^*-=+?"
    for i in wrong_symbol:
        wrong_symbol_ids = rep_common.convert_lst_to_str_by_other_symbol(real_id_lst, i)
        rc, stdout = rep_common.disable_rep_server(wrong_symbol_ids)
        common.judge_rc_unequal(rc, 0, 'enable_rep_server Successful!')

    return


def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
