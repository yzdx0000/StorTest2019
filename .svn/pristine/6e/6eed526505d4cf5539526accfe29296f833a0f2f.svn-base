# -*-coding:utf-8 -*
#######################################################
# author zhangchengyu
# date 2018-08-13
# @summary：
# 16_0_2_15     5节点，其中一个节点处于被动重建状态创建访问区
# @steps:
# 0> 检查环境是否大于等于五个节点，大于等于五节点可以执行该脚本
# 1> 修改断网时间后断网，制造一个节点处于被动重建状态
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
        """1> 修改断网时间后断网，制造一个节点处于被动重建状态"""
        log.info("\t[1 制造一个节点处于被动重建状态]")
        """获取节点id"""
        obj_node = common.Node()
        fault_node_ip = random.choice(FAULT_NODE_IP_LST)  # 可以做故障的节点IP
        fault_node_id = obj_node.get_node_id_by_ip(fault_node_ip)  # 通过故障节点IP找到节点ID
        """生成节点的配置文件"""
        config_file = make_fault.make_node_xml(fault_node_id)
        """获取节点所在的节点池的id"""
        node_pool_id = obj_node.get_nodepoolid_by_nodeid(fault_node_id)
        """获取节点中所有磁盘与存储池的对应关系"""
        relation_lst = make_fault.get_node_storage_pool_rel(fault_node_id)
        """更新节点参数"""
        common.update_param("MGR", "node_isolate_timeout", "300000")
        """选故障节点断数据网"""
        eth_list, data_ip_list, ip_mask_lst = obj_node.get_node_eth(fault_node_id)  # 通过id获取节点的网卡名
        print "down_eth"
        msg = make_fault.down_eth(fault_node_ip, eth_list)
        common.judge_rc(msg, 0, '%s down_eth failed!!!' % fault_node_ip)
        time.sleep(300)

        """ 2> 创建访问分区 """
        log.info("\t[2 create_access_zone ]")
        """查询是否进入被动重建状态"""
        node_state = ""
        begin_time = time.time()
        while "NODE_STATE_ISOLATE_REBUILDING" not in node_state:
            time.sleep(5)
            node = common.Node()
            node_info = node.get_nodes()     # 获取节点信息，检查节点状态是否进入主动重建
            node_state = []
            nodes = node_info['result']['nodes']
            for node in nodes:
                node_state.append(node["state"])
            now_time = time.time()
            time_use = now_time - begin_time    # 时间戳相减，获取的为秒数，浮点数
            if int(time_use) > 360:
                common.except_exit("节点360s仍无法进入被动重建状态，请检查节点状态")

        """节点进入被动重建状态后，开始创建访问分区"""
        access_zone_name = "access_zone_16_0_2_15"
        node = common.Node()
        outtext = node.get_nodes()
        nodes = outtext['result']['nodes']
        ids = []
        for node in nodes:
            ids.append(node['data_disks'][0]['nodeId'])
        print ids
        access_zone_node_id_16_0_2_15 = ','.join(str(p) for p in ids)
        msg1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_0_2_15, name=access_zone_name)
        if msg1["err_msg"] != "NODE_STATE_INVALID" or \
           msg1["detail_err_msg"].find("current state is NODE_STATE_ISOLATE_REBUILDING, not NODE_STATE_HEALTHY") == -1:
            common.except_exit("有节点在被动重建状态时，创建访问分区与预期不符，请检查节点状态与访问分区状态")

        """ 3> 恢复环境"""
        log.info("\t[3 recovery environment ]")
        """更新节点参数"""
        common.update_param("MGR", "node_isolate_timeout", "86400000")
        """恢复故障节点的网卡"""
        print "up_eth"
        make_fault.up_eth(fault_node_ip, eth_list, ip_mask_lst)
        time.sleep(20)
        """删除节点"""
        obj_node.remove_nodes(fault_node_id)
        """不断ping节点，直到可以ping通"""
        num = 0
        while True:
            time.sleep(20)
            if check_ping(fault_node_ip) is not False:
                log.info("wait 60s")
                time.sleep(60)
                break
            num += 1
            log.info('node %s cannot ping pass %ds' % (fault_node_ip, num * 20))

        """添加节点"""
        obj_node.add_node(config_file)
        time.sleep(60)
        """获取新的节点id"""
        node_id_new = obj_node.get_node_id_by_ip(fault_node_ip)
        """添加节点到节点池中"""
        make_fault.add_node_to_nodepool(node_pool_id, node_id_new)
        """启动系统"""
        make_fault.start_up_parastor()
        """将节点中的所有磁盘添加到对应的存储池"""
        make_fault.add_node_disks_to_storagepool(node_id_new, relation_lst)
        """检查节点服务是否正常"""
        rc = common.check_service_state()
        common.judge_rc(rc, True, 'check all services state failed')
    else:
        log.error("该集群环境节点数量不到五个节点，故不执行该脚本")

    return


def check_ping(ip):
    cmd = 'ping -c 3 %s | grep "0 received" | wc -l' % ip
    rc, stdout = common.run_command(node_ip, cmd)
    if '0' != stdout.strip():
        return False
    else:
        return True


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
    prepare_clean.nas_test_clean()
    log.info("（2）executing_case")
    executing_case1()
    clearing_environment()
    prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)
