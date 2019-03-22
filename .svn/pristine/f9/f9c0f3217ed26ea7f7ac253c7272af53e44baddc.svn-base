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
# 函数功能：检查节点运维界面,点击节点后的信息
# 脚本作者：duyuli
# 日期：2019-01-09
# testlink case: 3.0-54759
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
    node_info_lst = get_nodes_info()

    for node_name in node_names:
        value_info_list = obj_web_operation.get_node_operate_inside_node_base_info(node_name)

        for node_info in node_info_lst:
            if node_info['node_name'] == node_name:
                if (
                        # 比对机型
                        value_info_list[0] != node_info['model'] or
                        # 比对机柜
                        node_info['cabinet_name'] not in value_info_list[1] or
                        # 比对序列号
                        node_info['sn'] != "".join(value_info_list[2].split("\n")) or
                        # 比对健康状态
                        # value_info_list[3] != "正常" or
                        # 比对运行状态
                        value_info_list[4] != "正常"
                ):
                    obj_web_base.save_screenshot_now()
                    raise Exception("check node info error")
            break

    web_common.quit_web_driver(driver)


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
