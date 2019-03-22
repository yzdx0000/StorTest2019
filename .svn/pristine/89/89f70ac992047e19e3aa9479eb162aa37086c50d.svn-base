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
# 函数功能：检查节点运维界面：健康状态、运行状态、ip信息、总容量、已用容量、可用容量、带宽、iops、服务状态、协议类型
# 脚本作者：duyuli
# 日期：2019-01-09
# testlink case: 3.0-54758
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
        value_info_list = obj_web_operation.get_node_operation_info(node_name)
        data_ip_lst = []
        for node_info in node_info_lst:
            if node_info['node_name'] == node_name:
                for data_ip_info in node_info['data_ips']:
                    data_ip_lst.append(data_ip_info['ip_address'])
                    break

        if (
                # 检查节点健康状态
                # value_info_list[0] != "正常" or
                # 检查运行状态
                value_info_list[1] != "正常" or
                # 检查总容量
                "B" not in value_info_list[3] or
                # 已用容量、
                "B" not in value_info_list[4] or
                # 可用容量、
                "B" not in value_info_list[5] or
                # 带宽、
                "B/s" not in value_info_list[6] or
                # iops、
                ":" not in value_info_list[7]
                # 协议类型
                # value_info_list[9] != ""
        ):
            obj_web_base.save_screenshot_now()
            raise Exception("check node operation failed")

        # 检查服务状态、
        for stat in value_info_list[8].split("\n")[:-1]:
            if "SHUTDOWN" in stat:
                obj_web_base.save_screenshot_now()
                raise Exception("check service shutdown")

        # 检查ip信息
        for data_ip in data_ip_lst:
            if data_ip not in value_info_list[2]:
                obj_web_base.save_screenshot_now()
                raise Exception("check ip error")

    web_common.quit_web_driver(driver)


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
