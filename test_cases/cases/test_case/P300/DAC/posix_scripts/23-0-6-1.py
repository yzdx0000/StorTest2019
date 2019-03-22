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
# date 2018-11-20
# @summary：
#    posix客户端边界值测试：同时存在posix acl和user./trusted./security.名称的扩展属性；原P200测试用例23-0-6-1至23-0-6-3。
# @steps:
#    脚本运行前准备工作：a) 配置访问管理，包括访问区和Local认证服务器
#                        b) posix客户端授权并手动挂载，并将相应信息写入配置文件
#
#    1、获取节点信息:posix客户端ip、posix客户端挂载路径；
#    2、创建测试目录并将权限修改为777；
#    3、增加local认证服务器用户组/用户；
#    4、测试主体，测试同时存在posix acl和user./trusted./security.名称的扩展属性的上限；
#    5、删除第3步创建的local用户组/用户；
#
# @changelog：
##########################################################################

#################### 全局变量 ####################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[
    0]                 # 本脚本名字
FILE_NAME = FILE_NAME.replace('-', '_')
posix_file_dir = "posix_dir" + FILE_NAME
group_name = "group1_" + FILE_NAME
user_name = "user_" + FILE_NAME
user_passwd = "111111"
user_numbers = 6000
acl = "rwx"
attr_type_list = ["user", "trusted", "security"]
attr_num = 200
attr_key_pre = "key_"
attr_value = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" \
             "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" \
             "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" \
             "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" \
             "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" \
             "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" \
             "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" \
             "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" \
             "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" \
             "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"  # 500B
attr_key_list = []
attr_value_list = []
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
    common.judge_rc(rc, 0, "mkdir testdir failed")
    rc = common.command(
        "ssh %s \"chmod %s %s\"" %
        (parastor_ip, "777", posix_file_location))
    common.judge_rc(rc, 0, "chmod testdir failed")

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
    primary_group_id = group_id
    user_name_list = []
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

    log.info("4 > posix客户端边界值测试：同时存在posix acl和user./trusted./security.名称的扩展属性")
    log.info("4-1> 创建测试文件")
    testfile = posix_file_location + '/' + 'file_' + FILE_NAME
    testfile_num = len(attr_type_list)
    testfile_list = []
    for file_num in range(testfile_num):
        file_tmp = testfile + '_' + str(file_num)
        cmd = "ssh %s \"touch %s\"" % (parastor_ip, file_tmp)
        rc = common.command(cmd)
        common.judge_rc(rc, 0, "touch testfile failed")
        testfile_list.append(file_tmp)
    log.info("4-2> 采用多线程的方式，同时给文件设置posix acl和user./trusted./security. 扩展属性")
    dac_obj = dac_common.Dac()
    for k_num in range(attr_num):
        attr_key_list.append(attr_key_pre + str(k_num))

    for v_num in range(len(attr_key_list)):
        attr_value_list.append(attr_value + str(v_num))
    key_value_dict = dict(zip(attr_key_list, attr_value_list))

    attr_key_num = 0
    for file_tmp in testfile_list:
        p_acl_tmp = MyThread(
            dac_obj.set_acls,
            args=(
                parastor_ip,
                file_tmp,
                user_name_list,
                acl,),
            name="set_acl(%s)" % file_tmp
        )

        process_list.append(p_acl_tmp)

        p_attr_tmp = MyThread(
            dac_obj.set_xattrs,
            args=(
                parastor_ip,
                file_tmp,
                attr_type_list[attr_key_num],
                key_value_dict,),
            name="set_attr(%s)" % file_tmp
        )
        process_list.append(p_attr_tmp)
        attr_key_num = attr_key_num + 1

    for p in process_list:
        p.setDaemon(True)
        p.start()

    for p in process_list:
        p.join()

    flag = 0
    for p in process_list:
        if flag == 0:
            log.info(
                "in func %s, the (final_rc, acl_num) is %s" %
                (p.get_func_name, p.get_result()))
            flag = flag + 1
        else:
            log.info(
                "in func %s, the (final_rc, attr_num) is %s" %
                (p.get_func_name, p.get_result()))
            flag = 0

    log.info("4-3> 测试成功，删除测试目录%s" % posix_file_location)
    cmd = "ssh %s \"rm -fr %s\"" % (parastor_ip, posix_file_location)
    rc = common.command(cmd)
    common.judge_rc(rc, 0, "rm testdir %s failed" % posix_file_location)

    log.info("5> 删除local用户和用户组")
    log.info("5-1> 删除local用户")
    for user_num in range(user_numbers):
        nas_common.delete_auth_users(user_id_list[user_num])
    log.info("5-2> 删除local用户组")
    nas_common.delete_auth_groups(group_id)

    return


def main():
    prepare_clean.test_prepare(FILE_NAME)
    case()
    prepare_clean.test_clean(FILE_NAME)
    log.info('testcase %s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
