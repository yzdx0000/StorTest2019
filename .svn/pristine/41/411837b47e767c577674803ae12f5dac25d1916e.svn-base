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
#    根目录创建快照，浏览快照内容。
#@steps:
#    1、对挂载目录创建快照；
#    2、进入/mnt/parastor/.snapshot目录浏览快照数据；
#    3、修改目录下的文件和子目录；
#    4、进入/mnt/parastor/.snapshot目录浏览快照数据；
#    5、删除快照；
#    6、查看是否有快照入口路径；
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  #/snap/snap_13_0_0_0

def case():
    # 1> 对根目录创建快照
    snap_name = FILE_NAME + '_snapshot1'
    path1 = snap_common.VOLUME_NAME + ':/'
    rc, stdout = snap_common.create_snapshot(snap_name, path1)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name)
        raise Exception('create_snapshot %s failed!!!' % snap_name)

    # 2> 检查目录是否存在
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name)
    snap_dir = os.path.join(snap_path, 'snap')
    cmd = 'ls %s' % snap_dir
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 5> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_name(snap_name)
    if 0 != rc:
        log.error('%s delete failed!!!' % (snap_name))
        raise Exception('%s delete failed!!!' % (snap_name))

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

    # 6> 3个客户端检查快照路径入口是否存在
    snap_common.check_snap_entry(snap_path)

    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)