# -*-coding:utf-8 -*

import os

import utils_path
import log
import common
import get_config
import web_common
import prepare_clean
import quota_common

#######################################################
# 函数功能：界面自动化-----检查首页数据状态、健康状态、运行状态以及节点个数
# 脚本作者：duyuli
# 日期：2019-01-07
# testlink case: 3.0-54755
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
SYSTEM_IP_0 = get_config.get_parastor_ip(0)
node_ids = get_config.get_allparastor_ips()


def case():
    driver = web_common.init_web_driver()
    obj_web_base = web_common.Web_Base(driver)
    obj_web_home = web_common.Home(driver)
    obj_web_node_operation = web_common.Node_Operation(driver)

    # 检查首页状态
    data_stat, health_stat, run_stat, node_total = obj_web_home.get_data_health_run_stat()
    if data_stat != "正常" or run_stat != "运行":
        log.info("data_stat: %s run_stat: %s" % (data_stat, run_stat))
        obj_web_base.save_screenshot_now()
        raise Exception("check cluster name failed")

    # 检查节点个数
    node_names = obj_web_node_operation.get_node_name_list()
    node_numbers = obj_web_node_operation.get_node_total()
    if len(node_names) != node_numbers or node_numbers != node_total:
        log.info("nodes: %s  web_nodes: %s" % (len(node_names), node_numbers))
        obj_web_base.save_screenshot_now()
        raise Exception("check nodes failed")

    web_common.quit_web_driver(driver)


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
