# -*-coding:utf-8 -*
#######################################################
# author 张呈宇
# date 2018-04-24
# @summary：
# 16-0-1-19       1个用户属于多个用户组极限测试
# @steps:
# case 1、1个用户属于多个用户组极限测试
# case 2、查看信息是否正确
# @changelog：
#
#######################################################
import os
import commands
import utils_path
import common
import shell
import nas_common
import log
import get_config
import prepare_clean

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)  # /mnt/volume1/snap/snap_16_0_1_19
SYSTEM_IP = get_config.get_parastor_ip()
node_ip = SYSTEM_IP


#######################################################
# 1.executing_case1
# @function：1个用户属于多个用户组极限测试；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：1个用户属于多个用户组极限测试；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
# 1> 创建用户组group1
# 2> 创建本地用户user1
# 3> 创建用户组second group1
# 4> 添加用户second group
#######################################################
def executing_case1():
    
    # 1> 创建访问分区
    log.info("\t[case1 create_access_zone ]")
    access_zone_name = "access_zone_16_0_1_19"
    node = common.Node()
    ids = node.get_nodes_id()
    access_zone_node_id_16_0_1_19 = ','.join(str(p) for p in ids)
    msg1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_0_1_19, name=access_zone_name)
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
    auth_provider_id_16_0_1_19 = check_result3["result"]["access_zones"][0]["auth_provider_id"]
    global auth_provider_id_16_0_1_19
    
    """ 1> 创建用户组group1"""
    log.info("\t[case1 create_auth_group 1]")
    cmd = "create_auth_group "
    check_result2 = nas_common.create_auth_group(auth_provider_id=auth_provider_id_16_0_1_19, name="group_16_0_1_19_0")
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s create_auth_group 1 failed!!!' % node_ip)
    global primary_group_id_16_0_1_19_0
    primary_group_id_16_0_1_19_0 = msg2["result"]

    """ 2> 创建本地用户user1"""
    log.info("\t[ create_auth_user ]")
    cmd = "create_auth_user "
    check_result2 = nas_common.create_auth_user(auth_provider_id=auth_provider_id_16_0_1_19,
                                                name="user_16_0_1_19", password='111111',
                                                primary_group_id=primary_group_id_16_0_1_19_0,
                                                home_dir="/home/user_16_0_1_19")
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s create_auth_user failed!!!' % node_ip)
    global user_id_16_0_1_19
    user_id_16_0_1_19 = msg2["result"]

    """ 3> 创建用户组second group1"""
    log.info("\t[create_second_auth_group 1]")
    cmd = "create_auth_group"
    check_result2 = nas_common.create_auth_group(auth_provider_id=auth_provider_id_16_0_1_19, name="group_16_0_1_19_1")
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s create_second_auth_group 1 failed!!!' % node_ip)
    second_group_id_16_0_1_19_list = []
    second_group_id_16_0_1_19_list.append(msg2["result"])

    """ 4> 添加用户second group"""
    for i in range(2, 11):
        """ 4-1> 创建用户组second group"""
        log.info("\t[create_second_auth_group %s]" % i)
        group_name = "group_16_0_1_19_%s" % i
        cmd = "create_auth_group"
        check_result2 = nas_common.create_auth_group(auth_provider_id=auth_provider_id_16_0_1_19,
                                                     name=group_name)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        msg2 = check_result2
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
            raise Exception('create_second_auth_group %s failed!!!' % i)
        second_group_id_16_0_1_19_list.append(msg2["result"])
        second_group_id_16_0_1_19 = ','.join(str(j) for j in second_group_id_16_0_1_19_list)
        """ 4-2> 更新用户的second group"""
        log.info("\t[update_auth_user ]")
        cmd = "update_auth_user"
        check_result1 = nas_common.update_auth_user(user_id=user_id_16_0_1_19,
                                                    password="222222",
                                                    primary_group_id=primary_group_id_16_0_1_19_0,
                                                    secondary_group_ids=second_group_id_16_0_1_19)
        log.info('node_ip = %s, cmd = %s, check_result1 = %s' % (node_ip, cmd, check_result1))
        msg1 = check_result1
        if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
            raise Exception('update_auth_user %s failed!!!' % i)
    return


#######################################################
# 2.executing_case2
# @function：查看修改结果是否正确
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：查看修改结果是否正确
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
# 1> get_auth_users
# 2> 判断信息是否正确
#######################################################
def executing_case2():
    log.info("\t[case2 get_auth_users ]")
    cmd = "get_auth_users"
    rc, check_result2 = nas_common.get_auth_users(auth_provider_id=auth_provider_id_16_0_1_19,
                                              group_id=primary_group_id_16_0_1_19_0)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "" or msg2["result"]["auth_users"] == []:
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_users failed!!!' % node_ip)

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
    clearing_environment()
    prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)