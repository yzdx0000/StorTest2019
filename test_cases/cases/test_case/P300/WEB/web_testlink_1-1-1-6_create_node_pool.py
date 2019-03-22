# -*-coding:utf-8 -*

import os

import utils_path
import log
import common
import get_config
import web_common
import prepare_clean

#######################################################
# 函数功能：界面自动化-----批量创建节点池（4+2:1）
# 脚本作者：duyuli
# 日期：2018-12-22
# testlink case: 3.0-51022~51023
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
mode = "erasure_codes"   # 纠删码
erasure_codes_value = "4+2:1"

def case():
    driver = web_common.init_web_driver()
    obj_web_node_pool = web_common.Node_Pool(driver)

    # 批量创建节点池（4+2:1）
    obj_web_node_pool.create_node_pool(mode=mode, erasure_codes_value=erasure_codes_value)

    web_common.quit_web_driver(driver)


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
