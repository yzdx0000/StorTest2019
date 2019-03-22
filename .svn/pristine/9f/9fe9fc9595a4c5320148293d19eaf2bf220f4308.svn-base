#-*-coding:utf-8 -*
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
#@summary：
#    软连接创建快照，浏览快照内容。
#@steps:
#    1、分别对一个目录和文件创建软连接；
#    2、分别对目录的软连接和文件的软连接创建快照；
#    3、进入/mnt/parastor/.snapshot目录浏览快照数据；
#    4、修改快照文件；
#    5、修改软连接的源文件，再进入/mnt/parastor/.snapshot目录浏览快照数据；
#    6、删除快照；
#    7、查看是否有快照入口路径；
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  #/snap/snap_13_0_0_0

def case():
    # 创建目录和文件
    test_dir_1 = os.path.join(SNAP_TRUE_PATH, 'test_dir_1')
    cmd = 'mkdir %s' % test_dir_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    test_file_1 = os.path.join(SNAP_TRUE_PATH, 'test_file_1')
    cmd = 'echo 111 > %s' % test_file_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 1> 创建软连接
    cmd = 'ln -s %s %s' % (test_dir_1, os.path.join(SNAP_TRUE_PATH, 'test_dir_1_sf'))
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    cmd = 'ln -s %s %s' % (test_file_1, os.path.join(SNAP_TRUE_PATH, 'test_file_1_sf'))
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 2> 创建快照
    snap_name1 = FILE_NAME + '_snapshot1'
    path1 = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_dir_1_sf')
    rc, stdout = snap_common.create_snapshot(snap_name1, path1)
    stdout = common.json_loads(stdout)
    if 'Invalid parameters' != stdout['detail_err_msg']:
        log.error('create_snapshot %s failed!!!' % snap_name1)
        raise Exception('create_snapshot %s failed!!!' % snap_name1)

    snap_name2 = FILE_NAME + '_snapshot2'
    path1 = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_file_1_sf')
    rc, stdout = snap_common.create_snapshot(snap_name2, path1)
    stdout = common.json_loads(stdout)
    if 'Invalid parameters' != stdout['detail_err_msg']:
        log.error('create_snapshot %s failed!!!' % snap_name2)
        raise Exception('create_snapshot %s failed!!!' % snap_name2)

    # 6> 手动删除快照
    rc, stdout = snap_common.delete_snapshot_by_name(FILE_NAME)
    if 0 != rc:
        log.error('%s delete failed!!!' % (FILE_NAME))
        raise Exception('%s delete failed!!!' % (FILE_NAME))

    log.info('waiting for 10s')
    time.sleep(10)
    judge_mark = True
    while judge_mark:
        delete_check = snap_common.get_snapshot_by_name(snap_name1)
        if delete_check != -1:
            log.info('waiting for 10s')
            time.sleep(10)
        else:
            judge_mark = False

    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)