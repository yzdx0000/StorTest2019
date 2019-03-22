# -*-coding:utf-8 -*
import os

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
#    对不存在的文件和目录创建快照策略
# @steps:
#    1、对不存在的文件创建快照策略;
#    2、对不存在的目录创建快照策略;
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              # /mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   # /snap/snap_13_0_0_0


def case():
    # 1> 对不存在的文件创建快照策略
    snapshot_strategy_name = FILE_NAME + '_snapstrategy1'
    path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_file')
    rc, stdout = snap_common.create_snapstrategy(name=snapshot_strategy_name, path=path, period_type='BY_YEAR',
                                                 months=1, days=1, hours=1, minute=1, expire_time=0)
    stdout = common.json_loads(stdout)
    common.judge_rc(stdout['detail_err_msg'], 'Item is not exist',
                    "snapshot_strategy's detail_err_msg is not right!!!")

    # 2> 对不存在的卷创建快照
    path = 'abc111:/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapstrategy(name=snapshot_strategy_name, path=path, period_type='BY_YEAR',
                                                 months=1, days=1, hours=1, minute=1, expire_time=0)
    stdout = common.json_loads(stdout)
    common.judge_rc(stdout['detail_err_msg'], 'Can not find the volume:abc111',
                    "snapshot_strategy's detail_err_msg is not right!!!")
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)