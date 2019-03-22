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
# 函数功能：界面自动化-----第三个访问分区创建用户组用户
# 脚本作者：duyuli
# 日期：2019-01-04
# testlink case: 3.0-51083
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字

def case():
    driver = web_common.init_web_driver()
    obj_web_access = web_common.Access_Manage(driver)
    obj_web_node_operation = web_common.Node_Operation(driver)

    # 获取界面上的节点名称列表
    node_name_list = obj_web_node_operation.get_node_name_list()
    
    # 创建访问分区
    obj_web_access.create_access_zone(quota_common.QUOTA_ACCESS_ZONE,
                                      node_hostname_list=node_name_list[0:1], nfs=True, smb=True, ftp=True)

    # 创建第二个访问分区
    obj_web_access.create_access_zone(quota_common.QUOTA_ACCESS_ZONE + "1",
                                      node_hostname_list=node_name_list[1:2], nfs=True, smb=True, ftp=True)

    # 创建第三个访问分区
    obj_web_access.create_access_zone(quota_common.QUOTA_ACCESS_ZONE + "2",
                                      node_hostname_list=node_name_list[2:3], nfs=True, smb=True, ftp=True)

    # 创建用户组用户
    obj_web_access.create_group_user(quota_common.QUOTA_GROUP,
                                     quota_common.QUOTA_USER,
                                     quota_common.QUOTA_ACCESS_ZONE + "2")
    
    web_common.quit_web_driver(driver)


def main():
    prepare_clean.nas_test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
