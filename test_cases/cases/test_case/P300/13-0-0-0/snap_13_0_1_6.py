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
#    软连接创建快照。
# @steps:
#    1、对目录/mnt/parastor/snap/创建软连接/mnt/parastor/snap_so/；
#    2、对文件/mnt/parastor/snap/test_file1创建软连接/mnt/parastor/test_file_so(使用ln -s命令)；
#    3、对软连接/mnt/parastor/snap_so/创建快照a1；
#    4、对软连接/mnt/parastor/test_file_so创建快照a2；
#    5、查询快照；
#    6、删除快照a1、a2；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             # /mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  # /snap/snap_13_0_0_0


def case():
    # 创建子目录
    test_dir_1 = os.path.join(SNAP_TRUE_PATH, 'test_dir_1')
    cmd = 'mkdir %s' % test_dir_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 创建子文件
    test_file_1 = os.path.join(SNAP_TRUE_PATH, 'test_file_1')
    cmd = 'touch %s' % test_file_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 1> 对目录创建软连接
    cmd = 'ln -s %s %s/test_dir_soft' % (test_dir_1, SNAP_TRUE_PATH)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 2> 对文件创建软连接
    cmd = 'ln -s %s %s/test_file_soft' % (test_file_1, SNAP_TRUE_PATH)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 3> 创建快照1
    name1 = FILE_NAME + '_snapshot1'
    path1 = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_dir_soft')
    rc, stdout = snap_common.create_snapshot(name1, path1)
    stdout = common.json_loads(stdout)
    if stdout['detail_err_msg'] != 'Invalid parameters':
        log.error('create_snapshot %s failed!!!' % name1)
        raise Exception('create_snapshot %s failed!!!' % name1)

    # 4> 创建快照2
    name2 = FILE_NAME + '_snapshot2'
    path2 = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_file_soft')
    rc, stdout = snap_common.create_snapshot(name2, path2)
    stdout = common.json_loads(stdout)
    if stdout['detail_err_msg'] != 'Invalid parameters':
        log.error('create_snapshot %s failed!!!' % name2)
        raise Exception('create_snapshot %s failed!!!' % name2)

    # 6> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_path(CREATE_SNAP_PATH)
    if 0 != rc:
        log.error('%s delete failed!!!' % (CREATE_SNAP_PATH))
        raise Exception('%s delete failed!!!' % (CREATE_SNAP_PATH))
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)