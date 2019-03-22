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
# 函数功能：界面自动化-----检查集群名称
# 脚本作者：duyuli
# 日期：2019-01-07
# testlink case: 3.0-54754
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
SYSTEM_IP_0 = get_config.get_parastor_ip(0)
cluster_name = common.get_sysname()


def case():
    driver = web_common.init_web_driver()
    obj_web_home = web_common.Home(driver)

    # 获取首页右上角系统名称
    cluster_name1, cluster_name2 = obj_web_home.get_cluster_name()

    if cluster_name1 != cluster_name or cluster_name2 != cluster_name:
        log.info("cluster_name_pscli: %s web_cluster_name: %s %s" % (cluster_name, cluster_name1, cluster_name2))
        raise Exception("check cluster name failed")

    web_common.quit_web_driver(driver)


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
