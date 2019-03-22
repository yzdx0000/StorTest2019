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
#    根目录下隐藏目录创建快照
#@steps:
#    1、部署3个客户端；
#    2、在根路径/mnt/parastor/下创建隐藏目录.snap/；
#    3、对目录/mnt/parastor/.snap/创建快照a1，(使用命令pscli --command=create_snapshot)；
#    4、到/mnt/parastor/.snapshot/检查快照a1的数据；
#    5、对/mnt/parastor/创建快照a2；
#    6、到/mnt/parastor/.snapshot/检查a2数据；
#    7、删除快照；
#    8、查看是否有快照入口路径；
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   #/snap/snap_13_0_0_0

def case():
    # 2> 创建隐藏目录
    test_dir_1 = os.path.join(SNAP_TRUE_PATH, '.test_dir_1')
    cmd = 'mkdir %s' % test_dir_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 隐藏目录里创建文件
    test_file_1 = os.path.join(test_dir_1, 'test_file_1')
    cmd = 'touch %s' % test_file_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 3> 隐藏目录创建快照
    snap_name1 = FILE_NAME + '_snapshot1'
    path1 = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, '.test_dir_1')
    rc, stdout = snap_common.create_snapshot(snap_name1, path1)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name1)
        raise Exception('create_snapshot %s failed!!!' % snap_name1)

    # 4> 检查快照数据
    snap_path_1 = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name1)
    snap_file1 = os.path.join(snap_path_1, 'test_file_1')
    cmd = 'ls %s' % snap_file1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 5> 创建快照
    snap_name2 = FILE_NAME + '_snapshot2'
    path2 = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name2, path2)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name2)
        raise Exception('create_snapshot %s failed!!!' % snap_name2)

    # 6> 检查快照数据
    snap_path_2 = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name2)
    snap_file2 = os.path.join(snap_path_2, 'test_file_1')
    cmd = 'ls %s' % snap_file2
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 7> 手动删除快照
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