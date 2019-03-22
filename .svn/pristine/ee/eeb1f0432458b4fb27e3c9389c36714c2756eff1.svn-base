# -*-coding:utf-8 -*
#######################################################
# author 张呈宇
# date 2018-04-24
# @summary：
# 16-0-1-26        创建/删除/创建100个用户组，观察gid循环递增不重复
# @steps:
# case1、创建2个删除1个用户组，直到创建100个；观察这100个用户组的gid;
# case2、查看用户组
# @changelog：
#
#######################################################
import os
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
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)  # /mnt/volume1/snap/snap_16_0_1_26
SYSTEM_IP = get_config.get_parastor_ip()
node_ip = SYSTEM_IP


#######################################################
# 1.executing_case1
# @function：创建2个删除1个用户组，直到创建100个；观察这100个用户组的gid；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：创建2个删除1个用户组，直到创建100个；观察这100个用户组的gid；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
# 1> 创建第一个用户组
# 2> 创建第二个用户组
# 3> 删除第一个用户组
# 4> 比较用户的uid
#######################################################
def executing_case1():
    # 1> 创建访问分区
    log.info("\t[case1 create_access_zone ]")
    access_zone_name = "access_zone_16_0_1_26"
    node = common.Node()
    ids = node.get_nodes_id()
    access_zone_node_id_16_0_1_26 = ','.join(str(p) for p in ids)
    msg1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_0_1_26, name=access_zone_name)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('%s create_access_zone failed!!!' % node_ip)
    access_zone_id = msg1["result"]

    # 2> 启动NAS
    log.info("\t[ enable_nas ]")
    msg2 = nas_common.enable_nas(access_zone_id=access_zone_id, protocol_types="NFS")
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s enable_nas failed!!!' % node_ip)

    # 3> 查看NAS是否按配置启动
    log.info("\t[ get_access_zones ]")
    check_result3 = nas_common.get_access_zones(ids=access_zone_id)
    name = check_result3["result"]["access_zones"][0]["name"]
    if name != access_zone_name:
        common.except_exit('%s enable_nas failed!!!' % node_ip)
    auth_provider_id_16_0_1_26 = check_result3["result"]["access_zones"][0]["auth_provider_id"]
    global auth_provider_id_16_0_1_26

    global group_id_16_0_1_26_delete_list
    group_id_16_0_1_26_delete_list = []
    group_id_16_0_1_26_list = []
    group_id_16_0_1_26_list.append(0)
    for i in range(1, 101):
        """1> 创建第一个用户组"""
        log.info("\t[case1 create_auth_group %s 1]" % i)
        group_name = "group_16_0_1_26_%s_1" % i
        cmd = "create_auth_group "
        check_result2 = nas_common.create_auth_group(auth_provider_id=auth_provider_id_16_0_1_26,
                                                     name=group_name)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        msg2 = check_result2
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
            raise Exception('create_auth_group %s 1 failed!!!' % i)
        group_id_16_0_1_26_1 = msg2["result"]

        """2> 创建第二个用户组"""
        log.info("\t[case1 create_auth_group %s 2]" % i)
        group_name = "group_16_0_1_26_%s_2" % i
        cmd = "create_auth_group "
        check_result2 = nas_common.create_auth_group(auth_provider_id=auth_provider_id_16_0_1_26,
                                                     name=group_name)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        msg2 = check_result2
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
            raise Exception('create_auth_group %s 2 failed!!!' % i)
        group_id_16_0_1_26_list.append(msg2["result"])
        group_id_16_0_1_26_delete_list.append(msg2["result"])

        """ 3> 删除第一个用户组"""
        log.info("\t[ delete_auth_groups ]")
        cmd = "delete_auth_groups "
        check_result2 = nas_common.delete_auth_groups(ids=group_id_16_0_1_26_1)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        msg2 = check_result2
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
            raise Exception('delete_auth_groups %s 1 failed!!!' % i)

        """4> 比较用户的uid"""
        a = group_id_16_0_1_26_list[i] - group_id_16_0_1_26_list[i - 1]
        if a <= 0:
            log.error('group_id_16_0_1_26_list[%s] is ERROR' % i)
            raise Exception('group_id_16_0_1_26_list[%s] is ERROR' % i)
    return


#######################################################
# 2.executing_case2
# @function：查看用户组
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：查看用户组
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
# 1>
# 2>
#######################################################
def executing_case2():
    log.info("\t[case2 get_auth_groups ]")
    cmd = "get_auth_groups "
    check_result2 = nas_common.get_auth_groups(auth_provider_id=auth_provider_id_16_0_1_26)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "" or msg2["result"]["auth_groups"] == []:
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_groups failed!!!' % node_ip)
    auth_groups = msg2["result"]["auth_groups"]
    d = len(auth_groups)
    print d

    return


#######################################################
# @function：清理环境
# @parameter：
# @return：
# @steps:
#######################################################
def clearing_environment():
    log.info("（3）clearing_environment")
    log.info("（3）删除用户组")
    group_id_16_0_1_26_delete = ','.join(str(p) for p in group_id_16_0_1_26_delete_list)
    cmd = "delete_auth_groups "
    check_result2 = nas_common.delete_auth_groups(ids=group_id_16_0_1_26_delete)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s delete_auth_groups failed!!!' % node_ip)
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
    clearing_environment()
    prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)