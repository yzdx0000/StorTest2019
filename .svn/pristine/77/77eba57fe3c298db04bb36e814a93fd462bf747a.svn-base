# -*-coding:utf-8 -*
#######################################################
# author 张呈宇
# date 2018-05-09
# @summary：
# 16-0-4-114      规格极限最大客户端数量
# @steps:
# case1、通过脚本添加NFS授权客户端数量到集群规格；
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
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)  # /mnt/volume1/snap/snap_16_0_4_114
SYSTEM_IP = get_config.get_parastor_ip()
node_ip = SYSTEM_IP


#######################################################
# 1.executing_case1
# @function：通过脚本添加NFS授权客户端数量到集群规格;
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：通过脚本添加NFS授权客户端数量到集群规格;
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
# 0> 查看目前已有数目
# 1> 检查目录并creat file
# 2> 检查file是否创建成功
# 3> 创建导出路径
# 4> 检查导出路径
# 5>
# 6> 检查总数量
# 7> 创建第65537个nfs导出
#######################################################
def executing_case1():
    """准备环境"""
    # 1> 创建访问分区
    log.info("\t[case1 create_access_zone ]")
    access_zone_name = "access_zone_16_0_4_114"
    node = common.Node()
    ids = node.get_nodes_id()
    print ids
    access_zone_node_id_16_0_4_114 = ','.join(str(p) for p in ids)
    msg1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_0_4_114, name=access_zone_name)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('%s create_access_zone failed!!!' % node_ip)
    global access_zone_id_16_0_4_114
    access_zone_id_16_0_4_114 = msg1["result"]

    # 2> 启动NAS
    log.info("\t[ enable_nas ]")
    msg2 = nas_common.enable_nas(access_zone_id=access_zone_id_16_0_4_114, protocol_types="NFS")
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s enable_nas failed!!!' % node_ip)

    # 3> 查看NAS是否按配置启动
    log.info("\t[ get_access_zones ]")
    check_result3 = nas_common.get_access_zones(ids=access_zone_id_16_0_4_114)
    name = check_result3["result"]["access_zones"][0]["name"]
    if name != access_zone_name:
        common.except_exit('%s enable_nas failed!!!' % node_ip)
    global auth_provider_id_16_0_4_114
    auth_provider_id_16_0_4_114 = check_result3["result"]["access_zones"][0]["auth_provider_id"]
    global delete_nfs_export_id
    delete_nfs_export_id = []

    """0> 查看目前已有exprorts并删除"""
    log.info("\t[ case1-0 delete_old_nfs_exports ]")
    totalnumber = 5  # 65537
    global number_16_0_4_114
    number_16_0_4_114 = totalnumber
    for i in range(1, number_16_0_4_114):
        """1> 检查目录并creat file"""
        log.info("\t[ case1-1 create_file %d]" % i)
        global nfs_path
        nfs_path = nas_common.ROOT_DIR + "nfs_dir_16_0_4_114_1_%s" % i

        cmd = "create_file "
        check_result6 = nas_common.create_file(path=nfs_path, posix_permission="rwxr-xr-x")
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result6))
        msg6 = check_result6
        if msg6["err_msg"] != "" or msg6["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result6))
            raise Exception('%s create_file failed!!!' % node_ip)

        """2> 检查file是否创建成功"""
        log.info("\t[case1-2 get_file_list %d]" % i)
        cmd = "get_file_list"
        check_result7 = nas_common.get_file_list(path=nfs_path)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result7))
        msg7 = check_result7
        if msg7["err_msg"] != "" or msg7["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result7))
            raise Exception('%s get_file_list failed!!!' % node_ip)

        """3> 创建导出路径"""
        log.info("\t[ case1-3 create_nfs_export %d]" % i)
        global nfs_export_name
        nfs_export_name = "nfs_exp_test_16_0_4_114_1_%s" % i
        global description_nfs
        cmd = "create_nfs_export "
        check_result1 = nas_common.create_nfs_export(access_zone_id=access_zone_id_16_0_4_114,
                                                     export_name=nfs_export_name,
                                                     export_path=nfs_path)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        msg1 = check_result1
        if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
            raise Exception('%s create_nfs_export failed!!!' % node_ip)
        global nfs_export_id_16_0_4_114
        nfs_export_id_16_0_4_114 = msg1["result"]
        delete_nfs_export_id.append(msg1["result"])

        """4>检查导出路径"""
        """4-1> get_ftp_exports"""
        log.info("\t[ case1-4-1 get_nfs_exports %d]" % i)
        cmd = "get_nfs_exports "
        check_result = nas_common.get_nfs_exports(ids=nfs_export_id_16_0_4_114)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result))
        msg = check_result
        if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result))
            raise Exception('%s get_nfs_exports failed!!!' % node_ip)
        """4-2> 对比设置参数"""
        log.info("\t[ case1-4-2 contrast parameters]")
        access_zone_id = check_result["result"]["exports"][0]["access_zone_id"]
        export_name = check_result["result"]["exports"][0]["export_name"]
        export_path = check_result["result"]["exports"][0]["export_path"]
        if access_zone_id != access_zone_id_16_0_4_114:
            raise Exception('%s access_zone_id failed!!!' % node_ip)
        if export_name != nfs_export_name:
            raise Exception('%s export_name failed!!!' % node_ip)
        if export_path != nfs_path:
            raise Exception('%s export_path failed!!!' % node_ip)

        """5>检查导出路径"""
        log.info("\t[ case1-5 add_nfs_export_auth_clients %d]" % i)
        global auth_clients_permission_level
        auth_clients_permission_level = 'rw'
        for j in range(1, 21):  # 21
            for k in range(0, 250):
                m = (i - 1) * 5000 + (j - 1) * 250 + k  # ->5000
                h = i // 256
                n = i % 256
                log.info("\t[ case1-5 add_nfs_export_auth_clients %d ]" % m)
                global auth_clients_name
                auth_clients_name = "%s.%s.%s.%s" % (j, k, h, n)
                """1> add_nfs_export_auth_clients"""
                log.info("\t[ case1-5 step1 add_nfs_export_auth_clients %d]" % m)
                cmd = "add_nfs_export_auth_clients "
                check_result = nas_common.add_nfs_export_auth_clients(export_id=nfs_export_id_16_0_4_114,
                                                                      name=auth_clients_name,
                                                                      permission_level=auth_clients_permission_level)
                log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result))
                msg = check_result
                if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
                    log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result))
                    raise Exception('%s add_nfs_export_auth_clients failed!!!' % node_ip)
                global nfs_export_clients_id_16_0_4_114
                nfs_export_clients_id_16_0_4_114 = msg["result"][0]
                print nfs_export_clients_id_16_0_4_114

                """2> get_nfs_export_auth_clients"""
                log.info("\t[ case3 step2 get_nfs_export_auth_clients %d]" % m)
                cmd = "get_nfs_export_auth_clients"
                check_result = nas_common.get_nfs_export_auth_clients(export_ids=nfs_export_id_16_0_4_114)
                log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result))
                msg = check_result
                if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
                    log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result))
                    raise Exception('%s get_nfs_export_auth_clients failed!!!' % node_ip)

                """3> 对比设置参数"""
                log.info("\t[ case3 step3 contrast parameters %d]" % m)
                s = m % 5000
                anongid = check_result["result"]["nfs_export_auth_clients"][s]["anongid"]
                anonuid = check_result["result"]["nfs_export_auth_clients"][s]["anonuid"]
                id = check_result["result"]["nfs_export_auth_clients"][s]["id"]
                export_id = check_result["result"]["nfs_export_auth_clients"][s]["export_id"]
                name = check_result["result"]["nfs_export_auth_clients"][s]["name"]
                permission_constraint = check_result["result"]["nfs_export_auth_clients"][s]["permission_constraint"]
                permission_level = check_result["result"]["nfs_export_auth_clients"][s]["permission_level"]
                port_constraint = check_result["result"]["nfs_export_auth_clients"][s]["port_constraint"]
                write_mode = check_result["result"]["nfs_export_auth_clients"][s]["write_mode"]
                if anongid != 65534:
                    raise Exception('%s anongid failed!!!' % node_ip)
                if anonuid != 65534:
                    raise Exception('%s anonuid failed!!!' % node_ip)
                if id != nfs_export_clients_id_16_0_4_114:
                    raise Exception('%s id failed!!!' % node_ip)
                if export_id != nfs_export_id_16_0_4_114:
                    raise Exception('%s export_id failed!!!' % node_ip)
                if name != auth_clients_name:
                    raise Exception('%s name failed!!!' % node_ip)
                if permission_constraint != "root_squash":
                    raise Exception('%s permission_constraint failed!!!' % node_ip)
                if permission_level != auth_clients_permission_level:
                    raise Exception('%s permission_level failed!!!' % node_ip)
                if port_constraint != "secure":
                    raise Exception('%s port_constraint failed!!!' % node_ip)
                if write_mode != "async":
                    raise Exception('%s write_mode failed!!!' % node_ip)
                k = k + 1
            j = j + 1
        i = i + 1

    """6>检查总数量"""
    log.info("\t[ case1-6 get_nfs_export_auth_clients ]")
    cmd = "get_nfs_export_auth_clients"
    check_result = nas_common.get_nfs_export_auth_clients()
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result))
    msg = check_result
    if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result))
        raise Exception('%s get_nfs_export_auth_clients failed!!!' % node_ip)
    number = msg["result"]["total"]
    print number
    '''
    if number != 327680000:  #1000->327680000
        raise Exception('%s total number ERROR!!!' % node_ip)

    """7>创建第327680001个nfs_export_auth_clients"""
    log.info("\t[ case1-7 创建第327680001个nfs_export_auth_clients ]")
    """7-1> 检查目录并creat file"""
    log.info("\t[ case1-7-1 create_file ]")
    global nfs_path
    nfs_path = nas_common.ROOT_DIR + "nfs_dir_16_0_4_114_1_65537" 
    cmd = "create_file " 
    check_result6 = nas_common.create_file(path=nfs_path, posix_permission="rwxr-xr-x")
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result6))
    msg6 = check_result6
    if msg6["err_msg"] != "" or msg6["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result6))
        raise Exception('%s create_file failed!!!' % node_ip)

    """7-2> 检查file是否创建成功"""
    log.info("\t[case1-7-2 get_file_list ]")
    cmd = "get_file_list " 
    check_result7 = nas_common.get_file_list(path=nfs_path)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result7))
    msg7 = check_result7
    if msg7["err_msg"] != "" or msg7["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result7))
        raise Exception('%s get_file_list failed!!!' % node_ip)

    """7-3> 创建导出路径"""
    log.info("\t[ case1-7-3 create_nfs_export ]")
    global nfs_export_name
    nfs_export_name = "nfs_exp_test_16_0_4_114_1_65537"
    cmd = "create_nfs_export " 
    check_result1 = nas_common.create_nfs_export(access_zone_id=access_zone_id_16_0_4_114,
                                                 export_name=nfs_export_name,
                                                 export_path=nfs_path)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
    msg1 = check_result1
    if msg1["err_msg"] == "" or msg1["detail_err_msg"] == "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        raise Exception('%s create_nfs_export 65537 failed!!!' % node_ip)

    """7-4> 删除导出路径"""
    log.info("\t[ case1-7-4 删除导出路径 65537]")
    NAS_PATH = get_config.get_one_nas_test_path() + "/nfs_dir_16_0_4_114_1_65537"
    cmd1 = "ssh %s rm -rf %s " % (node_ip, NAS_PATH)
    rc, stdout, stderr = shell.ssh(node_ip, cmd1)
    print stdout
    if rc != 0:
        log.info("rc = %s" % rc)
        log.info("WARNING: \ncmd = %s\nstdout = %s\nstderr = %s" % (cmd1, stdout, stderr))
        raise Exception('%s rm file failed!!!' % node_ip)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd1, stdout))
    '''
    return


