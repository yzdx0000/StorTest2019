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
#    重建重名的目录。
#@steps:
#    1、部署3个客户端；
#    2、对目录/mnt/parastor/snap/(目录下存在文件test_file1，目录test_dir1)创建快照a1，(使用命令pscli --command=create_snapshot)；
#    3、客户端1删除test_dir1；
#    4、客户端2添加test_dir1（内容和之前不同）到目录/mnt/parastor/snap/下；
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
    # 创建目录和文件
    test_dir_1 = os.path.join(SNAP_TRUE_PATH, 'test_dir_1')
    cmd = 'mkdir %s' % test_dir_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    test_file_1 = os.path.join(SNAP_TRUE_PATH, 'test_file_1')
    cmd = 'echo 111 > %s' % test_file_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    test_file_2 = os.path.join(test_dir_1, 'test_file_2')
    cmd = 'touch %s' % test_file_2
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    rc, file1_md5 = snap_common.get_file_md5(snap_common.CLIENT_IP_1, test_file_1)

    # 2> 创建快照
    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name)
        raise Exception('create_snapshot %s failed!!!' % snap_name)

    # 3> 删除目录和文件
    common.rm_exe(snap_common.CLIENT_IP_1,SNAP_TRUE_PATH)

    # 4> 重新创建目录和文件
    cmd = 'mkdir %s' % test_dir_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    cmd = 'echo 222 > %s' % test_file_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    test_file_3 = os.path.join(test_dir_1, 'test_file_3')
    cmd = 'touch %s' % test_file_3
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 5> 检查快照内容
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name)
    snap_file_1 = os.path.join(snap_path, 'test_file_1')
    snap_file_2 = os.path.join(snap_path, 'test_dir_1', 'test_file_2')

    snap_common.check_snap_md5(file1_md5, snap_file_1)
    cmd = 'ls %s' % snap_file_2
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if rc != 0:
        log.error('%s is not exist!!!' % (snap_file_2))
        raise Exception('%s is not exist!!!' % (snap_file_2))

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