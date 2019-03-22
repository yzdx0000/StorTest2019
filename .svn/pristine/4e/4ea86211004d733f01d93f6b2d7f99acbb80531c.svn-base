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
#    整个集群下创建20001个快照，最后一个创建失败
# @steps:
#    1、/mnt/parastor/snap1/到/mnt/parastor/snap20/每个目录上创建1000个快照，一共20000个快照；
#    2、对目录/mnt/parastor/snap21/创建快照；
#    3、删除快照；
#    4、3个客户端检查是否有快照入口路径；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              # /mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   # /snap/snap_13_0_0_0


def case():
    # 检查环境中是否有快照，如果有此用例无法执行
    snap_num = snap_common.get_snapshot_num()
    if snap_num != 0:
        log.warn('parastor snapshot is not 0!!!')
        return

    # 1> 每个目录创建1000个快照，共20000个快照
    for i in range(20):
        # 创建子目录
        dir_test_1 = os.path.join(SNAP_TRUE_PATH, 'dir_test_%d' % i)
        cmd = 'mkdir %s' % dir_test_1
        common.run_command(snap_common.CLIENT_IP_1, cmd)
        for j in range(1000):
            # 创建快照
            snap_name1 = FILE_NAME + '_snapshot_%d_%d' % (i, j)
            path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'dir_test_%d' % i)
            rc, stdout = snap_common.create_snapshot(snap_name1, path)
            if 0 != rc:
                log.error('create_snapshot %s failed!!!' % snap_name1)
                raise Exception('create_snapshot %s failed!!!' % snap_name1)

    # 2> 创建第20001个快照
    dir_test_1 = os.path.join(SNAP_TRUE_PATH, 'dir_test_21')
    cmd = 'mkdir %s' % dir_test_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    snap_name1 = FILE_NAME + '_snapshot'
    path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'dir_test_21')
    rc, stdout = snap_common.create_snapshot(snap_name1, path)
    stdout = common.json_loads(stdout)
    if stdout['detail_err_msg'] != 'Too many snapshots created!':
        log.error('create_snapshot %s failed!!!' % snap_name1)
        raise Exception('create_snapshot %s failed!!!' % snap_name1)

    # 3> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_name(FILE_NAME)
    if 0 != rc:
        log.error('%s delete snapshot failed!!!' % (FILE_NAME))
        raise Exception('%s delete snapshot failed!!!' % (FILE_NAME))

    # 检查快照是否删除
    start_time = time.time()
    while True:
        time.sleep(10)
        rc = snap_common.check_snap_exist(FILE_NAME)
        if rc:
            exist_time = int(time.time() - start_time)
            m, s = divmod(exist_time, 60)
            h, m = divmod(m, 60)
            log.info('%dh:%dm:%ds, snapshot %s still not delete!' % (h, m, s, FILE_NAME))
        else:
            break

    time.sleep(10)
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)