#######################################################
# @function：清理环境
# @parameter：
# @return：
# @steps:
#######################################################
def clearing_environment():
    log.info("（3）clearing_environment")
    for i in range(1, number_16_0_4_114):
        '''1> 删除export'''
        log.info("\t[ 删除export ]")
        delete_nfs_export_id_a = delete_nfs_export_id[i - 1]
        cmd = "delete_nfs_exports "
        check_result1 = nas_common.delete_nfs_exports(ids=delete_nfs_export_id_a)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        msg1 = check_result1
        if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
            raise Exception('%s delete_nfs_export failed!!!' % node_ip)

        '''2> 删除目录'''
        global NAS_PATH
        NAS_PATH = get_config.get_one_nas_test_path() + "/nfs_dir_16_0_4_114_1_%s" % i
        cmd1 = "ssh %s rm -rf %s " % (node_ip, NAS_PATH)
        rc, stdout, stderr = shell.ssh(node_ip, cmd1)
        print stdout
        if rc != 0:
            log.info("rc = %s" % rc)
            log.info("WARNING: \ncmd = %s\nstdout = %s\nstderr = %s" % (cmd1, stdout, stderr))
            raise Exception('%s rm file failed!!!' % node_ip)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd1, stdout))

    return


#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def executing_case():
    log.info("（2）executing_case")

    '''
    1、测试执行
    2、结果检查
    '''

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
    clearing_environment()
    prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)