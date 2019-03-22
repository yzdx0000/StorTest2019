# -*-coding:utf-8 -*
#######################################################
# author 张呈宇
# date 2018-05-02
# @summary：
# 16-0-4-115     单个NFS支持最大客户端数量
# @steps:
# case1、在az1上创建nfs共享，输入正确的名称和共享路径；
# pscli --command=create_nfs_export --access_zone_id=x --export_name=nfs_exp_test --export_path=volume:/nas/nfs_dir
# case2、查看nfs共享路径配置成功，信息是否与配置信息匹配；
# pscli --command=get_nfs_exports
# case3、添加nfs客户端5000个
# pscli --command=add_nfs_export_auth_clients --export_id=x --name=x.x.x.x/24 --permission_level=rw
# @changelog：
#
#######################################################
import os
import commands
import utils_path
import get_config
import log
import shell
import common
import nas_common
import get_config
import prepare_clean


FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)  # /mnt/volume1/snap/snap_16_0_4_115
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
    access_zone_name = "access_zone_16_0_4_115"
    node = common.Node()
    ids = node.get_nodes_id()
    print ids
    access_zone_node_id_16_0_4_115 = ','.join(str(p) for p in ids)
    msg1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_0_4_115, name=access_zone_name)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('%s create_access_zone failed!!!' % node_ip)
    global access_zone_id_16_0_4_115
    access_zone_id_16_0_4_115 = msg1["result"]

    # 2> 启动NAS
    log.info("\t[ enable_nas ]")
    msg2 = nas_common.enable_nas(access_zone_id=access_zone_id_16_0_4_115, protocol_types="NFS")
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('%s enable_nas failed!!!' % node_ip)

    # 3> 查看NAS是否按配置启动
    log.info("\t[ get_access_zones ]")
    check_result3 = nas_common.get_access_zones(ids=access_zone_id_16_0_4_115)
    name = check_result3["result"]["access_zones"][0]["name"]
    if name != access_zone_name:
        common.except_exit('%s enable_nas failed!!!' % node_ip)
    global auth_provider_id_16_0_4_115
    auth_provider_id_16_0_4_115 = check_result3["result"]["access_zones"][0]["auth_provider_id"]
    
    """1> 检查目录并creat file"""
    log.info("\t[ case1 step1 create_file ]")
    global nfs_path
    nfs_path = nas_common.ROOT_DIR + "nfs_dir_16_0_4_115"
    global NAS_PATH
    NAS_PATH = get_config.get_one_nas_test_path() + "/nfs_dir_16_0_4_115"
    cmd = "create_file "
    check_result6 = nas_common.create_file(path=nfs_path,
                                           posix_permission="rwxr-xr-x")
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result6))
    msg6 = check_result6
    if msg6["err_msg"] != "" or msg6["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result6))
        raise Exception('%s create_file failed!!!' % node_ip)

    """2> 检查file是否创建成功"""
    log.info("\t[case1 step2 get_file_list ]")
    cmd = "get_file_list "
    check_result7 = nas_common.get_file_list(path=nfs_path)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result7))
    msg7 = check_result7
    if msg7["err_msg"] != "" or msg7["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result7))
        raise Exception('%s get_file_list failed!!!' % node_ip)

    """3> 创建导出路径"""
    log.info("\t[ case1 step3 create_nfs_export ]")
    global nfs_export_name
    nfs_export_name = "nfs_exp_test_16_0_4_115"
    global description_nfs
    description_nfs = 'old_export_description'
    cmd = "create_nfs_export"
    check_result1 = nas_common.create_nfs_export(access_zone_id=access_zone_id_16_0_4_115,
                                                 export_name=nfs_export_name,
                                                 export_path=nfs_path,
                                                 description=description_nfs)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
    msg1 = check_result1
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        raise Exception('%s create_nfs_export failed!!!' % node_ip)
    global nfs_export_id_16_0_4_115
    nfs_export_id_16_0_4_115 = msg1["result"]

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
    log.info("\t[ case2 step1 get_nfs_exports ]")
    cmd = "get_nfs_exports"
    check_result = nas_common.get_nfs_exports(ids=nfs_export_id_16_0_4_115)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result))
    msg = check_result
    if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result))
        raise Exception('%s get_nfs_exports failed!!!' % node_ip)

    """2> 对比设置参数"""
    log.info("\t[ case2 step2 contrast parameters]")
    access_zone_id = check_result["result"]["exports"][0]["access_zone_id"]
    export_name = check_result["result"]["exports"][0]["export_name"]
    export_path = check_result["result"]["exports"][0]["export_path"]
    description = check_result["result"]["exports"][0]["description"]
    if access_zone_id != access_zone_id_16_0_4_115:
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
# @function：添加nfs客户端5000个；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：添加nfs客户端5000个；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
# 1> add_nfs_export_auth_clients
# 2> get_nfs_export_auth_clients
# 3> 对比设置参数
#######################################################
def executing_case3():
    log.info("\t[ case3-1 add_nfs_export_auth_clients ]")
    global auth_clients_permission_level
    auth_clients_permission_level = 'rw'
    for j in range(1, 21):
        for i in range(0, 250):
            m = (j - 1) * 250 + i
            log.info("\t[ case3 add_nfs_export_auth_clients %d ]" % m)
            global auth_clients_name
            auth_clients_name = "10.2.%s.%s" % (j, i)
            """1> add_nfs_export_auth_clients"""
            log.info("\t[ case3 step1 add_nfs_export_auth_clients ]")
            cmd = "add_nfs_export_auth_clients"
            check_result = nas_common.add_nfs_export_auth_clients(export_id=nfs_export_id_16_0_4_115,
                                                                  name=auth_clients_name,
                                                                  permission_level=auth_clients_permission_level)
            msg = check_result
            if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
                log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result))
                raise Exception('%s add_nfs_export_auth_clients failed!!!' % node_ip)
            global nfs_export_clients_id_16_0_4_115
            nfs_export_clients_id_16_0_4_115 = msg["result"][0]
            print nfs_export_clients_id_16_0_4_115

            """2> get_nfs_export_auth_clients"""
            log.info("\t[ case3 step2 get_nfs_export_auth_clients ]")
            cmd = "get_nfs_export_auth_clients"
            check_result = nas_common.get_nfs_export_auth_clients(export_ids=nfs_export_id_16_0_4_115)
            msg = check_result
            if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
                log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result))
                raise Exception('%s get_nfs_export_auth_clients failed!!!' % node_ip)

            """3> 对比设置参数"""
            log.info("\t[ case3 step3 contrast parameters]")
            anongid = check_result["result"]["nfs_export_auth_clients"][m]["anongid"]
            anonuid = check_result["result"]["nfs_export_auth_clients"][m]["anonuid"]
            id = check_result["result"]["nfs_export_auth_clients"][m]["id"]
            export_id = check_result["result"]["nfs_export_auth_clients"][m]["export_id"]
            name = check_result["result"]["nfs_export_auth_clients"][m]["name"]
            permission_constraint = check_result["result"]["nfs_export_auth_clients"][m]["permission_constraint"]
            permission_level = check_result["result"]["nfs_export_auth_clients"][m]["permission_level"]
            port_constraint = check_result["result"]["nfs_export_auth_clients"][m]["port_constraint"]
            write_mode = check_result["result"]["nfs_export_auth_clients"][m]["write_mode"]
            if anongid != 65534:
                raise Exception('%s anongid failed!!!' % node_ip)
            if anonuid != 65534:
                raise Exception('%s anonuid failed!!!' % node_ip)
            if id != nfs_export_clients_id_16_0_4_115:
                raise Exception('%s id failed!!!' % node_ip)
            if export_id != nfs_export_id_16_0_4_115:
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
            i = i+1
        j = j+1

    log.info("\t[ case3-2 add_nfs_export_auth_clients 5001]")
    global auth_clients_name
    auth_clients_name = nas_common.NFS_1_CLIENT_IP
    """1> add_nfs_export_auth_clients"""
    log.info("\t[ case3-2  add_nfs_export_auth_clients 5001]")
    cmd = "add_nfs_export_auth_clients "
    check_result = nas_common.add_nfs_export_auth_clients(export_id=nfs_export_id_16_0_4_115,
                                                          name=auth_clients_name,
                                                          permission_level=auth_clients_permission_level)
    msg = check_result
    if msg["err_msg"] == "" or msg["detail_err_msg"] == "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result))
        raise Exception('%s add_nfs_export_auth_clients failed!!!' % node_ip)

    return


#######################################################
# @function：清理环境
# @parameter：
# @return：
# @steps:
#######################################################
def clearing_environment():
    log.info("（3）clearing_environment")
    '''1> 删除export'''
    log.info("\t[ 删除export ]")
    cmd = "delete_nfs_exports "
    check_result1 = nas_common.delete_nfs_exports(ids=nfs_export_id_16_0_4_115)
    msg1 = check_result1
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        raise Exception('%s delete_nfs_export failed!!!' % node_ip)

    '''2> 删除目录'''
    log.info("\t[  删除目录 ]")
    global NAS_PATH
    NAS_PATH = get_config.get_one_nas_test_path() + "/nfs_dir_16_0_4_115"
    cmd1 = "ssh %s rm -rf %s " % (node_ip, NAS_PATH)
    rc, stdout, stderr = shell.ssh(node_ip, cmd1)
    print stdout
    if rc != 0:
        log.error("rc = %s" % rc)
        log.error("WARNING: \ncmd = %s\nstdout = %s\nstderr = %s" % (cmd1, stdout, stderr))
        raise Exception('%s rm file failed!!!' % node_ip)

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
    executing_case2()
    executing_case3()
    clearing_environment()
    prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)