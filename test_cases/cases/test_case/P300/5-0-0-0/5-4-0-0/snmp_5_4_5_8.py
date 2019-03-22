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
#           集群节点cpu状态
# @steps:
#           1> snmpwalk获取集群各节点cpu状态
#           2> pscli --command=get_nodes获取集群各节点cpu状态
#           3> 比较获取信息是否一致
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
'''集群节点ip'''
SYSTEM_IP_0 = get_config.get_parastor_ip()
SYSTEM_IP_1 = get_config.get_parastor_ip(1)
SYSTEM_IP_2 = get_config.get_parastor_ip(2)

# [' ok; ', ' ok; ', ' ok; ']
node_cpu_status_list = snmp_common.get_node_cpu_status_list()

def compare_node_cpu_state(node_ip):
    list_value = snmp_common.get_nodeid_by_nodeip(node_ip) - 1
    stdout = snmp_common.get_node_value_info(node_ip)
    pscli_node_state = stdout["result"]["nodes"][0]["reported_info"]["hardware"]["cpu"][0]["status"]
    # mib_node_state = node_cpu_status_list[list_value].strip()[:-1]    # 虚拟机
    mib_node_state = node_cpu_status_list[list_value].split(";")[0].strip()  # 物理机
    if pscli_node_state == mib_node_state:
        return True
    else:
        common.except_exit("%s compare node cpu state failed!!!" % node_ip)

def case():
    node_ip_list = get_config.get_allparastor_ips()
    for node_ip in node_ip_list:
        compare_node_cpu_state(node_ip)
    log.info("compare node cpu state success")

def main():
    prepare_clean.test_prepare(FILE_NAME)
    log.info("case begin")
    case()
    snmp_common.disable_snmp()  # 关闭snmp
    prepare_clean.test_clean()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)