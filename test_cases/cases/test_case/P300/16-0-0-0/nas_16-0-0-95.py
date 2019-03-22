# -*-coding:utf-8 -*
#######################################################
# author 张呈宇
# date 2018-04-20
# @summary：
# 16-0-0-95      本地认证的查询测试
# @steps:
# case1、集群配置3节点的访问分区；
# pscli --command=create_access_zone --node_ids=1,2,3 --name=az_test
# case2、启动访问区的nas服务；
# pscli --command=enable_nas --access_zone_id=x --protocol_types=NFS
# case3、观察本地认证服务信息填写是否正确；
# pscli --command=get_auth_providers_local
#
#######################################################
import os
import time
import random
import commands
import utils_path
import common
import nas_common
import log
import get_config
import prepare_clean


FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)              # /mnt/volume1/snap/snap_13_0_0_0
SYSTEM_IP = get_config.get_parastor_ip()
node_ip = SYSTEM_IP


#######################################################
# 1.executing_case1
# @function：集群配置3节点的访问分区；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：集群配置3节点的访问分区；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
#
#######################################################
def executing_case1():
    log.info("\t[case1 create_access_zone ]")
    global access_zone_name
    access_zone_name = "access_zone_16_0_0_95"
    node = common.Node()
    ids = node.get_nodes_id()
    access_zone_node_id = ','.join(str(p) for p in ids)
    msg2 = nas_common.create_access_zone(name=access_zone_name,
                                         node_ids=access_zone_node_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s create_access_zone failed!!!' % node_ip)
    global id_16_0_0_95
    id_16_0_0_95 = msg2["result"]
    return


#######################################################
# 2.executing_case2
# @function：启动访问区的nas服务；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：启动访问区的nas服务；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
#
#
#######################################################
def executing_case2():
    log.info("\t[case2 enable_nas ]")
    cmd = "enable_nas"
    check_result2 = nas_common.enable_nas(access_zone_id=id_16_0_0_95, protocol_types="NFS")
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    wait_time1 = random.randint(10, 15)
    time.sleep(wait_time1)
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s enable_nas failed!!!' % node_ip)
    return


#######################################################
# 3.executing_case3
# @function：观察本地认证服务信息填写是否正确；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：观察本地认证服务信息填写是否正确；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:

#######################################################
def executing_case3():
    log.info("\t[case3 get_auth_providers_local ]")
    cmd = "get_auth_providers_local"
    check_result1 = nas_common.get_auth_providers_local()
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
    msg1 = check_result1
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        raise Exception('%s get_auth_providers_local failed!!!' % node_ip)
    name = msg1["result"]["auth_providers"][0]["name"]
    type = msg1["result"]["auth_providers"][0]["type"]
    if name != access_zone_name or type != "LOCAL":
        raise Exception('%s enable_nas failed!!!' % node_ip)

    return


#######################################################
# @function：清理环境
# @parameter：
# @return：
# @steps:
#######################################################
def clearing_environment():

    log.info("（3）clearing_environment")

    return


#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def executing_case():
    log.info("（2）executing_case")

    '''
    1、测试执行
    2、结果检查
    '''

    return


#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def preparing_environment():
    log.info("（1）preparing_environment")

    '''
    1、下发nas相关的配置
    2、创建nas测试相关的目录和文件
    '''

    return


#######################################################
# 函数功能：本用例入口函数
# 函数入参：无
# 函数返回值：无
#######################################################
def nas_main():
    preparing_environment()
    prepare_clean.nas_test_prepare(FILE_NAME)
    log.info("（2）executing_case")
    executing_case1()
    executing_case2()
    executing_case3()
    clearing_environment()
    prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)