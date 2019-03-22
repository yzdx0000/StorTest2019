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
#           磁盘坏道数
# @steps:
#           1> snmpwalk获取集群节点各磁盘对应的坏道数
#           2> pscli --command=get_disks获取集群节点各磁盘的坏道数
#           3> 比较获取信息是否一致
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
'''集群节点ip'''
SYSTEM_IP_0 = get_config.get_parastor_ip()
SYSTEM_IP_1 = get_config.get_parastor_ip(1)
SYSTEM_IP_2 = get_config.get_parastor_ip(2)


def compare_node_disks_bad_sector(node_ip):
    disk_bad_sector = snmp_common.get_disk_bad_sector_number()
    disk_devid_and_badsector = {}
    list_value = snmp_common.get_nodeid_by_nodeip(node_ip) - 1
    stdout = snmp_common.get_disk_value_info(node_ip)
    for disk_info in disk_bad_sector[list_value].split("; ")[:-1]:
        devid = str(disk_info.split()[0][:-1])
        badsector = str(disk_info[3:])
        disk_devid_and_badsector[devid] = badsector

    for disk in stdout["result"]["disks"]:
        pscli_panel_number = str(disk["physical_disks"][0]["panel_number"])
        mib_badsector = disk_devid_and_badsector[pscli_panel_number].strip()
        pscli_badsector = str(disk["physical_disks"][0]["hdd_bad_sectors_count"])
        if (pscli_panel_number not in disk_devid_and_badsector.keys()) or \
                mib_badsector == pscli_badsector:
            continue
        else:
            log.info("failed info mib:%s pscli:%s" % (mib_badsector, pscli_badsector))
            common.except_exit("disk smart info compare failed")

    return

def case():
    node_ip_list = get_config.get_allparastor_ips()
    for node_ip in node_ip_list:
        compare_node_disks_bad_sector(node_ip)
    log.info("system disk smart info compare is success")

def main():
    prepare_clean.test_prepare(FILE_NAME)
    log.info("case begin")
    case()
    snmp_common.disable_snmp()  # 关闭snmp
    prepare_clean.test_clean()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)