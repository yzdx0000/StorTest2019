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
# Date: 2018-08-08
# @summary：
#    相同的快照策略生成快照测试
# @steps:
#    1、创建两个相同的快照策略;
#    2、到时间后，检查快照策略是否生成了快照;
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              # /mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   # /snap/snap_13_0_0_0


def case():
    log.info("创建两个相同的快照策略")
    """获取当前时间"""
    rc, stdout = snap_common.get_current_time()
    current_time = int(stdout.strip())
    create_time = current_time + 120
    cmd = 'date -d @%d' % create_time
    rc, stdout = common.run_command(snap_common.SYSTEM_IP, cmd)
    hour = stdout.split()[3].split(':')[0].strip()
    minute = stdout.split()[3].split(':')[1].strip()

    expire_time = 90

    snapshot_strategy_name1 = FILE_NAME + '_snapstrategy1'
    snapshot_strategy_name2 = FILE_NAME + '_snapstrategy2'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    snap_common.create_snapstrategy(name=snapshot_strategy_name1, path=path, period_type='BY_DAY',
                                    hours=hour, minute=minute, expire_time=expire_time)
    snap_common.create_snapstrategy(name=snapshot_strategy_name2, path=path, period_type='BY_DAY',
                                    hours=hour, minute=minute, expire_time=expire_time)

    # 2分钟后检查快照是否生成
    log.info('wait 135s')
    time.sleep(135)

    log.info("检查快照是否创建")
    rc, id_lst = snap_common.get_snapshot_ids_by_name(snapshot_strategy_name1)
    common.judge_rc(rc, 0, "%s's snapshot is not create!!!" % snapshot_strategy_name1)
    rc, id_lst = snap_common.get_snapshot_ids_by_name(snapshot_strategy_name2)
    common.judge_rc(rc, 0, "%s's snapshot is not create!!!" % snapshot_strategy_name2)

    log.info("检查快照是否删除")
    log.info('wait %ds' % expire_time)
    time.sleep(expire_time)
    rc, id_lst = snap_common.get_snapshot_ids_by_name(FILE_NAME)
    common.judge_rc_unequal(rc, 0, "%s's snapshot is not delete!!!" % FILE_NAME)
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)