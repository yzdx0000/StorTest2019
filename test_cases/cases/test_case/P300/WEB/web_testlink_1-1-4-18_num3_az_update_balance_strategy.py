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
# 函数功能：界面自动化-----第三个访问分区创建IP池后，修改负载均衡策略
# 脚本作者：duyuli
# 日期：2019-01-03
# testlink case: 3.0-51080
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
subnet_name = "subnet"
subnet_name_modify = subnet_name + "_modify"
svip_mask = "255.255.252.0"
svip = "80.2.42.101"
svip1 = "80.2.42.102"
svip2 = "80.2.42.103"
vip_address = ["80.2.42.104-106", "80.2.42.107"]
vip_address1 = ["80.2.42.108-109"]
vip_address2 = ["80.2.42.110"]
svip_modify = "80.2.42.100"
domain_name = "www.sugon2.com"
balance_strategy = "LB_CONNECTION_COUNT"


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

    # 创建subnet2 vip_pool
    obj_web_access.create_subnet(quota_common.QUOTA_ACCESS_ZONE + "2",
                                 subnet_name + "2",
                                 svip2,
                                 svip_mask,
                                 [get_config.get_web_eth_name_data_list()[0]],
                                 domain_name,
                                 vip_address2)

    # 修改负载均衡策略为连接数
    obj_web_access.modify_vip_pool(quota_common.QUOTA_ACCESS_ZONE + "2",
                                   subnet_name + "2",
                                   domain_name,
                                   balance_strategy=balance_strategy)
    
    web_common.quit_web_driver(driver)


def main():
    prepare_clean.nas_test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
