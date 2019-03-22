# -*-coding:utf-8 -*
#######################################################
# author 张呈宇
# date 2018-04-28
# @summary：
# 16-0-4-103     权限级别RO
# @steps:
# case1、在az1上创建nfs共享，输入正确的名称和共享路径；
# pscli --command=create_nfs_export --access_zone_id=x --export_name=nfs_exp_test --export_path=volume:/nas/nfs_dir
# case2、查看nfs共享路径配置成功，信息是否与配置信息匹配；
# pscli --command=get_nfs_exports
# case3、添加nfs客户端
# pscli --command=add_nfs_export_auth_clients --export_id=x --name=x.x.x.x/24 --permission_level=rw
# case4、查看nfs客户单信息与配置信息是否匹配
# pscli --command=get_nfs_export_auth_clients
# case5、验证ro权限
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

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)  # /mnt/volume1/snap/snap_16_0_4_103
SYSTEM_IP = get_config.get_parastor_ip()
node_ip = SYSTEM_IP


#######################################################
# 1.executing_case1
# @function：在az1上创建nfs共享，输入正确的名称和共享路径；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：在az1上创建nfs共享，输入正确的名称和共享路径；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
# 1> 检查目录并creat file
# 2> 检查file是否创建成功
# 3> 创建导出路径
#######################################################
def executing_case1():
    """准备环境"""
    # 1> 创建访问分区
    log.info("\t[case1 create_access_zone ]")
    access_zone_name = "access_zone_16_0_4_103"
    node = common.Node()
    ids = node.get_nodes_id()
    access_zone_node_ids = ','.join(str(p) for p in ids)
    msg1 = nas_common.create_access_zone(node_ids=access_zone_node_ids, name=access_zone_name)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('%s create_access_zone failed!!!' % node_ip)
    global access_zone_id_16_0_4_103
    access_zone_id_16_0_4_103 = msg1["result"]

    # 2> 启动NAS
    log.info("\t[ enable_nas ]")
    msg2 = nas_common.enable_nas(access_zone_id=access_zone_id_16_0_4_103, protocol_types="NFS")
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s enable_nas failed!!!' % node_ip)

    # 3> 查看NAS是否按配置启动
    log.info("\t[ get_access_zones ]")
    check_result3 = nas_common.get_access_zones(ids=access_zone_id_16_0_4_103)
    name = check_result3["result"]["access_zones"][0]["name"]
    if name != access_zone_name:
        common.except_exit('%s enable_nas failed!!!' % node_ip)
    global auth_provider_id_16_0_4_103
    auth_provider_id_16_0_4_103 = check_result3["result"]["access_zones"][0]["auth_provider_id"]

    """1> 检查目录并creat file"""
    log.info("\t[ case1 create_file ]")
    # prepath = '/mnt/volume/nas'
    # isExists = os.path.exists(prepath)
    # if not isExists:
    #     os.makedirs(prepath)
    global nfs_path
    nfs_path = nas_common.ROOT_DIR + "nfs_dir_16_0_4_103_1"
    global NAS_PATH
    NAS_PATH = get_config.get_one_nas_test_path() + "/nfs_dir_16_0_4_103_1"
    cmd = "create_file --path=%s --posix_permission=rwxr-xr-x" % nfs_path
    check_result6 = nas_common.create_file(path=nfs_path, posix_permission="rwxr-xr-x")
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result6))
    msg6 = check_result6
    if msg6["err_msg"] != "" or msg6["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result6))
        raise Exception('%s create_file failed!!!' % node_ip)

    """2> 检查file是否创建成功"""
    log.info("\t[case1 get_file_list ]")
    cmd = "get_file_list --path=%s" % nfs_path
    check_result7 = nas_common.get_file_list(path=nfs_path)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result7))
    msg7 = check_result7
    if msg7["err_msg"] != "" or msg7["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result7))
        raise Exception('%s get_file_list failed!!!' % node_ip)

    """3> 创建导出路径"""
    log.info("\t[ case1 create_nfs_export ]")
    global nfs_export_name
    nfs_export_name = "nfs_exp_test_16_0_4_103_1"
    global description_nfs
    description_nfs = 'old_export_description'
    cmd = "create_nfs_export --access_zone_id=%s " \
          "--export_name=%s --export_path=%s --description=%s" % (access_zone_id_16_0_4_103, nfs_export_name,
                                                                  nfs_path, description_nfs)
    check_result1 = nas_common.create_nfs_export(access_zone_id=access_zone_id_16_0_4_103, export_name=nfs_export_name,
                                                 export_path=nfs_path, description=description_nfs)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
    msg1 = check_result1
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        raise Exception('%s create_nfs_export failed!!!' % node_ip)
    global nfs_export_id_16_0_4_103
    nfs_export_id_16_0_4_103 = msg1["result"]

    return


#######################################################
# 2.executing_case2
# @function：查看nfs共享路径配置成功，信息是否与配置信息匹配；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：查看nfs共享路径配置成功，信息是否与配置信息匹配；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
# 1> get_ftp_exports
# 2> 对比设置参数
#######################################################
def executing_case2():
    """1> get_ftp_exports"""
    log.info("\t[ case2 get_nfs_exports ]")
    cmd = "get_nfs_exports --ids=%s" % nfs_export_id_16_0_4_103
    check_result = nas_common.get_nfs_exports(ids=nfs_export_id_16_0_4_103)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result))
    msg = check_result
    if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result))
        raise Exception('%s get_nfs_exports failed!!!' % node_ip)

    """2> 对比设置参数"""
    access_zone_id = check_result["result"]["exports"][0]["access_zone_id"]
    export_name = check_result["result"]["exports"][0]["export_name"]
    export_path = check_result["result"]["exports"][0]["export_path"]
    description = check_result["result"]["exports"][0]["description"]
    if access_zone_id != access_zone_id_16_0_4_103:
        raise Exception('%s access_zone_id failed!!!' % node_ip)
    if export_name != nfs_export_name:
        raise Exception('%s export_name failed!!!' % node_ip)
    if export_path != nfs_path:
        raise Exception('%s export_path failed!!!' % node_ip)
    if description != description_nfs:
        raise Exception('%s description failed!!!' % node_ip)

    return


