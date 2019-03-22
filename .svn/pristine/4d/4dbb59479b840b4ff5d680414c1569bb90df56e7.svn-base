# -*-coding:utf-8 -*
# !/usr/bin/python

import os
import time
import commands

import utils_path
import common
import snap_common
import log
import prepare_clean
import tool_use

# =================================================================================
#  latest update:2018-05-07                                                     =
#  author:wangguanglin                                                           =
# =================================================================================
# 2018-05-07:
# 修改者：wangguanglin
# @summary：
#    根目录创建快照，对快照revert，观察数据正确性
# @steps:
#   1、部署3个客户端；
#   2、客户端1对目录/mnt/wangguanglin/snap/snap_13_0_5_33执行vdbench 00脚本（创建文件）；
#   3、对目录/mnt/wangguanglin/snap/snap_13_0_5_33创建快照a1；
#   4、客户端2对目录/mnt/wangguanglin/snap/snap_13_0_5_33使用vdbench修改文件内容；
#   5、对快照a1进行revert；
#   6、客户端2在目录/mnt/wangguanglin/snap/snap_13_0_5_33下执行vdbench 01脚本（校验数据一致性）；
#   7、删除快照；
#   8、3个客户端下观察是否有快照路径入口；
#
#
# changelog:
######################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             #/mnt/wangguanglin/snap/snap_13_0_5_33
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  #/snap/snap_13_0_5_33


def case():
    """创建子目录/mnt/wangguanglin/snap/snap_13_0_5_33/vdbench"""
    test_dir = os.path.join(SNAP_TRUE_PATH, 'vdbench')
    cmd = 'mkdir %s' % test_dir
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    """客户端1对目录/mnt/wangguanglin/snap/snap_13_0_5_33执行vdbench 00脚本"""
    tool_use.vdbench_run(test_dir, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, run_create=True)

    """对目录/mnt/wangguanglin/snap/snap_13_0_5_33创建快照"""
    snap_name1 = FILE_NAME + '_snapshot'
    path1 = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'vdbench')
    rc, stdout = snap_common.create_snapshot(snap_name1, path1)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name1)
        raise Exception('create_snapshot %s failed!!!' % snap_name1)

    """客户端2对目录/mnt/wangguanglin/snap/snap_13_0_5_33执行vdbench 修改文件内容"""
    tool_use.vdbench_run(test_dir, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, run_write=True)

    """对快照进行revert"""
    snap_info1 = snap_common.get_snapshot_by_name(snap_name1)
    snap_id1 = snap_info1['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id1)
    if 0 != rc:
        log.error('revert_snapshot %s failed!!!' % snap_name1)
        raise Exception('revert_snapshot %s failed!!!' % snap_name1)
    snap_common.check_revert_finished(snap_id1)

    """客户端2对目录/mnt/wangguanglin/snap/snap_13_0_5_33执行vdbench 01 脚本(校验数据一致性)"""
    tool_use.vdbench_run(test_dir, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, run_check=True)

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