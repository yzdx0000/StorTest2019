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
#    快照策略名字特殊字符和长度
# @steps:
#    1、对/mnt/parastor/snap/test文件创建快照策略，名字含有特殊字符(！~*%#^?.-_等)；；
#    2、对/mnt/parastor/snap/test文件创建快照策略，名字长度超过32个字符；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              # /mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   # /snap/snap_13_0_0_0


def case():
    # 1> 创建快照，含特殊字符
    name1 = FILE_NAME + '~!%?,.'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapstrategy(name=name1, path=path, period_type='BY_YEAR',
                                                 months=1, days=1, hours=1, minute=1, expire_time=0)
    stdout = common.json_loads(stdout)
    common.judge_rc(stdout['err_msg'], 'ILLEGAL_ARGUMENT', 'create_snapshot %s failed!!!' % name1)

    # 2> 创建快照，名字长度超过32个字符
    name_part = ''
    for i in range(0, 32 - len(FILE_NAME)):
        name_part += 'a'
    name2 = FILE_NAME + name_part
    rc, stdout = snap_common.create_snapstrategy(name=name2, path=path, period_type='BY_YEAR',
                                                 months=1, days=1, hours=1, minute=1, expire_time=0)
    stdout = common.json_loads(stdout)
    common.judge_rc(stdout['err_msg'], 'ILLEGAL_ARGUMENT', 'create_snapshot %s failed!!!' % name1)

    # 创建快照，名字长度为31个字符
    name_part = ''
    for i in range(0, 31 - len(FILE_NAME)):
        name_part += 'a'
    name3 = FILE_NAME + name_part
    rc, stdout = snap_common.create_snapstrategy(name=name3, path=path, period_type='BY_YEAR',
                                                 months=1, days=1, hours=1, minute=1, expire_time=0)
    common.judge_rc(rc, 0, 'create_snapshot %s failed!!!' % name3)

    # 删除快照策略
    rc, stdout = snap_common.delete_snapshotstrategy_by_path(path)
    common.judge_rc(rc, 0, "%s delete failed!!!" % path)
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)