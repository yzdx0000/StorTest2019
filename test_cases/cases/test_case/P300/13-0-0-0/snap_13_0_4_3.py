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
#    快照策略测试
# @steps:
#    1、对目录/mnt/parastor/snap/创建快照策略snap_strategy1，period_type为BY_YEAR，expire_time为0，
#       其他参数自己根据情况创建(使用pscli --command=create_snapshot _strategy);
#    2、查询快照策略(使用pscli --command=get_snapshot_strategy);
#    3、修改快照策略，period_type为BY_DAY，expire_time为具体时间值，其他参数自己根据情况创建;
#    4、查询快照策略;
#    5、观察快照策略是否可以生成快照;
#    6、删除快照策略;
#    7、查询快照策略;
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              # /mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   # /snap/snap_13_0_0_0


def case():
    # 1> 对目录创建策略
    snapshot_strategy_name = FILE_NAME + '_snapstrategy1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = common.create_snapshot_strategy(snapshot_strategy_name, path, period_type='BY_YEAR', months=1,days=1, hours=1,
                                    minute=1, expire_time=0)
    common.judge_rc(rc, 0, 'create_snapshot_strategy failed')

    # 2> 查询快照策略
    snapshot_strategy = snap_common.get_snapshotstrategy_by_name(snapshot_strategy_name)
    if -1 == snapshot_strategy:
        log.error('snapshot_strategy %s is not exist!!!' % snapshot_strategy_name)
        raise Exception('snapshot_strategy %s is not exist!!!' % snapshot_strategy_name)

    # 获取当前时间
    rc, stdout = snap_common.get_current_time()
    current_time = int(stdout.strip())
    create_time = current_time + 240
    cmd = 'date -d @%d' % create_time
    rc, stdout = common.run_command(snap_common.SYSTEM_IP, cmd)
    hour = stdout.split()[3].split(':')[0].strip()
    minute = stdout.split()[3].split(':')[1].strip()

    expire_time = 120
    # 3> 修改快照策略
    rc, stdout = common.update_snapshot_strategy(snapshot_strategy['id'], period_type='BY_DAY', hours=hour,
                                                 minute=minute, expire_time=expire_time,
                                                 description='"I am a snapshot_strategy, P300!"')
    common.judge_rc(rc, 0, 'update_snapshot_strategy failed')

    # 4> 查询快照策略
    snapshot_strategy1 = snap_common.get_snapshotstrategy_by_name(snapshot_strategy_name)
    if -1 == snapshot_strategy1:
        log.error('snapshot_strategy %s is not exist!!!' % snapshot_strategy_name)
        raise Exception('snapshot_strategy %s is not exist!!!' % snapshot_strategy_name)
    if snapshot_strategy1['description'] != "I am a snapshot_strategy, P300!":
        log.error("%s's description is not right!!!" % snapshot_strategy_name)
        raise Exception("%s's description is not right!!!" % snapshot_strategy_name)

    # 2分钟后检查快照是否生成
    log.info('wait 255s')
    time.sleep(255)

    # 5> 根据路径查询快照
    rc, id_lst = snap_common.get_snapshot_ids_by_path(path)
    if rc != 0:
        log.error("%s's snapshot is not create!!!" % snapshot_strategy_name)
        raise Exception("%s's snapshot is not create!!!" % snapshot_strategy_name)

    # 等待120s后检查快照是否删除
    log.info('wait %ds' % expire_time)
    time.sleep(expire_time)
    rc, id_lst = snap_common.get_snapshot_ids_by_path(path)
    if rc == 0:
        log.error("%s's snapshot is not delete!!!" % snapshot_strategy_name)
        raise Exception("%s's snapshot is not delete!!!" % snapshot_strategy_name)

    # 6> 删除快照策略
    rc, stdout = snap_common.delete_snapshotstrategy_by_path(path)
    if rc != 0:
        log.error("%s delete failed!!!" % snapshot_strategy_name)
        raise Exception("%s snapshot delete failed!!!" % snapshot_strategy_name)

    # 7> 检查快照策略
    snapshot_strategy1 = snap_common.get_snapshotstrategy_by_name(snapshot_strategy_name)
    if -1 != snapshot_strategy1:
        log.error('snapshot_strategy %s is exist!!!' % snapshot_strategy_name)
        raise Exception('snapshot_strategy %s is exist!!!' % snapshot_strategy_name)

    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
