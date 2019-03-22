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
#    创建单个文件快照后，修改和删除快照文件
#@steps:
#    1、对文件创建快照a1（文件有内容）；
#    2、客户端进入/mnt/parastor/.snapshot修改快照文件的名字；
#    3、客户端进入/mnt/parastor/.snapshot修改快照文件的内容；
#    4、客户端进入/mnt/parastor/.snapshot修改快照文件的权限；
#    5、客户端进入/mnt/parastor/.snapshot删除快照文件；
#    6、删除快照a1；
#    7、客户端进入/mnt/parastor/.snapshot观察是否还有快照入口；
#
#@changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  #/snap/snap_13_0_0_0

def case():
    # 创建文件
    file_path = os.path.join(SNAP_TRUE_PATH, 'test_file1')
    test_str_1 = '1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111' \
                 '1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111'
    cmd = 'echo %s > %s' % (test_str_1, file_path)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 1> 创建快照
    snap_name1 = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_file1')
    rc, stdout = snap_common.create_snapshot(snap_name1, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name1)
        raise Exception('create_snapshot %s failed!!!' % snap_name1)

    # 2> 修改快照文件名字
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name1)
    snap_path_change = os.path.join(snap_common.SNAPSHOT_PAHT, 'test_file')
    cmd = 'mv %s %s' % (snap_path, snap_path_change)
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if rc == 0 :
        log.error('%s succeed!!!' % cmd)
        raise Exception('%s succeed!!!' % cmd)

    # 3> 修改快照文件内容
    test_str_2 = '22222'
    cmd = 'echo %s >> %s' % (test_str_2, snap_path)
    rc, stdout = common.run_command(snap_common.CLIENT_IP_2, cmd)
    if rc == 0:
        log.error('%s succeed!!!' % cmd)
        raise Exception('%s succeed!!!' % cmd)

    # 4> 修改快照文件权限
    cmd = 'chmod 777 %s' % snap_path
    rc, stdout = common.run_command(snap_common.CLIENT_IP_2, cmd)
    if rc == 0:
        log.error('%s succeed!!!' % cmd)
        raise Exception('%s succeed!!!' % cmd)

    # 5> 删除快照文件
    cmd = 'rm -rf %s' % snap_path
    rc, stdout = common.run_command(snap_common.CLIENT_IP_2, cmd)
    if rc == 0:
        log.error('%s succeed!!!' % cmd)
        raise Exception('%s succeed!!!' % cmd)

    # 6> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_path(path)
    if 0 != rc:
        log.error('%s delete failed!!!' % (path))
        raise Exception('%s delete failed!!!' % (path))

    time.sleep(10)

    # 7> 3个客户端检查快照路径入口是否存在
    snap_common.check_snap_entry(snap_path)

    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)
