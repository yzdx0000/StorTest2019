# -*-coding:utf-8 -*

import os

import utils_path
import log
import common
import get_config
import web_common
import prepare_clean

#######################################################
# 函数功能：界面自动化-----在添加节点的时候进行扩容
# 脚本作者：duyuli
# 日期：2018-12-25
# testlink case: 3.0-51031,3.0-51024,3.0-51025,3.0-51034
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
node_name = get_config.get_web_node_name()
node_ip_all = get_config.get_web_node_ip()
node_control_ip = node_ip_all.split(",")[0]
data_ip_list = node_ip_all.split(",")[1:]
update_to_node_pool_name = "NodePool_1"


def case():
    driver = web_common.init_web_driver()
    obj_web_node_operation = web_common.Node_Operation(driver)

    # 删除节点
    obj_web_node_operation.remove_node(node_name)

    # 添加节点同时进行扩容
    obj_web_node_operation.add_node(node_control_ip, data_ip_list, update_to_node_pool_name=update_to_node_pool_name)

    web_common.quit_web_driver(driver)


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)