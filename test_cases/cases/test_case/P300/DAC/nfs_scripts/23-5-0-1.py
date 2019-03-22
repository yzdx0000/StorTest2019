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
import dac_common
import threading

##########################################################################
#
# Author: zhanghan
# date 2018-11-23
# @summary：
#    多客户端权限测试：nfs/posix客户端，多进程并发同时修改一个文件权限，然后读取文件权限，执行数小时；原P200测试用例23-5-0-1。
# @steps:
#    脚本运行前准备工作：a) 配置访问管理，包括访问区、Local认证服务器、业务子网；并将相关信息写入配置文件
#
#    1、获取节点信息:nfs/posix客户端ip、nfs/posix客户端挂载路径、vip池；
#    2、添加nfs授权并挂载nfs客户端
#    3、创建测试目录并将权限修改为777；
#    4、增加local认证服务器用户组/用户；
#    5、nfs/posix客户端创建与local认证服务器相同的用户和组；
#    6、测试主体，nfs/posix客户端，多进程并发同时修改一个文件权限，然后读取文件权限，执行数小时；
#    7、nfs/posix客户端删除第4步创建的用户/用户组；
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
multi_file_fir = "nfs_dir" + FILE_NAME
group_name = "group1_" + FILE_NAME
user_name = "user_" + FILE_NAME
user_passwd = "111111"
user_numbers = 25
acl_list = ["rwx", "rw", "rx", "wx", "w", "x", "---"]
process_list = []
process_num = 20
set_acl_times = 10000


class MyThread(threading.Thread):
    def __init__(self, func, args=(), name=""):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args
        self.name = name

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result  # 如果子线程不使用join方法，此处可能会报没有self.result的错误
        except Exception:
            return None

    def get_func_name(self):
        return self.name


