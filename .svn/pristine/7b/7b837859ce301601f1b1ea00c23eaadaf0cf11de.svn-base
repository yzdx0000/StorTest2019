# -*-coding:utf-8 -*
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
# @summary：
#    创建单个文件快照后，修改文件名字，浏览快照内容
# @steps:
#    1、部署3个客户端；
#    2、对文件创建快照a1（文件有内容）；
#    3、客户端1修改文件名字；
#    4、3个客户端进入/mnt/parastor/.snapshot目录浏览a1快照数据；
#    5、客户端2修改文件权限；
#    6、3个客户端进入/mnt/parastor/.snapshot目录浏览a1快照数据；
#    7、删除快照a1；
#    8、3个客户端进入/mnt/parastor/.snapshot观察是否还有快照入口；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             # /mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  # /snap/snap_13_0_0_0


def case():
    # 创建文件
    file_path = os.path.join(SNAP_TRUE_PATH, 'test_file1')
    test_str_1 = '111111111111111111111111111111111111111111111111111' \
                 '1111111111111111111111111111111111111111111111111111' \
                 '1111111111111111111111111111111111111111111111111111' \
                 '111111111111111111111111111111111111111111111111111'
    cmd = 'echo %s > %s' % (test_str_1, file_path)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 获取文件的md5值
    rc, file_md5_1_0 = snap_common.get_file_md5(snap_common.CLIENT_IP_1, file_path)
    if rc != 0:
        log.error('get %s md5 failed!!!' % file_path)
        raise Exception('get %s md5 failed!!!' % file_path)

    # 修改文件权限
    cmd = 'chmod 555 %s' % file_path
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 获取文件的权限
    rc, file_permission0 = snap_common.get_file_permission(snap_common.CLIENT_IP_1, file_path)

    # 2> 创建快照
    snap_name1 = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_file1')
    rc, stdout = snap_common.create_snapshot(snap_name1, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name1)
        raise Exception('create_snapshot %s failed!!!' % snap_name1)

    # 3> 修改文件名字
    file_path2 = os.path.join(SNAP_TRUE_PATH, 'test_file2')
    cmd = 'mv %s %s' % (file_path, file_path2)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 4> 三个客户端浏览快照数据
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name1)
    snap_common.check_snap_md5(file_md5_1_0, snap_path)

    # 5> 修改文件权限
    cmd = 'chmod 777 %s' % file_path2
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 6> 三个客户端浏览快照数据
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name1)
    rc, file_permission1 = snap_common.get_file_permission(snap_common.CLIENT_IP_1, snap_path)
    if file_permission1 != file_permission0:
        log.error('%s %s is not right!!!' % (snap_common.CLIENT_IP_1, snap_path))
        raise Exception('%s %s is not right!!!' % (snap_common.CLIENT_IP_1, snap_path))
    rc, file_permission2 = snap_common.get_file_permission(snap_common.CLIENT_IP_2, snap_path)
    if file_permission2 != file_permission0:
        log.error('%s %s is not right!!!' % (snap_common.CLIENT_IP_2, snap_path))
        raise Exception('%s %s is not right!!!' % (snap_common.CLIENT_IP_2, snap_path))
    rc, file_permission3 = snap_common.get_file_permission(snap_common.CLIENT_IP_3, snap_path)
    if file_permission3 != file_permission0:
        log.error('%s %s is not right!!!' % (snap_common.CLIENT_IP_3, snap_path))
        raise Exception('%s %s is not right!!!' % (snap_common.CLIENT_IP_3, snap_path))

    # 7> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_path(path)
    if 0 != rc:
        log.error('%s delete failed!!!' % (path))
        raise Exception('%s delete failed!!!' % (path))

    time.sleep(10)

    # 8> 3个客户端检查快照路径入口是否存在
    snap_common.check_snap_entry(snap_path)


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
