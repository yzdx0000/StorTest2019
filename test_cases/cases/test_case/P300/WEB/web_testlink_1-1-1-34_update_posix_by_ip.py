# -*-coding:utf-8 -*
import os
import utils_path
import log
import common
import get_config
import web_common
import prepare_clean

#######################################################
# 函数功能：界面自动化-----修改授权（ip地址）
# 脚本作者：duyuli
# 日期：2018-12-28
# testlink case: 3.0-51050
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
client_ips_list = get_config.get_allclient_ip()
client_ips_list_update = client_ips_list.append("10.2.42.110")
volume_name = "volume2"

def case():
    driver = web_common.init_web_driver()
    obj_web_client_auth = web_common.Client_Auth(driver)

    # 创建授权
    obj_web_client_auth.create_posix_auth([volume_name], client_ips_list)

    # 修改授权ip地址
    obj_web_client_auth.update_posix_auth(volume_name, client_ips_list=client_ips_list_update)

    # 删除授权
    obj_web_client_auth.delete_posix_auth(client_ips_list)

    web_common.quit_web_driver(driver)


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
