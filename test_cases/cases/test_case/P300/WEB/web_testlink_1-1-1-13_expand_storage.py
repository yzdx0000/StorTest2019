# -*-coding:utf-8 -*
import os
import utils_path
import log
import common
import get_config
import web_common
import prepare_clean

#######################################################
# 函数功能：界面自动化-----扩容存储池（通过存储池扩容）
# 脚本作者：duyuli
# 日期：2018-12-25
# testlink case: 3.0-51029
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
storage_pool_name1 = "storage_pool_1"
storage_pool_name2 = "storage_pool_2"

def case():
    driver = web_common.init_web_driver()
    obj_web_storage_pool = web_common.Storage_Pool(driver)

    # 扩容存储池
    vir_phy = get_config.get_web_machine()
    if vir_phy == "phy":
        obj_web_storage_pool.expand_storage_pool(storage_pool_name1, disk_all=False)

    obj_web_storage_pool.expand_storage_pool(storage_pool_name2, disk_all=True)

    web_common.quit_web_driver(driver)


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
