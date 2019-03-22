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
#    策略创建快照，执行revert，观察快照内容
# @steps:
#    1、部署3个客户端；
#    2、对目录/mnt/parastor/snap/创建快照策略a1；
#    3、快照策略创建快照成功；
#    4、修改/mnt/parastor/snap/下的内容；
#    5、对快照进行revert；
#    6、删除快照；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              # /mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   # /snap/snap_13_0_0_0


def case():
    # 创建文件
    test_file = os.path.join(SNAP_TRUE_PATH, 'snap_file_1')
    cmd = 'echo 111111 > %s' % test_file
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    """获取当前时间"""
    wait_time = 120
    rc, stdout = snap_common.get_current_time()
    current_time = int(stdout.strip())
    create_time = current_time + wait_time
    cmd = 'date -d @%d' % create_time
    rc, stdout = common.run_command(snap_common.SYSTEM_IP, cmd)
    hour = stdout.split()[3].split(':')[0].strip()
    minute = stdout.split()[3].split(':')[1].strip()

    # 2> 对目录创建策略
    snapshot_strategy_name = FILE_NAME + '_snapstrategy1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    snap_common.create_snapstrategy(name=snapshot_strategy_name, path=path, period_type='BY_DAY',
                                    hours=hour, minute=minute, expire_time=0)

    # 检查快照是否生成
    log.info('wait %ds' % (wait_time + 10))
    time.sleep(wait_time + 10)

    # 3> 根据路径查询快照
    rc, id = snap_common.get_snapshot_ids_by_path(path)
    common.judge_rc(rc, 0, "%s's snapshot is not create!!!" % snapshot_strategy_name)

    # 4> 修改文件内容
    cmd = 'echo 222222 > %s' % test_file
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 5> 对快照进行revert
    rc, snap_id_lst = snap_common.get_snapshot_ids_by_path(path)
    snap_id = snap_id_lst[0]
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id)
    common.judge_rc(rc, 0, "revert snapshot %s failed!!!" % path)
    snap_common.check_revert_finished(snap_id)

    # 检查文件内容是否正确
    cmd = 'cat %s' % test_file
    rc, stdout = common.run_command(snap_common.CLIENT_IP_2, cmd)
    common.judge_rc(stdout.strip(), '111111', '%s is not right!!!' % test_file)

    # 6> 删除快照和策略
    rc, stdout = snap_common.delete_snapshotstrategy_by_path(path)
    common.judge_rc(rc, 0, "%s delete failed!!!" % snapshot_strategy_name)

    rc, stdout = snap_common.delete_snapshot_by_path(path)
    common.judge_rc(rc, 0, '%s delete snapshot failed!!!' % (path))

    time.sleep(10)
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)