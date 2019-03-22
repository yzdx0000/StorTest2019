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
# date 2018-08-28
# @summary：
#           系统盘利用率比对
# @steps:
#           1> snmpwalk获取集群节点系统盘利用率
#           2> df -h获取集群节点系统盘利用率
#           3> 比较获取信息是否一致
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
'''集群节点ip'''
SYSTEM_IP_0 = get_config.get_parastor_ip()
SYSTEM_IP_1 = get_config.get_parastor_ip(1)
SYSTEM_IP_2 = get_config.get_parastor_ip(2)


def compare_system_disk_usage(node_ip):
    system_disk_usage_list = snmp_common.get_system_disk_usage()
    list_value = snmp_common.get_nodeid_by_nodeip(node_ip) - 1

    cmd = "df -h"
    rc, stdout = common.run_command(node_ip, cmd)
    common.judge_rc(rc, 0, "get system disk usage failed!!!")

    system_disk_usage = ""
    for line in stdout.split("\n"):
        value_list = line.split()
        if value_list[5] == "/":
            system_disk_usage = value_list[4].replace("%", "")
            break
    if abs(int(system_disk_usage) - int(system_disk_usage_list[list_value])) <= snmp_common.normal_percent_scope:
        return True
    else:
        common.except_exit("compare system usage failed!!!")

def case():
    node_ip_list = get_config.get_allparastor_ips()
    for node_ip in node_ip_list:
        compare_system_disk_usage(node_ip)
    log.info("system disk stat compare is success")

def main():
    prepare_clean.test_prepare(FILE_NAME)
    log.info("case begin")
    case()
    snmp_common.disable_snmp()  # 关闭snmp
    prepare_clean.test_clean()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)