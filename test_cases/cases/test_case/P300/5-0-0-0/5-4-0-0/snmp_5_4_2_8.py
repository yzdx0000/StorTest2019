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
#           磁盘温度
# @steps:
#           1> snmpwalk获取集群节点各磁盘对应的温度
#           2> pscli --command=get_disks获取集群节点各磁盘的温度
#           3> 比较获取信息是否一致
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
'''集群节点ip'''
SYSTEM_IP_0 = get_config.get_parastor_ip()
SYSTEM_IP_1 = get_config.get_parastor_ip(1)
SYSTEM_IP_2 = get_config.get_parastor_ip(2)


def compare_node_disks_temperature(node_ip):
    disks_temperature_list = snmp_common.get_disk_temperature()
    list_value = snmp_common.get_nodeid_by_nodeip(node_ip) - 1
    disk_devid_and_temperature = {}
    stdout = snmp_common.get_disk_value_info(node_ip)

    for disk_info in disks_temperature_list[list_value].split("; ")[:-1]:
        devid = str(disk_info.split()[0][:-1])
        temperature = str(disk_info[3:])
        disk_devid_and_temperature[devid] = temperature

    for disk in stdout["result"]["disks"]:
        pscli_panel_number = str(disk["physical_disks"][0]["panel_number"])
        mib_temperature = disk_devid_and_temperature[pscli_panel_number].strip()           # MIB树中信息
        pscli_temperature = str(disk["physical_disks"][0]["temperature"])          # pscli中信息

        if (pscli_panel_number not in disk_devid_and_temperature.keys()) or \
                mib_temperature == pscli_temperature:
            continue
        else:
            common.except_exit("disk temperature compare failed")

    return

def case():
    node_ip_list = get_config.get_allparastor_ips()
    for node_ip in node_ip_list:
        compare_node_disks_temperature(node_ip)
    log.info("system temperature compare is success")

def main():
    prepare_clean.test_prepare(FILE_NAME)
    log.info("case begin")
    case()
    snmp_common.disable_snmp()  # 关闭snmp
    prepare_clean.test_clean()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)