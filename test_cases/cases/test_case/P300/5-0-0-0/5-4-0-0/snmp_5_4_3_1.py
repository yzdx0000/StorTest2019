# -*-coding:utf-8 -*
import os

import utils_path
import common
import get_config
import log
import prepare_clean
import snmp_common
####################################################################################
#
# author liyi
# date 2018-09-1
# @summary：
#           最小元数据副本数比较
# @steps:
#           1>通过snmp协议方式获取最小元数据副本数
#           2>通过p300系统发起请求获取最小元数据副本数
#           3>对两种方式获取到的最小元数据副本数进行比较
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]

def case():
    """
    :return:
    """

    allparastor_ips = get_config.get_allparastor_ips()
    for node_ip in allparastor_ips:
        snmp_min_meta_replica = snmp_common.get_min_meta_replica()
        min_meta_replica = snmp_common.get_parastor_min_meta_replica()
        log.info("min_meta_replica:%s" % min_meta_replica)
        if snmp_min_meta_replica != min_meta_replica:
            common.except_exit("%s min_meta_replica compare is failed!!" % node_ip)
    log.info("min_meta_replica compare is succeed!!")


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    log.info("case begin")
    case()
    prepare_clean.defect_test_clean(FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)