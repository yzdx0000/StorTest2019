# -*-coding:utf-8 -*
import os
import time
import random

import utils_path
import common
import log
import tool_use
import get_config
import prepare_clean

#################################################################
#
# Author: chenjy1
# Date: 2017-07-24
# @summary：
#    虚拟机6节点集群，运行vdbench脚本创建文件过程中，客户端出现1800s超时crash
# @steps:
#    1.6节点集群，4个客户端，
#    2.每个客户端120线程，4k小文件，总数量级60G数据
#    3.创建文件过程中大约60%左右，4个客户端出现1800s超时crash
#
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
VDBENCH_PATH = os.path.join(prepare_clean.DEFECT_PATH, FILE_NAME)


def vdbench_run(anchor_path, journal_path, *args):
    """
    :author :             chenjy1
    :date:                2018.07.30
    :description:         跑vdbench总量60G文件
    :param anchor_path:  vdbench anchor目录
    :param journal_path: journal目录
    :param args:         跑vdbench节点IP
    :return:
    """
    vdb = tool_use.Vdbenchrun(size='4k', depth=1, width=1, files=5800, threads=120)
    rc = vdb.run_create(anchor_path, journal_path, *args)
    return rc


def case():
    log.info("case begin")
    count = 1
    """获取客户端节点"""
    ip_list = get_config.get_allclient_ip()

    for i in range(count):
        rc = vdbench_run(VDBENCH_PATH, VDBENCH_PATH, ip_list[0])
        common.judge_rc(rc, 0, "case failed")

    log.info("case succeed!")
    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)
