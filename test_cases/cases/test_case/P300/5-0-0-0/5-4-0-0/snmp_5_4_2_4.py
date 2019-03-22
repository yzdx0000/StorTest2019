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
# date 2018-08-29
# @summary：
#           磁盘（不包括系统盘）状态比对
# @steps:
#           1> snmpwalk获取集群节点磁盘状态
#           2> pscli --command=get_disks获取集群节点磁盘状态
#           3> 比较获取信息是否一致
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
'''集群节点ip'''
SYSTEM_IP_0 = get_config.get_parastor_ip()
SYSTEM_IP_1 = get_config.get_parastor_ip(1)
SYSTEM_IP_2 = get_config.get_parastor_ip(2)


def compare_node_disks_state(node_ip):
    disk_status_list = snmp_common.get_disk_status()
    disk_devname_state = {}
    list_value = snmp_common.get_nodeid_by_nodeip(node_ip) - 1
    stdout = snmp_common.get_disk_value_info(node_ip)
    for disk_info in disk_status_list[list_value].split(";")[:-1]:
        devname = disk_info.split()[0][:-1]
        state = disk_info.split()[1]
        disk_devname_state[devname] = state
    for disk in stdout["result"]["disks"]:
        if (disk["devname"] not in disk_devname_state.keys()) or disk_devname_state[disk["devname"]] == disk["state"]:
            continue
        else:
            common.except_exit("disk state compare failed")

    return

def case():
    node_ip_list = get_config.get_allparastor_ips()
    for node_ip in node_ip_list:
        compare_node_disks_state(node_ip)
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