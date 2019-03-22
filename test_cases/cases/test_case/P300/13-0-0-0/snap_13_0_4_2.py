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
#    快照策略名字重复性检查
# @steps:
#    1、对/mnt/parastor/snap/test文件创建快照策略a1(使用命令pscli --command=create_snapshot_strategy)；
#    2、对/mnt/parastor/snap/test文件创建快照策略a1(使用命令pscli --command=create_snapshot_strategy)；
#    3、对/mnt/parastor/snap/test文件创建快照策略a2(使用命令pscli --command=create_snapshot_strategy)；
#    4、对/mnt/parastor/snap/test1文件创建快照策略a2(使用命令pscli --command=create_snapshot_strategy)；
#    5、查询快照策略(使用命令pscli --command=get_snapshot_strategy)；
#    6、删除所有快照策略(使用命令pscli --command=delete_snapshot_strategy)；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              # /mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   # /snap/snap_13_0_0_0


def case():
    # 创建文件
    file_path_1 = os.path.join(SNAP_TRUE_PATH, 'test_file1')
    file_path_2 = os.path.join(SNAP_TRUE_PATH, 'test_file2')
    cmd1 = 'touch %s' % file_path_1
    cmd2 = 'touch %s' % file_path_2
    common.run_command(snap_common.CLIENT_IP_1, cmd1)
    common.run_command(snap_common.CLIENT_IP_1, cmd2)

    # 创建快照
    name1 = FILE_NAME + '_snapshot1'
    name2 = FILE_NAME + '_snapshot2'
    # 1> 对第一个文件创建快照策略1
    path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_file1')
    rc, stdout = snap_common.create_snapstrategy(name=name1, path=path, period_type='BY_YEAR',
                                                 months=1, days=1, hours=1, minute=1, expire_time=0)
    common.judge_rc(rc, 0, 'create_snapshot %s failed!!!' % name1)
    # 2> 对第一个文件创建快照策略1
    rc, stdout = snap_common.create_snapstrategy(name=name1, path=path, period_type='BY_YEAR',
                                                 months=1, days=1, hours=1, minute=1, expire_time=0)
    stdout = common.json_loads(stdout)
    common.judge_rc(stdout['err_no'], 14016, 'create_snapshot %s succeed!!!' % name1)

    # 3> 对第一个文件创建快照策略2
    rc, stdout = snap_common.create_snapstrategy(name=name2, path=path, period_type='BY_YEAR',
                                                 months=1, days=1, hours=1, minute=1, expire_time=0)
    common.judge_rc(rc, 0, 'create_snapshot %s failed!!!' % name2)

    # 4> 对第二个文件创建快照策略2
    path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_file2')
    rc, stdout = snap_common.create_snapstrategy(name=name2, path=path, period_type='BY_YEAR',
                                                 months=1, days=1, hours=1, minute=1, expire_time=0)
    stdout = common.json_loads(stdout)
    common.judge_rc(stdout['err_no'], 14016, 'create_snapshot %s succeed!!!' % name2)

    # 6> 删除快照策略
    rc, stdout = snap_common.delete_snapshotstrategy_by_name(FILE_NAME)
    common.judge_rc(rc, 0, "%s delete failed!!!" % FILE_NAME)
    time.sleep(10)
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)