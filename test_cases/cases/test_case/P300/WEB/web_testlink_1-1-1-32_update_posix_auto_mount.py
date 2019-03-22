# -*-coding:utf-8 -*
import os
import utils_path
import log
import common
import get_config
import web_common
import prepare_clean

#######################################################
# 函数功能：界面自动化-----修改授权（删除、添加自动挂载）
# 脚本作者：duyuli
# 日期：2018-12-27
# testlink case: 3.0-51048
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
client_ips_list = get_config.get_allclient_ip()
volume_name = "volume1"

def case():
    driver = web_common.init_web_driver()
    obj_web_client_auth = web_common.Client_Auth(driver)

    # 创建授权
    obj_web_client_auth.create_posix_auth([volume_name], client_ips_list)

    # 修改posix授权（取消自动挂载）
    obj_web_client_auth.update_posix_auth(volume_name, auto_mount=False)

    # 修改posix授权（添加自动挂载）
    obj_web_client_auth.update_posix_auth(volume_name, auto_mount=True)

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
