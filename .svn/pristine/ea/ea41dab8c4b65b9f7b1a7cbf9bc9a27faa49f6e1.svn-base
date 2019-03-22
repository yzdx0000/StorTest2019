# -*-coding:utf-8 -*
#######################################################
# author zhangchengyu
# date 2018-08-14
# @summary：
# 16_0_2_18     5节点，其中一个节点oMgcd服务异常
# @steps:
# 0> 检查环境是否大于等于五个节点，大于等于五节点可以执行该脚本
# 1> 制造一个节点处于oMgcd服务异常状态
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
        """1> 制造一个节点处于oMgcd服务异常状态"""
        log.info("\t[1 制造一个节点处于oMgcd服务异常状态]")
        """获取故障节点的id"""
        rc, stdout = common.get_master()
        msg = common.json_loads(stdout)
        ip_master_a = str(msg["result"]["data_ips"][0]["ip_address"])       # 获取master的ip
        node = common.Node()
        id_master = node.get_node_id_by_ip(ip_master_a)                     # 获取master的id
        node_ip_1 = NODE_IP_LIST[random.randint(0, len(NODE_IP_LIST) - 1)]  # 获取故障节点ip
        node_id_1 = node.get_node_id_by_ip(node_ip_1)                       # 获取故障节点id
        node_id = node.get_node_id_by_ip(node_ip)                           # 获取当下执行操作节点id
        while id_master == node_id_1 or node_id == node_id_1:               # 排除当下执行命令的id与master的id
            node_ip_1 = NODE_IP_LIST[random.randint(0, len(NODE_IP_LIST) - 1)]
            node_id_1 = node.get_node_id_by_ip(node_ip_1)
        print node_ip_1
        """制造故障"""
        cmd = "ps -ef | grep oMgcd | grep -v grep |awk '{print $2}'"
        rc, pid = common.run_command(node_ip_1, cmd)
        common.judge_rc(rc, 0, "get PID of oMgcd fialed")
        cmd1 = "kill -SIGSTOP %s" % pid
        rc, stdout = common.run_command(node_ip_1, cmd1)
        common.judge_rc(rc, 0, "stop oMgcd failed")
        time.sleep(5)
        """"检查oMgcd进程是否被停止"""
        cmd2 = "ps afx | grep oMgcd | grep -v grep | awk '{print $3}'"
        rc, stdout = common.run_command(node_ip_1, cmd2)
        common.judge_rc(rc, 0, "check oMgcd failed")
        if stdout.find("Tsl") == -1:
            common.except_exit("检查oMgcd进程是否被停止失败")

        """ 2> 创建访问分区 """
        log.info("\t[2 create_access_zone ]")
        access_zone_name = "access_zone_16_0_2_18"
        node = common.Node()
        outtext = node.get_nodes()
        nodes = outtext['result']['nodes']
        ids = []
        for node in nodes:
            ids.append(node['data_disks'][0]['nodeId'])
        print ids
        access_zone_node_id_16_0_2_18 = ','.join(str(p) for p in ids)
        msg1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_0_2_18, name=access_zone_name)
        if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
            common.except_exit("有节点在oMgcd服务异常状态时，创建访问分区与预期不符，请检查节点状态与访问分区状态")

        """ 3> 恢复环境"""
        log.info("\t[3 recovery environment ]")
        """节点oMgcd服务恢复正常"""
        cmd1 = "kill -SIGCONT %s" % pid
        rc, stdout = common.run_command(node_ip_1, cmd1)
        common.judge_rc(rc, 0, "start oMgcd failed")
        time.sleep(10)
        """"检查oMgcd进程是否恢复正常"""
        cmd2 = "ps afx | grep oMgcd | grep -v grep | awk '{print $3}'"
        rc, stdout = common.run_command(node_ip_1, cmd2)
        common.judge_rc(rc, 0, "check oMgcd failed")
        if stdout.find("Ssl") == -1:
            common.except_exit("恢复oMgcd进程失败")
        """检查节点服务是否正常"""
        rc = common.check_service_state()
        common.judge_rc(rc, True, 'check all services state')
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
