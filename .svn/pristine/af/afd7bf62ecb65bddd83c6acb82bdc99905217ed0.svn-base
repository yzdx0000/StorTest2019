#-*-coding:utf-8 -*
import os
import time
import json

import utils_path
import common
import snap_common
import log
import prepare_clean

####################################################################################
#
# Author: baorb
# date 2018-04-25
#@summary：
#    对一个快照进行多次revert
#@steps:
#    1、在/mnt/parastor/snap下使用truncate创建文件test1；
#    2、对文件test1创建快照a1；
#    3、追加内容到test1中；
#    4、检查/mnt/parastor/.snapshot/a1的内容；
#    5、对快照进行revert；
#    6、检查test1的内容；
#    7、删除快照；
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   #/snap/snap_13_0_0_0

def case():
    """1> 使用truncate创建文件"""
    file_test = os.path.join(SNAP_TRUE_PATH, 'test_file')
    cmd = 'truncate %s -s 8k' % file_test
    common.run_command(snap_common.CLIENT_IP_1, cmd)\

    """2> 对文件创建快照"""
    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_file')
    rc, stdout = snap_common.create_snapshot(snap_name, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name)
        raise Exception('create_snapshot %s failed!!!' % snap_name)

    """获取文件的md5值"""
    rc, md5_source = snap_common.get_file_md5(snap_common.CLIENT_IP_1, file_test)

    """3> 修改文件内容"""
    cmd = 'echo 111 >> %s' % file_test
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    """4> 检查快照文件的md5值"""
    snap_file = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name)
    rc, md5_snap = snap_common.get_file_md5(snap_common.CLIENT_IP_1, snap_file)

    if md5_source != md5_snap:
        log.error("md5_source md5: %s, md5_snap md5: %s, is not right!!!" % (md5_source, md5_snap))
        raise Exception("%s md5 is not right!!!" % snap_file)

    """5> 对快照进行revert"""
    snap_info = snap_common.get_snapshot_by_name(snap_name)
    snap_id = snap_info['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id)
    if rc != 0:
        log.error("revert snapshot %s failed!!!" % snap_name)
        raise Exception("revert snapshot %s failed!!!" % snap_name)
    snap_common.check_revert_finished(snap_id)

    """6> 获取文件的md5值"""
    rc, md5_new = snap_common.get_file_md5(snap_common.CLIENT_IP_1, file_test)

    if md5_source != md5_new:
        log.error("%s md5 is not right!!!" % file_test)
        raise Exception("%s md5 is not right!!!" % file_test)

    """7> 删除快照"""
    rc, stdout = snap_common.delete_snapshot_by_path(path)
    if 0 != rc:
        log.error('%s delete snapshot failed!!!' % (path))
        raise Exception('%s delete snapshot failed!!!' % (path))

    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)