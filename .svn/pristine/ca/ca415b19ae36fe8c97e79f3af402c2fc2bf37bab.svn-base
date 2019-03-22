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
#    创建单个目录快照后，修改目录权限，浏览快照内容。
#@steps:
#    1、部署3个客户端；
#    2、对目录/mnt/parastor/snap/(目录下存在文件test_file1，目录test_dir1)创建快照a1，(使用命令pscli --command=create_snapshot)；
#    3、客户端1修改test_file1的权限；
#    4、客户端2修改test_dir1的权限；
#    5、客户端3修改目录/mnt/parastor/snap/的权限；
#    6、3个客户端进入/mnt/parastor/.snapshot目录浏览a1快照数据；
#    7、删除快照；
#    8、3个客户端查看是否有快照入口路径；
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  #/snap/snap_13_0_0_0

def case():
    # 创建子文件
    test_file_1 = os.path.join(SNAP_TRUE_PATH, 'test_file_1')
    cmd = 'touch %s' % test_file_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 创建子目录
    test_dir_1 = os.path.join(SNAP_TRUE_PATH, 'test_dir_1')
    cmd = 'mkdir %s' % test_dir_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 2> 创建快照
    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name)
        raise Exception('create_snapshot %s failed!!!' % snap_name)

    # 3 4> 获取目录和文件权限
    rc, permission_0 = snap_common.get_file_permission(snap_common.CLIENT_IP_1, test_file_1)
    rc, permission_1 = snap_common.get_file_permission(snap_common.CLIENT_IP_1, test_dir_1)
    rc, permission_2 = snap_common.get_file_permission(snap_common.CLIENT_IP_1, SNAP_TRUE_PATH)

    # 5> 修改文件的权限
    cmd1 = 'chmod 777 %s' % test_file_1
    cmd2 = 'chmod 777 %s' % test_dir_1
    cmd3 = 'chmod 777 %s' % SNAP_TRUE_PATH
    common.run_command(snap_common.CLIENT_IP_1, cmd1)
    common.run_command(snap_common.CLIENT_IP_1, cmd2)
    common.run_command(snap_common.CLIENT_IP_1, cmd3)

    # 6> 获取快照文件的权限
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name)
    snap_file_path = os.path.join(snap_path, 'test_file_1')
    snap_dir_path = os.path.join(snap_path, 'test_dir_1')
    rc, snap_permission_0 = snap_common.get_file_permission(snap_common.CLIENT_IP_1, snap_file_path)
    rc, snap_permission_1 = snap_common.get_file_permission(snap_common.CLIENT_IP_1, snap_dir_path)
    rc, snap_permission_2 = snap_common.get_file_permission(snap_common.CLIENT_IP_1, snap_path)

    if permission_0 != snap_permission_0:
        log.error('%s %s permission is not right!!!' % (snap_common.CLIENT_IP_1, snap_file_path))
        raise Exception('%s %s permission is not right!!!' % (snap_common.CLIENT_IP_1, snap_file_path))
    if permission_1 != snap_permission_1:
        log.error('%s %s permission is not right!!!' % (snap_common.CLIENT_IP_1, snap_dir_path))
        raise Exception('%s %s permission is not right!!!' % (snap_common.CLIENT_IP_1, snap_dir_path))
    if permission_2 != snap_permission_2:
        log.error('%s %s permission is not right!!!' % (snap_common.CLIENT_IP_1, snap_path))
        raise Exception('%s %s permission is not right!!!' % (snap_common.CLIENT_IP_1, snap_path))

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