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
#    创建单个目录快照后，快照内移动目录，浏览快照内容。
#@steps:
#    1、部署3个客户端；
#    2、对目录/mnt/parastor/snap/(目录下存在目录test_dir1，test_dir1下还有文件test_file1和test_file2)创建快照a1，(使用命令pscli --command=create_snapshot)；
#    3、客户端1移动test_dir1成/mnt/parastor/snap/test_dir2；
#    4、客户端2修改/mnt/parastor/snap/test_dir2/test_file1的内容；
#    5、客户端1再创建/mnt/parastor/snap/test_dir1/（目录下的内容和之前不一样）；
#    6、3个客户端进入/mnt/parastor/.snapshot目录浏览a1快照数据
#    7、删除快照；
#    8、3个客户端查看是否有快照入口路径；
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  #/snap/snap_13_0_0_0

def case():
    # 创建子目录
    test_dir_1 = os.path.join(SNAP_TRUE_PATH, 'test_dir_1')
    cmd = 'mkdir %s' % test_dir_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 创建子文件
    test_file_1 = os.path.join(test_dir_1, 'test_file_1')
    cmd = 'echo 111 > %s' % test_file_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    test_file_2 = os.path.join(test_dir_1, 'test_file_2')
    cmd = 'echo 222 > %s' % test_file_2
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    rc, file1_md5 = snap_common.get_file_md5(snap_common.CLIENT_IP_1, test_file_1)
    rc, file2_md5 = snap_common.get_file_md5(snap_common.CLIENT_IP_1, test_file_2)

    # 2> 创建快照
    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name)
        raise Exception('create_snapshot %s failed!!!' % snap_name)

    # 3> 修改目录名字
    test_dir_new_1 = os.path.join(SNAP_TRUE_PATH, 'test_dir_new_1')
    cmd = 'mv %s %s' % (test_dir_1, test_dir_new_1)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 4> 修改文件内容
    test_file_new_1 = os.path.join(test_dir_new_1, 'test_file_1')
    cmd = 'echo aaa > %s' % test_file_new_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 5> 重新创建test_dir_1目录
    cmd = 'mkdir %s' % test_dir_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 创建子文件
    cmd = 'echo aaa > %s' % test_file_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    cmd = 'echo bbb > %s' % test_file_2
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 6> 检查文件内容
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name)
    snap_test_file_1 = os.path.join(snap_path, 'test_dir_1', 'test_file_1')
    snap_test_file_2 = os.path.join(snap_path, 'test_dir_1', 'test_file_2')
    snap_common.check_snap_md5(file1_md5, snap_test_file_1)
    snap_common.check_snap_md5(file2_md5, snap_test_file_2)

    # 7> 手动删除快照
    rc, stdout = snap_common.delete_snapshot_by_name(snap_name)
    if 0 != rc:
        log.error('%s delete failed!!!' % (snap_name))
        raise Exception('%s delete failed!!!' % (snap_name))

    time.sleep(10)

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