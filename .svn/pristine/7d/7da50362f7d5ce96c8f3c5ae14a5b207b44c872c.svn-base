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
#    对多个文件创建多个快照，每个文件做不同的操作
#@steps:
#    1、部署3个客户端；
#    2、对6个文件分别创建快照a1..6（文件有内容）；
#    3、客户端1修改第一个文件的内容；
#    4、客户端2使用truncate修改第二个文件的内容；
#    5、客户端3修改第三个文件的权限；
#    6、客户端1修改第四个文件的名字；
#    7、客户端2 move第五个文件到其他目录；
#    8、客户端3删除第六个文件；
#    9、3个客户端分别查看快照a1..6的内容；
#    10、删除所有快照；
#    11、3个客户端查看是否还有快照入口；
#
#@changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  #/snap/snap_13_0_0_0

def case():
    # 创建文件
    file_path1 = os.path.join(SNAP_TRUE_PATH, 'test_file1')
    file_path2 = os.path.join(SNAP_TRUE_PATH, 'test_file2')
    file_path3 = os.path.join(SNAP_TRUE_PATH, 'test_file3')
    file_path4 = os.path.join(SNAP_TRUE_PATH, 'test_file4')
    file_path5 = os.path.join(SNAP_TRUE_PATH, 'test_file5')
    file_path6 = os.path.join(SNAP_TRUE_PATH, 'test_file6')
    test_str_1 = '1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111' \
                 '1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111'
    cmd1 = 'echo %s > %s' % (test_str_1, file_path1)
    cmd2 = 'echo %s > %s' % (test_str_1, file_path2)
    cmd3 = 'echo %s > %s' % (test_str_1, file_path3)
    cmd4 = 'echo %s > %s' % (test_str_1, file_path4)
    cmd5 = 'echo %s > %s' % (test_str_1, file_path5)
    cmd6 = 'echo %s > %s' % (test_str_1, file_path6)
    common.run_command(snap_common.CLIENT_IP_1, cmd1)
    common.run_command(snap_common.CLIENT_IP_1, cmd2)
    common.run_command(snap_common.CLIENT_IP_1, cmd3)
    common.run_command(snap_common.CLIENT_IP_1, cmd4)
    common.run_command(snap_common.CLIENT_IP_1, cmd5)
    common.run_command(snap_common.CLIENT_IP_1, cmd6)

    # 2> 创建快照
    path1 = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_file1')
    path2 = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_file2')
    path3 = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_file3')
    path4 = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_file4')
    path5 = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_file5')
    path6 = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_file6')
    name1 = FILE_NAME + '_snapshot1'
    name2 = FILE_NAME + '_snapshot2'
    name3 = FILE_NAME + '_snapshot3'
    name4 = FILE_NAME + '_snapshot4'
    name5 = FILE_NAME + '_snapshot5'
    name6 = FILE_NAME + '_snapshot6'
    snap_common.create_snapshot(name1, path1)
    snap_common.create_snapshot(name2, path2)
    snap_common.create_snapshot(name3, path3)
    snap_common.create_snapshot(name4, path4)
    snap_common.create_snapshot(name5, path5)
    snap_common.create_snapshot(name6, path6)

    # 3> 修改文件
    rc, file_md5_1_0 = snap_common.get_file_md5(snap_common.CLIENT_IP_1, file_path1)
    test_str_2 = '2222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222' \
                 '2222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222'
    cmd = 'echo %s > %s' % (test_str_2, file_path1)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 4> 使用truncate修改文件
    rc, file_md5_2_0 = snap_common.get_file_md5(snap_common.CLIENT_IP_1, file_path2)
    cmd = 'truncate %s -s 10' % file_path2
    common.run_command(snap_common.CLIENT_IP_2, cmd)

    # 5> 修改文件权限
    rc, file_permission_0 = snap_common.get_file_permission(snap_common.CLIENT_IP_1, file_path3)
    cmd = 'chmod 777 %s' % file_path3
    common.run_command(snap_common.CLIENT_IP_3, cmd)

    # 6> 修改文件名字
    rc, file_md5_4_0 = snap_common.get_file_md5(snap_common.CLIENT_IP_1, file_path4)
    file_path_new_4 = os.path.join(SNAP_TRUE_PATH, 'test_file_new_4')
    cmd = 'mv %s %s' % (file_path4, file_path_new_4)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 7> 移动文件到其他路径
    rc, file_md5_5_0 = snap_common.get_file_md5(snap_common.CLIENT_IP_1, file_path5)
    file_path_new_5 = os.path.join(snap_common.SNAP_PATH, 'test_file5')
    cmd = 'mv %s %s' % (file_path5, file_path_new_5)
    common.run_command(snap_common.CLIENT_IP_2, cmd)

    # 8> 删除文件
    rc, file_md5_6_0 = snap_common.get_file_md5(snap_common.CLIENT_IP_1, file_path6)
    common.rm_exe(snap_common.CLIENT_IP_3,file_path6)

    # 9> 校验快照数据
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, name1)
    snap_common.check_snap_md5(file_md5_1_0, snap_path)
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, name2)
    snap_common.check_snap_md5(file_md5_2_0, snap_path)
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, name4)
    snap_common.check_snap_md5(file_md5_4_0, snap_path)
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, name5)
    snap_common.check_snap_md5(file_md5_5_0, snap_path)
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, name6)
    snap_common.check_snap_md5(file_md5_6_0, snap_path)

    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, name3)
    rc, file_permission_1 = snap_common.get_file_permission(snap_common.CLIENT_IP_1, snap_path)
    if file_permission_1 != file_permission_0:
        log.error('%s %s permission is not right!!!' % (snap_common.CLIENT_IP_1, snap_path))
        raise Exception('%s %s permission is not right!!!' % (snap_common.CLIENT_IP_1, snap_path))
    rc, file_permission_2 = snap_common.get_file_permission(snap_common.CLIENT_IP_2, snap_path)
    if file_permission_2 != file_permission_0:
        log.error('%s %s permission is not right!!!' % (snap_common.CLIENT_IP_2, snap_path))
        raise Exception('%s %s permission is not right!!!' % (snap_common.CLIENT_IP_2, snap_path))
    rc, file_permission_2 = snap_common.get_file_permission(snap_common.CLIENT_IP_3, snap_path)
    if file_permission_2 != file_permission_0:
        log.error('%s %s permission is not right!!!' % (snap_common.CLIENT_IP_3, snap_path))
        raise Exception('%s %s permission is not right!!!' % (snap_common.CLIENT_IP_3, snap_path))

    # 10> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_name(FILE_NAME)
    if 0 != rc:
        log.error('%s delete failed!!!' % (FILE_NAME))
        raise Exception('%s delete failed!!!' % (FILE_NAME))

    time.sleep(10)

    # 11> 3个客户端检查快照路径入口是否存在
    snap_common.check_snap_entry(snap_path)

    return

def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)
