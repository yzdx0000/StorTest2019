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
# date 2018-11-19
# @summary：
#    nfs客户端权限测试：u2属于多个组，检测目录权限；原P200测试用例23-0-4-3。
# @steps:
#    脚本运行前准备工作：a) 配置访问管理，包括访问区、Local认证服务器、业务子网；并将相关信息写入配置文件
#
#    1、获取节点信息:nfs客户端ip、nfs客户端挂载路径、vip池；
#    2、添加nfs授权并挂载nfs客户端
#    3、创建测试目录并将权限修改为777；
#    4、增加local认证服务器用户组/用户；
#    5、nfs客户端创建与local认证服务器相同的用户和组；
#    6、测试主体，u2属于多个组，检测目录权限；
#    7、nfs客户端删除第4步创建的用户/用户组；
#    8、删除第3步创建的local用户组/用户；
#    9、卸载nfs挂载目录并删除授权
#
# @changelog：
##########################################################################

#################### 全局变量 ####################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[
    0]                 # 本脚本名字
FILE_NAME = FILE_NAME.replace('-', '_')
export_name_nfs = 'nfs' + FILE_NAME    # nfs共享名称
nfs_file_dir = "nfs_dir" + FILE_NAME
group_list = ["group1_" + FILE_NAME, "group2_" + FILE_NAME]
user_name_list = ["user1_" + FILE_NAME, "user2_" + FILE_NAME]
user_passwd = "111111"


