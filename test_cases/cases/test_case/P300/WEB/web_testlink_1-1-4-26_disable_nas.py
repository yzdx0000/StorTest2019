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
# 函数功能：界面自动化-----nas服务单独启停，全部启停
# 脚本作者：duyuli
# 日期：2019-01-04
# testlink case: 3.0-51088
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
quota_test_dir = quota_common.QUOTA_PATH + "/smb"
quota_volume_name = os.path.basename(quota_common.BASE_QUOTA_PATH)  # volume1
quota_create_path = quota_volume_name + ':/' + quota_common.QUOTA_PATH_BASENAME + "/smb"  # volume1:/quota_test_dir
SYSTEM_IP_0 = get_config.get_parastor_ip(0)


def case():
    driver = web_common.init_web_driver()

    obj_web_nas = web_common.Nas(driver)

    # 创建访问分区
    obj_web_nas.create_access_zone(quota_common.QUOTA_ACCESS_ZONE, nodes_all=True, smb=True, nfs=True, ftp=True)

    # 停用smb服务
    obj_web_nas.disable_or_enable_nas(quota_common.QUOTA_ACCESS_ZONE, smb=False, nfs=True, ftp=True)

    # 停用nfs服务
    obj_web_nas.disable_or_enable_nas(quota_common.QUOTA_ACCESS_ZONE, smb=False, nfs=False, ftp=True)

    # 停用ftp服务
    obj_web_nas.disable_or_enable_nas(quota_common.QUOTA_ACCESS_ZONE, smb=False, nfs=False, ftp=False)

    # 删除访问分区
    obj_web_nas.delete_access_zone(quota_common.QUOTA_ACCESS_ZONE)

    web_common.quit_web_driver(driver)


def main():
    prepare_clean.nas_test_prepare(FILE_NAME, env_check=False)
    common.mkdir_path(SYSTEM_IP_0, quota_test_dir)
    case()
    common.rm_exe(SYSTEM_IP_0, quota_test_dir)
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
