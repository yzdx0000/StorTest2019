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
#    快照名字重复性检查。
# @steps:
#    1、对/mnt/parastor/snap/test文件创建快照a1(使用命令pscli --command=create_snapshot  expire_time为0)；
#    2、对/mnt/parastor/snap/test文件创建快照a1(使用命令pscli --command=create_snapshot  expire_time为0)；
#    3、对/mnt/parastor/snap/test文件创建快照a2(使用命令pscli --command=create_snapshot  expire_time为0)；
#    4、对/mnt/parastor/snap/test1文件创建快照a2(使用命令pscli --command=create_snapshot  expire_time为0)；
#    5、查询快照(使用命令pscli --command=get_snapshot)；
#    6、删除所有快照(使用命令pscli --command=delete_snapshot)；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             # /mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  # /snap/snap_13_0_0_0


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
    # 1> 对第一个文件创建快照1
    path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_file1')
    rc, stdout = snap_common.create_snapshot(name1, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % name1)
        raise Exception('create_snapshot %s failed!!!' % name1)
    # 2> 对第一个文件创建快照1
    rc, stdout = snap_common.create_snapshot(name1, path)
    stdout = common.json_loads(stdout)
    if 14003 != stdout['err_no']:
        log.error('create_snapshot %s succeed!!!' % name1)
        raise Exception('create_snapshot %s succeed!!!' % name1)
    # 3> 对第一个文件创建快照2
    rc, stdout = snap_common.create_snapshot(name2, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % name2)
        raise Exception('create_snapshot %s failed!!!' % name2)
    # 4> 对第二个文件创建快照2
    path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_file2')
    rc, stdout = snap_common.create_snapshot(name2, path)
    stdout = common.json_loads(stdout)
    if 14003 != stdout['err_no']:
        log.error('create_snapshot %s succeed!!!' % name2)
        raise Exception('create_snapshot %s succeed!!!' % name2)

    # 6> 删除所有快照
    rc, stdout = snap_common.delete_snapshot_by_path(CREATE_SNAP_PATH)
    if 0 != rc:
        log.error('%s delete failed!!!' % (CREATE_SNAP_PATH))
        raise Exception('%s delete failed!!!' % (CREATE_SNAP_PATH))

    time.sleep(10)

    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)