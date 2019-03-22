#-*-coding:utf-8 -*
from multiprocessing import Process
import os
import time

import utils_path
import common
import snap_common
import log
import shell
import get_config
import prepare_clean
import json
import random

####################################################################################
#
# Author: liyao
# date 2018-07-13
# @summary：
#    测试配额文件数硬阈值设置与实际获取值是否相符
# @steps:
#    1、部署3节点集群；
#    2、执行get_master获取oJmgs的主节点，并检查节点信息是否正确；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]        # 本脚本名字
DEFECT_PATH = get_config.get_one_defect_test_path()                # "/mnt/volume1/defect_case"
DEFECT_TRUE_PATH = os.path.join(DEFECT_PATH, FILE_NAME)            # "/mnt/volume1/defect_case/qc_689"
BASE_DEFECT_PATH = os.path.dirname(DEFECT_PATH)                    # "/mnt/volume1"
DEFECT_PATH_BASENAME = os.path.basename(DEFECT_PATH)               # "defect"
DEFECT_PATH_ABSPATH = os.path.abspath(DEFECT_PATH)                 # "/mnt/volume1/defect"
SNAPSHOT_PAHT = os.path.join(BASE_DEFECT_PATH, '.snapshot')      # "/mnt/volume1/.snapshot"
CREATE_SNAP_PATH = os.path.join(DEFECT_PATH_BASENAME, FILE_NAME)   # "/defect/qc_689"


def case():
    # 2> 执行get_master，并检查节点信息是否正确
    node = common.Node()
    sys_nodes_id = node.get_nodes_id()

    rc, stdout = common.get_master()
    stdout = common.json_loads(stdout)
    master_info = stdout['result']['node_id']

    # 判断节点信息是否正确
    if master_info not in sys_nodes_id:
        log.error('get_master failed !!!')
        raise Exception('get_master failed !!!')

    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
