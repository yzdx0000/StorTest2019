#!usr/bin/python
# -*-coding:utf-8 -*

import utils_path
import os
import prepare_clean
import common
import snmp_common
import get_config
import log

####################################################################################
#
# author duyuli
# date 2018-08-30
# @summary：
#           集群节点磁盘容量（总容量，已用容量，可用容量）
# @steps:
#           1> snmpwalk获取集群各节点容量信息
#           2> pscli --command=get_nodes获取集群各节点容量信息
#           3> 比较获取信息是否一致
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
'''集群节点ip'''
SYSTEM_IP_0 = get_config.get_parastor_ip()
SYSTEM_IP_1 = get_config.get_parastor_ip(1)
SYSTEM_IP_2 = get_config.get_parastor_ip(2)
normal_byte_scope = 50000000   # 执行时间不同给定50M的范围误差

# ['71219281920', '41724936192', '41724936192', '41724936192']  第一项无效 ip为 0.0.0.0 非集群节点
# node_total_capacity = snmp_common.get_node_total_capacity()
# ['610970289', '390070272', '383778816', '381681664']          第一项无效 ip为 0.0.0.0 非集群节点
# node_used_capacity = snmp_common.get_node_used_capacity()
# ['70608311631', '41334865920', '41341157376', '41343254528']  第一项无效 ip为 0.0.0.0 非集群节点
# node_unused_capacity = snmp_common.get_node_unused_capacity()
# ['70608311631', '41334865920', '41341157376', '41343254528']  第一项无效 ip为 0.0.0.0 非集群节点
# node_available_capacity = snmp_common.get_node_available_capacity()

def compare_node_total_capacity(node_ip):
    node_total_capacity = snmp_common.get_node_total_capacity()
    list_value = snmp_common.get_nodeid_by_nodeip(node_ip)
    stdout = snmp_common.get_node_value_info(node_ip)
    pscli_node_total_capacity = int(stdout["result"]["nodes"][0]["total_bytes"])
    mib_node_total_capacity = int(node_total_capacity[list_value])
    if abs(pscli_node_total_capacity - mib_node_total_capacity) <= normal_byte_scope:
        return True
    else:
        common.except_exit("%s compare node total capacity failed!!!" % node_ip)

def compare_node_used_capacity(node_ip):
    node_used_capacity = snmp_common.get_node_used_capacity()
    list_value = snmp_common.get_nodeid_by_nodeip(node_ip)
    stdout = snmp_common.get_node_value_info(node_ip)
    pscli_node_used_capacity = int(stdout["result"]["nodes"][0]["used_bytes"])
    mib_node_used_capacity = int(node_used_capacity[list_value])
    if pscli_node_used_capacity - mib_node_used_capacity < normal_byte_scope:
        return True
    else:
        common.except_exit("%s compare node total capacity failed!!!" % node_ip)

def compare_node_unused_capacity(node_ip):
    node_unused_capacity = snmp_common.get_node_unused_capacity()
    list_value = snmp_common.get_nodeid_by_nodeip(node_ip)
    stdout = snmp_common.get_node_value_info(node_ip)
    pscli_node_unused_capacity = int(stdout["result"]["nodes"][0]["avail_bytes"])
    mib_node_unused_capacity = int(node_unused_capacity[list_value])
    if pscli_node_unused_capacity - mib_node_unused_capacity < normal_byte_scope:
        return True
    else:
        common.except_exit("%s compare node total capacity failed!!!" % node_ip)

def case():
    node_ip_list = get_config.get_allparastor_ips()
    for node_ip in node_ip_list:
        compare_node_total_capacity(node_ip)
        compare_node_used_capacity(node_ip)
        compare_node_unused_capacity(node_ip)
    log.info("compare node capacity success")

def main():
    prepare_clean.test_prepare(FILE_NAME)
    log.info("case begin")
    case()
    snmp_common.disable_snmp()  # 关闭snmp
    prepare_clean.test_clean()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)