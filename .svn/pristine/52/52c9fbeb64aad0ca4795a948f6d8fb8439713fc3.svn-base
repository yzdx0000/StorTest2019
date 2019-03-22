# -*-coding:utf-8 -*

import os

import utils_path
import log
import common
import get_config
import web_common
import prepare_clean

#######################################################
# 函数功能：界面自动化-----创建、修改、删除NIS认证服务器
# 脚本作者：duyuli
# 日期：2018-12-14
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
nis_name = "nis_server"
nis_name_update = "nis_update"


def case():
    driver = web_common.init_web_driver()

    obj_web_acess = web_common.Access_Manage(driver)

    # 添加NIS认证服务器
    obj_web_acess.add_auth_provider_nis(name=nis_name,
                                        domain_name=get_config.get_nis_domain_name()[0],
                                        ip_addresses=get_config.get_nis_ip_address()[0],
                                        check=True)
    # 修改NIS认证服务器
    obj_web_acess.update_auth_provider_nis(name_to_be_updated=nis_name,
                                           name=nis_name_update,
                                           domain_name=get_config.get_nis_domain_name()[0],
                                           ip_addresses=get_config.get_nis_ip_address()[0],
                                           check=True)

    # 删除NIS认证服务器
    obj_web_acess.delete_auth_provider_nis(nis_name_update)

    web_common.quit_web_driver(driver)


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
