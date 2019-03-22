# -*-coding:utf-8 -*

import os

import utils_path
import log
import common
import get_config
import web_common
import prepare_clean
import quota_common
import time

#######################################################
# 函数功能：界面自动化-----限制配额测试（包含业务）
# 脚本作者：duyuli
# 日期：2019-01-02
# testlink case: 3.0-51095
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
quota_test_dir = quota_common.QUOTA_PATH
quota_volume_name = os.path.basename(quota_common.BASE_QUOTA_PATH)                # volume1
quota_create_path = quota_volume_name + ':/' + quota_common.QUOTA_PATH_BASENAME   # volume1:/quota_test_dir/A
SYSTEM_IP_0 = get_config.get_parastor_ip(0)
SYSTEM_IP_1 = get_config.get_parastor_ip(1)

def case():
    driver = web_common.init_web_driver()
    obj_web_quota = web_common.Quota(driver)

    # 创建目录的配额20G
    obj_web_quota.create_quota(path=quota_create_path,
                               logical_quota_cal_type=quota_common.CAL_TYPE_LIMIT,
                               logical_hard_threshold=20)

    # 配额目录下创建目录A
    dir_son_path = os.path.join(quota_test_dir, "A")
    common.mkdir_path(SYSTEM_IP_0, dir_son_path)

    # 客户端向quota_test_dir写入10G文件、A目录中写入6G文件
    quota_common.creating_files(SYSTEM_IP_0, quota_test_dir, 10, 1024, "test1")
    quota_common.creating_files(SYSTEM_IP_0, os.path.join(quota_test_dir, "A"), 6, 1024, "A1")

    # 继续写入
    quota_common.creating_files(SYSTEM_IP_0, quota_test_dir, 5, 1024, "test2")
    quota_common.creating_files(SYSTEM_IP_0, os.path.join(quota_test_dir, "A"), 5, 1024, "A2")

    # 检查是否限制住
    time.sleep(20)
    obj_web_quota.check_quota_until_valid(quota_path=quota_create_path)

    used_capacity = obj_web_quota.get_quota_used_capacity(quota_path=quota_create_path)
    if used_capacity != "20.00":
        log.info("quota_used_capacity : %s" % used_capacity)
        raise Exception("check quota used capacity failed")

    # 修改配额为30G
    obj_web_quota.modify_quota(quota_create_path,
                               logical_quota_cal_type=quota_common.CAL_TYPE_LIMIT,
                               logical_hard_threshold=30)

    # 继续写入15G内容，预期写入10G后，剩下的5G写入不进去
    quota_common.creating_files(SYSTEM_IP_0, quota_test_dir,
                                file_count=15, file_size=1024, file_name_identifier="modify")

    # 检查是否限制住
    time.sleep(20)
    obj_web_quota.check_quota_until_valid(quota_path=quota_create_path)

    used_capacity = obj_web_quota.get_quota_used_capacity(quota_path=quota_create_path)
    if used_capacity != "30.00":
        log.info("quota_used_capacity : %s" % used_capacity)
        raise Exception("check quota used capacity failed")

    web_common.quit_web_driver(driver)


def main():
    prepare_clean.quota_test_prepare(FILE_NAME, env_check=False)
    common.mkdir_path(SYSTEM_IP_0, quota_test_dir)
    case()
    prepare_clean.quota_test_clean(FILE_NAME)
    common.rm_exe(SYSTEM_IP_0, quota_test_dir)
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
