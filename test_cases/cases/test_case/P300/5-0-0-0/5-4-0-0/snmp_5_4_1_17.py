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
#           系统数据状态比较
# @steps:
#           1>通过snmp协议方式获取系统数据状态
#           2>通过p300系统发起请求获取系统数据状态
#           3>对两种方式获取到的系统数据状态进行比较
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]

def get_parastor_system_data_status():
    """
     author:liyi
     date:  2018.8.31
     description:获取系统数据状态（P300系统发起请求获取的）
     :return:
     """
    cmd = "pscli --command=get_cluster_overview"
    rc, stdout = common.run_command(common.SYSTEM_IP_0, cmd, print_flag=False)
    common.judge_rc(rc, 0, "get_cluster_overview failed!!")
    check_result = common.json_loads(stdout)
    system_data_status = []
    system_data_status.append(check_result["result"]["cluster_data_state"])
    return system_data_status

def case():
    """
    :return:
    """

    allparastor_ips = get_config.get_allparastor_ips()
    for node_ip in allparastor_ips:
        snmp_system_data_status = snmp_common.get_system_data_abnormal()
        system_data_status = snmp_common.get_parastor_system_data_status()
        log.info("system_data_status:%s" % system_data_status)
        '''比较两种方式获取的内存是否一致'''
        if snmp_system_data_status != system_data_status:
            common.except_exit("%s system_data_status compare is failed!!" % node_ip)
    log.info("system_data_status compare is succeed!!")


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    log.info("case begin")
    case()
    prepare_clean.defect_test_clean(FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)