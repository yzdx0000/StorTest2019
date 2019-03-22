# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import json

import utils_path
import common
import log
import get_config
import prepare_clean
import upgrade_common
import tool_use
import online_upgrade

####################################################################################
#
# author 刘俊鑫
# date 2018-07-27
# @summary：
#   执行在线升级操作
# @steps:
#   step1: vdvench创建文件
#   step2：执行在线升级
#   step3：vdbench读写、检查循环
#
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
DEFECT_PATH = get_config.get_one_defect_test_path()                         # DEFECT_PATH = /mnt/volume1/defect_case
DEFECT_TRUE_PATH = os.path.join(DEFECT_PATH, FILE_NAME)                     # DEFECT_TRUE_PATH= volume:/defect_case/p300
VDBENCH_WRITE_PATH = os.path.join(DEFECT_TRUE_PATH, 'write')                # vdbench读写路径
VDBENCH_JN_PATH = os.path.join(DEFECT_TRUE_PATH, 'jn')                      # vdbench校验文件路径
client_ip_lst = get_config.get_allclient_ip()                               # 客户端ip列表


def case():
    """
    :author:         liujx
    :date            2018.07 28
    :description:
    :return:
    """
    """创建vebench读写路径与校验路径"""
    cmd1 = 'mkdir %s' % VDBENCH_WRITE_PATH
    cmd2 = 'mkdir %s' % VDBENCH_JN_PATH
    common.command(cmd1)
    common.command(cmd2)
    """初始化vdbench"""
    vdbench = tool_use.Vdbenchrun()
    p1 = Process(target=vdbench.run_create, args=(VDBENCH_WRITE_PATH, VDBENCH_JN_PATH, client_ip_lst[0]))
    p2 = Process(target=online_upgrade.case, args=())
    """等待vdbench create完文件"""
    p1.start()
    p1.join()
    """开始升级"""
    p2.start()
    """开始读写并校验文件"""
    vdbench1 = tool_use.Vdbenchrun(elapsed=50)
    while p2.is_alive():
        log.info("##########vdbench check begin#############")
        rc = vdbench1.run_check(VDBENCH_WRITE_PATH, VDBENCH_JN_PATH, client_ip_lst[0])
        if rc != 0:
            raise Exception("vdbench check failed")
        log.info("##########vdbench write begin#############")
        vdbench.run_write_jn(VDBENCH_WRITE_PATH, VDBENCH_JN_PATH, client_ip_lst[0])
        if rc != 0:
            raise Exception("vdbench write failed")
    """升级结束后结束读写与校验文件"""
    p2.join()


def main():
    upgrade_common.delete_upgrade()
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    upgrade_common.delete_upgrade()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
