# -*-coding:utf-8 -*
import utils_path
import time
import os
import common
import log
import prepare_clean
import quota_common
import get_config
import web_common
from selenium import webdriver
from selenium.webdriver.support.select import Select

#######################################################
# 函数功能：界面自动化-----配额相关的创建（包括用户阈值）
# 脚本作者：duyuli
# 日期：2018-11-28
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
quota_test_dir = quota_common.QUOTA_PATH
quota_volume_name = os.path.basename(quota_common.BASE_QUOTA_PATH)                # volume1
quota_create_path = quota_volume_name + ':/' + quota_common.QUOTA_PATH_BASENAME   # volume1:/quota_test_dir

SYSTEM_IP_0 = get_config.get_parastor_ip(0)


def case():
    driver = web_common.init_web_driver()

    obj_web_quota = web_common.Quota(driver)
    # 创建访问分区
    obj_web_quota.create_access_zone(quota_common.QUOTA_ACCESS_ZONE, nodes_all=True, nfs=True)

    # 创建用户组用户
    obj_web_quota.create_group_user(quota_common.QUOTA_GROUP, quota_common.QUOTA_USER, quota_common.QUOTA_ACCESS_ZONE)

    # 创建用户配额
    obj_web_quota.create_quota(quota_create_path,
                               auth_provider_name=quota_common.QUOTA_ACCESS_ZONE,
                               user_type=quota_common.TYPE_USER,
                               user_or_group_name=quota_common.QUOTA_USER,
                               logical_quota_cal_type=quota_common.CAL_TYPE_LIMIT,
                               logical_hard_threshold=3,
                               logical_soft_threshold=2,
                               logical_grace_time=1,
                               logical_suggest_threshold=1,
                               filenr_quota_cal_type=quota_common.CAL_TYPE_LIMIT,
                               filenr_hard_threshold=3,
                               filenr_soft_threshold=2,
                               filenr_grace_time=1,
                               filenr_suggest_threshold=1)

    # 删除配额
    obj_web_quota.delete_quota(quota_create_path)

    # 删除用户
    obj_web_quota.delete_group_user(quota_common.QUOTA_GROUP, quota_common.QUOTA_USER, quota_common.QUOTA_ACCESS_ZONE)

    # 删除访问分区
    obj_web_quota.delete_access_zone(quota_common.QUOTA_ACCESS_ZONE)

    web_common.quit_web_driver(driver)


def main():
    prepare_clean.quota_test_prepare(FILE_NAME, env_check=False)
    common.mkdir_path(SYSTEM_IP_0, quota_test_dir)
    case()
    common.rm_exe(SYSTEM_IP_0, quota_test_dir)
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
