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
# date 2018-11-26
# @summary：
#    DAC posix客户端自动化脚本集合，原P200开发写的最小用例集。
# @steps:
#    脚本运行前准备工作：a) 配置访问管理，包括LOCAL认证服务器、访问区并将相应信息写入配置文件
#                        b) posix客户端授权并手动挂载，并将相应信息写入配置文件
#
#    1、获取节点信息:posix客户端ip、posix客户端挂载路径；
#    2、创建测试目录并将权限修改为777；
#    3、增加local认证服务器用户组/用户；
#    4、posix客户端创建与local认证服务器相同的用户和组；
#    5、测试主体，测试用户权限；
#    6、posix客户端删除第4步创建的用户/用户组；
#    7、删除第3步创建的local用户组/用户；
#
# @changelog：
##########################################################################

#################### 全局变量 ####################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[
    0]                 # 本脚本名字
posix_file_dir = "posix_dir_" + FILE_NAME
group_list = ["g1", "g2", "g3"]
user_name_list = ["u1", "u2", "u3"]
user_passwd = "111111"
posix_scripts_dir = "/tmp/posix_minimun_set"
scripts_dir = "/home/StorTest/test_cases/cases/test_case/P300/DAC/posix_scripts/posix_minimun_set"


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

    parastor_ip = get_config.get_parastor_ip()
    log.info("parastor_ip is: %s" % parastor_ip)

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
    for g_num in range(len(group_info)):
        for g_name in group_list:
            if g_name in group_info[g_num]["name"]:
                group_id = group_info[g_num]["id"]
                group_id_list.append(group_id)

    log.info("3-2> 增加local认证服务器用户")
    g1_tmp = group_id_list[0]
    nas_common.create_auth_user(
        auth_provider_id,
        user_name_list[0],
        user_passwd,
        g1_tmp)

    g2_tmp = group_id_list[1]
    g2_id_list_tmp = map(str, group_id_list[:-1])
    g2_secondary_group_ids = ','.join(g2_id_list_tmp)
    nas_common.create_auth_user(
        auth_provider_id,
        user_name_list[1],
        user_passwd,
        g2_tmp,
        g2_secondary_group_ids)

    g3_tmp = group_id_list[2]
    g3_id_list_tmp = map(str, group_id_list)
    g3_secondary_group_ids = ','.join(g3_id_list_tmp)
    nas_common.create_auth_user(
        auth_provider_id,
        user_name_list[2],
        user_passwd,
        g3_tmp,
        g3_secondary_group_ids)

    (rc, user_info) = nas_common.get_auth_users(auth_provider_id)
    user_info = user_info["result"]["auth_users"]
    user_id_list = []
    for u_num in range(len(user_info)):
        for u_name in user_name_list:
            if u_name in user_info[u_num]["name"]:
                user_id = user_info[u_num]["id"]
                user_id_list.append(user_id)

    log.info("4> posix客户端创建与local认证服务器相同的用户和组")
    for g_num in range(len(group_list)):
        cmd_add_group = "ssh %s \"groupadd -g %d %s\"" % (
            client_ip, group_id_list[g_num], group_list[g_num])
        rc = common.command(cmd_add_group)
        common.judge_rc(rc, 0, "add group in client %s failed" % client_ip)

    cmd_add_user1 = "ssh %s \"useradd -g %s -G %s -u %d %s\"" % (
        client_ip, group_list[0], group_list[0], user_id_list[0], user_name_list[0])
    rc = common.command(cmd_add_user1)
    common.judge_rc(rc, 0, "add user in client %s failed" % client_ip)

    cmd_add_user2 = "ssh %s \"useradd -g %s -G %s,%s -u %d %s\"" % (
        client_ip, group_list[1], group_list[1], group_list[0], user_id_list[1], user_name_list[1])
    rc = common.command(cmd_add_user2)
    common.judge_rc(rc, 0, "add user in client %s failed" % client_ip)

    cmd_add_user3 = "ssh %s \"useradd -g %s -G %s,%s,%s -u %d %s\"" % (
        client_ip, group_list[2], group_list[2], group_list[1], group_list[0], user_id_list[2], user_name_list[2])
    rc = common.command(cmd_add_user3)
    common.judge_rc(rc, 0, "add user in client %s failed" % client_ip)

    log.info("5> posix客户端权限验证用例集合")
    log.info("5-1> 将所需脚本拷贝到posix客户端指定目录下")
    cmd = "ssh %s \"if [ ! -d \"%s\" ];then mkdir -p %s;fi\"" % (
        client_ip, posix_scripts_dir, posix_scripts_dir)
    rc = common.command(cmd)
    common.judge_rc(
        rc, 0, "mkdir %s in posix client %s failed" %
               (posix_scripts_dir, client_ip))
    cmd = "scp -r %s/* %s:%s" % (scripts_dir, client_ip, posix_scripts_dir)
    rc = common.command(cmd)
    common.judge_rc(
        rc,
        0,
        "scp test scripts to nfs client %s failed" %
        client_ip)
    log.info("5-2> posix客户端执行测试")
    run_times = 1
    cmd = "cd %s;sh main.sh %s %d %s" % (
        posix_scripts_dir, parastor_ip, run_times, posix_file_location)
    (rc, output) = common.run_command(client_ip, cmd)
    common.judge_rc(rc, 0, "posix acl minimun set of cases excute failed")
    log.info("5-3> 判断是否有失败项，有失败项则退出")
    cmd = "cd %s;cat dac_error.log | wc -l" % posix_scripts_dir
    (rc, output) = common.run_command(client_ip, cmd)
    output = output.strip()
    if int(output) > 2:
        rc_exit = 1
        common.judge_rc(
            rc_exit, 0, "posix acl minimun set of cases test failed, please check %s/dac_error.log in %s " %
            (posix_scripts_dir, client_ip))
    log.info("5-4> 测试成功，删除测试脚本%s" % posix_scripts_dir)
    cmd = "ssh %s \"rm -fr %s\"" % (client_ip, posix_scripts_dir)
    rc = common.command(cmd)
    common.judge_rc(rc, 0, "rm test scripts %s failed" % posix_scripts_dir)
    log.info("5-5> 测试成功，则删除测试目录中所有内容")
    rc = common.command(
        "ssh %s \"rm -fr %s\"" %
        (client_ip, posix_file_location))
    common.judge_rc(rc, 0, "rm testdir")

    log.info("6> 删除posix客户端与local认证服务器相同的用户和用户组")
    log.info("6-1> 删除posix客户端与local认证服务器相同的用户")
    for u_name in user_name_list:
        cmd_del_user = "ssh %s \"userdel %s\"" % (client_ip, u_name)
        rc = common.command(cmd_del_user)
        common.judge_rc(rc, 0, "del user in client %s failed" % client_ip)
    log.info("6-2> 删除posix客户端与local认证服务器相同的用户组")
    for g_name in group_list:
        cmd_del_group = "ssh %s \"groupdel %s\"" % (
            client_ip, g_name)
        rc = common.command(cmd_del_group)
        common.judge_rc(rc, 0, "del group in client %s failed" % client_ip)

    log.info("7> 删除local用户和用户组")
    log.info("7-1> 删除local用户")
    for u_id in user_id_list:
        nas_common.delete_auth_users(u_id)
    log.info("7-2> 删除local用户组")
    for g_id in group_id_list:
        nas_common.delete_auth_groups(g_id)

    return


def main():
    prepare_clean.test_prepare(FILE_NAME)
    case()
    prepare_clean.test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
