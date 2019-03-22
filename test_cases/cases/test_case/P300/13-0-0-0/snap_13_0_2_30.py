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
#    快照文件和源文件权限
#@steps:
#    1、部署3个客户端；
#    2、客户端1在目录/mnt/parastor/snap/创建权限为755的文件test_file1；
#    3、对文件/mnt/parastor/snap/test_file1创建快照a1，(使用命令pscli --command=create_snapshot)；
#    4、到/mnt/parastor/.snapshot/检查test_file1的权限；
#    5、客户端2修改test_file1的权限为533；
#    6、到/mnt/parastor/.snapshot/检查test_file1的权限；
#    7、删除快照；
#    8、查看是否有快照入口路径；
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   #/snap/snap_13_0_0_0

def case():
    # 2> 创建文件
    test_file_1 = os.path.join(SNAP_TRUE_PATH, 'test_file_1')
    cmd = 'echo 111 > %s' % test_file_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    cmd = 'chmod 755 %s' % test_file_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 3> 创建快照
    snap_name = FILE_NAME + '_snapshot1'
    path1 = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name, path1)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name)
        raise Exception('create_snapshot %s failed!!!' % snap_name)

    # 5> 修改权限
    cmd = 'chmod 533 %s' % test_file_1
    common.run_command(snap_common.CLIENT_IP_2, cmd)

    # 6> 检查快照文件权限
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name)
    snap_file = os.path.join(snap_path, 'test_file_1')
    rc, permission = snap_common.get_file_permission(snap_common.CLIENT_IP_1, snap_file)
    if permission != '755':
        log.error('%s permission is not right!!!' % snap_name)
        raise Exception('%s permission is not right!!!' % snap_name)
    rc, permission = snap_common.get_file_permission(snap_common.CLIENT_IP_2, snap_file)
    if permission != '755':
        log.error('%s permission is not right!!!' % snap_name)
        raise Exception('%s permission is not right!!!' % snap_name)
    rc, permission = snap_common.get_file_permission(snap_common.CLIENT_IP_3, snap_file)
    if permission != '755':
        log.error('%s permission is not right!!!' % snap_name)
        raise Exception('%s permission is not right!!!' % snap_name)

    # 7> 手动删除快照
    rc, stdout = snap_common.delete_snapshot_by_name(FILE_NAME)
    if 0 != rc:
        log.error('%s delete failed!!!' % (FILE_NAME))
        raise Exception('%s delete failed!!!' % (FILE_NAME))

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

    # 8> 3个客户端检查快照路径入口是否存在
    snap_common.check_snap_entry(snap_path)

    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)