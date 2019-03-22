# -*- coding:utf-8 -*-

######################################################
# Author: jiangxiaoguang
# Date: 2018-08-xx
# @summary：
#   None
# @steps:
#   None
# @changelog：
#   None
######################################################

import os

import utils_path
import log
import common
import nas_common
import prepare_clean

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]     # 脚本名称


def executing_case():
    """测试执行
    :return:无
    """
    log.info('（2）executing_case')

    return


def nas_main():
    """脚本入口函数
    :return:无
    """
    prepare_clean.nas_test_prepare(FILE_NAME)
    executing_case()
    if nas_common.DEBUG != 'on':
        prepare_clean.nas_test_clean()
    return


if __name__ == '__main__':
    common.case_main(nas_main)
