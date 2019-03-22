# -*-coding:utf-8 -*
import os
import utils_path
import log
import common
import get_config
import web_common
import prepare_clean

#######################################################
# 函数功能：界面自动化-----创建存储池（1个节点池跨多个存储池）
# 脚本作者：duyuli
# 日期：2018-12-22
# testlink case: 3.0-51028
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
storage_pool_name2 = "storage_pool_2"
service_type = "FILE"

def case():
    driver = web_common.init_web_driver()
    obj_web_storage_pool = web_common.Storage_Pool(driver)

    # 创建存储池
    obj_web_storage_pool.create_storage_pool(name=storage_pool_name2, service_type=service_type)

    web_common.quit_web_driver(driver)


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)