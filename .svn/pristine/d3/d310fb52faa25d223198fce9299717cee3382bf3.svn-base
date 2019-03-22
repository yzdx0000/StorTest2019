# -*-coding:utf-8 -*
from multiprocessing import Process
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
#   策略参数检测
# @steps:
#   1、[主]创建复制域和通道
#   2、[主]创建pair
#   3、[主]创建策略，每次有一个参数随机非法
#   4、[主]成功创建一条策略
#   5、[主]更新策略，每次有一个参数随机非法
#   6、[主]删除策略，参数非法
#   7、[主]查看策略，参数非法
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
REP_ABS_PATH = os.path.join(rep_common.REP_PATH, FILE_NAME)                 # /mnt/volume1/snap/filename
FILE_MASTER_PATH = os.path.join(rep_common.MASTER_PAIR_PATH, FILE_NAME)     # /mnt/parastor/rep_test_dir/filename
FILE_SLAVE_PATH = os.path.join(rep_common.SLAVE_PAIR_PATH, FILE_NAME)       # /mnt/(slave)parastor/(slave)rep_test/filename
NEED_CLUSTER_LIST = [rep_common.MASTER, rep_common.SLAVE]
THREADS_NUMBER = 10



def case():
    log.info('case begin')
    log.info('1>[主从]准备复制域和通道')
    rc, ready_info = rep_common.format_area_channel()
    common.judge_rc(rc, 0, 'format_area_channel failed')
    channelid = ready_info['channel']
    m_dir_lst = rep_common.create_dir(rep_common.MASTER_NODE_LST[0], FILE_MASTER_PATH, 'dir', 20)
    s_dir_lst = rep_common.create_dir(rep_common.SLAVE_NODE_LST[0], FILE_SLAVE_PATH, 'dir', 20)

    log.info('2> [主]正常创建pair')
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=m_dir_lst[0],
                                        destination_directory=s_dir_lst[0])
    common.judge_rc(rc, 0, 'create_rep_pair faled')
    rc, pairid = rep_common.get_one_pair_id(rep_channel_id=channelid, source_directory=m_dir_lst[0],
                                            destination_directory=s_dir_lst[0])
    common.judge_rc(rc, 0, 'get_one_pair_id failed')

    log.info('3> [主]创建策略，每次有一个参数随机非法')

    '''name'''
    wrong_param = rep_common.generate_special_symbol_name()
    rc, stdout = common.create_rep_policy(name=wrong_param, rep_pair_id=pairid, period_type='BY_YEAR',
                                          months=1, days=1, hours=1, minute=1, expire_time=0)
    common.judge_rc_unequal(rc, 0, 'create_rep_policy successful')

    '''rep_pair_id'''
    wrong_param = rep_common.generate_special_symbol_name()
    rc, stdout = common.create_rep_policy(name=FILE_NAME, rep_pair_id=wrong_param, period_type='BY_YEAR',
                                          months=1, days=1, hours=1, minute=1, expire_time=0)
    common.judge_rc_unequal(rc, 0, 'create_rep_policy successful')

    '''period_type'''
    wrong_param = rep_common.generate_special_symbol_name()
    rc, stdout = common.create_rep_policy(name=FILE_NAME, rep_pair_id=pairid, period_type=wrong_param,
                                          months=1, days=1, hours=1, minute=1, expire_time=0)
    common.judge_rc_unequal(rc, 0, 'create_rep_policy successful')

    '''months'''
    wrong_param = rep_common.generate_special_symbol_name()
    rc, stdout = common.create_rep_policy(name=FILE_NAME, rep_pair_id=pairid, period_type='BY_YEAR',
                                          months=wrong_param , days=1, hours=1, minute=1, expire_time=0)
    common.judge_rc_unequal(rc, 0, 'create_rep_policy successful')

    '''days'''
    wrong_param = rep_common.generate_special_symbol_name()
    rc, stdout = common.create_rep_policy(name=FILE_NAME, rep_pair_id=pairid, period_type='BY_YEAR',
                                          months=1, days=wrong_param, hours=1, minute=1, expire_time=0)
    common.judge_rc_unequal(rc, 0, 'create_rep_policy successful')

    '''hours'''
    wrong_param = rep_common.generate_special_symbol_name()
    rc, stdout = common.create_rep_policy(name=FILE_NAME, rep_pair_id=pairid, period_type='BY_YEAR',
                                          months=1, days=1, hours=wrong_param, minute=1, expire_time=0)
    common.judge_rc_unequal(rc, 0, 'create_rep_policy successful')

    '''minute'''
    wrong_param = rep_common.generate_special_symbol_name()
    rc, stdout = common.create_rep_policy(name=FILE_NAME, rep_pair_id=pairid, period_type='BY_YEAR',
                                          months=1, days=1, hours=1, minute=wrong_param, expire_time=0)
    common.judge_rc_unequal(rc, 0, 'create_rep_policy successful')

    '''expire_time'''
    wrong_param = rep_common.generate_special_symbol_name()
    rc, stdout = common.create_rep_policy(name=FILE_NAME, rep_pair_id=pairid, period_type='BY_YEAR',
                                          months=1, days=1, hours=1, minute=0, expire_time=wrong_param)
    common.judge_rc_unequal(rc, 0, 'create_rep_policy successful')

    '''week_days'''
    wrong_param = rep_common.generate_special_symbol_name()
    rc, stdout = common.create_rep_policy(name=FILE_NAME, rep_pair_id=pairid, period_type='BY_WEEK',
                                          week_days=wrong_param, hours=1, minute=1, expire_time=0)
    common.judge_rc_unequal(rc, 0, 'create_rep_policy successful')


    log.info('4> [主]成功创建一条策略')
    rc, stdout = common.create_rep_policy(name=FILE_NAME, rep_pair_id=pairid, period_type='BY_YEAR',
                                          months=1, days=1, hours=1, minute=0, expire_time=0)
    common.judge_rc(rc, 0, 'create_rep_policy failed')
    rc, policyid = rep_common.get_rep_policy_id(name=FILE_NAME)
    common.judge_rc(rc, 0, 'get_rep_policy_id failed')
    
    log.info('5> [主]更新策略，每次有一个参数随机非法')
    '''id'''
    wrong_param = rep_common.generate_special_symbol_name()
    rc, stdout = common.create_rep_policy(id=wrong_param, name=FILE_NAME, rep_pair_id=pairid, period_type='BY_YEAR',
                                          months=1, days=1, hours=1, minute=1, expire_time=0)
    common.judge_rc_unequal(rc, 0, 'create_rep_policy successful')

    '''name'''
    wrong_param = rep_common.generate_special_symbol_name()
    rc, stdout = common.update_rep_policy(id=policyid, name=wrong_param, rep_pair_id=pairid, period_type='BY_YEAR',
                                          months=1, days=1, hours=1, minute=1, expire_time=0)
    common.judge_rc_unequal(rc, 0, 'update_rep_policy successful')
    rep_common.update_rep_policy()

    '''rep_pair_id'''
    wrong_param = rep_common.generate_special_symbol_name()
    rc, stdout = common.update_rep_policy(id=policyid, name=FILE_NAME, rep_pair_id=wrong_param, period_type='BY_YEAR',
                                          months=1, days=1, hours=1, minute=1, expire_time=0)
    common.judge_rc_unequal(rc, 0, 'update_rep_policy successful')

    '''period_type'''
    wrong_param = rep_common.generate_special_symbol_name()
    rc, stdout = common.update_rep_policy(id=policyid, name=FILE_NAME, rep_pair_id=pairid, period_type=wrong_param,
                                          months=1, days=1, hours=1, minute=1, expire_time=0)
    common.judge_rc_unequal(rc, 0, 'update_rep_policy successful')

    '''months'''
    wrong_param = rep_common.generate_special_symbol_name()
    rc, stdout = common.update_rep_policy(id=policyid, name=FILE_NAME, rep_pair_id=pairid, period_type='BY_YEAR',
                                          months=wrong_param , days=1, hours=1, minute=1, expire_time=0)
    common.judge_rc_unequal(rc, 0, 'update_rep_policy successful')

    '''days'''
    wrong_param = rep_common.generate_special_symbol_name()
    rc, stdout = common.update_rep_policy(id=policyid, name=FILE_NAME, rep_pair_id=pairid, period_type='BY_YEAR',
                                          months=1, days=wrong_param, hours=1, minute=1, expire_time=0)
    common.judge_rc_unequal(rc, 0, 'update_rep_policy successful')

    '''hours'''
    wrong_param = rep_common.generate_special_symbol_name()
    rc, stdout = common.update_rep_policy(id=policyid, name=FILE_NAME, rep_pair_id=pairid, period_type='BY_YEAR',
                                          months=1, days=1, hours=wrong_param, minute=1, expire_time=0)
    common.judge_rc_unequal(rc, 0, 'update_rep_policy successful')

    '''minute'''
    wrong_param = rep_common.generate_special_symbol_name()
    rc, stdout = common.update_rep_policy(id=policyid, name=FILE_NAME, rep_pair_id=pairid, period_type='BY_YEAR',
                                          months=1, days=1, hours=1, minute=wrong_param, expire_time=0)
    common.judge_rc_unequal(rc, 0, 'update_rep_policy successful')

    '''expire_time'''
    wrong_param = rep_common.generate_special_symbol_name()
    rc, stdout = common.update_rep_policy(id=policyid, name=FILE_NAME, rep_pair_id=pairid, period_type='BY_YEAR',
                                          months=1, days=1, hours=1, minute=0, expire_time=wrong_param)
    common.judge_rc_unequal(rc, 0, 'update_rep_policy successful')

    '''week_days'''
    wrong_param = rep_common.generate_special_symbol_name()
    rc, stdout = common.update_rep_policy(id=policyid, name=FILE_NAME, rep_pair_id=pairid, period_type='BY_WEEK',
                                          week_days=wrong_param, hours=1, minute=1, expire_time=0)
    common.judge_rc_unequal(rc, 0, 'update_rep_policy successful')

    log.info('6> [主]删除策略，参数非法')
    wrong_param = rep_common.generate_wrong_id()
    rc, stdout = common.delete_rep_policies(ids=wrong_param)
    common.judge_rc_unequal(rc, 0, 'delete_rep_policies successful')

    log.info('7> [主]查看策略，参数非法')
    wrong_param = rep_common.generate_wrong_id()
    rc, stdout = common.get_rep_policies(ids=wrong_param)
    common.judge_rc_unequal(rc, 0, 'get_rep_policies successful')

    return



def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
