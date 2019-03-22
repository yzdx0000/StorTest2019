# -*-coding:utf-8 -*

import os

import utils_path
import common
import get_config
import log
import prepare_clean
import vdbench_common as vdbench

#
# Author: caizhenxing
# date 2018/9/29
# @summary：
#   多客户端操作同一文件（同步）
# @steps:
# @changelog：
#

# 当前脚本名称
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
VDBENCH_PATH = os.path.join(prepare_clean.MOUNT_PAHT, FILE_NAME)


def vdbench_run(anchor_path, journal_path, *args):
    """
    :author :             caizhenxing
    :date:                2018.09.29
    :description:         跑vdbench
    :param anchor_path:  vdbench anchor目录
    :param journal_path: journal目录
    :param args:         跑vdbench节点IP
    :return:
    """
    vdb = vdbench.Vdbenchrun(files=10,
                             openflags="o_sync",
                             threads=8,
                             fileio="(random,shared)",
                             forrdpct=50,
                             forseekpct=50,
                             elapsed=7200)

    rc = vdb.run_create(VDBENCH_PATH, VDBENCH_PATH, *args)
    common.judge_rc(rc, 0, "vdbench run_create failed!!!!!!")

    rc = vdb.run_write(VDBENCH_PATH, VDBENCH_PATH, *args)
    common.judge_rc(rc, 0, "vdbench run_write failed!!!!!!")

    rc = vdb.run_clean(VDBENCH_PATH, VDBENCH_PATH, *args)
    common.judge_rc(rc, 0, "vdbench run_clean failed!!!!!!")

    return


def case():
    log.info("case begin")
    """获取客户端节点"""
    client_ip_list = get_config.get_allclient_ip()
    log.info("1> vdbench读写")
    vdbench_run(VDBENCH_PATH, VDBENCH_PATH, client_ip_list)
    log.info("case succeed!")
    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
