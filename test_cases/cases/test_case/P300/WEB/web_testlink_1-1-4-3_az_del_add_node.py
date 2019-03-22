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
# 函数功能：界面自动化-----修改访问分区(移除，添加访问分区中的节点)
# 脚本作者：duyuli
# 日期：2019-01-02
# testlink case: 3.0-51065,3.0-51063
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
control_ip_list = get_config.get_allparastor_ips()
access_zone_name = quota_common.QUOTA_ACCESS_ZONE
node_name = get_config.get_web_node_name()
node_ip = get_config.get_web_node_ip()
ctrl_ip = node_ip.split(",")[0]
data_ip = node_ip.split(",")[1:]

def case():
    driver = web_common.init_web_driver()
    obj_web_access_manage = web_common.Access_Manage(driver)
    obj_web_node_operation = web_common.Node_Operation(driver)

    # 获取界面上的节点名称列表
    node_name_list = obj_web_node_operation.get_node_name_list()

    # 创建访问分区
    obj_web_access_manage.create_access_zone(access_zone_name, nodes_all=True, smb=True, nfs=True, ftp=True)

    # 移除访问分区中的节点
    obj_web_access_manage.update_access_zone(access_zone_name, node_name_list=node_name_list[1:])

    # 添加访问分区中的节点
    obj_web_access_manage.update_access_zone(access_zone_name, node_name_list=node_name_list)

    web_common.quit_web_driver(driver)


def main():
    prepare_clean.nas_test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)