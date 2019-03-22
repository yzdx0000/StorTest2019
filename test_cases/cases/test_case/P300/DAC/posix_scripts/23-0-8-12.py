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
# date 2018-11-22
# @summary：
#    posix客户端权限测试：对目录进行chgrp操作，检验目录权限；原P200测试用例23-0-8-12。
# @steps:
#    脚本运行前准备工作：a) 配置访问管理，包括访问区、Local认证服务器；并将相关信息写入配置文件
#                        b) posix客户端授权并手动挂载，并将相应信息写入配置文件
#
#    1、获取节点信息:posix客户端ip、posix客户端挂载路径；
#    2、创建测试目录并将权限修改为777；
#    3、增加local认证服务器用户组/用户；
#    4、posix客户端创建与local认证服务器相同的用户和组；
#    5、测试主体，对目录进行chgrp操作，检验目录权限；
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
group_list = [
    "group1_" +
    FILE_NAME,
    "group2_" +
    FILE_NAME,
    "group3_" +
    FILE_NAME]
user_name_list = [
    "user1_" +
    FILE_NAME,
    "user2_" +
    FILE_NAME,
    "user3_" +
    FILE_NAME]
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

    log.info("3> 创建测试目录")
    rc = common.command(
        "ssh %s \"mkdir %s\"" %
        (client_ip, posix_file_location))
    common.judge_rc(rc, 0, "mkdir posix_file_location failed")
    rc = common.command(
        "ssh %s \"chmod %s %s\"" %
        (client_ip, "777", posix_file_location))
    common.judge_rc(rc, 0, "chmod posix_file_location failed")

    log.info("4> 增加local认证服务器用户组/用户")
    log.info("4-1> 增加local认证服务器用户组")
    for g_num in range(len(group_list)):
        nas_common.create_auth_group(auth_provider_id, group_list[g_num])
    group_info = nas_common.get_auth_groups(auth_provider_id)
    group_info = group_info["result"]["auth_groups"]
    group_id_list = []
    for num in range(len(group_info)):
        if FILE_NAME in group_info[num]["name"]:
            group_id = group_info[num]["id"]
            group_id_list.append(group_id)
    log.info("4-2> 增加local认证服务器用户")
    user_id_list = []
    for u_num in range(len(user_name_list)):
        primary_group_id_tmp = group_id_list[u_num]
        nas_common.create_auth_user(
            auth_provider_id,
            user_name_list[u_num],
            user_passwd,
            primary_group_id_tmp)
    (rc, user_info) = nas_common.get_auth_users(auth_provider_id)
    user_info = user_info["result"]["auth_users"]
    for num in range(len(user_info)):
        if FILE_NAME in user_info[num]["name"]:
            user_id = user_info[num]["id"]
            user_id_list.append(user_id)

    log.info("5> posix客户端创建与local认证服务器相同的用户和组")
    for g_num in range(len(group_list)):
        cmd_add_group = "ssh %s \"groupadd -g %d %s\"" % (
            client_ip, group_id_list[g_num], group_list[g_num])
        rc = common.command(cmd_add_group)
        common.judge_rc(rc, 0, "add group in client %s failed" % client_ip)

    for u_num in range(len(user_name_list)):
        cmd_add_user = "ssh %s \"useradd -g %s -G %s -u %d %s\"" % (
            client_ip, group_list[u_num], group_list[u_num], user_id_list[u_num], user_name_list[u_num])
        rc = common.command(cmd_add_user)
        common.judge_rc(rc, 0, "add user in client %s failed" % client_ip)

    log.info("6> 测试主体：对目录进行追加写操作，检验目录权限")
    log.info("6-1> 创建测试目录并设置权限775")
    testdir = 'dir_' + FILE_NAME
    cmd = "ssh %s \"su %s -c 'cd %s;mkdir %s;chmod 775 %s'\" " % (
        client_ip, user_name_list[0], posix_file_location, testdir, testdir)
    rc = common.command(cmd)
    common.judge_rc(rc, 0, "mkdir testdir failed")
    log.info("6-2> 修改目录的属组")
    cmd = "ssh %s \"cd %s;chgrp %s %s\"" % (
        client_ip, posix_file_location, group_list[1], testdir)
    rc = common.command(cmd)
    common.judge_rc(rc, 0, "chgrp failed")
    log.info("6-3> 分别使用用户%s和%s对目录进行创建子文件操作" %
             (user_name_list[0], user_name_list[1]))
    for u_name in user_name_list[:-1]:
        cmd_u_tmp = "ssh %s \"su %s -c 'cd %s;touch %s/%s'\"" % (
            client_ip, u_name, posix_file_location, testdir, 'file_' + u_name)
        rc = common.command(cmd_u_tmp)
        common.judge_rc(
            rc, 0, "user %s, echo >> failed, the acl dosen't take effect" %
                   u_name)

    cmd_u3 = "ssh %s \"su %s -c 'cd %s;touch %s/%s'\"" % (
        client_ip, user_name_list[2], posix_file_location, testdir, 'file_' + user_name_list[2])
    rc = common.command(cmd_u3)
    common.judge_rc_unequal(
        rc,
        0,
        "user %s, echo >> success, the acl dosen't take effect" %
        user_name_list[2])
    log.info("6-4> testdir权限检测成功，删除测试目录%s" % posix_file_location)
    cmd = "ssh %s \"rm -fr %s\"" % (client_ip, posix_file_location)
    rc = common.command(cmd)
    common.judge_rc(
        rc, 0, "rm posix_file_location %s failed" %
        posix_file_location)

    log.info("7> 删除posix客户端与local认证服务器相同的用户和用户组")
    log.info("7-1> 删除posix客户端与local认证服务器相同的用户")
    for u_name in user_name_list:
        cmd_del_user = "ssh %s \"userdel %s\"" % (client_ip, u_name)
        rc = common.command(cmd_del_user)
        common.judge_rc(rc, 0, "del user in client %s failed" % client_ip)
    log.info("7-2> 删除posix客户端与local认证服务器相同的用户组")
    for g_name in group_list:
        cmd_del_group = "ssh %s \"groupdel %s\"" % (
            client_ip, g_name)
        rc = common.command(cmd_del_group)
        common.judge_rc(rc, 0, "del group in client %s failed" % client_ip)

    log.info("8> 删除local用户和用户组")
    log.info("8-1> 删除local用户")
    for u_id in user_id_list:
        nas_common.delete_auth_users(u_id)
    log.info("8-2> 删除local用户组")
    for g_id in group_id_list:
        nas_common.delete_auth_groups(g_id)

    return


def main():
    prepare_clean.test_prepare(FILE_NAME)
    case()
    prepare_clean.test_clean(FILE_NAME)
    log.info('testcase %s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
