# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import common
import snap_common
import log
import get_config
import prepare_clean

#################################################################
#
# Author: baorb
# Date: 2018-08-07
# @summary：
#    同时创建两个快照策略。
# @steps:
#    1, 同时创建两个快照策略
#    2, 成功查询两个快照策略
#
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             # /mnt/volume1/snap/P300_1423
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  # /snap/P300_1423


def create_snapshot_strategy(name, path):
    rc, stdout = snap_common.create_snapstrategy(name=name, path=path,
                                                 period_type='BY_YEAR',
                                                 months=1, days=1, hours=1, minute=1, expire_time=0)
    common.judge_rc(rc, 0, 'create snapshot strategy')


def case():
    log.info("1> 同时创建两个快照策略")
    name1 = FILE_NAME + 'snapshot_strategy1'
    name2 = FILE_NAME + 'snapshot_strategy2'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    p1 = Process(target=create_snapshot_strategy, args=(name1, path))
    p2 = Process(target=create_snapshot_strategy, args=(name2, path))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    common.judge_rc(p1.exitcode, 0, 'snapshot_strategy1 create')
    common.judge_rc(p2.exitcode, 0, 'snapshot_strategy2 create')

    log.info("2> 检查快照策略是否存在")
    snapshot_strategy = snap_common.get_snapshotstrategy_by_name(name1)
    common.judge_rc_unequal(snapshot_strategy, -1, 'snapshot_strategy %s is not exist' % name1)
    snapshot_strategy = snap_common.get_snapshotstrategy_by_name(name2)
    common.judge_rc_unequal(snapshot_strategy, -1, 'snapshot_strategy %s is not exist' % name2)


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
