# -*-coding:utf-8 -*
#######################################################
# author 张呈宇
# date 2018-04-23
# @summary：
# 16-0-1-23      用户组极限测试（50000）
# @steps:
# case 1、创建5万个本地用户组；
# @changelog：
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
import shell
import get_config
import json
import prepare_clean

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)  # /mnt/volume1/snap/snap_16_0_1_23
SYSTEM_IP = get_config.get_parastor_ip()
node_ip = SYSTEM_IP


#######################################################
# 1.executing_case1
# @function：创建5万个本地用户组；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：创建5万个本地用户组；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
# 1>
#######################################################
def executing_case1():
    # 0-1> 创建访问分区
    log.info("\t[0-1 create_access_zone ]")
    access_zone_name = "access_zone_16_0_1_23"
    node = common.Node()
    ids = node.get_nodes_id()
    access_zone_node_id_16_0_1_23 = ','.join(str(p) for p in ids)
    cmd = "create_access_zone"
    check_result1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_0_1_23, name=access_zone_name)
    log.info('node_ip = %s, cmd = %s, check_result1 = %s' % (node_ip, cmd, check_result1))
    msg1 = check_result1
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        raise Exception('%s create_access_zone failed!!!' % node_ip)
    access_zone_id = msg1["result"]

    # 0-2> 启动NAS
    log.info("\t[0-2 enable_nas ]")
    cmd = "enable_nas "
    check_result2 = nas_common.enable_nas(access_zone_id=access_zone_id)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s enable_nas failed!!!' % node_ip)

    """1>获取auth_provider_id"""
    cmd = "get_auth_providers_local"
    check_result2 = nas_common.get_auth_providers_local()
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    global auth_provider_id_16_0_1_23
    auth_provider_id_16_0_1_23 = check_result2["result"]["auth_providers"][0]["id"]

    """2>创建5万个本地用户组"""
    cmd = "get_auth_groups "
    check_result2 = nas_common.get_auth_groups(auth_provider_id=auth_provider_id_16_0_1_23)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_groups failed!!!' % node_ip)
    prenumber = msg2["result"]["total"]
    global auth_group_list
    auth_group_list = []
    for i in range(prenumber + 1, 50001):
        log.info("\t[case1-1 create_auth_group %s]" % i)
        group_name = "group_16_0_1_23_%s" % i
        cmd = "create_auth_group"
        check_result2 = nas_common.create_auth_group(auth_provider_id=auth_provider_id_16_0_1_23,
                                                     name=group_name)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        msg2 = check_result2
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
            raise Exception('create_auth_group i failed!!!' % (i))
        auth_group_list.append(msg2["result"])

    i = 50001
    log.info("\t[case1-2 create_auth_group %s]" % i)
    group_name = "group_16_0_1_23_%s" % i
    cmd = "create_auth_group"
    check_result2 = nas_common.create_auth_group(auth_provider_id=auth_provider_id_16_0_1_23,
                                                 name=group_name)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "ILLEGAL_OPERATION" or msg2["detail_err_msg"].find("has reached the limit:50000") == -1:
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('创建50001个用户组成功!!!' )

    return


#######################################################
# 2.executing_case2
# @function：查询本地用户组group；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：查询本地用户组group；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
#
#######################################################
def executing_case2():
    log.info("\t[case2 get_auth_groups ]")
    cmd = "get_auth_groups"
    check_result2 = nas_common.get_auth_groups(auth_provider_id=auth_provider_id_16_0_1_23)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_groups failed!!!' % node_ip)
    d = msg2["result"]["total"]
    print d
    if d != 50000:
        log.error('node_ip = %s, 创建的用户组个数不为50000' % node_ip)
        raise Exception('%s get_auth_groups failed!!!' % node_ip)
    return


#######################################################
# @function：清理环境
# @parameter：
# @return：
# @steps:
#######################################################
def clearing_environment():
    log.info("（3）clearing_environment")
    d = len(auth_group_list)
    k = d // 10000
    m = d - k * 10000
    log.info("（3）1-1.删除用户组最后%s个" % m)
    if m > 0:
        global auth_group_delete_1_list
        auth_group_delete_1_list = []
        for c in range(k * 10000, d):
            auth_group_delete_1_list.append(auth_group_list[c])
        auth_group_delete_1 = ','.join(str(p) for p in auth_group_delete_1_list)
        cmd = "delete_auth_groups"
        check_result2 = nas_common.delete_auth_groups(ids=auth_group_delete_1)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        msg2 = check_result2
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
            raise Exception('%s delete_auth_groups %s-%s failed!!!' % (node_ip, k * 10000, d))

    for j in range(0, k):
        a = j * 10000
        b = j * 10000 + 10000
        log.info("（3）1-2.删除用户前%s-%s个" % (a, b))
        global auth_group_delete_2_list
        auth_group_delete_2_list = []
        for i in range(a, b):
            auth_group_delete_2_list.append(auth_group_list[i])
        auth_group_delete = ','.join(str(p) for p in auth_group_delete_2_list)
        cmd = "delete_auth_groups"
        check_result2 = nas_common.delete_auth_groups(ids=auth_group_delete)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        msg2 = check_result2
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
            raise Exception('%s delete_auth_groups %s-%s failed!!!' % (node_ip, a, b))
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
    clearing_environment()
    prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)