# -*-coding:utf-8 -*
import os
import time
import json

import utils_path
import common
import snap_common
import log
import prepare_clean

####################################################################################
#
# Author: baorb
# date 2018-01-19
# @summary：
#    创建快照策略时，输入无效参数
# @steps:
#    1、创建快照，BY_YEAR、BY_MONTH、BY_DAY、BY_WEEKDAY的每个模式下，
#       其他每个参数都设置一遍无效值。（每次创建都有一个参数无效）;
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              # /mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   # /snap/snap_13_0_0_0


def case():
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH

    # 周期为年，不写月
    rc, stdout = common.create_snapshot_strategy(name='brb', path=path, period_type='BY_YEAR', days=1, hours=1,
                                                 minute=1, expire_time=0)
    if rc == 0:
        log.error('create_snapshot_strategy succeed!!!')
        raise Exception('create_snapshot_strategy succeed!!!')

    # 周期为年，不写日
    rc, stdout = common.create_snapshot_strategy(name='brb', path=path, period_type='BY_YEAR', months=1, hours=1,
                                                 minute=1, expire_time=0)
    if rc == 0:
        log.error('create_snapshot_strategy succeed!!!')
        raise Exception('create_snapshot_strategy succeed!!!')

    # 周期为年，写上星期
    rc, stdout = common.create_snapshot_strategy(name='brb', path=path, period_type='BY_YEAR', months=1, week_days=1,
                                                 days=1, hours=1, minute=1, expire_time=0)
    stdout = common.json_loads(stdout)
    if stdout['detail_err_msg'] != "week_days must be null when period_type is 'BY_YEAR'":
        log.error('create_snapshot_strategy is not right!!!')
        raise Exception('create_snapshot_strategy is not right!!!')

    # 周期为年，月不在有效范围内
    rc, stdout = common.create_snapshot_strategy(name='brb', path=path, period_type='BY_YEAR', months=0, days=1,
                                                 hours=1, minute=1, expire_time=0)
    if rc == 0:
        log.error('create_snapshot_strategy succeed!!!')
        raise Exception('create_snapshot_strategy succeed!!!')

    rc, stdout = common.create_snapshot_strategy(name='brb', path=path, period_type='BY_YEAR', months=13, days=1,
                                                 hours=1, minute=1, expire_time=0)
    if rc == 0:
        log.error('create_snapshot_strategy succeed!!!')
        raise Exception('create_snapshot_strategy succeed!!!')

    # 周期为月，参数有月
    rc, stdout = common.create_snapshot_strategy(name='brb', path=path, period_type='BY_MONTH', months=1, days=1,
                                                 hours=1, minute=1, expire_time=0)
    stdout = common.json_loads(stdout)
    if stdout['detail_err_msg'] != "months and week_days must be null when period_type is 'BY_MONTH'":
        log.error('create_snapshot_strategy is not right!!!')
        raise Exception('create_snapshot_strategy is not right!!!')

    # 周期为月，参数星期
    rc, stdout = common.create_snapshot_strategy(name='brb', path=path, period_type='BY_MONTH', days=1,week_days=1,
                                                 hours=1, minute=1, expire_time=0)
    stdout = common.json_loads(stdout)
    if stdout['detail_err_msg'] != "months and week_days must be null when period_type is 'BY_MONTH'":
        log.error('create_snapshot_strategy is not right!!!')
        raise Exception('create_snapshot_strategy is not right!!!')

    # 周期为月，参数没有日
    rc, stdout = common.create_snapshot_strategy(name='brb', path=path, period_type='BY_MONTH', hours=1, minute=1,
                                                 expire_time=0)
    if rc == 0:
        log.error('create_snapshot_strategy succeed!!!')
        raise Exception('create_snapshot_strategy succeed!!!')

    # 周期为月，日没有在有效范围内
    rc, stdout = common.create_snapshot_strategy(name='brb', path=path, period_type='BY_MONTH', days=0, hours=1,
                                                 minute=1, expire_time=0)
    if rc == 0:
        log.error('create_snapshot_strategy succeed!!!')
        raise Exception('create_snapshot_strategy succeed!!!')

    rc, stdout = common.create_snapshot_strategy(name='brb', path=path, period_type='BY_MONTH', days=32, hours=1,
                                                 minute=1, expire_time=0)
    if rc == 0:
        log.error('create_snapshot_strategy succeed!!!')
        raise Exception('create_snapshot_strategy succeed!!!')

    # 周期为星期，参数有月
    rc, stdout = common.create_snapshot_strategy(name='brb', path=path, period_type='BY_WEEK', months=1,
                                                 week_days=1, hours=1, minute=1, expire_time=0)
    stdout = common.json_loads(stdout)
    if stdout['detail_err_msg'] != "months and days must be null when period_type is 'BY_WEEK'":
        log.error('create_snapshot_strategy is not right!!!')
        raise Exception('create_snapshot_strategy is not right!!!')

    # 周期为星期，参数有日
    rc, stdout = common.create_snapshot_strategy(name='brb', path=path, period_type='BY_WEEK', days=1, week_days=1,
                                                 hours=1, minute=1, expire_time=0)
    stdout = common.json_loads(stdout)
    if stdout['detail_err_msg'] != "months and days must be null when period_type is 'BY_WEEK'":
        log.error('create_snapshot_strategy is not right!!!')
        raise Exception('create_snapshot_strategy is not right!!!')

    # 周期为星期，参数没有星期
    rc, stdout = common.create_snapshot_strategy(name='brb', path=path, period_type='BY_WEEK', hours=1, minute=1,
                                                 expire_time=0)
    if rc == 0:
        log.error('create_snapshot_strategy succeed!!!')
        raise Exception('create_snapshot_strategy succeed!!!')

    # 周期为星期，星期参数超出范围
    rc, stdout = common.create_snapshot_strategy(name='brb', path=path, period_type='BY_WEEK', week_days=7,
                                                 hours=1, minute=1, expire_time=0)
    if rc == 0:
        log.error('create_snapshot_strategy succeed!!!')
        raise Exception('create_snapshot_strategy succeed!!!')

    # 周期为日，参数有月
    rc, stdout = common.create_snapshot_strategy(name='brb', path=path, period_type='BY_DAY', months=7,
                                                 hours=1, minute=1, expire_time=0)
    stdout = common.json_loads(stdout)
    if stdout['detail_err_msg'] != "months, week_days and days must be null when period_type is 'BY_DAY'":
        log.error('create_snapshot_strategy succeed!!!')
        raise Exception('create_snapshot_strategy succeed!!!')

    # 周期为日，参数有日
    rc, stdout = common.create_snapshot_strategy(name='brb', path=path, period_type='BY_DAY', days=7, hours=1,
                                                 minute=1, expire_time=0)
    stdout = common.json_loads(stdout)
    if stdout['detail_err_msg'] != "months, week_days and days must be null when period_type is 'BY_DAY'":
        log.error('create_snapshot_strategy succeed!!!')
        raise Exception('create_snapshot_strategy succeed!!!')

    # 周期为日，参数有星期
    rc, stdout = common.create_snapshot_strategy(name='brb', path=path, period_type='BY_DAY', week_days=1, hours=1,
                                                 minute=1, expire_time=0)
    stdout = common.json_loads(stdout)
    if stdout['detail_err_msg'] != "months, week_days and days must be null when period_type is 'BY_DAY'":
        log.error('create_snapshot_strategy succeed!!!')
        raise Exception('create_snapshot_strategy succeed!!!')

    # 周期为日，参数小时不在有效范围内
    rc, stdout = common.create_snapshot_strategy(name='brb', path=path, period_type='BY_DAY', hours=24, minute=1,
                                                 expire_time=0)
    if rc == 0:
        log.error('create_snapshot_strategy succeed!!!')
        raise Exception('create_snapshot_strategy succeed!!!')

    # 周期为日，参数分钟不在有效范围内
    rc, stdout = common.create_snapshot_strategy(name='brb', path=path, period_type='BY_DAY', hours=4, minute=60,
                                                 expire_time=0)
    if rc == 0:
        log.error('create_snapshot_strategy succeed!!!')
        raise Exception('create_snapshot_strategy succeed!!!')

    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)