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
#    对目录创建快照，删除目录下文件，创建一个同名文件，revert文件，观察是什么结果
#@steps:
#    1、部署3个客户端；
#    2、对目录/mnt/parastor/snap/创建快照a1（/mnt/parastor/snap/下有文件test_file1）；
#    3、删除文件test_file1，重新创建文件test_file1（内容和之前不一致）；
#    4、对快照a1进行revert，3个客户端观察/mnt/parastor/snap/下的内容；
#    5、删除快照；
#    6、3个客户端检查是否有快照入口路径；
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   #/snap/snap_13_0_0_0

def case():
    # 创建文件
    file_path1 = os.path.join(SNAP_TRUE_PATH, 'test_file1')
    test_str_1 = '1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111' \
                 '1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111'
    cmd = 'echo %s > %s' % (test_str_1, file_path1)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 获取文件的md5值
    rc, file_md5_1 = snap_common.get_file_md5(snap_common.CLIENT_IP_1, file_path1)
    if rc != 0:
        log.error('get %s md5 failed!!!' % file_path1)
        raise Exception('get %s md5 failed!!!' % file_path1)

    # 2> 创建快照
    snap_name1 = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name1, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name1)
        raise Exception('create_snapshot %s failed!!!' % snap_name1)

    # 3> 删除文件
    common.rm_exe(snap_common.CLIENT_IP_1,file_path1)

    # 创建同名文件
    test_str_2 = '2222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222' \
                 '2222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222'
    cmd = 'echo %s > %s' % (test_str_2, file_path1)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 4> 对快照进行revert
    snap_info = snap_common.get_snapshot_by_name(snap_name1)
    snap_id = snap_info['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id)
    if rc != 0:
        log.error("revert snapshot %s failed!!!" % snap_name1)
        raise Exception("revert snapshot %s failed!!!" % snap_name1)
    snap_common.check_revert_finished(snap_id)

    # 获取文件的md5值
    rc, file_md5_2 = snap_common.get_file_md5(snap_common.CLIENT_IP_1, file_path1)
    if rc != 0:
        log.error('get %s md5 failed!!!' % file_path1)
        raise Exception('get %s md5 failed!!!' % file_path1)

    if file_md5_1 != file_md5_2:
        log.error('%s before revert md5:%s, after revert md5:%s!!!' % (file_path1, file_md5_1, file_md5_2))
        raise Exception('%s before revert md5:%s, after revert md5:%s!!!' % (file_path1, file_md5_1, file_md5_2))

    # 5> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_path(path)
    if 0 != rc:
        log.error('%s delete snapshot failed!!!' % (path))
        raise Exception('%s delete snapshot failed!!!' % (path))

    time.sleep(10)

    # 6> 3个客户端检查快照路径入口是否存在
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name1)
    snap_common.check_snap_entry(snap_path)

    return

def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)
