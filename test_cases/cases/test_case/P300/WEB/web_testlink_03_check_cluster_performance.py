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
# 函数功能：界面自动化-----检查集群性能是否为无数据状态
# 脚本作者：duyuli
# 日期：2019-01-07
# testlink case: 3.0-54757
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
SYSTEM_IP_0 = get_config.get_parastor_ip(0)


def case():
    driver = web_common.init_web_driver()
    obj_web_home = web_common.Home(driver)

    # 检查集群性能
    obj_web_home.check_cluster_performance_normal()

    web_common.quit_web_driver(driver)


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
