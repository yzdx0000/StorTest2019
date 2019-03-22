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
# 函数功能：界面自动化-----修改业务子网（修改SVIP）
# 脚本作者：duyuli
# 日期：2019-01-03
# testlink case: 3.0-51071
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
subnet_name = "subnet"
subnet_name_modify = subnet_name + "_modify"
svip_mask = "255.255.252.0"
svip = "80.2.42.99"
svip_update = "80.2.42.98"
vip_address = ["80.2.42.101-111", "80.2.42.112"]
vip_address_modify = ["80.2.42.113-124"]
svip_modify = "80.2.42.100"


def case():
    driver = web_common.init_web_driver()
    obj_web_access = web_common.Access_Manage(driver)

    # 创建访问分区
    obj_web_access.create_access_zone(quota_common.QUOTA_ACCESS_ZONE, nodes_all=True, nfs=True, smb=True, ftp=True)

    # 创建subnet vip_pool
    obj_web_access.create_subnet(quota_common.QUOTA_ACCESS_ZONE,
                                 subnet_name,
                                 svip,
                                 svip_mask,
                                 [get_config.get_web_eth_name_data_list()[0]],
                                 get_config.get_vip_domain_name()[0],
                                 vip_address)

    # 修改subnet（修改svip）
    obj_web_access.modify_subnet(quota_common.QUOTA_ACCESS_ZONE,
                                 subnet_name,
                                 svip=svip_update)
    
    web_common.quit_web_driver(driver)


def main():
    prepare_clean.nas_test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
