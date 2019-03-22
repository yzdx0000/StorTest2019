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
#    创建单个目录快照后，修改目录下内容，浏览快照内容。
#@steps:
#    1、部署3个客户端；
#    2、对目录/mnt/parastor/snap/(目录下存在文件test_file1和test_file2，目录test_dir1)创建快照a1，(使用命令pscli --command=create_snapshot)；
#    3、客户端1在目录/mnt/parastor/snap/下创建文件test_file3；
#    4、客户端2在目录/mnt/parastor/snap/下删除文件test_file1；
#    5、客户端3在目录/mnt/parastor/snap/下修改文件test_file2内容；
#    6、客户端1在目录/mnt/parastor/snap/下删除目录test_dir1；
#    7、客户端2在目录/mnt/parastor/snap/下添加目录test_dir2；
#    8、3个客户端进入/mnt/parastor/.snapshot目录浏览a1快照数据；
#    9、删除快照；
#    10、3个客户端查看是否有快照入口路径；
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  #/snap/snap_13_0_0_0

def case():
    # 快照目录下创建文件test_file1
    file1_name = os.path.join(SNAP_TRUE_PATH, 'test_file1')
    cmd1 = 'touch %s' % file1_name
    common.run_command(snap_common.CLIENT_IP_1, cmd1)

    # 快照目录下创建文件test_file2
    str_check = '11111'
    file2_name = os.path.join(SNAP_TRUE_PATH, 'test_file2')
    cmd2 = 'echo %s > %s' % (str_check, file2_name)
    common.run_command(snap_common.CLIENT_IP_1, cmd2)

    # 快照目录下创建目录test_dir1
    dir1_name = os.path.join(SNAP_TRUE_PATH, 'test_dir1')
    cmd3 = 'mkdir %s' % dir1_name
    common.run_command(snap_common.CLIENT_IP_1, cmd3)

    # 2> 创建快照
    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name)
        raise Exception('create_snapshot %s failed!!!' % snap_name)

    # 3> 客户端1创建文件test_file3
    file3_name = os.path.join(SNAP_TRUE_PATH, 'test_file3')
    cmd4 = 'touch %s' % file3_name
    common.run_command(snap_common.CLIENT_IP_1, cmd4)

    # 4> 客户端2删除文件test_file1
    common.rm_exe(snap_common.CLIENT_IP_2,file1_name)

    # 5> 客户端3修改文件test_file2内容
    cmd6 = 'echo 22222 > %s' % file2_name
    common.run_command(snap_common.CLIENT_IP_3, cmd6)

    # 6> 客户端1删除目录test_dir1
    common.rm_exe(snap_common.CLIENT_IP_1,dir1_name)

    # 7> 客户端2添加目录test_dir2；
    dir2_name = os.path.join(SNAP_TRUE_PATH, 'test_dir2')
    cmd8 = 'mkdir %s' % dir2_name
    common.run_command(snap_common.CLIENT_IP_2, cmd8)

    # 8> 3个客户端到快照路径检查test_file1是否存在
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

    # 3个客户端到快照路径检查test_file2的内容是否正确
    snap_test_file2 = os.path.join(snap_path, 'test_file2')
    check_cmd2 = 'cat %s' % snap_test_file2
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, check_cmd2)
    if stdout.strip() != str_check:
        log.error('%s %s is not right!!!' % (snap_common.CLIENT_IP_1, snap_test_file2))
        raise Exception('%s %s is not right!!!' % (snap_common.CLIENT_IP_1, snap_test_file2))
    rc, stdout = common.run_command(snap_common.CLIENT_IP_2, check_cmd2)
    if stdout.strip() != str_check:
        log.error('%s %s is not right!!!' % (snap_common.CLIENT_IP_2, snap_test_file2))
        raise Exception('%s %s is not right!!!' % (snap_common.CLIENT_IP_2, snap_test_file2))
    rc, stdout = common.run_command(snap_common.CLIENT_IP_3, check_cmd2)
    if stdout.strip() != str_check:
        log.error('%s %s is not right!!!' % (snap_common.CLIENT_IP_3, snap_test_file2))
        raise Exception('%s %s is not right!!!' % (snap_common.CLIENT_IP_3, snap_test_file2))

    # 3个客户端到快照路径检查test_dir1是否存在
    snap_test_dir1 = os.path.join(snap_path, 'test_dir1')
    check_cmd3 = 'ls %s' % snap_test_dir1
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, check_cmd3)
    if rc != 0:
        log.error('%s %s is not exist!!!' % (snap_common.CLIENT_IP_1, snap_test_dir1))
        raise Exception('%s %s is not exist!!!' % (snap_common.CLIENT_IP_1, snap_test_dir1))
    rc, stdout = common.run_command(snap_common.CLIENT_IP_2, check_cmd3)
    if rc != 0:
        log.error('%s %s is not exist!!!' % (snap_common.CLIENT_IP_2, snap_test_dir1))
        raise Exception('%s %s is not exist!!!' % (snap_common.CLIENT_IP_2, snap_test_dir1))
    rc, stdout = common.run_command(snap_common.CLIENT_IP_3, check_cmd3)
    if rc != 0:
        log.error('%s %s is not exist!!!' % (snap_common.CLIENT_IP_3, snap_test_dir1))
        raise Exception('%s %s is not exist!!!' % (snap_common.CLIENT_IP_3, snap_test_dir1))

    # 3个客户端到快照路径检查test_file3是否存在
    snap_test_file3 = os.path.join(snap_path, 'test_file3')
    check_cmd4 = 'ls %s' % snap_test_file3
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, check_cmd4)
    if rc == 0:
        log.error('%s %s is exist!!!' % (snap_common.CLIENT_IP_1, snap_test_file3))
        raise Exception('%s %s is exist!!!' % (snap_common.CLIENT_IP_1, snap_test_file3))
    rc, stdout = common.run_command(snap_common.CLIENT_IP_2, check_cmd4)
    if rc == 0:
        log.error('%s %s is exist!!!' % (snap_common.CLIENT_IP_2, snap_test_file3))
        raise Exception('%s %s is exist!!!' % (snap_common.CLIENT_IP_2, snap_test_file3))
    rc, stdout = common.run_command(snap_common.CLIENT_IP_3, check_cmd4)
    if rc == 0:
        log.error('%s %s is exist!!!' % (snap_common.CLIENT_IP_3, snap_test_file3))
        raise Exception('%s %s is exist!!!' % (snap_common.CLIENT_IP_3, snap_test_file3))

    # 3个客户端到快照路径检查test_dir2是否存在
    snap_test_dir2 = os.path.join(snap_path, 'test_dir2')
    check_cmd5 = 'ls %s' % snap_test_dir2
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, check_cmd5)
    if rc == 0:
        log.error('%s %s is exist!!!' % (snap_common.CLIENT_IP_1, snap_test_dir2))
        raise Exception('%s %s is exist!!!' % (snap_common.CLIENT_IP_1, snap_test_dir2))
    rc, stdout = common.run_command(snap_common.CLIENT_IP_2, check_cmd5)
    if rc == 0:
        log.error('%s %s is exist!!!' % (snap_common.CLIENT_IP_2, snap_test_dir2))
        raise Exception('%s %s is exist!!!' % (snap_common.CLIENT_IP_2, snap_test_dir2))
    rc, stdout = common.run_command(snap_common.CLIENT_IP_3, check_cmd5)
    if rc == 0:
        log.error('%s %s is exist!!!' % (snap_common.CLIENT_IP_3, snap_test_dir2))
        raise Exception('%s %s is exist!!!' % (snap_common.CLIENT_IP_3, snap_test_dir2))

    # 9> 手动删除快照
    rc, stdout = snap_common.delete_snapshot_by_name(snap_name)
    if 0 != rc:
        log.error('%s delete failed!!!' % (snap_name))
        raise Exception('%s delete failed!!!' % (snap_name))

    time.sleep(10)

    # 10> 3个客户端检查快照路径入口是否存在
    snap_common.check_snap_entry(snap_path)

    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)
