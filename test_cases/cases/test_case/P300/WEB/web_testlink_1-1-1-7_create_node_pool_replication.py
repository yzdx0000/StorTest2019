# -*-coding:utf-8 -*

import os

import utils_path
import log
import common
import get_config
import web_common
import prepare_clean

#######################################################
# 函数功能：界面自动化-----批量创建节点池(2副本)
# 脚本作者：duyuli
# 日期：2018-12-22
# testlink case: 3.0-51023
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
mode = "replication"   # 副本
replica_num = 2
stripe_width = 1
node_parity_num = 1

def case():
    driver = web_common.init_web_driver()
    obj_web_node_pool = web_common.Node_Pool(driver)

    # 批量创建节点池（2副本）
    obj_web_node_pool.create_node_pool(mode=mode, replica_num=replica_num,
                                       stripe_width=stripe_width, node_parity_num=node_parity_num)

    web_common.quit_web_driver(driver)


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
