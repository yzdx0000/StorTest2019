# -*-coding:utf-8 -*
#######################################################
# author zhangchengyu
# date 2018-08-21
# @summary：
# 16_0_0_71_2         循环重复启停NAS100次
# @steps:
# case1、1、循环启停nas服务100次；2、观察集群NAS服务状态；
# @changelog：
#
#######################################################
import os
import time
import utils_path
import common
import nas_common
import log
import shell
import get_config
import prepare_clean


FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)              # /mnt/volume/nas/nas_16_0_0_71_2
NODE_IP_1 = get_config.get_parastor_ip(0)
NODE_IP_2 = get_config.get_parastor_ip(1)
NODE_IP_3 = get_config.get_parastor_ip(2)
NODE_IP_LIST = [NODE_IP_1, NODE_IP_2, NODE_IP_3]
node_ip = get_config.get_parastor_ip()
LDAP_IP = nas_common.LDAP_IP_ADDRESSES
LDAP_BASE_DN = nas_common.LDAP_BASE_DN
LDAP_USER_NAME = nas_common.LDAP_USER_2_NAME


#######################################################
# 1.executing_case1
# @function：循环启停nas服务100次；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：循环启停nas服务100次；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
#  1> create_access_zone
#  2> get_access_zones
#  3> enable_nas
#  4> 查看NAS服务状态
#  5> disable_nas
#######################################################
def executing_case1():

    '''1> create_access_zone'''
    log.info("\t[1 create_access_zone ]")
    access_zone_name = "access_zone_16_0_0_71_2"
    cmd = 'pscli --command=get_nodes'
    rc, stdout = common.run_command(node_ip, cmd)
    outtext = common.json_loads(stdout)
    nodes = outtext['result']['nodes']
    ids = []
    for node in nodes:
        ids.append(node['data_disks'][0]['nodeId'])
    print ids
    access_zone_node_id = ','.join(str(p) for p in ids)
    m = len(ids)
    msg2 = nas_common.create_access_zone(name=access_zone_name,
                                         node_ids=access_zone_node_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s create_access_zone failed!!!' % node_ip)
    access_zone_id_16_0_0_71_2 = msg2["result"]

    '''2> get_access_zones'''
    log.info("\t[2 get_access_zones ]")
    msg2 = nas_common.get_access_zones(ids=access_zone_id_16_0_0_71_2)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "" or msg2["result"]["access_zones"][0] == "":
        common.except_exit('%s get_access_zones failed!!!' % node_ip)

    for i in range(1, 101):
        '''3> enable_nas '''
        log.info("\t[3 enable_nas %s]" % i)
        msg2 = nas_common.enable_nas(access_zone_id=access_zone_id_16_0_0_71_2)
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            common.except_exit('%s enable_nas failed!!!' % node_ip)

        '''4> 查看NAS服务状态'''
        log.info("\t[4 check_nas_status %s]" % i)
        rc = nas_common.check_nas_status(180)
        common.judge_rc(rc, 0, "超过规定时间（默认180s），NAS服务状态依然异常")

        """5> disable_nas"""
        log.info("\t[5 disable_nas ]")
        msg2 = nas_common.disable_nas(access_zone_id=access_zone_id_16_0_0_71_2)
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            common.except_exit('%s disable_nas failed!!!' % node_ip)
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
    prepare_clean.nas_test_clean()
    log.info("（2）executing_case")
    executing_case1()
    clearing_environment()
    prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)
