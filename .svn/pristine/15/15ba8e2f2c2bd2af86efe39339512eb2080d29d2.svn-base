# -*-coding:utf-8 -*
from multiprocessing import Process
import os

import utils_path
import common
import snap_common
import log
import tool_use
import prepare_clean

####################################################################################
#
# Author: liyao
# date 2018-05-03
# @summary：
#    目录修改时对其创建快照
# @steps:
#    1、部署3个客户端；
#    2、在目录/mnt/parastor/snap/下执行vdbench 00脚本（创建文件）；
#    3、在目录/mnt/parastor/snap/下执行vdbench 01（修改文件数据），在修改的过程中创建快照；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              # /mnt/liyao/snap/snap_13_0_1_9
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   # /snap/snap_13_0_1_9


def snapshot_create(snap_name, path):
    rc, stdout = snap_common.create_snapshot(snap_name, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name)
        raise Exception('create_snapshot %s failed!!!' % snap_name)
    return


def case():
    # 2> 运行00脚本
    tool_use.vdbench_run(SNAP_TRUE_PATH, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, run_create=True)

    # 3> 对目录创建快照并行修改文件
    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH

    p1 = Process(target=tool_use.vdbench_run,
                 args=(SNAP_TRUE_PATH, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2),
                 kwargs={'run_write': True})
    p2 = Process(target=snapshot_create, args=(snap_name, path))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    if p1.exitcode != 0:
        raise Exception("vdbench failed!!!!!!")
    if p2.exitcode != 0:
        raise Exception("snapshot %s is not created!!!!!!" % snap_name)
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
