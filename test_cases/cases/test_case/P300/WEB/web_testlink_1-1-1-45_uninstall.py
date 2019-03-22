# -*-coding:utf-8 -*

import os

import utils_path
import log
import common
import get_config
import web_common
import prepare_clean

#######################################################
# 函数功能：界面自动化-----卸载系统
# 脚本作者：duyuli
# 日期：2018-12-27
# testlink case: 3.0-51061
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字

def case():
    # 卸载parastor系统
    web_common.System_Install.uninstall_system()

def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
