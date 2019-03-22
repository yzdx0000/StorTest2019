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
#           存储池占用率比较
# @steps:
#           1>通过snmp协议方式获取存储池占用率
#           2>通过p300系统发起请求获取存储池占用率
#           3>对两种方式获取到的存储池占用率进行比较
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]

def get_parastor_storage_pool_usage():
    """
    author:liyi
    date:  2018.8.31
    description:获取存储池利用率（P300系统发起请求获取的）
    :return:  返回字典形式 eg:{stor1:1}
    """
    cmd = "pscli --command=get_storage_pools"
    rc, stdout = common.run_command(common.SYSTEM_IP_0, cmd, print_flag=False)
    common.judge_rc(rc, 0, "get_storage_pools failed!!")
    check_result = common.json_loads(stdout)

    storage_name = []
    used_ratio = []
    for storage_info in check_result["result"]["storage_pools"]:
        storage_name.append(storage_info["name"])
        used_ratio.append(storage_info["used_ratio"])
    storage_pool_usage = dict(zip(storage_name,used_ratio))
    return storage_pool_usage


def case():
    """
    :return:
    """

    allparastor_ips = get_config.get_allparastor_ips()
    for node_ip in allparastor_ips:
        snmp_storage_pool_usage = snmp_common.get_storage_pool_usage()
        storage_pool_usage = snmp_common.get_parastor_storage_pool_usage()
        log.info("storage_pool_usage:%s" % storage_pool_usage)
        '''比较两种方式获取的存储池利用率是否一致'''
        if snmp_storage_pool_usage != snmp_storage_pool_usage:
            common.except_exit("%s storage_pool_usage compare is failed!!" % node_ip)
    log.info("storage_pool_usage compare is succeed!!")


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    log.info("case begin")
    case()
    prepare_clean.defect_test_clean(FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)