#######################################################
# 3.executing_case3
# @function：添加nfs客户端；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：添加nfs客户端；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:

#######################################################
def executing_case3():
    log.info("\t[ case3 add_nfs_export_auth_clients ]")
    global auth_clients_name
    auth_clients_name = nas_common.NFS_1_CLIENT_IP
    global auth_clients_permission_level
    auth_clients_permission_level = 'ro'
    cmd = "add_nfs_export_auth_clients --export_id=%s " \
          "--name=%s --permission_level=%s" \
          % (nfs_export_id_16_0_4_103, auth_clients_name, auth_clients_permission_level)
    check_result = nas_common.add_nfs_export_auth_clients(export_id=nfs_export_id_16_0_4_103,
                                                          name=auth_clients_name,
                                                          permission_level=auth_clients_permission_level)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result))
    msg = check_result
    if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result))
        raise Exception('%s add_nfs_export_auth_clients failed!!!' % node_ip)
    global nfs_export_clients_id_16_0_4_103
    nfs_export_clients_id_16_0_4_103 = msg["result"][0]

    return


#######################################################
# 4.executing_case4
# @function：查看nfs客户单信息与配置信息是否匹配；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：查看nfs客户单信息与配置信息是否匹配；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
# 1> get_nfs_export_auth_clients
# 2> 对比设置参数
#######################################################
def executing_case4():
    """1> get_nfs_export_auth_clients"""
    log.info("\t[ case4 get_nfs_export_auth_clients ]")
    cmd = "get_nfs_export_auth_clients --export_ids=%s" % nfs_export_id_16_0_4_103
    check_result = nas_common.get_nfs_export_auth_clients(export_ids=nfs_export_id_16_0_4_103)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result))
    msg = check_result
    if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result))
        raise Exception('%s get_nfs_export_auth_clients failed!!!' % node_ip)

    """2> 对比设置参数"""
    anongid = check_result["result"]["nfs_export_auth_clients"][0]["anongid"]
    anonuid = check_result["result"]["nfs_export_auth_clients"][0]["anonuid"]
    id = check_result["result"]["nfs_export_auth_clients"][0]["id"]
    export_id = check_result["result"]["nfs_export_auth_clients"][0]["export_id"]
    name = check_result["result"]["nfs_export_auth_clients"][0]["name"]
    permission_constraint = check_result["result"]["nfs_export_auth_clients"][0]["permission_constraint"]
    permission_level = check_result["result"]["nfs_export_auth_clients"][0]["permission_level"]
    port_constraint = check_result["result"]["nfs_export_auth_clients"][0]["port_constraint"]
    write_mode = check_result["result"]["nfs_export_auth_clients"][0]["write_mode"]
    # subtree_check = check_result["result"]["nfs_export_auth_clients"][0]["subtree_check"]
    if anongid != 65534:
        raise Exception('%s anongid failed!!!' % node_ip)
    if anonuid != 65534:
        raise Exception('%s anonuid failed!!!' % node_ip)
    if id != nfs_export_clients_id_16_0_4_103:
        raise Exception('%s id failed!!!' % node_ip)
    if export_id != nfs_export_id_16_0_4_103:
        raise Exception('%s export_id failed!!!' % node_ip)
    if name != auth_clients_name:
        raise Exception('%s name failed!!!' % node_ip)
    if permission_constraint != "root_squash":
        raise Exception('%s permission_constraint failed!!!' % node_ip)
    if permission_level != auth_clients_permission_level:
        raise Exception('%s permission_level failed!!!' % node_ip)
    if port_constraint != "secure":
        raise Exception('%s port_constraint failed!!!' % node_ip)
    if write_mode != "sync":
        raise Exception('%s write_mode failed!!!' % node_ip)
    return


