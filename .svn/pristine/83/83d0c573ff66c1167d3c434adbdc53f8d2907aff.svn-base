# -*-coding:utf-8 -*
#######################################################
# author zhangchengyu
# date 2018-08-08
# @summary：
# 16_0_2_13     5节点，其中一个节点处于孤立状态创建访问区
# @steps:
# 0> 检查环境是否大于等于五个节点，大于等于五节点可以执行该脚本
# 1> 找一个节点断网，制造节点孤立状态
# 2> 创建访问分区
# 3> 恢复孤立节点的网卡
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
import get_config
import make_fault
import prepare_clean

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)  # /mnt/volume1/snap/snap_13_0_0_0
NODE_IP_1 = get_config.get_parastor_ip(0)
NODE_IP_2 = get_config.get_parastor_ip(1)
NODE_IP_3 = get_config.get_parastor_ip(2)
NODE_IP_LIST = [NODE_IP_1, NODE_IP_2, NODE_IP_3]
node_ip = get_config.get_parastor_ip()


def executing_case1():
    """ 0> 检查环境是否大于等于五个节点，大于等于五节点可以执行该脚本"""
    log.info("\t[0 check development]")
    node = common.Node()
    outtext = node.get_nodes()
    nodes = outtext['result']['nodes']
    if len(nodes) >= 5:
        """1> 找一个节点断网，制造节点孤立状态"""   # 节点断网5min会进入孤立状态
        log.info("\t[1 ifdown eth]")
        node = common.Node()
        msg = node.get_master()
        ip_master_a = str(msg["result"]["data_ips"][0]["ip_address"])
        # ip_master = ip_master_a.split('.')[-1]
        ip_master = node.get_node_id_by_ip(ip_master_a)
        node_ip_1 = NODE_IP_LIST[random.randint(0, len(NODE_IP_LIST) - 1)]
        # node_ip_a = node_ip_1.split('.')[-1]
        node_ip_a = node.get_node_id_by_ip(node_ip_1)
        # node_ip_b = node_ip.split('.')[-1]
        node_ip_b = node.get_node_id_by_ip(node_ip)
        while ip_master == node_ip_a or node_ip_b == node_ip_a:  # 排除当下执行命令的id与master的id
            node_ip_1 = NODE_IP_LIST[random.randint(0, len(NODE_IP_LIST) - 1)]
            # node_ip_a = node_ip_1.split('.')[-1]
            node_ip_a = node.get_node_id_by_ip(node_ip_1)
        print node_ip_1
        # eth_list = nas_common.ETH_LIST
        eth_id = node.get_node_id_by_ip(nas_common.ETH_IP)  # 指定要断网卡的ip，通过ip找到id
        eth_list, data_ip_list, ip_mask_lst = node.get_node_eth(eth_id)  # 通过id获取节点的网卡名
        print "down_eth"
        msg = make_fault.down_eth(node_ip_1, eth_list)
        common.judge_rc(msg, 0, '%s down_eth failed!!!' % node_ip_1)
        print "sleep 300s"
        time.sleep(300)

        """ 2> 创建访问分区 """
        log.info("\t[2 create_access_zone ]")
        access_zone_name = "access_zone_16_0_2_13"
        node = common.Node()
        ids = node.get_nodes_id()
        access_zone_node_id_16_0_2_13 = ','.join(str(p) for p in ids)
        msg1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_0_2_13,
                                             name=access_zone_name)
        if msg1["err_msg"] != "NODE_STATE_INVALID" or \
           msg1["detail_err_msg"].find("current state is NODE_STATE_ISOLATE, not NODE_STATE_HEALTHY") == -1:
            raise Exception('%s create_access_zone failed!!!' % node_ip)

        """ 3> 恢复孤立节点的网卡"""
        log.info("\t[3 ifconfig up eth ]")
        print "up_eth"
        make_fault.up_eth(node_ip_1, eth_list, ip_mask_lst)
        print "sleep 300s"
        time.sleep(300)
    else:
        log.error("该集群环境节点数量不到五个节点，故不执行该脚本")

    return


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
