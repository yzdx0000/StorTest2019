# -*-coding:utf-8 -*
#######################################################
# author 张呈宇
# date 2018-05-22
# @summary：
# 16-0-1-37             用户规格极限测试
# @steps:
# case1、查询已有用户
# case2、创建4万个用户
# case3、ldapserver删除用户
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


FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)              # /mnt/volume/nas/nas_16_0_1_36
SYSTEM_IP = get_config.get_parastor_ip()
node_ip = SYSTEM_IP


#######################################################
# 1.executing_case1
# @function：集群添加ldap认证；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：集群添加ldap认证；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
# 1> 集群添加ldap认证；
# pscli --command=add_auth_provider_ldap --name=ldap_test --ip_addresses=x.x.x.x --base_dn=dc=xxx,dc=com --port=389
# 2> 通过命令pscli --command=get_auth_provider_ldap查看ldap认证服务器配置信息；
# 3> 通过命令行pscli --command=check_auth_provider --ids=x查看认证配置信息是否能够正确的连接ldap认证服务器；
# 4> 查询LDAP认证用户；
# pscli --command=get_auth_users --auth_provider_id=x，x为LDAP认证服务器id
# 5> 查询LDAP认证用户组；
# pscli --command=get_auth_groups --auth_provider_id=x，x为LDAP认证服务器id
#######################################################
def executing_case1():
    log.info("\t[case1-1 add_auth_provider_ldap]")
    global LDAP_IP
    LDAP_IP = nas_common.LDAP_IP_ADDRESSES
    global LDAP_BASE_DN
    LDAP_BASE_DN = nas_common.LDAP_BASE_DN
    global LDAP_BIND_DN
    LDAP_BIND_DN = nas_common.LDAP_BIND_DN
    global LDAP_BIND_PASSWORD
    LDAP_BIND_PASSWORD = nas_common.LDAP_BIND_PASSWORD
    global LDAP_USER_SEARCH_PATH
    LDAP_USER_SEARCH_PATH = nas_common.LDAP_USER_SEARCH_PATH
    global LDAP_GROUP_SEARCH_PATH
    LDAP_GROUP_SEARCH_PATH = nas_common.LDAP_GROUP_SEARCH_PATH
    cmd = "add_auth_provider_ldap "
    check_result2 = nas_common.add_auth_provider_ldap(name="nas_16_0_1_36_ldap", base_dn=LDAP_BASE_DN,
                                                      ip_addresses=LDAP_IP, port=389,
                                                      user_search_path=LDAP_USER_SEARCH_PATH,
                                                      group_search_path=LDAP_GROUP_SEARCH_PATH)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s add_auth_provider_ldap failed!!!' % node_ip)
    global id_16_0_1_36
    id_16_0_1_36 = msg2["result"]

    log.info("\t[case1-2 get_auth_providers_ldap ]")
    cmd = "get_auth_providers_ldap "
    check_result2 = nas_common.get_auth_providers_ldap(ids=id_16_0_1_36)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_providers_ldap failed!!!' % node_ip)
    base_dn = msg2["result"]["auth_providers"][0]["base_dn"]
    ip_addresses = msg2["result"]["auth_providers"][0]["ip_addresses"][0]
    name = msg2["result"]["auth_providers"][0]["name"]
    port = msg2["result"]["auth_providers"][0]["port"]
    type = msg2["result"]["auth_providers"][0]["type"]
    group_search_path = msg2["result"]["auth_providers"][0]["group_search_path"]
    user_search_path = msg2["result"]["auth_providers"][0]["user_search_path"]
    if base_dn != LDAP_BASE_DN:
        raise Exception('%s base_dn error!!!' % node_ip)
    if ip_addresses != LDAP_IP:
        raise Exception('%s ip_addresses error!!!' % node_ip)
    if name != "nas_16_0_1_36_ldap":
        raise Exception('%s name error!!!' % node_ip)
    if port != 389:
        raise Exception('%s port error!!!' % node_ip)
    if type != "LDAP":
        raise Exception('%s type error!!!' % node_ip)
    if group_search_path != LDAP_GROUP_SEARCH_PATH:
        raise Exception('%s group_search_path error!!!' % node_ip)
    if user_search_path != LDAP_USER_SEARCH_PATH:
        raise Exception('%s user_search_path error!!!' % node_ip)

    log.info("\t[case1-3 check_auth_provider ]")
    wait_time1 = random.randint(2, 5)
    time.sleep(wait_time1)
    cmd = "check_auth_provider "
    check_result2 = nas_common.check_auth_provider(provider_id=id_16_0_1_36)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s check_auth_provider failed!!!' % node_ip)

    log.info("\t[case1-4 get_auth_users]")
    wait_time1 = random.randint(1, 3)
    time.sleep(wait_time1)
    cmd = "get_auth_users "
    rc, check_result2 = nas_common.get_auth_users(auth_provider_id=id_16_0_1_36)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "" or msg2["result"]["auth_users"] == []:
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s get_auth_users failed!!!' % node_ip)
    global usertotalnumber
    usertotalnumber = msg2["result"]["total"]
    return


