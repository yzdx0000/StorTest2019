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
#           磁盘使用率（不包括系统盘）比对
# @steps:
#           1> snmpwalk获取集群节点各磁盘对应的使用率
#           2> pscli --command=get_disks获取集群节点各磁盘的使用率
#           3> 比较获取信息是否一致
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
'''集群节点ip'''
SYSTEM_IP_0 = get_config.get_parastor_ip()
SYSTEM_IP_1 = get_config.get_parastor_ip(1)
SYSTEM_IP_2 = get_config.get_parastor_ip(2)

# ['/dev/sde: 0.01; /dev/sdf: 0.01; /dev/sdg: 0.01; /dev/sdh: 0.01; /dev/sdi: 0.01;    \
#  /dev/sdc: 0.01; /dev/sdd: 0.01; /dev/sdb: 0.00; '  * disks_num]


def compare_node_disks_usage(node_ip):
    disks_usage_list = snmp_common.get_disk_usage_rate()
    list_value = snmp_common.get_nodeid_by_nodeip(node_ip) - 1
    disk_devname_and_usage = {}
    stdout = snmp_common.get_disk_value_info(node_ip)

    for disk_info in disks_usage_list[list_value].split("; ")[:-1]:
        devname = str(disk_info.split()[0][:-1])
        usage = str(disk_info.split()[1])
        disk_devname_and_usage[devname] = usage         # 生成devid为键rpm为值的字典

    for disk in stdout["result"]["disks"]:
        disk_devname = str(disk["devname"])
        if disk_devname not in disk_devname_and_usage.keys() or disk["usedState"] == "UNUSED":
            continue

        mib_usage = float(disk_devname_and_usage[disk_devname])                     # MIB树中信息
        pscli_total_bytes = float(disk["capacity"])                                 # pscli中信息
        pscli_used_bytes = pscli_total_bytes - float(disk["avail_bytes"])
        pscli_usage = float("%.2f" % (pscli_used_bytes / pscli_total_bytes))

        if abs(mib_usage - pscli_usage) <= snmp_common.normal_percent_scope_point:
            continue
        else:
            log.info("failed info mib:%s pscli:%s" % (mib_usage, pscli_usage))
            common.except_exit("%s disk usage compare failed" % node_ip)

    return

def case():
    node_ip_list = get_config.get_allparastor_ips()
    for node_ip in node_ip_list:
        compare_node_disks_usage(node_ip)
    log.info("system usage compare is success")

def main():
    prepare_clean.test_prepare(FILE_NAME)
    log.info("case begin")
    case()
    snmp_common.disable_snmp()  # 关闭snmp
    prepare_clean.test_clean()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)