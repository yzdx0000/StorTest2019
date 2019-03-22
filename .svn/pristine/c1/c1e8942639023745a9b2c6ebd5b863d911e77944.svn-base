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
# 函数功能：检查节点运维界面,点击节点后的网络设备信息
# 脚本作者：duyuli
# 日期：2019-01-09
# testlink case: 3.0-54760
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
SYSTEM_IP_0 = get_config.get_parastor_ip(0)

def get_nodes_info():
    rc, stdout = common.get_nodes()
    common.judge_rc(rc, 0, "get_nodes failed!!!\nstdout:%s" % stdout)
    stdout = common.json_loads(stdout)
    nodes_info_lst = stdout['result']['nodes']

    return nodes_info_lst

def case():
    driver = web_common.init_web_driver()
    obj_web_base = web_common.Web_Base(driver)
    obj_web_operation = web_common.Node_Operation(driver)

    # 获取节点运维界面信息
    node_names = obj_web_operation.get_node_name_list()
    # node_info_lst = get_nodes_info()

    for node_name in node_names:
        value_info_list = obj_web_operation.get_node_operate_inside_node_network_device_info(node_name)

        # 检查网络状态是否正常
        for i in range(2, len(value_info_list), 10):
            if value_info_list[i] != "正常":
                obj_web_base.save_screenshot_now()
                raise Exception("check network state error")

    web_common.quit_web_driver(driver)


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
