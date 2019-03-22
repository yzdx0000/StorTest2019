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
#           oStor状态比较
# @steps:
#           1>通过snmp协议方式获取ostor状态
#           2>通过p300系统发起请求获取到的ostor状态
#           3>对两种方式获取到的opera状态进行比较
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]

def case():
    """
    :return:
    """

    allparastor_ips = get_config.get_allparastor_ips()
    for node_ip in allparastor_ips:
        snmp_ostor_status = snmp_common.get_one_node_service_ostor_status(node_ip)
        ostor_status = snmp_common.get_one_node_ostor_status(node_ip)
        log.info("ostor_status:%s" % ostor_status)
        if snmp_ostor_status != ostor_status:
            common.except_exit("%s ostor_status compare is failed!!" % node_ip)
    log.info("ostor_status compare is succeed!!")


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    log.info("case begin")
    case()
    prepare_clean.defect_test_clean(FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)