#######################################################
# 5.executing_case5
# @function：验证ro权限；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：验证ro权限；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
# 1> 创建一个文件，并写入内容
# 2> 客户端mount共享路径
# 3> 测试"r"
# 4> 测试"w"
# 5> 客户端umount共享路径
# 6> 客户端删除mount路径
#######################################################
def executing_case5():
    """1> 创建一个文件，并写入内容"""
    log.info("\t[ case5 create_file ]")

    cmd = "ssh %s touch %s/test && echo 'test' > %s/test" % (node_ip, NAS_PATH, NAS_PATH)
    rc, stdout, stderr = shell.ssh(node_ip, cmd)
    if rc != 0:
        log.info("rc = %s" % (rc))
        log.info("WARNING: \ncmd = %s\nstdout = %s\nstderr = %s" % (cmd, stdout, stderr))
        raise Exception('%s create_file failed!!!' % node_ip)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, stdout))

    """2> 客户端mount共享路径"""
    log.info("\t[ case5 客户端mount共享路径 ]")
    """2-1> 客户端创建mount路径"""
    cmd = "ssh %s ls /mnt/nfs_dir_16_0_4_103_1" % auth_clients_name
    rc, stdout, stderr = shell.ssh(node_ip, cmd)
    if stdout == "":
        cmd = "ssh %s umount -l /mnt/nfs_dir_16_0_4_103_1" % auth_clients_name
        rc, stdout, stderr = shell.ssh(node_ip, cmd)
        cmd = "ssh %s rm -rf /mnt/nfs_dir_16_0_4_103_1" % auth_clients_name
        rc, stdout, stderr = shell.ssh(node_ip, cmd)
        if rc != 0:
            log.error("WARNING: \ncmd = %s\nstdout = %s\nstderr = %s" % (cmd, stdout, stderr))
            raise Exception('%s rm -rf client file failed!!!' % node_ip)
    cmd = "ssh %s mkdir /mnt/nfs_dir_16_0_4_103_1" % auth_clients_name
    rc, stdout, stderr = shell.ssh(node_ip, cmd)
    if rc != 0:
        log.info("rc = %s" % (rc))
        log.info("WARNING: \ncmd = %s\nstdout = %s\nstderr = %s" % (cmd, stdout, stderr))
        raise Exception('%s create_file failed!!!' % node_ip)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, stdout))

    """2-2> 客户端mount共享路径"""
    wait_time1 = random.randint(3, 5)
    time.sleep(wait_time1)
    cmd1 = "ssh %s mount -t nfs %s:%s /mnt/nfs_dir_16_0_4_103_1" % (auth_clients_name, node_ip, NAS_PATH)
    rc, stdout, stderr = shell.ssh(node_ip, cmd1)
    print stdout
    if rc != 0:
        log.info("rc = %s" % (rc))
        log.info("WARNING: \ncmd = %s\nstdout = %s\nstderr = %s" % (cmd1, stdout, stderr))
        raise Exception('%s mount file failed!!!' % node_ip)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd1, stdout))

    """3> 测试r"""
    log.info("\t[ case5 test-r ]")
    cmd1 = "ssh %s ls /mnt/nfs_dir_16_0_4_103_1" % (auth_clients_name)
    rc, stdout, stderr = shell.ssh(node_ip, cmd1)
    print stdout
    if rc != 0 or stdout == "":
        log.info("rc = %s" % (rc))
        log.info("WARNING: \ncmd = %s\nstdout = %s\nstderr = %s" % (cmd1, stdout, stderr))
        raise Exception('%s test-r failed!!!' % node_ip)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd1, stdout))

    """4> 测试w"""
    log.info("\t[ case5 test-w ]")
    cmd2 = "ssh %s touch /mnt/nfs_dir_16_0_4_103_1/test2" % (auth_clients_name)
    rc, stdout, stderr = shell.ssh(node_ip, cmd2)
    if rc == 0:
        log.info("rc = %s" % (rc))
        log.info("WARNING: \ncmd = %s\nstdout = %s\nstderr = %s" % (cmd2, stdout, stderr))
        raise Exception('%s test-w failed!!!' % node_ip)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd2, stdout))

    """5> 客户端umount共享路径"""
    log.info("\t[ case5 客户端umount共享路径 ]")
    cmd1 = "ssh %s umount /mnt/nfs_dir_16_0_4_103_1" % (auth_clients_name)
    rc, stdout, stderr = shell.ssh(node_ip, cmd1)
    print stdout
    if rc != 0:
        log.info("rc = %s" % (rc))
        log.info("WARNING: \ncmd = %s\nstdout = %s\nstderr = %s" % (cmd1, stdout, stderr))
        raise Exception('%s umount file failed!!!' % node_ip)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd1, stdout))

    """6> 客户端删除mount路径"""
    log.info("\t[ case5 客户端删除mount路径 ]")
    cmd1 = "ssh %s rm -rf /mnt/nfs_dir_16_0_4_103_1 " % (auth_clients_name)
    rc, stdout, stderr = shell.ssh(node_ip, cmd1)
    print stdout
    if rc != 0:
        log.info("rc = %s" % (rc))
        log.info("WARNING: \ncmd = %s\nstdout = %s\nstderr = %s" % (cmd1, stdout, stderr))
        raise Exception('%s rm file failed!!!' % node_ip)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd1, stdout))

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
    executing_case1()
    executing_case2()
    executing_case3()
    executing_case4()
    executing_case5()
    prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)