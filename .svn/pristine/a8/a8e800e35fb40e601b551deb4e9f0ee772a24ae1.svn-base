# -*-coding:utf-8 -*
#######################################################
# author 张呈宇
# date 2018-05-24
# @summary：
# 16-0-0-50         规格内连接多个LDAP认证服务器
# @steps:
# case1、集群内6节点，分别创建三个2节点访问区；
# case2、每个访问区配置不同的认证服务；
# case3、连接，启动nas服务，观察服务是否工作正常；
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
import prepare_clean

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)              # /mnt/volume/nas/nas_16_0_0_50
SYSTEM_IP = get_config.get_parastor_ip()
node_ip = SYSTEM_IP


#######################################################
# 1.executing_case1
# @function：集群内6节点，分别创建三个2节点访问区；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：集群内6节点，分别创建三个2节点访问区；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
#
#######################################################
def executing_case1():
    log.info("\t[手动创建6节点的节点池 ]")
    log.info("\t[case1 集群内6节点，分别创建三个2节点访问区 ]")

    return


#######################################################
# 2.executing_case2
# @function：每个访问区配置不同的认证服务；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：每个访问区配置不同的认证服务；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
#  1> add_auth_provider_ldap
#  2> get_auth_providers_ldap
#  3> check_auth_provider
#######################################################
def executing_case2():
    '''1> add_auth_provider_ldap '''
    log.info("\t[case2-1 add_auth_provider_ldap ]")
    '''1-1> add_auth_provider_ldap 1'''
    log.info("\t[case2-1-1 add_auth_provider_ldap 1 ]")
    global LDAP_IP
    LDAP_IP = nas_common.LDAP_IP_ADDRESSES
    global LDAP_BASE_DN
    LDAP_BASE_DN = nas_common.LDAP_BASE_DN
    cmd = "add_auth_provider_ldap"
    check_result2 = nas_common.add_auth_provider_ldap(name="nas_16_0_0_50_1_ldap", base_dn=LDAP_BASE_DN,
                                                      ip_addresses=LDAP_IP, port=389)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s add_auth_provider_ldap failed!!!' % node_ip)
    global id_16_0_0_50_1
    id_16_0_0_50_1 = msg2["result"]

    '''1-2> add_auth_provider_ldap 2'''
    log.info("\t[case2-1-2 add_auth_provider_ldap 2 ]")
    global LDAP_2_IP
    LDAP_2_IP = nas_common.LDAP_2_IP_ADDRESSES
    global LDAP_2_BASE_DN
    LDAP_2_BASE_DN = nas_common.LDAP_2_BASE_DN
    cmd = "add_auth_provider_ldap"
    check_result2 = nas_common.add_auth_provider_ldap(name="nas_16_0_0_50_2_ldap", base_dn=LDAP_2_BASE_DN,
                                                      ip_addresses=LDAP_2_IP, port=389)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s add_auth_provider_ldap failed!!!' % node_ip)
    global id_16_0_0_50_2
    id_16_0_0_50_2 = msg2["result"]

    '''1-3> add_auth_provider_ldap 3'''
    log.info("\t[case2-1-3 add_auth_provider_ldap 3 ]")
    global LDAP_3_IP
    LDAP_3_IP = nas_common.LDAP_3_IP_ADDRESSES
    global LDAP_3_BASE_DN
    LDAP_3_BASE_DN = nas_common.LDAP_3_BASE_DN
    cmd = "add_auth_provider_ldap"
    check_result2 = nas_common.add_auth_provider_ldap(name="nas_16_0_0_50_3_ldap", base_dn=LDAP_3_BASE_DN,
                                                      ip_addresses=LDAP_3_IP, port=389)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s add_auth_provider_ldap failed!!!' % node_ip)
    global id_16_0_0_50_3
    id_16_0_0_50_3 = msg2["result"]

    '''2> get_auth_providers_ldap'''
    log.info("\t[case2 get_auth_providers_ldap ]")
    '''2-1> get_auth_providers_ldap 1'''
    log.info("\t[case2-2-1 get_auth_providers_ldap 1]")
    wait_time1 = random.randint(2, 5)
    time.sleep(wait_time1)
    cmd = "get_auth_providers_ldap"
    check_result2 = nas_common.get_auth_providers_ldap(ids=id_16_0_0_50_1)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_providers_ldap failed!!!' % node_ip)
    name1 = msg2["result"]["auth_providers"][0]["name"]
    base_dn1 = msg2["result"]["auth_providers"][0]["base_dn"]
    id1 = msg2["result"]["auth_providers"][0]["id"]
    key1 = msg2["result"]["auth_providers"][0]["key"]
    ip_addresses1 = msg2["result"]["auth_providers"][0]["ip_addresses"][0]
    port1 = msg2["result"]["auth_providers"][0]["port"]
    type1 = msg2["result"]["auth_providers"][0]["type"]
    if name1 != "nas_16_0_0_50_1_ldap":
        raise Exception('%s name1 error!!!' % node_ip)
    if base_dn1 != LDAP_BASE_DN:
        raise Exception('%s base_dn1 error!!!' % node_ip)
    if id1 != id_16_0_0_50_1:
        raise Exception('%s id1 error!!!' % node_ip)
    if key1 != id_16_0_0_50_1:
        raise Exception('%s key1 error!!!' % node_ip)
    if ip_addresses1 != LDAP_IP:
        raise Exception('%s ip_addresses1 error!!!' % node_ip)
    if port1 != 389:
        raise Exception('%s port1 error!!!' % node_ip)
    if type1 != "LDAP":
        raise Exception('%s type1 error!!!' % node_ip)

    '''2-2> get_auth_providers_ldap 1'''
    log.info("\t[case2-2-2 get_auth_providers_ldap 2]")
    cmd = "get_auth_providers_ldap "
    check_result2 = nas_common.get_auth_providers_ldap(ids=id_16_0_0_50_2)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_providers_ldap failed!!!' % node_ip)
    name1 = msg2["result"]["auth_providers"][0]["name"]
    base_dn1 = msg2["result"]["auth_providers"][0]["base_dn"]
    id1 = msg2["result"]["auth_providers"][0]["id"]
    key1 = msg2["result"]["auth_providers"][0]["key"]
    ip_addresses1 = msg2["result"]["auth_providers"][0]["ip_addresses"][0]
    port1 = msg2["result"]["auth_providers"][0]["port"]
    type1 = msg2["result"]["auth_providers"][0]["type"]
    if name1 != "nas_16_0_0_50_2_ldap":
        raise Exception('%s name1 error!!!' % node_ip)
    if base_dn1 != LDAP_2_BASE_DN:
        raise Exception('%s base_dn1 error!!!' % node_ip)
    if id1 != id_16_0_0_50_2:
        raise Exception('%s id1 error!!!' % node_ip)
    if key1 != id_16_0_0_50_2:
        raise Exception('%s key1 error!!!' % node_ip)
    if ip_addresses1 != LDAP_2_IP:
        raise Exception('%s ip_addresses1 error!!!' % node_ip)
    if port1 != 389:
        raise Exception('%s port1 error!!!' % node_ip)
    if type1 != "LDAP":
        raise Exception('%s type1 error!!!' % node_ip)

    '''2-3> get_auth_providers_ldap 3'''
    log.info("\t[case2-2-3 get_auth_providers_ldap 3]")
    cmd = "get_auth_providers_ldap"
    check_result2 = nas_common.get_auth_providers_ldap(ids=id_16_0_0_50_3)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_providers_ldap failed!!!' % node_ip)
    name1 = msg2["result"]["auth_providers"][0]["name"]
    base_dn1 = msg2["result"]["auth_providers"][0]["base_dn"]
    id1 = msg2["result"]["auth_providers"][0]["id"]
    key1 = msg2["result"]["auth_providers"][0]["key"]
    ip_addresses1 = msg2["result"]["auth_providers"][0]["ip_addresses"][0]
    port1 = msg2["result"]["auth_providers"][0]["port"]
    type1 = msg2["result"]["auth_providers"][0]["type"]
    if name1 != "nas_16_0_0_50_3_ldap":
        raise Exception('%s name1 error!!!' % node_ip)
    if base_dn1 != LDAP_3_BASE_DN:
        raise Exception('%s base_dn1 error!!!' % node_ip)
    if id1 != id_16_0_0_50_3:
        raise Exception('%s id1 error!!!' % node_ip)
    if key1 != id_16_0_0_50_3:
        raise Exception('%s key1 error!!!' % node_ip)
    if ip_addresses1 != LDAP_3_IP:
        raise Exception('%s ip_addresses1 error!!!' % node_ip)
    if port1 != 389:
        raise Exception('%s port1 error!!!' % node_ip)
    if type1 != "LDAP":
        raise Exception('%s type1 error!!!' % node_ip)

    '''3> check_auth_provider'''
    log.info("\t[case2 check_auth_provider ]")
    '''3-1> check_auth_provider 1'''
    log.info("\t[case2-3-1 check_auth_provider 1]")
    wait_time1 = random.randint(2, 5)
    time.sleep(wait_time1)
    cmd = "check_auth_provider"
    check_result2 = nas_common.check_auth_provider(provider_id=id_16_0_0_50_1)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s check_auth_provider 1 failed!!!' % node_ip)

    '''3-2> check_auth_provider 2'''
    log.info("\t[case2-3-1 check_auth_provider 2]")
    wait_time1 = random.randint(2, 5)
    time.sleep(wait_time1)
    cmd = "check_auth_provider --id=%s"
    check_result2 = nas_common.check_auth_provider(provider_id=id_16_0_0_50_2)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s check_auth_provider 2 failed!!!' % node_ip)

    '''3-3> check_auth_provider 3'''
    log.info("\t[case2-3-1 check_auth_provider 3]")
    wait_time1 = random.randint(2, 5)
    time.sleep(wait_time1)
    cmd = "check_auth_provider"
    check_result2 = nas_common.check_auth_provider(provider_id=id_16_0_0_50_3)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s check_auth_provider 3 failed!!!' % node_ip)

    # 1> 创建访问分区
    log.info("\t[case1 create_access_zone ]")
    access_zone_name = "access_zone_16_0_0_50_1"
    node = common.Node()
    nodes = node.get_nodes_id()
    ids = []
    ids.append(nodes[0])
    ids.append(nodes[1])
    m = len(ids)
    access_zone_node_id_16_1_1_27 = ','.join(str(p) for p in ids)
    node_name_list = nas_common.get_node_name_list(ids)
    cmd = "create_access_zone"
    msg1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_1_1_27, name=access_zone_name,
                                         auth_provider_id=id_16_0_0_50_1)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, msg1))
        raise Exception('%s create_access_zone failed!!!' % node_ip)
    access_zone_id_1 = msg1["result"]

    access_zone_name = "access_zone_16_0_0_50_2"
    node = common.Node()
    nodes = node.get_nodes_id()
    ids = []
    ids.append(nodes[2])
    ids.append(nodes[3])
    m = len(ids)
    access_zone_node_id_16_1_1_27 = ','.join(str(p) for p in ids)
    node_name_list = nas_common.get_node_name_list(ids)
    cmd = "create_access_zone"
    msg1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_1_1_27, name=access_zone_name,
                                         auth_provider_id=id_16_0_0_50_2)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, msg1))
        raise Exception('%s create_access_zone failed!!!' % node_ip)
    access_zone_id_2 = msg1["result"]

    access_zone_name = "access_zone_16_0_0_50_3"
    node = common.Node()
    nodes = node.get_nodes_id()
    ids = []
    ids.append(nodes[4])
    ids.append(nodes[5])
    m = len(ids)
    access_zone_node_id_16_1_1_27 = ','.join(str(p) for p in ids)
    node_name_list = nas_common.get_node_name_list(ids)
    cmd = "create_access_zone"
    msg1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_1_1_27, name=access_zone_name,
                                         auth_provider_id=id_16_0_0_50_3)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, msg1))
        raise Exception('%s create_access_zone failed!!!' % node_ip)
    access_zone_id_3 = msg1["result"]

    # 2> 启动NAS
    log.info("\t[ enable_nas 1]")
    msg2 = nas_common.enable_nas(access_zone_id=access_zone_id_1)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s enable_nas failed!!!' % node_ip)

    log.info("\t[ enable_nas 2]")
    msg2 = nas_common.enable_nas(access_zone_id=access_zone_id_2)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s enable_nas failed!!!' % node_ip)

    log.info("\t[ enable_nas 3]")
    msg2 = nas_common.enable_nas(access_zone_id=access_zone_id_3)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s enable_nas failed!!!' % node_ip)
    return


