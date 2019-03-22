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
#    创建策略执行时间参数错误测试，名称重复性检查
# @steps:
#    1、[主]创建复制域和通道
#    2、[主]创建pair
#    3、[主]创建策略，创建策略，BY_YEAR、BY_MONTH、BY_DAY、BY_WEEKDAY的每个模式下，
#           其他每个参数都设置一遍无效值。（每次创建都有一个参数无效）;
#    4、名称重复性测试
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
REP_ABS_PATH = os.path.join(rep_common.REP_PATH, FILE_NAME)                 # /mnt/volume1/snap/filename
FILE_MASTER_PATH = os.path.join(rep_common.MASTER_PAIR_PATH, FILE_NAME)     # /mnt/parastor/rep_test_dir/filename
FILE_SLAVE_PATH = os.path.join(rep_common.SLAVE_PAIR_PATH, FILE_NAME)       # /mnt/(slave)parastor/(slave)rep_test/filename
NEED_CLUSTER_LIST = [rep_common.MASTER, rep_common.SLAVE]
THREADS_NUMBER = 20
BUTTON = True

def delete_rep_pair(id=None, print_flag=True, fault_node_ip=None, run_cluster=rep_common.MASTER):
    rc, pscli_info = rep_common.delete_rep_pair(id=id, print_flag=print_flag, fault_node_ip=fault_node_ip,
                                                run_cluster=run_cluster)
    common.judge_rc(rc, 0, 'create_rep_pair failed')


