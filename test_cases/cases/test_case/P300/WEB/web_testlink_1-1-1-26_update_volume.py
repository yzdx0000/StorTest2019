# -*-coding:utf-8 -*
import os
import utils_path
import log
import common
import get_config
import web_common
import prepare_clean

#######################################################
# 函数功能：界面自动化-----修改文件系统（修改限制配额）
# 脚本作者：duyuli
# 日期：2018-12-27
# testlink case: 3.0-51042
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
volume_limit_name = "volume1_limit"
storage_name = "storage_pool_2"
volume_quota_limit = "10"
volume_quota_limit_update = "20"
volume_name_list = [volume_limit_name]

def case():
    driver = web_common.init_web_driver()
    obj_web_file_system = web_common.File_System(driver)

    # 创建文件系统
    obj_web_file_system.create_volume(volume_limit_name, storage_name, volume_quota_limit=volume_quota_limit)

    # 修改文件系统配额大小
    obj_web_file_system.update_volume(volume_limit_name=volume_limit_name, volume_quota_limit=volume_quota_limit_update)

    # 删除文件系统
    obj_web_file_system.delete_volumes(volume_name_list)

    web_common.quit_web_driver(driver)


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