def case():
    log.info("1> 获取节点信息")
    vip_domain_name = get_config.get_vip_domain_name()[0]
    log.info("vip_domain_name is: %s" % vip_domain_name)

    nfs_ip = get_config.get_nfs_client_ip()[0]
    log.info("nfs client ip is: %s" % nfs_ip)

    nfs_mount_path = get_config.get_nfs_mount_path()[0]
    log.info("nfs_mount_path is: %s" % nfs_mount_path)

    nfs_file_location = os.path.join(nfs_mount_path, nfs_file_dir)
    log.info("nfs_file_location is: %s" % nfs_file_location)

    auth_provider_info = nas_common.get_auth_providers_local()
    auth_provider_id = auth_provider_info["result"]["auth_providers"][0]["id"]

    log.info("2> 添加nfs授权，并挂载nfs客户端")
    log.info("2-1> 添加nfs授权")
    access_zone_name = get_config.get_access_zone_name()[0]
    access_zone_info = nas_common.get_access_zones()
    access_zone_info = access_zone_info["result"]["access_zones"]
    access_zone_id = ''
    for access_zone_tmp in access_zone_info:
        if access_zone_name in access_zone_tmp["name"]:
            access_zone_id = access_zone_tmp["id"]
    if '' == access_zone_id:
        common.judge_rc(1, 0, "get access_zone_id failed")
    else:
        pass
    mount_path = get_config.get_one_mount_path()
    export_path = mount_path.split('/')[-1] + ':/'
    nas_common.create_nfs_export(access_zone_id, export_name_nfs, export_path)
    nfs_export_msg = nas_common.get_nfs_exports()
    nfs_export_msg = nfs_export_msg["result"]["exports"]
    nfs_export_id = ""
    for nfs_info in nfs_export_msg:
        if export_name_nfs in nfs_info["export_name"]:
            nfs_export_id = nfs_info["id"]
    if nfs_export_id == "":
        common.judge_rc(1, 0, "get nfs_export_id failed")
    nas_common.add_nfs_export_auth_clients(
        nfs_export_id, '*', 'rw', 'sync', 'secure', 'no_root_squash')
    log.info("2-2> 挂载nfs客户端")
    cmd = "ssh %s \"if [ ! -d \"%s\" ];then mkdir -p %s;fi\"" % (
        nfs_ip, nfs_mount_path, nfs_mount_path)
    rc = common.command(cmd)
    common.judge_rc(
        rc,
        0,
        "the nfs_mount_path is not exit and mkdir nfs_mount_path failed")
    rc = common.command(
        "ssh %s \"mount -t nfs %s:%s %s\"" %
        (nfs_ip, vip_domain_name, mount_path, nfs_mount_path))
    common.judge_rc(rc, 0, "mount nfs client failed")
    time.sleep(5)

    log.info("3> 创建测试目录")
    rc = common.command(
        "ssh %s \"mkdir %s\"" %
        (nfs_ip, nfs_file_location))
    common.judge_rc(rc, 0, "mkdir nfs_file_location failed")
    rc = common.command(
        "ssh %s \"chmod %s %s\"" %
        (nfs_ip, "777", nfs_file_location))
    common.judge_rc(rc, 0, "chmod nfs_file_location failed")

    log.info("4> 增加local认证服务器用户组/用户")
    log.info("4-1> 增加local认证服务器用户组")
    for g_num in range(len(group_list)):
        nas_common.create_auth_group(auth_provider_id, group_list[g_num])
    group_info = nas_common.get_auth_groups(auth_provider_id)
    group_info = group_info["result"]["auth_groups"]
    group_id_list = []
    for group_infp_tmp in group_info:
        if FILE_NAME in group_infp_tmp["name"]:
            group_id = group_infp_tmp["id"]
            group_id_list.append(group_id)
    log.info("4-2> 增加local认证服务器用户")
    g1_primary_group_id = group_id_list[0]
    g1_secondary_group_ids = group_id_list[0]
    nas_common.create_auth_user(
        auth_provider_id,
        user_name_list[0],
        user_passwd,
        g1_primary_group_id,
        g1_secondary_group_ids)

    g2_primary_group_id = group_id_list[1]
    group_id_list_tmp = map(str, group_id_list)
    g2_secondary_group_ids = ','.join(group_id_list_tmp)
    nas_common.create_auth_user(
        auth_provider_id,
        user_name_list[1],
        user_passwd,
        g2_primary_group_id,
        g2_secondary_group_ids)
    (rc, user_info) = nas_common.get_auth_users(auth_provider_id)
    user_info = user_info["result"]["auth_users"]
    user_id_list = []
    for user_infp_tmp in user_info:
        if FILE_NAME in user_infp_tmp["name"]:
            user_id = user_infp_tmp["id"]
            user_id_list.append(user_id)

    log.info("5> nfs客户端创建与local认证服务器相同的用户和组")
    for g_num in range(len(group_list)):
        cmd_add_group = "ssh %s \"groupadd -g %d %s\"" % (
            nfs_ip, group_id_list[g_num], group_list[g_num])
        rc = common.command(cmd_add_group)
        common.judge_rc(rc, 0, "add group in client %s failed" % nfs_ip)

    cmd_add_user_1 = "ssh %s \"useradd -g %s -G %s -u %d %s\"" % (
        nfs_ip, group_list[0], group_list[0], user_id_list[0], user_name_list[0])
    rc = common.command(cmd_add_user_1)
    common.judge_rc(rc, 0, "add user1 in client %s failed" % nfs_ip)

    cmd_add_user_2 = "ssh %s \"useradd -g %s -G %s,%s -u %d %s\"" % (
        nfs_ip, group_list[1], group_list[0], group_list[1], user_id_list[1], user_name_list[1])
    rc = common.command(cmd_add_user_2)
    common.judge_rc(rc, 0, "add user2 in client %s failed" % nfs_ip)

    log.info("6> 测试主体：%s属于多个组，测试目录权限" % user_name_list[1])
    log.info("6-1> 创建测试目录并设置权限555")
    testdir = 'dir_' + FILE_NAME
    cmd = "ssh %s \"su %s -c 'cd %s;mkdir %s;chmod 555 %s'\" " % (
        nfs_ip, user_name_list[0], nfs_file_location, testdir, testdir)
    rc = common.command(cmd)
    common.judge_rc(rc, 0, "make testdir failed")
    log.info("6-2> 给用户组%s设置rw权限" % group_list[0])
    cmd = "ssh %s \"cd %s;setfacl -m g:%s:rw %s\"" % (
        nfs_ip, nfs_file_location, group_list[0], testdir)
    rc = common.command(cmd)
    common.judge_rc(rc, 0, "setfacl %s:rw failed" % group_list[0])
    log.info("6-3> 用户%s向%s中创建新目录" % (user_name_list[1], testdir))
    sub_dir_name = "%s" % user_name_list[1]
    cmd = "ssh %s \"su %s -c 'cd %s;mkdir %s/%s'\"" % (
        nfs_ip, user_name_list[1], nfs_file_location, testdir, sub_dir_name)
    rc = common.command(cmd)
    common.judge_rc(
        rc, 0, "make subdir failed, the acl dosen't take effect")
    log.info("6-4> testdir权限检测成功，删除测试目录%s" % nfs_file_location)
    cmd = "ssh %s \"rm -fr %s\"" % (nfs_ip, nfs_file_location)
    rc = common.command(cmd)
    common.judge_rc(rc, 0, "rm nfs_file_location %s failed" % nfs_file_location)

    log.info("7> 删除nfs客户端与local认证服务器相同的用户和用户组")
    log.info("7-1> 删除nfs客户端与local认证服务器相同的用户")
    for u_name in user_name_list:
        cmd_del_user = "ssh %s \"userdel %s\"" % (nfs_ip, u_name)
        rc = common.command(cmd_del_user)
        common.judge_rc(rc, 0, "del user in client %s failed" % nfs_ip)
    log.info("7-2> 删除nfs客户端与local认证服务器相同的用户组")
    for g_name in group_list:
        cmd_del_group = "ssh %s \"groupdel %s\"" % (
            nfs_ip, g_name)
        rc = common.command(cmd_del_group)
        common.judge_rc(rc, 0, "del group in client %s failed" % nfs_ip)

    log.info("8> 删除local用户和用户组")
    log.info("8-1> 删除local用户")
    for u_id in user_id_list:
        nas_common.delete_auth_users(u_id)
    log.info("8-2> 删除local用户组")
    for g_id in group_id_list:
        nas_common.delete_auth_groups(g_id)

    log.info("9> 卸载nfs客户端挂载目录，并删除授权")
    log.info("9-1> 卸载nfs客户端挂载目录")
    rc = common.command(
        "ssh %s \"umount -l %s\"" %
        (nfs_ip, nfs_mount_path))
    common.judge_rc(rc, 0, "umount nfs client failed")
    log.info("9-2> 删除nfs授权")
    nas_common.delete_nfs_exports(nfs_export_id)

    return


def main():
    prepare_clean.test_prepare(FILE_NAME)
    case()
    prepare_clean.test_clean(FILE_NAME)
    log.info('testcase %s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
