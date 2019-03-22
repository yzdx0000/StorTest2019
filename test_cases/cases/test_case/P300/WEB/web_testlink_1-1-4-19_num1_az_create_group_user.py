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
# 函数功能：界面自动化-----第一个访问分区创建用户组用户
# 脚本作者：duyuli
# 日期：2019-01-04
# testlink case: 3.0-51081
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字

def case():
    driver = web_common.init_web_driver()
    obj_web_access = web_common.Access_Manage(driver)

    # 创建访问分区
    obj_web_access.create_access_zone(quota_common.QUOTA_ACCESS_ZONE, nodes_all=True, smb=True, nfs=True, ftp=True)

    # 创建用户组用户
    obj_web_access.create_group_user(quota_common.QUOTA_GROUP, quota_common.QUOTA_USER, quota_common.QUOTA_ACCESS_ZONE)

    web_common.quit_web_driver(driver)


def main():
    prepare_clean.nas_test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
