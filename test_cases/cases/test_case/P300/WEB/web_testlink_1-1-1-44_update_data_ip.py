# -*-coding:utf-8 -*

import os

import utils_path
import log
import common
import get_config
import web_common
import prepare_clean

#######################################################
# 函数功能：界面自动化-----修改系统ip（修改数据ip）
# 脚本作者：duyuli
# 日期：2018-12-29
# testlink case: 3.0-51060,3.0-51059
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
cluster_name = "duyuli"
node_name = get_config.get_web_node_name()
node_ips = get_config.get_web_node_ip()
ctrl_ip = node_ips.split(",")[0]
data_ip_list = [ctrl_ip]  # 修改为复用控制ip

def case():
    driver = web_common.init_web_driver(auto_connect=False)
    obj_web_system_install = web_common.System_Install(driver)

    # 修改控制ip和数据ip
    obj_web_system_install.modify_system_ip(cluster_name, node_name, ctrl_ip=ctrl_ip, data_ip_list=data_ip_list)

    web_common.quit_web_driver(driver)


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
