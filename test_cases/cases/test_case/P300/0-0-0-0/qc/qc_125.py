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
import tool_use


####################################################################################
#
# Author: chenjy1
# Date： 2018-07-12
# @summary：
#    物理机3节点集群，iozone集群
# @steps:
#    1、物理机3节点集群，运行iozone集群测试
#    2、iozone：90线程文件20G大小
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字


def case():
    log.info("case begin")
    path = os.path.join(prepare_clean.DEFECT_PATH, FILE_NAME)
    """iozone_run(配置文件中节点个数, 配置文件中每个节点行数,
    跑iozone路径,线程数,文件大小,数据传输大小)"""
    log.info("1> 物理机3节点集群，运行iozone集群测试，90线程文件20G大小")
    tool_use.iozone_run(2, 2, path, 2, '10m', '64k')
    #tool_use.iozone_run(3, 35, path, 90, '20G', '4M')

    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)