#######################################################
# 2.executing_case2
# @function：添加并查询用户组信息；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：添加并查询用户组信息；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
# 1> ldapserver添加用户组
# 2> nas端查询用户组
#######################################################
def executing_case2():
    '''1> ldapserver添加用户组'''
    global totalnumber
    totalnumber = 40000   # 40000
    global indexnumber
    indexnumber = 2
    addnumber = totalnumber - usertotalnumber
    global ldapserver_ip
    ldapserver_ip = LDAP_IP
    for i in range(usertotalnumber+1, totalnumber+1):
        log.info("\t[case2-1 ldapserver添加用户组 %s]" % i)
        username = "user%s" % i
        user_home_dir = "/home/%s" % username
        cmd = "ssh %s echo "" > /root/ldapuser.ldif &&" \
              " echo 'dn: uid=%s,ou=People,dc=test,dc=com' > /root/ldapuser.ldif &&" \
              " echo 'uid: %s' >> /root/ldapuser.ldif &&" \
              " echo 'cn: %s' >> /root/ldapuser.ldif &&" \
              " echo 'sn: %s' >> /root/ldapuser.ldif &&" \
              " echo 'mail: %s@test.com' >> /root/ldapuser.ldif &&" \
              " echo 'objectClass: person' >> /root/ldapuser.ldif &&" \
              " echo 'objectClass: organizationalPerson' >> /root/ldapuser.ldif &&" \
              " echo 'objectClass: inetOrgPerson' >> /root/ldapuser.ldif &&" \
              " echo 'objectClass: posixAccount' >> /root/ldapuser.ldif &&" \
              " echo 'objectClass: top' >> /root/ldapuser.ldif &&" \
              " echo 'userPassword: {crypt}x' >> /root/ldapuser.ldif &&" \
              " echo 'loginShell: /bin/bash' >> /root/ldapuser.ldif &&" \
              " echo 'uidNumber: 1002' >> /root/ldapuser.ldif &&" \
              " echo 'gidNumber: 1002' >> /root/ldapuser.ldif &&" \
              " echo 'homeDirectory: %s' >> /root/ldapuser.ldif &&" \
              " ldapadd -x -w 111111 -D cn=root,dc=test,dc=com -f /root/ldapuser.ldif"\
              % (ldapserver_ip, username, username, username, username, username, user_home_dir)
        rc, stdout, stderr = shell.ssh(ldapserver_ip, cmd)
        if rc != 0:
            log.info("rc = %s" % (rc))
            log.error("WARNING: \ncmd = %s\nstdout = %s\nstderr = %s" % (cmd, stdout, stderr))
            raise Exception('%s create ldapserver user failed!!!' % node_ip)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, stdout))

        '''2> nas端查询用户组'''
        log.info("\t[case2-2 nas端查询用户 %s]" % i)
        log.info("\t[case2-2-1 get_auth_users]")
        cmd = "get_auth_users "
        rc, check_result2 = nas_common.get_auth_users(auth_provider_id=id_16_0_1_36, start=indexnumber, limit=1)
        indexnumber = indexnumber + 1
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        msg2 = check_result2
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "" or msg2["result"]["auth_users"] == []:
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
            raise Exception('%s get_auth_users failed!!!' % node_ip)

        log.info("\t[case2-2-2 Parameter comparison %s]" % i)
        auth_provider_id = msg2["result"]["auth_users"][0]["auth_provider_id"]
        home_dir = msg2["result"]["auth_users"][0]["home_dir"]
        id = msg2["result"]["auth_users"][0]["id"]
        key = msg2["result"]["auth_users"][0]["key"]
        name = msg2["result"]["auth_users"][0]["name"]
        primary_group_id = msg2["result"]["auth_users"][0]["primary_group_id"]
        if auth_provider_id != id_16_0_1_36:
            raise Exception('%s auth_provider_id error!!!' % node_ip)
        if home_dir != user_home_dir:
            raise Exception('%s home_dir error!!!' % node_ip)
        if id != 1002:
            raise Exception('%s id error!!!' % node_ip)
        if key != 1002:
            raise Exception('%s key error!!!' % node_ip)
        if name != username:
            raise Exception('%s name error!!!' % node_ip)
        if primary_group_id != 1002:
            raise Exception('%s primary_group_id error!!!' % node_ip)
        i = i+1
    return


#######################################################
# 3.executing_case3
# @function：ldapserver删除用户组；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：ldapserver删除用户组；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
#
#
#######################################################
def executing_case3():
    log.info("\t[case3 ldapserver删除用户]")
    for i in range(usertotalnumber + 1, totalnumber + 1):
        log.info("\t[case3 ldapserver删除用户 %s]" % i)
        username = "user%s" % i
        cmd = "ssh %s ldapdelete -x -D 'cn=root,dc=test,dc=com' -w 111111 'uid=%s,ou=People,dc=test,dc=com'"\
              % (ldapserver_ip, username)
        rc, stdout, stderr = shell.ssh(ldapserver_ip, cmd)
        if rc != 0:
            log.info("rc = %s" % (rc))
            log.error("WARNING: \ncmd = %s\nstdout = %s\nstderr = %s" % (cmd, stdout, stderr))
            raise Exception('%s delete ldapserver user failed!!!' % node_ip)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, stdout))

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