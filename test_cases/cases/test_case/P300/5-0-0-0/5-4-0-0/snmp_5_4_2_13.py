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
#           磁盘厂商比对
# @steps:
#           1> snmpwalk获取集群节点各磁盘对应的厂商
#           2> pscli --command=get_disks获取集群节点各磁盘的厂商
#           3> 比较获取信息是否一致
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
'''集群节点ip'''
SYSTEM_IP_0 = get_config.get_parastor_ip()
SYSTEM_IP_1 = get_config.get_parastor_ip(1)
SYSTEM_IP_2 = get_config.get_parastor_ip(2)

# ['4: VMware; 5: VMware; 6: VMware; 7: VMware; 8: VMware; 2: VMware; 3: VMware; 0: ; 1: VMware; '  * disks_num]

def compare_node_disks_vendor(node_ip):
    disks_vendor_list = snmp_common.get_disk_vendor()
    list_value = snmp_common.get_nodeid_by_nodeip(node_ip) - 1
    disk_devid_and_vendor = {}
    stdout = snmp_common.get_disk_value_info(node_ip)

    for disk_info in disks_vendor_list[list_value].split("; ")[:-1]:
        devid = str(disk_info.split()[0][:-1])
        vendor = str(disk_info[3:])
        disk_devid_and_vendor[devid] = vendor         # 生成devid为键rpm为值的字典

    for disk in stdout["result"]["disks"]:
        pscli_panel_number = str(disk["physical_disks"][0]["panel_number"])
        mib_vendor = disk_devid_and_vendor[pscli_panel_number].strip()               # MIB树中信息
        pscli_vendor = str(disk["physical_disks"][0]["vendor"])               # pscli中信息

        if (pscli_panel_number not in disk_devid_and_vendor.keys()) or \
                mib_vendor == pscli_vendor:
            continue
        else:
            common.except_exit("disk rpm compare failed")

    return

def case():
    node_ip_list = get_config.get_allparastor_ips()
    for node_ip in node_ip_list:
        compare_node_disks_vendor(node_ip)
    log.info("system rpm compare is success")

def main():
    prepare_clean.test_prepare(FILE_NAME)
    log.info("case begin")
    case()
    snmp_common.disable_snmp()  # 关闭snmp
    prepare_clean.test_clean()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)