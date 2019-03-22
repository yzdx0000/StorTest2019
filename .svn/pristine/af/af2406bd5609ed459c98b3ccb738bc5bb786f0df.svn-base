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
#           磁盘备用块数
# @steps:
#           1> snmpwalk获取集群节点各磁盘对应的备用块数
#           2> pscli --command=get_disks获取集群节点各磁盘的块数
#           3> 比较获取信息是否一致
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
'''集群节点ip'''
SYSTEM_IP_0 = get_config.get_parastor_ip()
SYSTEM_IP_1 = get_config.get_parastor_ip(1)
SYSTEM_IP_2 = get_config.get_parastor_ip(2)


def compare_node_disks_standby_block(node_ip):
    disks_standby_block_list = snmp_common.get_disk_bad_sector_number()
    list_value = snmp_common.get_nodeid_by_nodeip(node_ip) - 1
    disk_devid_and_standby_block = {}
    stdout = snmp_common.get_disk_value_info(node_ip)

    for disk_info in disks_standby_block_list[list_value].split("; ")[:-1]:
        devid = str(disk_info.split()[0][:-1])
        standby_block = str(disk_info[3:])
        disk_devid_and_standby_block[devid] = standby_block

    for disk in stdout["result"]["disks"]:
        pscli_panel_number = str(disk["physical_disks"][0]["panel_number"])
        mib_standby_block = disk_devid_and_standby_block[pscli_panel_number].strip()           # MIB树中信息
        pscli_standby_block = str(disk["physical_disks"][0]["hdd_bad_sectors_count"])   # pscli中信息

        if (pscli_panel_number not in disk_devid_and_standby_block.keys()) or \
                mib_standby_block == pscli_standby_block:
            continue
        else:
            log.info("failed info mib:%s, pscli:%s" % (mib_standby_block, pscli_standby_block))
            common.except_exit("disk standby block num compare failed")

    return

def case():
    node_ip_list = get_config.get_allparastor_ips()
    for node_ip in node_ip_list:
        compare_node_disks_standby_block(node_ip)
    log.info("system disk standby block compare is success")

def main():
    prepare_clean.test_prepare(FILE_NAME)
    log.info("case begin")
    case()
    snmp_common.disable_snmp()  # 关闭snmp
    prepare_clean.test_clean()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)