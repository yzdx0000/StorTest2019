# -*-coding:utf-8 -*
import os
import time

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
#    批量删除快照策略
# @steps:
#    1、对/mnt/parastor/snap/目录创建多个快照策略;
#    2、查询快照策略(使用命令pscli --command=get_snapshot_strategy);
#    3、批量删除所有快照策略(使用命令pscli --command=delete_snapshot_strategy);
#    4、查询快照策略(使用命令pscli --command=get_snapshot_strategy);
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              # /mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   # /snap/snap_13_0_0_0


def case():
    # 查询所有快照策略
    # 1> 创建10个文件
    snap_strategy_name_lst = []
    for i in range(10):
        snap_true_path = os.path.join(SNAP_TRUE_PATH, 'test_file_%d' % i)
        snap_create_path = os.path.join(CREATE_SNAP_PATH, 'test_file_%d' % i)
        cmd = 'touch %s' % snap_true_path
        common.run_command(snap_common.CLIENT_IP_1, cmd)
        path = snap_common.VOLUME_NAME + ':/' + snap_create_path
        # 每个目录创建10个快照
        for j in range(10):
            snapshot_strategy_name = FILE_NAME + '_%d_%d' % (i, j)
            snap_strategy_name_lst.append(snapshot_strategy_name)

            rc, stdout = snap_common.create_snapstrategy(name=snapshot_strategy_name,
                                                         path=path,
                                                         period_type='BY_YEAR',
                                                         months=1,
                                                         days=1,
                                                         hours=1,
                                                         minute=1,
                                                         expire_time=0)
            common.judge_rc(rc, 0, 'create_snapshot %s failed!!!' % snapshot_strategy_name)

    # 2> 查询快照是否都存在
    for snap_name in snap_strategy_name_lst:
        snapshot1_info = snap_common.get_snapshotstrategy_by_name(snap_name)
        if -1 == snapshot1_info:
            log.error('snap_strategy %s is not exist!!!' % snap_name)
            raise Exception('snap_strategy %s is not exist!!!' % snap_name)

    # 3> 批量删除快照
    rc, stdout = snap_common.delete_snapshotstrategy_by_name(FILE_NAME)
    if 0 != rc:
        log.error('delete_snapshot %s failed!!!' % FILE_NAME)
        raise Exception('delete_snapshot %s failed!!!' % FILE_NAME)

    # 4> 检查快照
    num = 0
    while True:
        time.sleep(5)
        num += 1
        snapshot1_info = snap_common.get_snapshotstrategy_by_name(FILE_NAME)
        if snapshot1_info != -1:
            log.info('%ds, snapshot %s still not delete!' % (num * 5, FILE_NAME))
        else:
            break
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)