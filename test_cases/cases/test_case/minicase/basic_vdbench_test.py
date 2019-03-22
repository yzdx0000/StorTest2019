# -*-coding:utf-8 -*
import os

import utils_path
import common
import log
import tool_use
import get_config
import prepare_clean

#################################################################
#
# Author: baorb
# date 2017-08-21
# @summary：
#    本测试主要测试3节点P300的vdbench进行创建和检验数据。
# @steps:
#    1，使用vdbench添加文件
#    2，使用vdbench校验数据
#
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                # 本脚本名字
MINI_TRUE_PATH = os.path.join(prepare_clean.MINICASE_PATH, FILE_NAME)      # /mnt/volume1/mini_case/3_0015_truncate_test


def case():
    """
    vdbench创建和校验数据
    :return:
    """
    log.info("----------case----------")
    '''随机获取集群内的一个节点，对其进行故障'''
    ip_list = get_config.get_allclient_ip()

    tool_use.vdbench_run(MINI_TRUE_PATH, ip_list[0], ip_list[1], run_create=True, run_check_write=True)

    '''检查系统'''
    common.ckeck_system()

    log.info("case succeed!")
    return


def main():
    prepare_clean.minicase_test_prepare(FILE_NAME)
    case()
    prepare_clean.minicase_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)
    return


if __name__ == '__main__':
    common.case_main(main)