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
# 函数功能：界面自动化-----跨节点池创建访问分区(需要提前创建多个节点池)
# 脚本作者：liujx
# 日期：2018-12-26
# testlink case: 3.0-51063
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
control_ip_list = get_config.get_allparastor_ips()
access_zone1_name = quota_common.QUOTA_ACCESS_ZONE
access_zone2_name = quota_common.QUOTA_ACCESS_ZONE + '1'
access_zone3_name = quota_common.QUOTA_ACCESS_ZONE + '2'

def case():
    driver = web_common.init_web_driver(auto_connect=True)

    obj_web_access_create = web_common.Access_Manage(driver)

    operation = web_common.Node_Operation
    node_hostname_list = operation.get_node_name_list(driver)
    n = 3 # n个访问分区
    access_zone1_hostname_list = []
    access_zone2_hostname_list = []
    access_zone3_hostname_list = []

    for i in range(1, len(node_hostname_list), n):
        access_zone1_hostname_list.append(node_hostname_list[i-1])
        access_zone2_hostname_list.append(node_hostname_list[i])
        access_zone3_hostname_list.append(node_hostname_list[i+1])

    obj_web_access_create.create_access_zone(name=access_zone1_name, auth_provider_name=None, nodes_all=False,
                                             node_hostname_list=access_zone1_hostname_list,
                                             enable_nas=True, nfs=True, smb=True, ftp=True, s3=False)
    obj_web_access_create.create_access_zone(name=access_zone2_name, auth_provider_name=None, nodes_all=False,
                                             node_hostname_list=access_zone2_hostname_list,
                                             enable_nas=True, nfs=True, smb=True, ftp=True, s3=False)
    obj_web_access_create.create_access_zone(name=access_zone3_name, auth_provider_name=None, nodes_all=False,
                                             node_hostname_list=access_zone3_hostname_list,
                                             enable_nas=True, nfs=True, smb=True, ftp=True, s3=False)
    web_common.quit_web_driver(driver)


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
