# -*-coding:utf-8 -*

import os

import utils_path
import log
import common
import get_config
import web_common
import prepare_clean
import quota_common
import time

#######################################################
# 函数功能：界面自动化-----创建访问分区(跨未用节点)
# 脚本作者：duyuli
# 日期：2019-01-02
# testlink case: 3.0-51064
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
control_ip_list = get_config.get_allparastor_ips()
access_zone_name = quota_common.QUOTA_ACCESS_ZONE
node_name = get_config.get_web_node_name()
node_ip = get_config.get_web_node_ip()
ctrl_ip = node_ip.split(",")[0]
data_ip = node_ip.split(",")[1:]
node_pool_name = "NodePool_1"
storage_pool_name1 = "storage_pool_1"
storage_pool_name2 = "storage_pool_2"

def case():
    driver = web_common.init_web_driver()
    obj_web_access_manage = web_common.Access_Manage(driver)
    obj_web_node_operation = web_common.Node_Operation(driver)
    obj_web_node_pool = web_common.Node_Pool(driver)
    obj_web_storage_pool = web_common.Storage_Pool(driver)

    # 删除节点
    obj_web_node_operation.remove_node(node_name)

    # 添加节点(不扩到节点池)
    obj_web_node_operation.add_node(ctrl_ip, data_ip_list=data_ip)

    # 创建访问分区
    obj_web_access_manage.create_access_zone(name=access_zone_name,
                                             nodes_all=True,
                                             nfs=True,
                                             smb=True,
                                             ftp=True)

    # 恢复环境
    obj_web_node_pool.update_node_pool(node_pool_name, [node_name])

    vir_phy = get_config.get_web_machine()
    if vir_phy == "phy":
        obj_web_storage_pool.expand_storage_pool(storage_pool_name1, disk_all=False)
    obj_web_storage_pool.expand_storage_pool(storage_pool_name2, disk_all=True)

    web_common.quit_web_driver(driver)


def main():
    prepare_clean.nas_test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)