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
#    创建单个目录快照后，移动目录，浏览快照内容。
#@steps:
#    1、部署3个客户端；
#    2、对目录/mnt/parastor/snap/(目录下存在文件test_file1，目录test_dir1)创建快照a1，(使用命令pscli --command=create_snapshot)；
#    3、客户端1移动test_file1到其他目录（还在/mnt/parastor/snap/下），修改test_file1文件；
#    4、客户端2移动test_file2到其他目录（在/mnt/parastor/snap/外），修改test_file2文件；
#    5、3个客户端进入/mnt/parastor/.snapshot目录浏览a1快照数据；
#    6、删除快照；
#    7、3个客户端查看是否有快照入口路径；
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  #/snap/snap_13_0_0_0

def case():
    # 创建两个子目录
    test_dir_1 = os.path.join(SNAP_TRUE_PATH, 'test_dir_1')
    cmd = 'mkdir %s' % test_dir_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    test_dir_2 = os.path.join(SNAP_TRUE_PATH, 'test_dir_2')
    cmd = 'mkdir %s' % test_dir_2
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 在test_dir1下创建一个子目录
    test_dir_1_1 = os.path.join(test_dir_1, 'test_dir_1_1')
    cmd = 'mkdir %s' % test_dir_1_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 创建文件
    test_file_1 = os.path.join(test_dir_1, 'test_file_1')
    cmd = 'touch %s' % test_file_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    test_file_2 = os.path.join(test_dir_1, 'test_file_2')
    cmd = 'touch %s' % test_file_2
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 2> 创建快照
    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_dir_1')
    rc, stdout = snap_common.create_snapshot(snap_name, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name)
        raise Exception('create_snapshot %s failed!!!' % snap_name)

    # 3,4> 移动文件
    cmd = 'mv %s %s' % (test_file_1, test_dir_1_1)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    cmd = 'mv %s %s' % (test_file_2, test_dir_2)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 5> 检查文件是否存在
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name)
    snap_file_path_1 = os.path.join(snap_path, 'test_file_1')
    snap_file_path_2 = os.path.join(snap_path, 'test_file_2')
    cmd1 = 'ls %s' % snap_file_path_1
    cmd2 = 'ls %s' % snap_file_path_2
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd1)
    if rc != 0:
        log.error('%s is not exist!!!' % (snap_file_path_1))
        raise Exception('%s is not exist!!!' % (snap_file_path_1))
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd2)
    if rc != 0:
        log.error('%s is not exist!!!' % (snap_file_path_2))
        raise Exception('%s is not exist!!!' % (snap_file_path_2))

    # 6> 手动删除快照
    rc, stdout = snap_common.delete_snapshot_by_name(snap_name)
    if 0 != rc:
        log.error('%s delete failed!!!' % (snap_name))
        raise Exception('%s delete failed!!!' % (snap_name))

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