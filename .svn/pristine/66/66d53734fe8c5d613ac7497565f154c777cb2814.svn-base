# -*-coding:utf-8 -*
import os
import time

import utils_path
import common
import get_config
import log
import prepare_clean
import remote
import nas_common

##########################################################################
#
# Author: zhanghan
# date 2018-11-15
# @summary：
#    posix客户端权限测试：u1属于多个组，检测目录权限；原P200测试用例23-0-3-1。
# @steps:
#    脚本运行前准备工作：a) 配置访问管理，包括访问区和Local认证服务器
#                        b) posix客户端授权并手动挂载，并将相应信息写入配置文件
#
#    1、获取节点信息:posix客户端ip、posix客户端挂载路径；
#    2、创建测试目录并将权限修改为777；
#    3、增加local认证服务器用户组/用户；
#    4、posix客户端创建与local认证服务器相同的用户和组；
#    5、测试主体，u1属于多个组，检测目录权限；
#    6、posix客户端删除第4步创建的用户/用户组；
#    7、删除第3步创建的local用户组/用户；
#
# @changelog：
##########################################################################

#################### 全局变量 ####################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[
    0]                 # 本脚本名字
FILE_NAME = FILE_NAME.replace('-', '_')
posix_file_dir = "posix_dir" + FILE_NAME
group_list = ["group1_" + FILE_NAME, "group2_" + FILE_NAME]
user_name = "user_" + FILE_NAME
user_passwd = "111111"


def case():
    log.info("1> 获取节点信息")

    client_ip = get_config.get_client_ip()
    log.info("posix client ip is: %s" % client_ip)

    # posix客户端需要预先手动挂载，且挂载目录需要与卷名称相同
    posix_mount_path = get_config.get_one_mount_path()
    log.info("posix_mount_path is: %s" % posix_mount_path)

    posix_file_location = os.path.join(posix_mount_path, posix_file_dir)
    log.info("posix_file_location is: %s" % posix_file_location)

    auth_provider_info = nas_common.get_auth_providers_local()
    auth_provider_id = auth_provider_info["result"]["auth_providers"][0]["id"]

    log.info("2> 创建测试目录")
    rc = common.command(
        "ssh %s \"mkdir %s\"" %
        (client_ip, posix_file_location))
    common.judge_rc(rc, 0, "mkdir testdir failed")
    rc = common.command(
        "ssh %s \"chmod %s %s\"" %
        (client_ip, "777", posix_file_location))
    common.judge_rc(rc, 0, "chmod testdir failed")

    log.info("3> 增加local认证服务器用户组/用户")
    log.info("3-1> 增加local认证服务器用户组")
    for g_num in range(len(group_list)):
        nas_common.create_auth_group(auth_provider_id, group_list[g_num])
    group_info = nas_common.get_auth_groups(auth_provider_id)
    group_info = group_info["result"]["auth_groups"]
    group_id_list = []
    for group_infp_tmp in group_info:
        if FILE_NAME in group_infp_tmp["name"]:
            group_id = group_infp_tmp["id"]
            group_id_list.append(group_id)

    log.info("3-2> 增加local认证服务器用户")
    primary_group_id = group_id_list[0]
    group_id_list_tmp = map(str, group_id_list)
    secondary_group_ids = ','.join(group_id_list_tmp)
    nas_common.create_auth_user(
        auth_provider_id,
        user_name,
        user_passwd,
        primary_group_id,
        secondary_group_ids)
    (rc, user_info) = nas_common.get_auth_users(auth_provider_id)
    user_info = user_info["result"]["auth_users"]
    user_id = ""
    for u_info_tmp in user_info:
        if FILE_NAME in u_info_tmp["name"]:
            user_id = u_info_tmp["id"]

    log.info("4> posix客户端创建与local认证服务器相同的用户和组")
    for g_num in range(len(group_list)):
        cmd_add_group = "ssh %s \"groupadd -g %d %s\"" % (
            client_ip, group_id_list[g_num], group_list[g_num])
        rc = common.command(cmd_add_group)
        common.judge_rc(rc, 0, "add group in client %s failed" % client_ip)

    cmd_add_user = "ssh %s \"useradd -g %s -G %s,%s -u %d %s\"" % (
        client_ip, group_list[0], group_list[0], group_list[1], user_id, user_name)
    rc = common.command(cmd_add_user)
    common.judge_rc(rc, 0, "add user in client %s failed" % client_ip)

    log.info("5> 测试主体：%s属于多个组，测试目录权限" % user_name)
    log.info("5-1> 创建测试目录并设置权限555")
    testdir = 'dir_' + FILE_NAME
    cmd = "ssh %s \"su %s -c 'cd %s;mkdir %s;chmod 555 %s'\" " % (
        client_ip, user_name, posix_file_location, testdir, testdir)
    rc = common.command(cmd)
    common.judge_rc(rc, 0, "make testdir failed")

    log.info("5-2> 给用户组%s设置rw权限" % group_list[1])
    cmd = "ssh %s \"cd %s;setfacl -m g:%s:rw %s\"" % (
        client_ip, posix_file_location, group_list[1], testdir)
    rc = common.command(cmd)
    common.judge_rc(rc, 0, "setfacl %s:rw failed" % group_list[1])

    log.info("5-3> 用户%s向%s中创建新目录" % (user_name, testdir))
    sub_dir_name = "%s" % user_name
    cmd = "ssh %s \"su %s -c 'cd %s;mkdir %s/%s'\"" % (client_ip, user_name, posix_file_location, testdir, sub_dir_name)
    rc = common.command(cmd)
    common.judge_rc_unequal(rc, 0, "make subdir success, the acl dosen't take effect")

    log.info("5-4> testdir权限检测成功，删除测试目录%s" % posix_file_location)
    cmd = "ssh %s \"rm -fr %s\"" % (client_ip, posix_file_location)
    rc = common.command(cmd)
    common.judge_rc(rc, 0, "rm testdir %s failed" % posix_file_location)


    log.info("6> 删除posix客户端与local认证服务器相同的用户和用户组")
    log.info("6-1> 删除posix客户端与local认证服务器相同的用户")
    cmd_del_user = "ssh %s \"userdel %s\"" % (client_ip, user_name)
    rc = common.command(cmd_del_user)
    common.judge_rc(rc, 0, "del user in client %s failed" % client_ip)
    log.info("6-2> 删除posix客户端与local认证服务器相同的用户组")
    for g_num in range(len(group_list)):
        cmd_del_group = "ssh %s \"groupdel %s\"" % (
            client_ip, group_list[g_num])
        rc = common.command(cmd_del_group)
        common.judge_rc(rc, 0, "del group in client %s failed" % client_ip)

    log.info("7> 删除local用户和用户组")
    log.info("7-1> 删除local用户")
    nas_common.delete_auth_users(user_id)
    log.info("7-2> 删除local用户组")
    group_ids = secondary_group_ids
    nas_common.delete_auth_groups(group_ids)

    return


def main():
    prepare_clean.test_prepare(FILE_NAME)
    case()
    prepare_clean.test_clean(FILE_NAME)
    log.info('testcase %s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
