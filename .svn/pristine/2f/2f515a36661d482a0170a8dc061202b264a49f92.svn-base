# -*-coding:utf-8 -*
import os
import utils_path
import log
import common
import get_config
import web_common
import prepare_clean

#######################################################
# 函数功能：界面自动化-----第二个、第三个存储池文件系统的创建
# 脚本作者：duyuli
# 日期：2018-12-24
# testlink case: 3.0-51044
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
volume_name = "volume2"
storage_name = "storage_pool_2"

def case():
    driver = web_common.init_web_driver()
    obj_web_file_system = web_common.File_System(driver)

    # 创建文件系统
    obj_web_file_system.create_volume(volume_name, storage_name)

    web_common.quit_web_driver(driver)


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
