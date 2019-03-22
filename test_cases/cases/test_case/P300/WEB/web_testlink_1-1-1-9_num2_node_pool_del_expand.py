# -*-coding:utf-8 -*

import os

import utils_path
import log
import common
import get_config
import web_common
import prepare_clean

#######################################################
# 函数功能：界面自动化-----第二个节点池中节点删除、节点扩容
# 脚本作者：duyuli
# 日期：2018-12-24
# testlink case: 3.0-51025
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
node_name = get_config.get_web_node_name()
node_ip_all = get_config.get_web_node_ip()
node_control_ip = node_ip_all.split(",")[0]
data_ip_list = node_ip_all.split(",")[1:]
node_pool_name = "NodePool_1"


def case():
    driver = web_common.init_web_driver()
    obj_web_node_operation = web_common.Node_Operation(driver)
    obj_web_node_pool = web_common.Node_Pool(driver)

    # 删除节点
    obj_web_node_operation.remove_node(node_name)

    # 添加节点
    obj_web_node_operation.add_node(node_control_ip, data_ip_list)

    # 扩容到节点池
    obj_web_node_pool.update_node_pool(node_pool_name, node_name_list=[node_name])

    web_common.quit_web_driver(driver)


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
