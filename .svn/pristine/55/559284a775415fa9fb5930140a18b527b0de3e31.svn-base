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
#           磁盘转速
# @steps:
#           1> snmpwalk获取集群节点各磁盘对应的转速
#           2> pscli --command=get_disks获取集群节点各磁盘的转速
#           3> 比较获取信息是否一致
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
'''集群节点ip'''
SYSTEM_IP_0 = get_config.get_parastor_ip()
SYSTEM_IP_1 = get_config.get_parastor_ip(1)
SYSTEM_IP_2 = get_config.get_parastor_ip(2)

# ['4: 0; 5: 0; 6: 0; 7: 0; 8: 0; 2: 0; 3: 0; 0: 0; 1: 0; '  * disks_num]


def compare_node_disks_rpm(node_ip):
    disks_rpm_list = snmp_common.get_disk_rpm()
    list_value = snmp_common.get_nodeid_by_nodeip(node_ip) - 1
    disk_devid_and_rpm = {}
    stdout = snmp_common.get_disk_value_info(node_ip)

    for disk_info in disks_rpm_list[list_value].split("; ")[:-1]:
        devid = str(disk_info.split()[0][:-1])
        rpm = str(disk_info[3:])
        disk_devid_and_rpm[devid] = rpm         # 生成devid为键rpm为值的字典

    for disk in stdout["result"]["disks"]:
        pscli_panel_number = str(disk["physical_disks"][0]["panel_number"])
        mib_rpm = disk_devid_and_rpm[pscli_panel_number].strip()               # MIB树中信息
        pscli_rpm = str(disk["physical_disks"][0]["disk_rpm"])          # pscli中信息

        if (pscli_panel_number not in disk_devid_and_rpm.keys()) or \
                mib_rpm == pscli_rpm:
            continue
        else:
            common.except_exit("disk rpm compare failed")

    return

def case():
    node_ip_list = get_config.get_allparastor_ips()
    for node_ip in node_ip_list:
        compare_node_disks_rpm(node_ip)
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