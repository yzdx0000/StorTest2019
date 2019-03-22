# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time

import utils_path
import common
import snap_common
import log
import tool_use
import get_config
import prepare_clean

####################################################################################
#
# Author: liyao
# date 2018-07-11
# @summary：
#    vdbench创建数据过程中，对数据读写目录创建快照
# @steps:
#    1、部署3节点集群；
#    2、使用vdbench在目录/mnt/volume1/defect/P300-282/下创建数据；
#    3、数据读写的同时对文件创建快照；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]        # 本脚本名字
DEFECT_PATH = get_config.get_one_defect_test_path()                # "/mnt/volume1/defect_case"
DEFECT_TRUE_PATH = os.path.join(DEFECT_PATH, FILE_NAME)            # "/mnt/volume1/defect_case/P300-282"
DEFECT_PATH_BASENAME = os.path.basename(DEFECT_PATH)               # "defect"
CREATE_SNAP_PATH = os.path.join(DEFECT_PATH_BASENAME, FILE_NAME)   # "/defect/P300-282"


def cre_snapshot(snap_name, path):
    rc, stdout = snap_common.create_snapshot(name=snap_name, path=path, expire_time=0)
    common.judge_rc(rc, 0, '%s creating failed !!!' % snap_name)
    return


def case():
    # 2&3> 使用vdbench在/mnt/volume1/defect/P300-282/下创建数据
    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH

    p1 = Process(target=tool_use.vdbench_run, args=(DEFECT_TRUE_PATH, snap_common.CLIENT_IP_1),
                 kwargs={'run_create': True})
    p2 = Process(target=cre_snapshot, args=(snap_name, path))

    p1.start()
    log.info('waiting for 5s')
    time.sleep(5)
    p2.start()

    p1.join()
    p2.join()

    if p2.exitcode != 0:
        raise Exception("snapshot %s is not created!!!!!!" % snap_name)
    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    snap_common.delete_snapshot_by_name(FILE_NAME)
    case()
    snap_common.delete_snapshot_by_name(FILE_NAME)
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
