# -*-coding:utf-8 -*
import os
import time

import utils_path
import common
import snap_common
import log
import shell
import get_config
import prepare_clean

####################################################################################
#
# Author: baorb
# date 2018-01-19
# @summary：
#    文件快照的批量删除。
# @steps:
#    1、对10个文件创建100个快照(每个文件10个快照，使用命令pscli --command=create_snapshot)；
#    2、查询快照(使用pscli --command=get_snapshot)；
#    3、批量删除快照(pscli --command=delete_snapshot)；
#    4、查询快照(使用pscli --command=get_snapshot)；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             # /mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  # /snap/snap_13_0_0_0


def case():
    # 1> 创建10个文件
    snap_name_lst = []
    for i in range(10):
        snap_true_path = os.path.join(SNAP_TRUE_PATH, 'test_file_%d' % i)
        snap_create_path = os.path.join(CREATE_SNAP_PATH, 'test_file_%d' % i)
        cmd = 'touch %s' % snap_true_path
        common.run_command(snap_common.CLIENT_IP_1, cmd)
        path = snap_common.VOLUME_NAME + ':/' + snap_create_path
        # 每个目录创建10个快照
        for j in range(10):
            snap_name = FILE_NAME + '_%d_%d' % (i, j)
            snap_name_lst.append(snap_name)
            rc, stdout = snap_common.create_snapshot(snap_name, path)
            if 0 != rc:
                log.error('create_snapshot %s failed!!!' % snap_name)
                raise Exception('create_snapshot %s failed!!!' % snap_name)

    # 2> 查询快照是否都存在
    for snap_name in snap_name_lst:
        snapshot1_info = snap_common.get_snapshot_by_name(snap_name)
        if -1 == snapshot1_info:
            log.error('snap %s is not exist!!!' % snap_name)
            raise Exception('snap %s is not exist!!!' % snap_name)

    # 3> 批量删除快照
    rc, stdout = snap_common.delete_snapshot_by_name(FILE_NAME)
    if 0 != rc:
        log.error('delete_snapshot %s failed!!!' % FILE_NAME)
        raise Exception('delete_snapshot %s failed!!!' % FILE_NAME)
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)