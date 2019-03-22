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
#    DAC nfs客户端自动化脚本集合，原P200开发写的最小用例集。
# @steps:
#    脚本运行前准备工作：a) 配置访问管理，包括访问区、Local认证服务器、业务子网；并将相关信息写入配置文件
#
#    1、获取节点信息:nfs客户端ip、nfs客户端挂载路径、vip池；
#    2、添加nfs授权并挂载nfs客户端
#    3、创建测试目录并将权限修改为777；
#    4、增加local认证服务器用户组/用户；
#    5、nfs客户端创建与local认证服务器相同的用户和组；
#    6、测试主体，nfs客户端权限验证用例集合；
#    7、nfs客户端删除第4步创建的用户/用户组；
#    8、删除第3步创建的local用户组/用户；
#    9、卸载nfs挂载目录并删除授权
#
# @changelog：
##########################################################################

#################### 全局变量 ####################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[
    0]                 # 本脚本名字
export_name_nfs = 'nfs' + FILE_NAME    # nfs共享名称
nfs_file_dir = "nfs_dir" + FILE_NAME
group_list = ["dg1", "dg2", "dg3"]
user_name_list = ["du1", "du2", "du3"]
user_passwd = "111111"
scripts_dir = "/home/StorTest/test_cases/cases/test_case/P300/DAC/nfs_scripts/nfs_minimun_set"


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

    parastor_ip = get_config.get_parastor_ip()
    log.info("parastor_ip is: %s" % parastor_ip)

    parastor_mount_path = get_config.get_one_mount_path()
    log.info("posix_mount_path is: %s" % parastor_mount_path)

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

    log.info("3> 创建测试目录")
    rc = common.command(
        "ssh %s \"mkdir %s\"" %
        (nfs_ip, nfs_file_location))
    common.judge_rc(rc, 0, "mkdir testdir failed")
    rc = common.command(
        "ssh %s \"chmod %s %s\"" %
        (nfs_ip, "777", nfs_file_location))
    common.judge_rc(rc, 0, "chmod testdir failed")

    log.info("4> 增加local认证服务器用户组/用户")
    log.info("4-1> 增加local认证服务器用户组")
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

    log.info("4-2> 增加local认证服务器用户")
    for u_num in range(len(user_name_list)):
        g_tmp = group_id_list[u_num]
        nas_common.create_auth_user(
            auth_provider_id,
            user_name_list[u_num],
            user_passwd,
            g_tmp)

    (rc, user_info) = nas_common.get_auth_users(auth_provider_id)
    user_info = user_info["result"]["auth_users"]
    user_id_list = []
    for u_num in range(len(user_info)):
        for u_name in user_name_list:
            if u_name in user_info[u_num]["name"]:
                user_id = user_info[u_num]["id"]
                user_id_list.append(user_id)

    log.info("5> nfs客户端创建与local认证服务器相同的用户和组")
    for g_num in range(len(group_list)):
        cmd_add_group = "ssh %s \"groupadd -g %d %s\"" % (
            nfs_ip, group_id_list[g_num], group_list[g_num])
        rc = common.command(cmd_add_group)
        common.judge_rc(rc, 0, "add group in client %s failed" % nfs_ip)

    for (
            user_name,
            user_id,
            group_name) in zip(
            user_name_list,
            user_id_list,
            group_list):
        cmd_add_user_tmp = "ssh %s \"useradd -g %s -G %s -u %s %s\"" % (
            nfs_ip, group_name, group_name, user_id, user_name)
        rc = common.command(cmd_add_user_tmp)
        common.judge_rc(rc, 0, "add user in client %s failed" % nfs_ip)

    log.info("6> nfs客户端权限验证用例集合")
    log.info("6-1> 将脚本拷贝到nfs客户端下指定目录")
    nfs_scripts_dir = "/tmp/nfs_minimun_set"
    cmd = "ssh %s \"if [ ! -d \"%s\" ];then mkdir -p %s;fi\"" % (
        nfs_ip, nfs_scripts_dir, nfs_scripts_dir)
    rc = common.command(cmd)
    common.judge_rc(
        rc, 0, "mkdir %s in nfs client %s failed" %
        (nfs_scripts_dir, nfs_ip))
    cmd = "scp -r %s/* %s:%s" % (scripts_dir, nfs_ip, nfs_scripts_dir)
    rc = common.command(cmd)
    common.judge_rc(rc, 0, "scp test scripts to nfs client %s failed" % nfs_ip)
    log.info("6-2> nfs客户端执行测试")
    parastor_test_path = os.path.join(parastor_mount_path, nfs_file_dir)
    cmd_exc = "ssh %s \"cd %s;sh main.sh %s %s %s %s %s %s %s %s %s\"" % (nfs_ip,
                                                                          nfs_scripts_dir,
                                                                          user_name_list[0],
                                                                          user_name_list[1],
                                                                          user_name_list[2],
                                                                          group_list[0],
                                                                          group_list[1],
                                                                          group_list[2],
                                                                          parastor_ip,
                                                                          parastor_test_path,
                                                                          nfs_file_location)
    rc = common.command(cmd_exc)
    common.judge_rc(rc, 0, "nfs acl minimun set of cases test failed")
    log.info("6-3> 检验执行失败项，若有失败项，则退出")

    cmd1 = "cd %s;cat dac_st.log | grep Total | sed -n 1p | cut -d \" \" -f11 | cut -d \"]\" -f1" % nfs_scripts_dir
    cmd2 = "cd %s;cat dac_st.log | grep Total | sed -n 2p | cut -d \" \" -f11 | cut -d \"]\" -f1" % nfs_scripts_dir
    (rc1, output1) = common.run_command(nfs_ip, cmd1)
    (rc2, output2) = common.run_command(nfs_ip, cmd2)
    output1 = output1.strip()
    output2 = output2.strip()
    rc_exit = 0
    if output1 == "0" and output2 == "0":
        pass
    else:
        rc_exit = 1
    common.judge_rc(rc_exit, 0, "nfs acl minimun set of cases test failed ,please check %s/dac_error.log in %s" % (nfs_scripts_dir, nfs_ip))
    log.info("6-4> 删除nfs客户端测试脚本")
    cmd = "ssh %s \"rm -fr %s\"" % (nfs_ip, nfs_scripts_dir)
    rc = common.command(cmd)
    common.judge_rc(rc, 0, "rm %s" % nfs_scripts_dir)
    log.info("6-5> 全部测试成功，则删除测试目录中所有内容")
    rc = common.command(
        "ssh %s \"rm -fr %s\"" %
        (nfs_ip, nfs_file_location))
    common.judge_rc(rc, 0, "rm testdir")

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
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
