# -*-coding:utf-8 -*
import os
import utils_path
import log
import common
import get_config
import web_common
import prepare_clean

#######################################################
# 函数功能：界面自动化-----第二个节点池元数据盘的删除
# 脚本作者：duyuli
# 日期：2018-12-26
# testlink case: 3.0-51033
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
node_name = get_config.get_web_node_name()
disk_type = "SHARED"
storage_pool_name = "storage_pool_2"

def case():
    driver = web_common.init_web_driver()
    obj_web_node_operation = web_common.Node_Operation(driver)

    # 删除第二个存储池元数据盘
    disk_name = obj_web_node_operation.remove_disk(node_name, share_disk=True)

    # 恢复环境添加回来（元数据盘不需要关联存储池，默认添加到共享池）
    obj_web_node_operation.add_disk(node_name, disk_type, disk_name)

    web_common.quit_web_driver(driver)


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
