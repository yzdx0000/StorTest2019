# -*-coding:utf-8 -*

import os
import random

import utils_path
import log
import common
import web_common
import prepare_clean

#######################################################
# 函数功能：界面自动化-----1、检查节点运维界面带宽和iops是否为N/A
# 脚本作者：duyuli
# 日期：2018-12-17
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
name_value = "vm102"
healthy_state_value = random.choice(["abnormal", "normal", "abnormal", "unknown"])
running_state_value = random.choice(["normal", "abnormal", "deleting", "reinstalling", "shutdown", "maintaining",
                                     "prepare_maintaining", "prepare_online", "zombie", "unknown"])


def case():
    driver = web_common.init_web_driver()

    obj_web_node = web_common.Node_Operation(driver)

    # 检查节点运维界面带宽和iops是否为N/A
    obj_web_node.check_node_operate_bandwidth_iops()

    web_common.quit_web_driver(driver)


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
