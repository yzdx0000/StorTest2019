#-*-coding:utf-8 -*
#!/usr/bin/python

import os
import time
import commands
import json

import utils_path
import common
import snap_common
import log
import prepare_clean

#=================================================================================
#  latest update:2018-05-08                                                     =
#  author:wangguanglin                                                           =
#=================================================================================
# 2018-05-11:
# 修改者：wangguanglin
#@summary：
#  大量空文件revert
#@steps:
#   1、部署3个客户端；
#   2、客户端1在目录/mnt/wangguanglin/snap/snap_13_0_5_35/执行mdtest，深度为4，宽度为10，每个节点100个文件；；
#   3、对目录/mnt/wangguanglin/snap/snap_13_0_5_35/创建快照a1；
#   4、删除所有创建的文件；
#   5、对快照a1进行revert（观察revert的时间）；
#   6、删除快照；
#   7、3个客户端下观察是否有快照路径入口；
#
#changelog:
######################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             #/mnt/wangguanglin/snap/snap_13_0_5_35
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  #/snap/snap_13_0_5_35


def case():
    """创建子目录/mnt/wangguanglin/snap/snap_13_0_5_35/dir"""
    test_dir = os.path.join(SNAP_TRUE_PATH, 'dir')
    cmd = 'mkdir %s' % test_dir
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    """
    客户端1在目录/mnt/wangguanglin/snap/snap_13_0_5_35/dir执行mdtest，
    深度为2，宽度为3，每个节点100个文件
    """
    cmd='mdtest -z 2 -b 3 -I 100 -C -d %s' % test_dir
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    """对目录/mnt/wangguanglin/snap/snap_13_0_5_35创建快照1"""
    snap_name1 = FILE_NAME + '_snapshot1'
    path1 = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name1, path1)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name1)
        raise Exception('create_snapshot %s failed!!!' % snap_name1)

    """删除所有创建的文件"""

    #cmd='rm -rf %s '% SNAP_TRUE_PATH
    #common.run_command(snap_common.CLIENT_IP_1, cmd)
    common.rm_exe(snap_common.CLIENT_IP_1, test_dir)

    """对快照1进行revert"""
    snap_info1 = snap_common.get_snapshot_by_name(snap_name1)
    snap_id1 = snap_info1['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id1)
    if 0 != rc:
        log.error('revert_snapshot %s failed!!!' % snap_name1)
        raise Exception('revert_snapshot %s failed!!!' % snap_name1)
    snap_common.check_revert_finished(snap_id1)

    """ 删除快照"""
    rc, stdout = snap_common.delete_snapshot_by_name(FILE_NAME)
    if 0 != rc:
        log.error('%s delete failed!!!' % (FILE_NAME))
        raise Exception('%s delete failed!!!' % (FILE_NAME))

    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
