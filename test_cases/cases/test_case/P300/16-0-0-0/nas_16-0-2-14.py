# -*-coding:utf-8 -*
#######################################################
# author zhangchengyu
# date 2018-08-11
# @summary：
# 16_0_2_14     5节点，其中一个节点处于主动重建状态创建访问区
# @steps:
# 0> 检查环境是否大于等于五个节点，大于等于五节点可以执行该脚本
# 1> 找一个节点删除，制造节点主动重建状态
# 2> 创建访问分区
# 3> 恢复环境
# @changelog：
#
#######################################################
import os
import time
import random
import commands
import utils_path
import common
import nas_common
import log
import shell
import get_config
import json
import make_fault
import prepare_clean

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)  # /mnt/volume1/snap/snap_13_0_0_0
NODE_IP_1 = get_config.get_parastor_ip(0)
NODE_IP_2 = get_config.get_parastor_ip(1)
NODE_IP_3 = get_config.get_parastor_ip(2)
NODE_IP_LIST = [NODE_IP_1, NODE_IP_2, NODE_IP_3]
node_ip = get_config.get_parastor_ip()
FAULT_NODE_IP_LST = nas_common.FAULT_NODE_IP_LST


def executing_case1():
    """ 0> 检查环境是否大于等于五个节点，大于等于五节点可以执行该脚本"""
    log.info("\t[0 check development]")
    node = common.Node()
    outtext = node.get_nodes()
    nodes = outtext['result']['nodes']
    if len(nodes) >= 5:
        fault_node_ip = random.choice(FAULT_NODE_IP_LST)  # 可以做故障的节点IP
        fault_node_id = node.get_node_id_by_ip(node_ip=fault_node_ip)  # 通过故障节点IP找到节点ID

        """ 1> 找一个节点删除，制造节点主动重建状态 """   # 删除一个节点，可制造该节点主动重建状态
        log.info("\t[1 remove_node ]")
        msg = node.remove_nodes(node_ids=fault_node_id, auto_query=False, msg_out=True)
        if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
            common.except_exit("remove_node failed")
        time.sleep(5)

        """ 2> 创建访问分区 """
        log.info("\t[2 create_access_zone ]")
        """"判断是否进入主动重建状态"""
        node_state = []
        begin_time = time.time()
        while "NODE_STATE_NORMAL_REBUILDING" not in node_state:
            node_state = []
            time.sleep(5)
            node = common.Node()
            node_info = node.get_nodes()          # 获取节点信息，检查节点状态是否进入主动重建
            nodes = node_info['result']['nodes']
            for node in nodes:
                node_state.append(node["state"])
            now_time = ""
            now_time = time.time()
            time_use = now_time - begin_time    # 时间戳相减，获取的为秒数，浮点数
            if int(time_use) > 120:
                common.except_exit("节点120s仍无法进入主动重建状态，请检查节点状态")

        """节点进入主动重建状态后，开始创建访问分区"""
        access_zone_name = "access_zone_16_0_2_14"
        node = common.Node()
        outtext = node.get_nodes()
        nodes = outtext['result']['nodes']
        ids = []
        for node in nodes:
            ids.append(node['data_disks'][0]['nodeId'])
        print ids
        access_zone_node_id_16_0_2_14 = ','.join(str(p) for p in ids)
        msg1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_0_2_14, name=access_zone_name)
        if msg1["err_msg"] != "NODE_STATE_INVALID" or \
           msg1["detail_err_msg"].find("current state is NODE_STATE_NORMAL_REBUILDING, not NODE_STATE_HEALTHY") == -1:
            raise Exception('%s create_access_zone failed!!!' % node_ip)

        """ 3> 恢复环境"""
        log.info("\t[3 cancel_remove_nodes ]")
        node = common.Node()
        msg = node.cancel_remove_nodes(node_ids=fault_node_id)
        if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
            common.except_exit("remove_node failed")
        time.sleep(10)

        """检查节点服务是否正常"""
        rc = common.check_service_state()
        common.judge_rc(rc, True, 'check all services state failed')
    else:
        log.error("该集群环境节点数量不到五个节点，故不执行该脚本")

    return


# def get_node_id_by_ip(node_ip):
#     node = common.Node()
#     msg = node.get_nodes()
#     nodes_info = msg["result"]["nodes"]
#     for node in nodes_info:
#         ctl_ip = node["ctl_ips"][0]["ip_address"]
#         if node_ip == ctl_ip:
#             return node["node_id"]
#     log.info("there is not a node's ip is %s!!!" % node_ip)


#######################################################
# @function：清理环境
# @parameter：
# @return：
# @steps:
#######################################################
def clearing_environment():
    log.info("（3）clearing_environment")

    return


#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def preparing_environment():
    log.info("（1）preparing_environment")

    '''
    1、下发nas相关的配置
    2、创建nas测试相关的目录和文件
    '''

    return


#######################################################
# 函数功能：本用例入口函数
# 函数入参：无
# 函数返回值：无
#######################################################
def nas_main():
    preparing_environment()
    prepare_clean.nas_test_prepare(FILE_NAME)
    log.info("（2）executing_case")
    executing_case1()
    clearing_environment()
    prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)
