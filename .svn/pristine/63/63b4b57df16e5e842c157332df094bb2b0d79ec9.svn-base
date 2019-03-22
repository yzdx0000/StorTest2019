#-*-coding:utf-8 -*
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
#@summary：
#    对隐藏文件创建快照，检查快照内容
#@steps:
#    1、创建隐藏文件；
#    2、对隐藏文件创建快照；
#    3、修改文件内容；
#    4、检查快照文件内容是否正确；
#    5、删除快照；
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   #/snap/snap_13_0_0_0

def case():
    # 1> 创建隐藏文件
    test_file_1 = os.path.join(SNAP_TRUE_PATH, '.test_file_1')
    cmd = 'echo 111 > %s' % test_file_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 2> 对隐藏文件创建快照
    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, '.test_file_1')
    rc, stdout = snap_common.create_snapshot(snap_name, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name)
        raise Exception('create_snapshot %s failed!!!' % snap_name)

    # 3> 修改文件内容
    cmd = 'echo 222222 > %s' % test_file_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 4> 检查快照文件内容是否正确
    snap_path_1 = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name)
    cmd = 'cat %s' % snap_path_1
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if stdout.strip() != '111':
        log.error('%s is not right!!!' % snap_path_1)
        raise Exception('%s is not right!!!' % snap_path_1)

    # 5> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_path(path)
    if 0 != rc:
        log.error('%s delete snapshot failed!!!' % (path))
        raise Exception('%s delete snapshot failed!!!' % (path))

    log.info('waiting for 10s')
    time.sleep(10)
    judge_mark = True
    while judge_mark:
        delete_check = snap_common.get_snapshot_by_name(snap_name)
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