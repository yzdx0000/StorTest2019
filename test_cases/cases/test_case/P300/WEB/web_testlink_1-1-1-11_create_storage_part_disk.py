# -*-coding:utf-8 -*

import os

import utils_path
import log
import common
import get_config
import web_common
import prepare_clean

#######################################################
# 函数功能：界面自动化-----创建存储池（1个存储池跨多个节点池）
# 脚本作者：duyuli
# 日期：2018-12-22
# testlink case: 3.0-51027
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
storage_pool_name1 = "storage_pool_1"
service_type = "FILE"
disk_part_value_list = ["/dev/sdf", "/dev/sdg"]

def case():
    driver = web_common.init_web_driver()
    obj_web_storage_pool = web_common.Storage_Pool(driver)

    # 创建存储池，每节点选中2块磁盘
    obj_web_storage_pool.create_storage_pool(name=storage_pool_name1, service_type=service_type,
                                             disk_all=False)

    web_common.quit_web_driver(driver)


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