#######################################################
# 3.executing_case3
# @function：连接，启动nas服务，观察服务是否工作正常；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：连接，启动nas服务，观察服务是否工作正常；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
#
#
#######################################################
def executing_case3():

    log.info("\t[case3 get_auth_users ]")
    wait_time1 = random.randint(2, 5)
    time.sleep(wait_time1)
    log.info("\t[case3-1 get_auth_users 1]")
    cmd = "get_auth_users"
    rc, check_result2 = nas_common.get_auth_users(auth_provider_id=id_16_0_0_50_1)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "" or msg2["result"]["auth_users"] == []:
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_users 1 failed!!!' % node_ip)
    totalnumber = msg2["result"]["total"]
    name_list = []
    for i in range(0, totalnumber):
        name_list.append(msg2["result"]["auth_users"][i]["name"])
    if "用户1" not in name_list:
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_users 信息不对 failed!!!' % node_ip)

    log.info("\t[case3-2 get_auth_users 2]")
    cmd = "get_auth_users "
    rc, check_result2 = nas_common.get_auth_users(auth_provider_id=id_16_0_0_50_2)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "" or msg2["result"]["auth_users"] == []:
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_users 2 failed!!!' % node_ip)
    totalnumber = msg2["result"]["total"]
    name_list = []
    for i in range(0, totalnumber):
        name_list.append(msg2["result"]["auth_users"][i]["name"])
    if "ldaptest" not in name_list:
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_users 信息不对 failed!!!' % node_ip)

    log.info("\t[case3-3 get_auth_users 3]")
    cmd = "get_auth_users "
    rc, check_result2 = nas_common.get_auth_users(auth_provider_id=id_16_0_0_50_3)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "" or msg2["result"]["auth_users"] == []:
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_users 3 failed!!!' % node_ip)
    totalnumber = msg2["result"]["total"]
    name_list = []
    for i in range(0, totalnumber):
        name_list.append(msg2["result"]["auth_users"][i]["name"])
    if "ldapuser59082" not in name_list:
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_users 信息不对 failed!!!' % node_ip)

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
    prepare_clean.nas_test_prepare(FILE_NAME)
    log.info("（2）executing_case")
    executing_case1()
    executing_case2()
    executing_case3()
    # prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)