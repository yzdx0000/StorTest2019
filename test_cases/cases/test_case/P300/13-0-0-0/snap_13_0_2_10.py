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
#    创建单个目录快照后，浏览快照内容
#@steps:
#    1、部署3个客户端；
#    2、对一个目录创建快照a1；
#    3、3个客户端分别进入/mnt/parastor/.snapshot目录浏览a1快照数据；
#    4、删除快照；
#    5、3个客户端进入/mnt/parastor/.snapshot观察是否还有快照入口；
#
#@changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  #/snap/snap_13_0_0_0

def case():
    # 2> 创建目录
    dir_path = os.path.join(SNAP_TRUE_PATH, 'test_dir1')
    cmd = 'mkdir %s' % (dir_path)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    file_path = os.path.join(dir_path, 'test_file')
    cmd = 'echo 111111 > %s' % file_path
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 创建快照
    snap_name1 = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_dir1')
    rc, stdout = snap_common.create_snapshot(snap_name1, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name1)
        raise Exception('create_snapshot %s failed!!!' % snap_name1)

    # 3> 检查快照目录数据
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name1, 'test_file')
    cmd = 'cat %s' % snap_path
    rc, stdout = common.run_command(snap_common.CLIENT_IP_2, cmd)
    if stdout.strip() != '111111':
        log.error('%s is not right!!!' % snap_path)
        raise Exception('%s is not right!!!' % snap_path)

    # 4> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_path(path)
    if 0 != rc:
        log.error('%s delete failed!!!' % (path))
        raise Exception('%s delete failed!!!' % (path))

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

    # 10> 3个客户端检查快照路径入口是否存在
    path_check=os.path.join(snap_common.SNAPSHOT_PAHT,snap_name1)
    snap_common.check_snap_entry(path_check)

    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)