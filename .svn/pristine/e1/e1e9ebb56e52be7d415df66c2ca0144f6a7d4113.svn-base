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
#    创建单个目录快照后，删除目录，浏览快照内容
#@steps:
#    1、对目录/mnt/parastor/snap/创建快照a1，(使用命令pscli --command=create_snapshot)；
#    2、进入/mnt/parastor/.snapshot目录浏览a1快照数据；
#    3、删除目录/mnt/parastor/snap/；
#    4、进入/mnt/parastor/.snapshot目录浏览a1快照数据；
#    5、删除快照a1；
#    6、进入/mnt/parastor/.snapshot目录查看快照路径入口；
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   #/snap/snap_13_0_0_0

def case():
    # 创建子文件test_file1
    file1_name = os.path.join(SNAP_TRUE_PATH, 'test_file1')
    cmd1 = 'touch %s' % file1_name
    common.run_command(snap_common.CLIENT_IP_1, cmd1)

    # 1> 对目录做快照
    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name)
        raise Exception('create_snapshot %s failed!!!' % snap_name)

    # 2> 检查/mnt/parastor/.snapshot下快照数据
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name)
    snap_test_file1 = os.path.join(snap_path, 'test_file1')
    check_cmd1 = 'ls %s' % snap_test_file1
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, check_cmd1)
    if rc != 0:
        log.error('%s %s is not exist!!!' % (snap_common.CLIENT_IP_1, snap_test_file1))
        raise Exception('%s %s is not exist!!!' % (snap_common.CLIENT_IP_1, snap_test_file1))
    rc, stdout = common.run_command(snap_common.CLIENT_IP_2, check_cmd1)
    if rc != 0:
        log.error('%s %s is not exist!!!' % (snap_common.CLIENT_IP_2, snap_test_file1))
        raise Exception('%s %s is not exist!!!' % (snap_common.CLIENT_IP_2, snap_test_file1))
    rc, stdout = common.run_command(snap_common.CLIENT_IP_3, check_cmd1)
    if rc != 0:
        log.error('%s %s is not exist!!!' % (snap_common.CLIENT_IP_3, snap_test_file1))
        raise Exception('%s %s is not exist!!!' % (snap_common.CLIENT_IP_3, snap_test_file1))

    # 3> 删除快照源目录
    common.rm_exe(snap_common.CLIENT_IP_1,SNAP_TRUE_PATH)

    # 4> 检查/mnt/parastor/.snapshot下快照数据
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name)
    snap_test_file1 = os.path.join(snap_path, 'test_file1')
    check_cmd1 = 'ls %s' % snap_test_file1
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, check_cmd1)
    if rc != 0:
        log.error('%s %s is not exist!!!' % (snap_common.CLIENT_IP_1, snap_test_file1))
        raise Exception('%s %s is not exist!!!' % (snap_common.CLIENT_IP_1, snap_test_file1))
    rc, stdout = common.run_command(snap_common.CLIENT_IP_2, check_cmd1)
    if rc != 0:
        log.error('%s %s is not exist!!!' % (snap_common.CLIENT_IP_2, snap_test_file1))
        raise Exception('%s %s is not exist!!!' % (snap_common.CLIENT_IP_2, snap_test_file1))
    rc, stdout = common.run_command(snap_common.CLIENT_IP_3, check_cmd1)
    if rc != 0:
        log.error('%s %s is not exist!!!' % (snap_common.CLIENT_IP_3, snap_test_file1))
        raise Exception('%s %s is not exist!!!' % (snap_common.CLIENT_IP_3, snap_test_file1))

    # 5> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_name(snap_name)
    if 0 != rc:
        log.error('%s delete failed!!!' % (snap_name))
        raise Exception('%s delete failed!!!' % (snap_name))

    time.sleep(10)

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
