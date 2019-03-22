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
# date 2018-11-21
# @summary：
#    nfs客户端权限测试：posix客户端，设置单个“文件/目录/目录可继承”ace数量直至上限；原P200测试用例23-0-7-4至23-0-7-6。
# @steps:
#    脚本运行前准备工作：a) 配置访问管理，包括访问区、Local认证服务器、业务子网；并将相关信息写入配置文件
#                        b) posix客户端授权并手动挂载，并将相应信息写入配置文件
#
#    1、获取节点信息:posix客户端ip、posix客户端挂载路径；
#    2、创建测试目录并将权限修改为777；
#    3、增加local认证服务器用户组/用户；
#    4、测试主体，测试posix客户端“文件/目录/目录可继承”ace权限极限值；
#    5、删除第3步创建的local用户组/用户；
#
# @changelog：
##########################################################################

#################### 全局变量 ####################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[
    0]                 # 本脚本名字
FILE_NAME = FILE_NAME.replace('-', '_')
export_name_nfs = 'posix' + FILE_NAME    # nfs共享名称
posix_file_dir = "posix_dir" + FILE_NAME
group_name = "posixgroup1_" + FILE_NAME
user_name = "posixuser_" + FILE_NAME
user_passwd = "111111"
user_numbers = 6000
testdir_num = 2
acl = "rwx"
process_list = []


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
    log.info("1> 获取节点信息")

    parastor_ip = get_config.get_parastor_ip()
    log.info("parastor ip is: %s" % parastor_ip)

    # 集群节点卷挂载目录当作posix客户端
    posix_mount_path = get_config.get_one_mount_path()
    log.info("posix_mount_path is: %s" % posix_mount_path)

    posix_file_location = os.path.join(posix_mount_path, posix_file_dir)
    log.info("posix_file_location is: %s" % posix_file_location)

    auth_provider_info = nas_common.get_auth_providers_local()
    auth_provider_id = auth_provider_info["result"]["auth_providers"][0]["id"]

    log.info("2> 创建测试目录")
    rc = common.command(
        "ssh %s \"mkdir %s\"" %
        (parastor_ip, posix_file_location))
    common.judge_rc(rc, 0, "mkdir nfs_file_location failed")
    rc = common.command(
        "ssh %s \"chmod %s %s\"" %
        (parastor_ip, "777", posix_file_location))
    common.judge_rc(rc, 0, "chmod nfs_file_location failed")

    log.info("3> 增加local认证服务器用户组/用户")
    log.info("3-1> 增加local认证服务器用户组")
    nas_common.create_auth_group(auth_provider_id, group_name)
    group_info = nas_common.get_auth_groups(auth_provider_id)
    group_info = group_info["result"]["auth_groups"]
    group_id = 0
    for group_infp_tmp in group_info:
        if group_name in group_infp_tmp["name"]:
            group_id = group_infp_tmp["id"]

    log.info("3-2> 增加local认证服务器用户")
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

    log.info("4> 测试主体：测试nfs客户端“文件/目录/目录可继承”ace权限极限值")
    log.info("4-1> 创建测试文件")
    testfile = posix_file_location + '/' + 'file_' + FILE_NAME + '_1'
    testdir = posix_file_location + '/' + 'dir_' + FILE_NAME
    destination_list = []
    cmd = "ssh %s \"touch %s\"" % (parastor_ip, testfile)
    rc = common.command(cmd)
    common.judge_rc(rc, 0, "touch testfile failed")
    destination_list.append(testfile)

    for dir_num in range(testdir_num):
        test_dir_tmp = testdir + '_' + str(dir_num)
        cmd = "ssh %s \"mkdir %s\"" % (parastor_ip, test_dir_tmp)
        rc = common.command(cmd)
        common.judge_rc(rc, 0, "mkdir testdir failed")
        destination_list.append(test_dir_tmp)

    log.info("4-2> 采用多线程的方式，同时设置“文件/目录/目录可继承”ace")
    dac_obj = dac_common.Dac()
    p_acl_file = MyThread(
        dac_obj.set_acls,
        args=(
            parastor_ip,
            destination_list[0],
            user_name_list,
            acl,),
        name="set_acl(%s)" % destination_list[0]
    )
    process_list.append(p_acl_file)

    p_acl_dir = MyThread(
        dac_obj.set_acls,
        args=(
            parastor_ip,
            destination_list[1],
            user_name_list,
            acl,),
        name="set_acl(%s)" % destination_list[1]
    )
    process_list.append(p_acl_dir)

    p_default_acl_dir = MyThread(
        dac_obj.set_dir_default_acls,
        args=(
            parastor_ip,
            destination_list[2],
            user_name_list,
            acl,),
        name="set_default_acl(%s)" % destination_list[2]
    )
    process_list.append(p_default_acl_dir)

    for p in process_list:
        p.setDaemon(True)
        p.start()

    for p in process_list:
        p.join()

    for p in process_list:
        log.info(
            "in func %s, the (final_rc, acl_num) is %s" %
            (p.get_func_name, p.get_result()))
        common.judge_rc(p.get_result()[0], 0, "the acl upperlimit test failed")

    log.info("4-3> 测试成功，删除测试目录%s" % posix_file_location)
    cmd = "ssh %s \"rm -fr %s\"" % (parastor_ip, posix_file_location)
    rc = common.command(cmd)
    common.judge_rc(rc, 0, "rm nfs_file_location %s failed" % posix_file_location)

    log.info("6> 删除local用户和用户组")
    log.info("6-1> 删除local用户")
    for u_id in user_id_list:
        nas_common.delete_auth_users(u_id)
    log.info("6-2> 删除local用户组")
    nas_common.delete_auth_groups(group_id)

    return


def main():
    prepare_clean.test_prepare(FILE_NAME)
    case()
    prepare_clean.test_clean(FILE_NAME)
    log.info('testcase %s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