def case():
    log.info("1> 获取节点信息")
    vip_domain_name = get_config.get_vip_domain_name()[0]
    log.info("vip_domain_name is: %s" % vip_domain_name)

    client_ip = get_config.get_client_ip()
    log.info("posix client ip is: %s" % client_ip)

    # posix客户端需要预先手动挂载，且挂载目录需要与卷名称相同
    posix_mount_path = get_config.get_one_mount_path()
    log.info("posix_mount_path is: %s" % posix_mount_path)

    posix_file_location = os.path.join(posix_mount_path, multi_file_fir)
    log.info("posix_file_location is: %s" % posix_file_location)

    nfs_ip = get_config.get_nfs_client_ip()[0]
    log.info("nfs client ip is: %s" % nfs_ip)

    nfs_mount_path = get_config.get_nfs_mount_path()[0]
    log.info("nfs_mount_path is: %s" % nfs_mount_path)

    nfs_file_location = os.path.join(nfs_mount_path, multi_file_fir)
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

    log.info("access_zone_id is %s" % access_zone_id)
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
    nas_common.create_auth_group(auth_provider_id, group_name)
    group_info = nas_common.get_auth_groups(auth_provider_id)
    group_info = group_info["result"]["auth_groups"]
    group_id = 0
    for group_infp_tmp in group_info:
        if group_name in group_infp_tmp["name"]:
            group_id = group_infp_tmp["id"]

    log.info("4-2> 增加local认证服务器用户")
    user_name_list = []
    primary_group_id = group_id
    for user_num in range(user_numbers):
        user_name_tmp = user_name + '_' + str(user_num)
        user_name_list.append(user_name_tmp)
        nas_common.create_auth_user(
            auth_provider_id,
            user_name_tmp,
            user_passwd,
            primary_group_id)
    (rc, user_info) = nas_common.get_auth_users(auth_provider_id)
    user_info = user_info["result"]["auth_users"]
    user_id_list = []
    for u_info_tmp in user_info:
        if user_name in u_info_tmp["name"]:
            user_id_list.append(u_info_tmp["id"])

    log.info("5> nfs/posix客户端创建与local认证服务器相同的用户和组")
    cmd_add_group_nfs = "ssh %s \"groupadd -g %d %s\"" % (
        nfs_ip, group_id, group_name)
    rc = common.command(cmd_add_group_nfs)
    common.judge_rc(rc, 0, "add group in client %s failed" % nfs_ip)
    cmd_add_group_posix = "ssh %s \"groupadd -g %d %s\"" % (
        client_ip, group_id, group_name)
    rc = common.command(cmd_add_group_posix)
    common.judge_rc(rc, 0, "add group in client %s failed" % client_ip)

    for u_num in range(len(user_id_list)):
        cmd_add_user_nfs = "ssh %s \"useradd -g %s -G %s -u %d %s\"" % (
            nfs_ip, group_name, group_name, user_id_list[u_num], user_name_list[u_num])
        rc = common.command(cmd_add_user_nfs)
        common.judge_rc(rc, 0, "add user in client %s failed" % nfs_ip)
        cmd_add_user_posix = "ssh %s \"useradd -g %s -G %s -u %d %s\"" % (
            client_ip, group_name, group_name, user_id_list[u_num], user_name_list[u_num])
        rc = common.command(cmd_add_user_posix)
        common.judge_rc(rc, 0, "add user in client %s failed" % client_ip)

    log.info("6> 测试主体：测试nfs客户端“文件/目录/目录可继承”ace权限极限值")
    log.info("6-1> 创建测试文件")
    subfile = 'file_' + FILE_NAME
    testfile_nfs = nfs_file_location + '/' + subfile
    testfile_posix = posix_file_location + '/' + subfile
    cmd = "ssh %s \"touch %s\"" % (nfs_ip, testfile_nfs)
    rc = common.command(cmd)
    common.judge_rc(rc, 0, "touch testfile failed")

    log.info("6-2> 采用多线程的方式，posix/nfs客户端同时设置文件的acl")
    dac_obj = dac_common.Dac()
    for p_num in range(process_num):
        p_acl_nfs_tmp = MyThread(
            dac_obj.set_acls_specified_times,
            args=(
                nfs_ip,
                testfile_nfs,
                user_name_list,
                acl_list, 'user', set_acl_times),
            name="process %d, set_acl(%s)" % (p_num, testfile_nfs)
        )
        process_list.append(p_acl_nfs_tmp)

        p_acl_posix_tmp = MyThread(
            dac_obj.set_acls_specified_times,
            args=(
                client_ip,
                testfile_posix,
                user_name_list,
                acl_list, 'user', set_acl_times),
            name="process %d set_acl(%s)" % (p_num, testfile_posix)
        )
        process_list.append(p_acl_posix_tmp)

    for p in process_list:
        p.setDaemon(True)
        p.start()

    for p in process_list:
        p.join()

    for p in process_list:
        log.info(
            "in func %s, the (final_rc, acl_num) is %s" %
            (p.get_func_name, p.get_result()))
        common.judge_rc(p.get_result()[0], 0, "'multi clients set acl the same time' test failed")

    log.info("6-3> 测试成功，删除测试目录%s" % nfs_file_location)
    cmd = "ssh %s \"rm -fr %s\"" % (nfs_ip, nfs_file_location)
    rc = common.command(cmd)
    common.judge_rc(
        rc, 0, "rm nfs_file_location %s failed" %
        nfs_file_location)

    log.info("7> 删除nfs/posix客户端与local认证服务器相同的用户和用户组")
    log.info("7-1> 删除nfs/posix客户端与local认证服务器相同的用户")
    for u_name in user_name_list:
        cmd_del_user_nfs = "ssh %s \"userdel %s\"" % (nfs_ip, u_name)
        rc = common.command(cmd_del_user_nfs)
        common.judge_rc(rc, 0, "del user in client %s failed" % nfs_ip)
        cmd_del_user_posix = "ssh %s \"userdel %s\"" % (client_ip, u_name)
        rc = common.command(cmd_del_user_posix)
        common.judge_rc(rc, 0, "del user in client %s failed" % client_ip)
    log.info("7-2> 删除nfs/posix客户端与local认证服务器相同的用户组")
    cmd_del_group_nfs = "ssh %s \"groupdel %s\"" % (
        nfs_ip, group_name)
    rc = common.command(cmd_del_group_nfs)
    common.judge_rc(rc, 0, "del group in client %s failed" % nfs_ip)
    cmd_del_group_posix = "ssh %s \"groupdel %s\"" % (
        client_ip, group_name)
    rc = common.command(cmd_del_group_posix)
    common.judge_rc(rc, 0, "del group in client %s failed" % client_ip)

    log.info("8> 删除local用户和用户组")
    log.info("8-1> 删除local用户")
    for u_id in user_id_list:
        nas_common.delete_auth_users(u_id)
    log.info("8-2> 删除local用户组")
    nas_common.delete_auth_groups(group_id)

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
    prepare_clean.test_prepare(FILE_NAME, False)
    case()
    # prepare_clean.test_clean(FILE_NAME)
    log.info('testcase %s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)