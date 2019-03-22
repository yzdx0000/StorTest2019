# -*-coding:utf-8 -*
#######################################################
# author 张呈宇
# date 2018-04-25
# @summary：
# 16-0-4-89      共享路径深度极限测试
# @steps:
# case1、创建一个共享路径深度为255的NFS共享；
# pscli --command=create_nfs_export --access_zone_id=x --export_name=export1
# --export_path=volume:/dir3/dir4/…/dir255（注：255含/mnt/volume/）
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
import prepare_clean

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)  # /mnt/volume1/snap/snap_16_0_4_89
SYSTEM_IP = get_config.get_parastor_ip()
node_ip = SYSTEM_IP


#######################################################
# 1.executing_case1
# @function：创建一个共享路径深度为255的NFS共享；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：创建一个共享路径深度为255的NFS共享；
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
# 1> 检查目录并creat file
# 2> 检查file是否创建成功
# 3> 创建导出路径
# 4> 检查导出路径
#######################################################
def executing_case1():
    log.info("\t[1 create_access_zone ]")
    """准备环境"""
    # 1> 创建访问分区
    log.info("\t[case1 create_access_zone ]")
    access_zone_name = "access_zone_16_0_4_89"
    node = common.Node()
    ids = node.get_nodes_id()
    print ids
    access_zone_node_id_16_0_4_89 = ','.join(str(p) for p in ids)
    msg1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_0_4_89, name=access_zone_name)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('%s create_access_zone failed!!!' % node_ip)
    global access_zone_id_16_0_4_89
    access_zone_id_16_0_4_89 = msg1["result"]
    global nfs_export_id_16_0_4_89_list
    nfs_export_id_16_0_4_89_list = []
    nfs_path_list = []
    base_path_a = '%s' % nas_common.ROOT_DIR
    base_path = str(base_path_a)[:-1]
    print base_path
    nfs_path_list.append(base_path)
    for i in range(4, 256):
        """1> 检查目录并creat file"""
        log.info("\t[ case1 create_file %s ]" % i)
        cmd = 'folder="%s/nas" && if [ ! -d "$folder"]; then mkdir "$folder" fi' % get_config.get_one_nas_test_path()
        rc, stdout, stderr = shell.ssh(node_ip, cmd)
        if rc != 0:
            log.info("rc = %s" % (rc))
            log.info("WARNING: \n cmd = %s\n stdout = %s\n stderr = %s" % (cmd, stdout, stderr))
        log.info(stdout)
        nfs_path_nfs_dir = "%s" % i
        nfs_path_list.append(nfs_path_nfs_dir)
        nfs_path = '/'.join(str(j) for j in nfs_path_list)
        cmd = "create_file "
        check_result6 = nas_common.create_file(path=nfs_path, posix_permission="rwxr-xr-x")
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result6))
        msg6 = check_result6
        if msg6["err_msg"] != "" or msg6["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result6))
            raise Exception('%s create_file failed!!!' % node_ip)

        """2> 检查file是否创建成功"""
        log.info("\t[case1 get_file_list ]")
        cmd = "get_file_list "
        check_result7 = nas_common.get_file_list(path=nfs_path)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result7))
        msg7 = check_result7
        if msg7["err_msg"] != "" or msg7["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result7))
            raise Exception('%s get_file_list failed!!!' % node_ip)

        """3> 创建导出路径"""
        log.info("\t[ case1 create_nfs_export %s]" % i)
        global nfs_export_name
        nfs_export_name = "nfs_exp_test_16_0_4_89_1_%s" % i
        cmd = "create_nfs_export "
        check_result1 = nas_common.create_nfs_export(access_zone_id=access_zone_id_16_0_4_89,
                                                     export_name=nfs_export_name,
                                                     export_path=nfs_path)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        msg1 = check_result1
        if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
            raise Exception('%s create_nfs_export failed!!!' % node_ip)
        global nfs_export_id_16_0_4_89
        nfs_export_id_16_0_4_89 = msg1["result"]
        nfs_export_id_16_0_4_89_list.append(msg1["result"])

        """4>检查导出路径"""
        log.info("\t[ case1 get_nfs_exports ]")
        cmd = "get_nfs_exports "
        check_result = nas_common.get_nfs_exports(ids=nfs_export_id_16_0_4_89)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result))
        msg = check_result
        if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result))
            raise Exception('%s get_nfs_exports failed!!!' % node_ip)
        access_zone_id = check_result["result"]["exports"][0]["access_zone_id"]
        export_name = check_result["result"]["exports"][0]["export_name"]
        export_path = check_result["result"]["exports"][0]["export_path"]
        if access_zone_id != access_zone_id_16_0_4_89:
            raise Exception('%s access_zone_id ERROR!!!' % node_ip)
        if export_name != nfs_export_name:
            raise Exception('%s export_name ERROR!!!' % node_ip)
        if export_path != nfs_path:
            raise Exception('%s export_path ERROR!!!' % node_ip)

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
    for nfs_export_id in nfs_export_id_16_0_4_89_list:
        cmd = "delete_nfs_exports "
        check_result1 = nas_common.delete_nfs_exports(ids=nfs_export_id)
        log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        msg1 = check_result1
        if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
            log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
            raise Exception('%s delete_nfs_export failed!!!' % node_ip)

    '''2> 删除目录'''
    log.info("\t[ 删除目录 ]")
    cmd = 'rm -rf %s/4' % get_config.get_one_nas_test_path()
    rc, stdout, stderr = shell.ssh(node_ip, cmd)
    if rc != 0:
        log.info("rc = %s" % (rc))
        log.info("WARNING: \n cmd = %s\n stdout = %s\n stderr = %s" % (cmd, stdout, stderr))
    log.info(stdout)

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
    prepare_clean.nas_test_prepare(FILE_NAME)
    preparing_environment()
    executing_case1()
    clearing_environment()
    prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)