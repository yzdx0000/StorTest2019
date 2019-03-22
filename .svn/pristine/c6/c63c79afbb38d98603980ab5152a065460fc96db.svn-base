# -*-coding:utf-8 -*

import os

import utils_path
import log
import common
import get_config
import web_common
import prepare_clean

#######################################################
# 函数功能：界面自动化-----创建、删除posix客户端授权
# 脚本作者：duyuli
# 日期：2018-12-04
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
client_ips_list = get_config.get_allclient_ip()
volume_name = get_config.get_one_volume_name()
volume_name_list = [volume_name]

def case():
    driver = web_common.init_web_driver()

    obj_web_clientauth = web_common.Client_Auth(driver)

    # 添加客户端授权ip
    obj_web_clientauth.create_posix_auth(volume_name_list, client_ips_list)

    # 删除客户端授权ip
    obj_web_clientauth.delete_posix_auth(client_ips_list)

    web_common.quit_web_driver(driver)


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)