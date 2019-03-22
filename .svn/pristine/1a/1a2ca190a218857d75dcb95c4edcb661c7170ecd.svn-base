# -*-coding:utf-8 -*
#######################################################
# author zhangchengyu
# date 2018-04-20
# @summary：
# 16-0-1-1     用户创建
# @steps:
# case1、通过启动nas服务来启动本地认证服务器服务；
# pscli --command=enable_nas --access_zone_id=x --protocol_types=['NFS', 'SMB', 'FTP']
# case2、创建本地用户user1；
# pscli --command=create_auth_user --auth_provider_id=x --name=user1 --password=xxx --primary_group_id=x
# --secondary_group_ids=x --home_dir=/home/${name}
# case3、查看本地用户user1；
# pscli --command=get_auth_users --auth_provider_id=x
# @changelog：
#
#######################################################
import os
import random
import time
import utils_path
import common
import get_config
import log
import nas_common
import shell
import prepare_clean

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)  # /mnt/volume1/snap/snap_13_0_0_0
node_ip = get_config.get_parastor_ip()


#######################################################
# 1.executing_case1
# @function：通过启动nas服务来启动本地认证服务器服务；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：通过启动nas服务来启动本地认证服务器服务；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
# 1> 创建访问分区
# 2> 启动NAS
# 3> 查看NAS是否按配置启动
# 4> 查看认证服务
#######################################################
def executing_case1():
    # 1> 创建访问分区
    log.info("\t[case1 create_access_zone ]")
    access_zone_name = "access_zone_16_0_1_1"
    node = common.Node()
    ids = node.get_nodes_id()
    access_zone_node_id_16_0_1_1 = ','.join(str(p) for p in ids)
    msg1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_0_1_1, name=access_zone_name)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('%s create_access_zone failed!!!' % node_ip)
    access_zone_id = msg1["result"]

    # 2> 启动NAS
    log.info("\t[ enable_nas ]")
    msg2 = nas_common.enable_nas(access_zone_id=access_zone_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s enable_nas failed!!!' % node_ip)

    # 3> 查看NAS是否按配置启动
    log.info("\t[ get_access_zones ]")
    check_result3 = nas_common.get_access_zones(ids=access_zone_id)
    name = check_result3["result"]["access_zones"][0]["name"]
    if name != access_zone_name:
        common.except_exit('%s enable_nas failed!!!' % node_ip)
    auth_provider_id_16_0_1_1 = check_result3["result"]["access_zones"][0]["auth_provider_id"]
    global auth_provider_id_16_0_1_1

    # 4> 查看认证服务
    log.info("\t[ auth_provider_server_status ]")
    nas_common.check_nas_status()
    # check_result4 = nas_common.get_nodes()
    # msg4 = check_result4
    # if msg4["result"]["nodes"][0]["reported_info"]["nas_protocol"]["server_status"]["auth_provider_server_status"] != "SERV_STATE_OK":
    #     common.except_exit('%s auth_provider_server_status ERROR!!!' % node_ip)

    return


#######################################################
# 2.executing_case2
# @function：创建本地用户user1；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：创建本地用户user1；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
# 1> 创建用户组group1
# 2> 创建用户user1
#######################################################
def executing_case2():
    # 1> 创建用户组group1
    log.info("\t[case2 create_auth_group ]")
    cmd = "create_auth_group "
    check_result2 = nas_common.create_auth_group(auth_provider_id=auth_provider_id_16_0_1_1, name="group1")
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s create_auth_group failed!!!' % node_ip)
    global primary_group_id_16_0_1_1
    primary_group_id_16_0_1_1 = msg2["result"]

    # 2> 创建用户user1
    log.info("\t[ create_auth_user ]")
    cmd = "create_auth_user"
    check_result2 = nas_common.create_auth_user(auth_provider_id=auth_provider_id_16_0_1_1,
                                                name="user1", password='111111',
                                                primary_group_id=primary_group_id_16_0_1_1,
                                                secondary_group_ids="", home_dir="/home")
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s create_auth_user failed!!!' % node_ip)
    global user_id_16_0_1_1
    user_id_16_0_1_1 = msg2["result"]

    return


#######################################################
# 3.executing_case3
# @function：查看本地用户user1；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：查看本地用户user1；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
#
#######################################################
def executing_case3():
    log.info("\t[case3 get_auth_users ]")
    cmd = "get_auth_users "
    rc, check_result2 = nas_common.get_auth_users(auth_provider_id=auth_provider_id_16_0_1_1)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_users failed!!!' % node_ip)
    home_dir = msg2["result"]["auth_users"][0]["home_dir"]
    id = msg2["result"]["auth_users"][0]["id"]
    name = msg2["result"]["auth_users"][0]["name"]
    primary_group_id = msg2["result"]["auth_users"][0]["primary_group_id"]
    primary_group_name = msg2["result"]["auth_users"][0]["primary_group_name"]
    if home_dir != "/home":
        raise Exception('%s home_dir Error!!!' % node_ip)
    if id != user_id_16_0_1_1:
        raise Exception('%s id Error!!!' % node_ip)
    if name != "user1":
        raise Exception('%s name Error!!!' % node_ip)
    if primary_group_id != primary_group_id_16_0_1_1:
        raise Exception('%s primary_group_id Error!!!' % node_ip)
    if primary_group_name != "group1":
        raise Exception('%s primary_group_name Error!!!' % node_ip)
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
    log.info("（2）executing_case")
    executing_case1()
    executing_case2()
    executing_case3()
    clearing_environment()
    prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)
