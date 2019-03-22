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
#    可执行文件进行revert
#@steps:
#    1、编译创建可执行文件，对文件创建快照a1；
#    2、修改文件内容；
#    3、对快照进行revert；
#    4、执行可执行文件；
#    5、删除快照；
#    6、3个客户端检查是否有快照入口路径；
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   #/snap/snap_13_0_0_0

def case():
    # 1> 创建c文件
    file_name1 = os.path.join(SNAP_TRUE_PATH, 'test_file.c')
    cmd = 'echo -e "#include<stdio.h>\nvoid main(){printf(\\"Hello world\\");}" > %s' % (file_name1)
    common.run_command(snap_common.CLIENT_IP_1, cmd)
    file_name2 = os.path.join(SNAP_TRUE_PATH, 'test_file.out')
    cmd = 'gcc %s -o %s' % (file_name1, file_name2)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 创建快照
    snap_name1 = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_file.out')
    rc, stdout = snap_common.create_snapshot(snap_name1, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name1)
        raise Exception('create_snapshot %s failed!!!' % snap_name1)

    # 2> 修改文件内容
    cmd = 'echo 11111111 > %s' % file_name2
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 快照目录执行可执行文件
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name1)
    rc, stdout = common.run_command(snap_common.CLIENT_IP_2, snap_path)
    if stdout.strip() != 'Hello world':
        log.error('%s is not right' % snap_path)
        raise Exception('%s is not right' % snap_path)

    # 3> 对快照进行revert
    snap_info = snap_common.get_snapshot_by_name(snap_name1)
    snap_id = snap_info['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id)
    if rc != 0:
        log.error("revert snapshot %s failed!!!" % snap_name1)
        raise Exception("revert snapshot %s failed!!!" % snap_name1)
    snap_common.check_revert_finished(snap_id)

    # 4> 执行可执行文件
    rc, stdout = common.run_command(snap_common.CLIENT_IP_3, file_name2)
    if stdout.strip() != 'Hello world':
        log.error('%s is not right' % snap_path)
        raise Exception('%s is not right' % snap_path)

    # 5> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_path(path)
    if 0 != rc:
        log.error('%s delete snapshot failed!!!' % (path))
        raise Exception('%s delete snapshot failed!!!' % (path))

    time.sleep(10)

    # 6> 3个客户端检查快照路径入口是否存在
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name1)
    snap_common.check_snap_entry(snap_path)


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)