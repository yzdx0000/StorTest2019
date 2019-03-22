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
#    对同一个文件创建多个快照。
# @steps:
#    1、对/mnt/parastor/snap/test文件创建快照a1(使用命令pscli --command=create_snapshot  expire_time为0)；
#    2、查询快照(使用pscli --command=get_snapshot )；
#    3、再次对/mnt/parastor/snap/test文件创建快照a2(使用命令pscli --command=create_snapshot  expire_time为具体时间)；
#    4、查询快照(使用pscli --command=get_snapshot)；
#    5、到快照a2生命周期到时间后，查询快照是否已删除(使用命令pscli --command=get_snapshot)；
#    6、手动删除快照(使用命令pscli --command=delete_snapshot )；
#    7、查询快照(使用命令pscli --command=get_snapshot)；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             # /mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  # /snap/snap_13_0_0_0


def case():
    # 创建文件
    snap_file = os.path.join(SNAP_TRUE_PATH, 'test_file')
    cmd = 'dd if=/dev/zero of=%s bs=1M count=260' % snap_file
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if 0 != rc:
        log.error('create %s failed!!!' % snap_file)
        raise Exception('create %s failed!!!' % snap_file)

    # 1> 对文件创建快照
    name1 = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_file')
    rc, stdout = snap_common.create_snapshot(name1, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % name1)
        raise Exception('create_snapshot %s failed!!!' % name1)

    # 2> 查询快照信息
    snapshot1_info = snap_common.get_snapshot_by_name(name1)
    if -1 == snapshot1_info:
        log.error('snap %s is not exist!!!' % name1)
        raise Exception('snap %s is not exist!!!' % name1)

    # 获取当前时间
    rc, stdout = snap_common.get_current_time()

    # 3> 对文件创建第二个快照
    expire_time = int(stdout) + 20
    name2 = FILE_NAME + '_snapshot2'
    rc, stdout = snap_common.create_snapshot(name2, path, expire_time=expire_time)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % name2)
        raise Exception('create_snapshot %s failed!!!' % name2)

    # 4> 查询快照信息
    snapshot2_info = snap_common.get_snapshot_by_name(name2)
    if -1 == snapshot2_info:
        log.error('snap %s is not exist!!!' % name2)
        raise Exception('snap %s is not exist!!!' % name2)
    elif snapshot2_info['expire_time'] != expire_time:
        log.error("%s expire_time's actual value is %s, expected value is %d!!!" %
                  (name2, snapshot2_info['expire_time'], expire_time))
        raise Exception("%s expire_time's actual value is %s, expected value is %d!!!" %
                        (name2, snapshot2_info['expire_time'], expire_time))

    # 5> 超时时间后检查快照是否删除
    log.info('wait 30s')
    time.sleep(30)
    snapshot2_info = snap_common.get_snapshot_by_name(name2)
    if -1 != snapshot2_info and snapshot2_info['state'] != 'SNAPSHOT_DELETING':
        rc1, stdout = snap_common.get_current_time()
        log.error('expire_time is %s, current time is %s, snap %s not delete!!!' %
                  (snapshot2_info['expire_time'], stdout, name2))
        raise Exception('expire_time is %s, current time is %s, snap %s not delete!!!' %
                        (snapshot2_info['expire_time'], stdout, name2))

    # 6> 手动删除快照1
    rc, stdout = snap_common.delete_snapshot_by_ids(snapshot1_info['id'])
    if 0 != rc:
        log.error('%s delete failed!!!' % (name1))
        raise Exception('%s delete failed!!!' % (name1))

    time.sleep(5)

    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)