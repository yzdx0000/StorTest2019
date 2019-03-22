# -*-coding:utf-8 -*

import os

import utils_path
import log
import common
import get_config
import web_common
import prepare_clean

#######################################################
# 函数功能：界面自动化-----扩容节点池
# 脚本作者：duyuli
# 日期：2018-12-24
# testlink case: 3.0-51024
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
name = "NodePool_1"
node_name = get_config.get_web_node_name()
node_name_list = [node_name]

def case():
    driver = web_common.init_web_driver()
    obj_web_node_pool = web_common.Node_Pool(driver)

    # 扩容节点池
    obj_web_node_pool.update_node_pool(name, node_name_list)

    web_common.quit_web_driver(driver)


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
