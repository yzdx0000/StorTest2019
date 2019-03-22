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
#    快照文件复制。
#@steps:
#    1、分别对一个目录和文件创建快照；
#    2、将快照文件cp到其他路径；
#    3、检查cp出的快照文件内容和属性；
#    4、删除快照；
#    5、查看是否有快照入口路径；
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  #/snap/snap_13_0_0_0

def case():
    # 创建文件
    test_file_1 = os.path.join(SNAP_TRUE_PATH, 'test_file_1')
    cmd = 'echo 111 > %s' % test_file_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 1> 创建快照
    snap_name = FILE_NAME + '_snapshot1'
    path1 = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name, path1)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name)
        raise Exception('create_snapshot %s failed!!!' % snap_name)

    # 2> 复制文件到其他路径
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name)
    snap_file_1 = os.path.join(snap_path, 'test_file_1')
    cmd = 'cp %s %s' % (snap_file_1, '/tmp/')
    common.run_command(snap_common.CLIENT_IP_2, cmd)

    # 3> 检查内容
    cmd = 'cat /tmp/test_file_1'
    rc, stdout = common.run_command(snap_common.CLIENT_IP_2, cmd)
    if stdout.strip() != '111':
        log.error('test_file_1 is not right!!!')
        raise Exception('test_file_1 is not right!!!')

    # 4> 删除快照
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

    # 5> 3个客户端检查快照路径入口是否存在
    snap_common.check_snap_entry(snap_path)

    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)