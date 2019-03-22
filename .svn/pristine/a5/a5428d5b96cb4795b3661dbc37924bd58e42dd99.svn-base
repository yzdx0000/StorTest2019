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
# 函数功能：界面自动化-----检查节点池、存储池、卷  数目的统计
# 脚本作者：duyuli
# 日期：2019-01-07
# testlink case: 3.0-54756
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
SYSTEM_IP_0 = get_config.get_parastor_ip(0)

def case():
    driver = web_common.init_web_driver()
    obj_web_base = web_common.Web_Base(driver)
    obj_web_home = web_common.Home(driver)
    obj_web_node_pool = web_common.Node_Pool(driver)
    obj_web_storage_pool = web_common.Storage_Pool(driver)
    obj_web_file_system = web_common.File_System(driver)

    # 获取首页节点池、存储池、卷数目
    obj_web_home.get_node_pool_storage_volume_total()
    node_pool_total, storage_total, volume_total = obj_web_home.get_node_pool_storage_volume_total()

    # 检查节点池数目统计
    node_pool_list = obj_web_node_pool.get_node_pool_names()
    node_pool_count = obj_web_node_pool.get_node_pool_count()
    if len(node_pool_list) != node_pool_count or node_pool_count != node_pool_total:
        log.info("len(node_pool_list): %s node_pool_count: %s" % (len(node_pool_list), node_pool_count))
        obj_web_base.save_screenshot_now()
        raise Exception("check resource count failed")

    # 检查存储池数目统计
    storage_pool_list = obj_web_storage_pool.get_storage_pool_names()
    storage_pool_count = obj_web_storage_pool.get_storage_pool_count()
    if len(storage_pool_list) != storage_pool_count or storage_pool_count != storage_total:
        log.info("len(storage_pool_list): %s storage_pool_count: %s" % (len(storage_pool_list), storage_pool_count))
        obj_web_base.save_screenshot_now()
        raise Exception("check resource count failed")

    # 检查卷数目统计
    volume_list = obj_web_file_system.get_volume_names()
    volume_count = obj_web_file_system.get_volume_count()
    if len(volume_list) != volume_count or volume_count != volume_total:
        log.info("len(volume_list): %s volume_count: %s" % (len(volume_list), volume_count))
        obj_web_base.save_screenshot_now()
        raise Exception("check resource count failed")

    web_common.quit_web_driver(driver)


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
