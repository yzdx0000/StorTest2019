# -*-coding:utf-8 -*
#######################################################
# author 张呈宇
# date 2018-04-23
# @summary：
# 16-0-1-14     用户组查看
# @steps:
# 1> 创建用户组group
# 2> 查看用户组group

# case1、查看本地用户组信息，查询内容包括：
# "auth_provider_id": 4, ——认证服务器ID，本地认证服务器时值为4
# "id": 1000001, ——用户组id，系统自动分配
# "key": 1000001, ——用户组key，系统自动分配
# "name": "local_group_name1", ——用户组名称，自己定义的
# "version": 0 ——没有含义，不用管
# @changelog：
#
#######################################################
import os
import commands
import utils_path
import shell
import common
import nas_common
import get_config
import log
import prepare_clean

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)  # /mnt/volume1/snap/snap_16_0_1_14
node_ip = get_config.get_parastor_ip()


def executing_case1():
    """ 1> 创建用户组group"""
    log.info("\t[case1 create_auth_group 1]")
    access_zone_name = "access_zone_16_0_1_14"
    node = common.Node()
    ids = node.get_nodes_id()
    access_zone_node_id_16_0_1_14 = ','.join(str(p) for p in ids)
    cmd = "create_access_zone "
    check_result1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_0_1_14, name=access_zone_name)
    log.info('node_ip = %s, cmd = %s, check_result1 = %s' % (node_ip, cmd, check_result1))
    msg1 = check_result1
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        raise Exception('%s create_access_zone failed!!!' % node_ip)
    access_zone_id = msg1["result"]

    # 2> 启动NAS
    log.info("\t[ enable_nas ]")
    msg2 = nas_common.enable_nas(access_zone_id=access_zone_id)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s enable_nas failed!!!' % node_ip)

    cmd = "get_auth_providers_local"
    check_result2 = nas_common.get_auth_providers_local()
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    global auth_provider_id_16_0_1_14
    auth_provider_id_16_0_1_14 = check_result2["result"]["auth_providers"][0]["id"]
    cmd = "create_auth_group "
    check_result2 = nas_common.create_auth_group(auth_provider_id=auth_provider_id_16_0_1_14, name="group_16_0_1_14")
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s create_auth_group 1 failed!!!' % node_ip)
    primary_group_id_16_0_1_14 = msg2["result"]

    """2> 查看用户组group"""
    log.info("\t[case1 get_auth_groups ]")
    cmd = "get_auth_groups "
    check_result2 = nas_common.get_auth_groups(auth_provider_id=auth_provider_id_16_0_1_14)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_groups failed!!!' % node_ip)
    auth_groups = msg2["result"]["auth_groups"]
    d = len(auth_groups)-1
    group_id = msg2["result"]["auth_groups"][d]["id"]
    group_name = msg2["result"]["auth_groups"][d]["name"]
    if group_id != primary_group_id_16_0_1_14:
        raise Exception('%s group_id ERROR!!!' % node_ip)
    if group_name != "group_16_0_1_14":
        raise Exception('%s group_name ERROR!!!' % node_ip)

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
    clearing_environment()
    prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)
