# -*-coding:utf-8 -*
import os
import time
from multiprocessing import Process

import utils_path
import common
import snap_common
import log
import tool_use
import prepare_clean


####################################################################################
#
# Author: liyao
# date 2018-05-07
# @summary：
#    通过策略不断创建快照，快照不断过期删除
# @steps:
#    1、对/mnt/parastor/snap/目录创建12个快照策略，每个策略创建快照的时间是5分、10分、15分..等等，快照的过期时间是5分钟;
#    2、查询快照策略(使用命令pscli --command=get_snapshot_strategy)
#    3、在/mnt/parastor/snap/一直进行数据读写;
#    4、查询快照是否按时创建删除;
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              # /mnt/volume1/snap/snap_13_0_4_5
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   # /snap/snap_13_0_4_5


def check_snapshots():
    # 4>查询快照是否正确创建及删除
    # 每隔5分钟获取当前快照信息
    for i in range(300):
        stdout = snap_common.get_all_snapshot()
        snapshot_create_time = stdout['result']['snapshots'][0]['create_time']
        snapshot_delete_time = snapshot_create_time + 300
        expected_delete_time = snapshot_delete_time
        log.info(expected_delete_time)

        # 比较快照期望删除时间与当前时间
        rc, current_time = snap_common.get_current_time()
        if int(current_time) > snapshot_delete_time:
            raise Exception('deleting snapshot failed !!!')

        log.info('waiting for 300s')
        time.sleep(300)
    return


def case():
    # 创建目录及文件
    test_file = os.path.join(SNAP_TRUE_PATH, 'test_file')
    cmd = 'dd if=%s of=%s bs=1k count=8' % (snap_common.get_system_disk(snap_common.CLIENT_IP_1), test_file)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 1>每小时对目录创建12个快照
    for i in range(1, 13):
        interval_time = 5 * (i-1)
        snapshot_strategy_name = 'snapstrategy_%s' % str(i)
        path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
        snap_common.create_snapstrategy(name=snapshot_strategy_name, path=path,
                                        period_type='BY_DAY',
                                        hours='0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23',
                                        minute=str(interval_time),
                                        expire_time=300)
        # 2> 查询快照策略
        snapshot_strategy = snap_common.get_snapshotstrategy_by_name(snapshot_strategy_name)
        if -1 == snapshot_strategy:
            log.error('snapshot_strategy %s is not exist!!!' % snapshot_strategy_name)
            raise Exception('snapshot_strategy %s is not exist!!!' % snapshot_strategy_name)

    '''获取所有快照策略的id'''
    stdout = snap_common.get_all_snapshotstrategy()
    if stdout == -1:
        raise Exception('get snapshot strategy failed !!!')
    snapshot_strategy_lst = stdout['result']['snapshot_strategies']
    strategy_id_lst = []
    for mem in snapshot_strategy_lst:
        strategy_id_lst.append(mem['id'])

    # 3> 快照创建及删除过程中，在目录下不断进行数据读写
    log.info('waiting for 300s')
    time.sleep(300)

    p1 = Process(target=tool_use.vdbench_run,
                 args=(SNAP_TRUE_PATH, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2),
                 kwargs={'run_create': True})
    p2 = Process(target=check_snapshots)

    p1.start()
    p2.start()

    p1.join()
    p2.terminate()
    p2.join()

    # 5> 删除快照策略
    for mem in snapshot_strategy_lst:
        rc, stdout = snap_common.delete_snapshotstrategy_by_ids(str(mem['id']))
        common.judge_rc(rc, 0, 'delete snapshot %s failed !!!' % mem['id'])
        log.info('waiting for 10s')
        time.sleep(10)

        '''检查快照策略'''
        rc, stdout = common.get_snapshot_strategy(ids=str(mem['id']))
        common.judge_rc_unequal(rc, 0, 'delete snapshot_strategy %s failed !!!' % mem['id'])

    """
    for i in range(1, 13):
        snapshot_strategy_name = 'snapstrategy_%s' % str(i)
        rc, stdout = snap_common.delete_snapshotstrategy_by_name(snapshot_strategy_name)
        if rc != 0:
            log.error("%s delete failed!!!" % snapshot_strategy_name)
            raise Exception("%s snapshot delete failed!!!" % snapshot_strategy_name)

        time.sleep(10)

        # 6> 检查快照策略
        snapshot_strategy1 = snap_common.get_snapshotstrategy_by_name(snapshot_strategy_name)
        if -1 != snapshot_strategy1:
            log.error('snapshot_strategy %s is exist!!!' % snapshot_strategy_name)
            raise Exception('snapshot_strategy %s is exist!!!' % snapshot_strategy_name)
    """
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)