def case():
    log.info('case begin')
    master_id_lst = []
    slave_id_lst = []

    if BUTTON is True:
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

        log.info('1>创建复制域及通道')
        master_nodeid_str = rep_common.convert_lst_to_str(master_id_lst)
        rc, pscli_info = rep_common.enable_rep_server(node_ids=master_nodeid_str)
        common.judge_rc(rc, 0, 'enable_rep_server failed')
        slave_nodeid_str = rep_common.convert_lst_to_str(slave_id_lst)
        rc, pscli_info = rep_common.enable_rep_server(node_ids=slave_nodeid_str, run_cluster=rep_common.SLAVE)
        common.judge_rc(rc, 0, 'enable_rep_server failed')

        rc, create_channel_ip = rep_common.ip_for_create_channel(slave_id_lst, run_cluster=rep_common.SLAVE)
        common.judge_rc(rc, 0, 'ip_for_create_channel failed')
        rc, stdout = common.create_rep_channel(ip=create_channel_ip)
        common.judge_rc(rc, 0, 'create_rep_channel failed')

        rc, channelid = rep_common.get_channel_id_by_ip(ip=create_channel_ip)
        common.judge_rc(rc, 0, 'get_rep_channels failed')
    else:
        master_id_lst = [1, 2, 3]
        slave_id_lst = [1, 2, 3]
        channelid=0

    m_dir_lst = rep_common.create_dir(rep_common.MASTER_NODE_LST[0], FILE_MASTER_PATH, 'dir', 2)
    s_dir_lst = rep_common.create_dir(rep_common.SLAVE_NODE_LST[0], FILE_SLAVE_PATH, 'dir', 2)

    log.info('2> [主]正常创建pair')
    rc, stdout = common.create_rep_pair(rep_channel_id=channelid, source_directory=m_dir_lst[0],
                                        destination_directory=s_dir_lst[0])
    common.judge_rc(rc, 0, 'create_rep_pair successful')

    rc, pairid = rep_common.get_one_pair_id(rep_channel_id=channelid, source_directory=m_dir_lst[0],
                                            destination_directory=s_dir_lst[0])
    common.judge_rc(rc, 0, 'get_one_pair_id failed')


    log.info('3>[主]创建策略，每个参数都设置一遍无效值')
    name1 = FILE_NAME
    path = rep_common.convert_abs_to_cmd(m_dir_lst[0])

    # 周期为年，不写月
    rc, stdout = common.create_rep_policy(name=FILE_NAME, rep_pair_id=pairid, period_type='BY_YEAR', days=1, hours=1,
                                          minute=1, expire_time=0)
    if rc == 0:
        log.error('create_rep_policy succeed!!!')
        raise Exception('create_rep_policy succeed!!!')

    # 周期为年，不写日
    rc, stdout = common.create_rep_policy(name=FILE_NAME, rep_pair_id=pairid, period_type='BY_YEAR', months=1, hours=1,
                                          minute=1, expire_time=0)
    if rc == 0:
        log.error('create_rep_policy succeed!!!')
        raise Exception('create_rep_policy succeed!!!')

    # 周期为年，写上星期
    rc, stdout = common.create_rep_policy(name=FILE_NAME, rep_pair_id=pairid, period_type='BY_YEAR', months=1, week_days=1,
                                          days=1, hours=1, minute=1, expire_time=0)
    stdout = common.json_loads(stdout)
    if stdout['detail_err_msg'] != "week_days must be null when period_type is 'BY_YEAR'":
        log.error('create_rep_policy is not right!!!')
        raise Exception('create_rep_policy is not right!!!')

    # 周期为年，月不在有效范围内
    rc, stdout = common.create_rep_policy(name=FILE_NAME, rep_pair_id=pairid, period_type='BY_YEAR', months=0, days=1,
                                          hours=1, minute=1, expire_time=0)
    if rc == 0:
        log.error('create_rep_policy succeed!!!')
        raise Exception('create_rep_policy succeed!!!')

    rc, stdout = common.create_rep_policy(name=FILE_NAME, rep_pair_id=pairid, period_type='BY_YEAR', months=13, days=1,
                                          hours=1, minute=1, expire_time=0)
    if rc == 0:
        log.error('create_rep_policy succeed!!!')
        raise Exception('create_rep_policy succeed!!!')

    # 周期为月，参数有月
    rc, stdout = common.create_rep_policy(name=FILE_NAME, rep_pair_id=pairid, period_type='BY_MONTH', months=1, days=1,
                                          hours=1, minute=1, expire_time=0)
    stdout = common.json_loads(stdout)
    if stdout['detail_err_msg'] != "months and week_days must be null when period_type is 'BY_MONTH'":
        log.error('create_rep_policy is not right!!!')
        raise Exception('create_rep_policy is not right!!!')

    # 周期为月，参数星期
    rc, stdout = common.create_rep_policy(name=FILE_NAME, rep_pair_id=pairid, period_type='BY_MONTH', days=1,week_days=1,
                                          hours=1, minute=1, expire_time=0)
    stdout = common.json_loads(stdout)
    if stdout['detail_err_msg'] != "months and week_days must be null when period_type is 'BY_MONTH'":
        log.error('create_rep_policy is not right!!!')
        raise Exception('create_rep_policy is not right!!!')

    # 周期为月，参数没有日
    rc, stdout = common.create_rep_policy(name=FILE_NAME, rep_pair_id=pairid, period_type='BY_MONTH', hours=1, minute=1,
                                          expire_time=0)
    if rc == 0:
        log.error('create_rep_policy succeed!!!')
        raise Exception('create_rep_policy succeed!!!')

    # 周期为月，日没有在有效范围内
    rc, stdout = common.create_rep_policy(name=FILE_NAME, rep_pair_id=pairid, period_type='BY_MONTH', days=0, hours=1,
                                          minute=1, expire_time=0)
    if rc == 0:
        log.error('create_rep_policy succeed!!!')
        raise Exception('create_rep_policy succeed!!!')

    rc, stdout = common.create_rep_policy(name=FILE_NAME, rep_pair_id=pairid, period_type='BY_MONTH', days=32, hours=1,
                                          minute=1, expire_time=0)
    if rc == 0:
        log.error('create_rep_policy succeed!!!')
        raise Exception('create_rep_policy succeed!!!')

    # 周期为星期，参数有月
    rc, stdout = common.create_rep_policy(name=FILE_NAME, rep_pair_id=pairid, period_type='BY_WEEK', months=1,
                                          week_days=1, hours=1, minute=1, expire_time=0)
    stdout = common.json_loads(stdout)
    if stdout['detail_err_msg'] != "months and days must be null when period_type is 'BY_WEEK'":
        log.error('create_rep_policy is not right!!!')
        raise Exception('create_rep_policy is not right!!!')

    # 周期为星期，参数有日
    rc, stdout = common.create_rep_policy(name=FILE_NAME, rep_pair_id=pairid, period_type='BY_WEEK', days=1, week_days=1,
                                          hours=1, minute=1, expire_time=0)
    stdout = common.json_loads(stdout)
    if stdout['detail_err_msg'] != "months and days must be null when period_type is 'BY_WEEK'":
        log.error('create_rep_policy is not right!!!')
        raise Exception('create_rep_policy is not right!!!')

    # 周期为星期，参数没有星期
    rc, stdout = common.create_rep_policy(name=FILE_NAME, rep_pair_id=pairid, period_type='BY_WEEK', hours=1, minute=1,
                                          expire_time=0)
    if rc == 0:
        log.error('create_rep_policy succeed!!!')
        raise Exception('create_rep_policy succeed!!!')

    # 周期为星期，星期参数超出范围
    rc, stdout = common.create_rep_policy(name=FILE_NAME, rep_pair_id=pairid, period_type='BY_WEEK', week_days=7,
                                          hours=1, minute=1, expire_time=0)
    if rc == 0:
        log.error('create_rep_policy succeed!!!')
        raise Exception('create_rep_policy succeed!!!')

    # 周期为日，参数有月
    rc, stdout = common.create_rep_policy(name=FILE_NAME, rep_pair_id=pairid, period_type='BY_DAY', months=7,
                                          hours=1, minute=1, expire_time=0)
    stdout = common.json_loads(stdout)
    if stdout['detail_err_msg'] != "months, week_days and days must be null when period_type is 'BY_DAY'":
        log.error('create_rep_policy succeed!!!')
        raise Exception('create_rep_policy succeed!!!')

    # 周期为日，参数有日
    rc, stdout = common.create_rep_policy(name=FILE_NAME, rep_pair_id=pairid, period_type='BY_DAY', days=7, hours=1,
                                          minute=1, expire_time=0)
    stdout = common.json_loads(stdout)
    if stdout['detail_err_msg'] != "months, week_days and days must be null when period_type is 'BY_DAY'":
        log.error('create_rep_policy succeed!!!')
        raise Exception('create_rep_policy succeed!!!')

    # 周期为日，参数有星期
    rc, stdout = common.create_rep_policy(name=FILE_NAME, rep_pair_id=pairid, period_type='BY_DAY', week_days=1, hours=1,
                                          minute=1, expire_time=0)
    stdout = common.json_loads(stdout)
    if stdout['detail_err_msg'] != "months, week_days and days must be null when period_type is 'BY_DAY'":
        log.error('create_rep_policy succeed!!!')
        raise Exception('create_rep_policy succeed!!!')

    # 周期为日，参数小时不在有效范围内
    rc, stdout = common.create_rep_policy(name=FILE_NAME, rep_pair_id=pairid, period_type='BY_DAY', hours=24, minute=1,
                                          expire_time=0)
    if rc == 0:
        log.error('create_rep_policy succeed!!!')
        raise Exception('create_rep_policy succeed!!!')

    # 周期为日，参数分钟不在有效范围内
    rc, stdout = common.create_rep_policy(name=FILE_NAME, rep_pair_id=pairid, period_type='BY_DAY', hours=4, minute=60,
                                          expire_time=0)
    if rc == 0:
        log.error('create_rep_policy succeed!!!')
        raise Exception('create_rep_policy succeed!!!')

    log.info('4>[主]名称重复性测试')
    rc, stdout = rep_common.create_rep_policy(name='samename', rep_pair_id=pairid, period_type='BY_YEAR',
                                              months=1, days=1, hours=1, minute=1, expire_time=0)
    common.judge_rc(rc, 0, 'create_rep_policy failed')

    rc, stdout = rep_common.create_rep_policy(name='samename', rep_pair_id=pairid, period_type='BY_YEAR',
                                              months=1, days=1, hours=1, minute=1, expire_time=0)
    common.judge_rc_unequal(rc, 0, 'create_rep_policy successful')

    return


def main():
    prepare_clean.rep_test_prepare(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    case()
    prepare_clean.rep_test_clean(FILE_NAME, rep_common.ENV_CHECK, True, clusters=NEED_CLUSTER_LIST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
