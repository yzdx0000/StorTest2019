# -*-coding:utf-8 -*
#######################################################
# author 张呈宇
# date 2018-04-24
# @summary：
# 16-0-4-83     正常创建NFS共享测试
# @steps:
# case1、创建3节点访问分区az1，启动nas服务；
# case2、创建共享路径volume:/nas/nfs_dir
# pscli --command=create_file --path=volume:/nas/nfs_dir
# case3、在az1上创建nfs共享，输入正确的名称和共享路径；
# pscli --command=create_nfs_export --access_zone_id=x --export_name=nfs_exp_test --export_path=volume:/nas/nfs_dir
# case4、查看nfs共享路径配置成功，信息是否与配置信息匹配；
# pscli --command=get_nfs_exports
# @changelog：
#
#######################################################
import json
import os
import random
import time
import commands
import utils_path
import common
import get_config
import log
import nas_common
import shell
import prepare_clean

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)  # /mnt/volume1/snap/snap_16_0_4_83
SYSTEM_IP = get_config.get_parastor_ip()
node_ip = SYSTEM_IP


#######################################################
# 1.executing_case1
# @function：创建3节点访问分区az1，启动nas服务；
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：满足一定格式的创建3节点访问分区az1
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
# 1> 更新参数
# 2> 创建node pool
# 3> start up
# 4> 创建访问分区
# 5> 启动NAS
# 6> 查看NAS是否按配置启动
#######################################################
def executing_case1():
    log.info("\t[ case1 update_access_zone ]")
    log.info("preparing_environment")
    """
    # 1> 更新参数
    log.info("update_param")
    cmd = " pscli --command=update_param --section=MGR " \
          "--name=min_meta_replica --current=1"
    check_result1 = nas_common.update_param(section="MGR", name="min_meta_replica", current=1)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
    msg1 = check_result1
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        raise Exception('%s update_param failed!!!' % node_ip)

    # 2> 创建node pool
    log.info("create_node_pool")
    cmd = "pscli --command=create_node_pool --node_ids=1,2,3 --replica_num=1 " \
          " --stripe_width=4 --disk_parity_num=2 --node_parity_num=1 " \
          "--name=firstpool"
    check_result2 = nas_common.create_node_pool(node_ids="1,2,3", replica_num=1, stripe_width=1, disk_parity_num=0,
                                                node_parity_num=0, name="firstpool")
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))

    msg2 = check_result2
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
        raise Exception('%s create_node_pool failed!!!' % node_ip)

    # 3> start up
    log.info("startup")
    cmd = "pscli --command=startup "
    check_result3 = nas_common.startup()
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result3))
    msg3 = check_result3
    if msg3["err_msg"] != "" or msg3["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result3))
        raise Exception('%s startup failed!!!' % node_ip)
    """
    '''4> 创建访问分区'''
    log.info("\t[case1 create_access_zone ]")
    access_zone_name = "access_zone_16_0_4_83"
    node = common.Node()
    ids = node.get_nodes_id()
    print ids
    access_zone_node_id_16_0_4_83 = ','.join(str(p) for p in ids)
    cmd = "create_access_zone "
    check_result1 = nas_common.create_access_zone(node_ids=access_zone_node_id_16_0_4_83,
                                                  name=access_zone_name,
                                                  isns_address="10.22.0.78")
    log.info('node_ip = %s, cmd = %s, check_result1 = %s' % (node_ip, cmd, check_result1))
    msg1 = check_result1
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        raise Exception('%s create_access_zone failed!!!' % node_ip)
    global access_zone_id_16_0_4_83
    access_zone_id_16_0_4_83 = msg1["result"]

    '''5> 启动NAS'''
    log.info("\t[ enable_nas ]")
    cmd = "enable_nas "
    check_result2 = nas_common.enable_nas(access_zone_id=access_zone_id_16_0_4_83, protocol_types="NFS")
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result2))
    msg = check_result2
    if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        raise Exception('%s enable_nas failed!!!' % node_ip)

    '''6> 查看NAS是否按配置启动'''
    log.info("\t[ get_access_zones ]")
    cmd = "get_access_zones "
    check_result3 = nas_common.get_access_zones()
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result3))
    name = check_result3["result"]["access_zones"][0]["name"]
    if name != access_zone_name:
        raise Exception('%s enable_nas failed!!!' % node_ip)
    return check_result3


#######################################################
# 2.executing_case2
# @function：创建共享路径volume:/nas/nfs_dir
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：创建共享路径volume:/nas/nfs_dir
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
# 1> 创建storage pool
# 2> 创建volume
# 3> 检查目录并creat file
# 4> 检查file是否创建成功
#######################################################
def executing_case2():
    """
    # 1> 创建storage pool
    log.info("case2 create_storage_pool")
    cmd = "pscli --command=create_storage_pool --name=stor1 --type=FILE --node_pool_ids=1"
    check_result4 = nas_common.create_storage_pool(name="stor1", type="FILE", node_pool_ids=1)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result4))
    msg4 = check_result4
    if msg4["err_msg"] != "" or msg4["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result4))
        raise Exception('%s create_storage_pool failed!!!' % node_ip)

    # 2> 创建volume
    log.info("create_volume")
    cmd = "pscli --command=create_volume --name=volume --storage_pool_id=2 " \
          "--is_simple_conf=true --min_throughput=0 --max_throughput=100 --min_iops=0 " \
          "--max_iops=100 --replica_num=1 --stripe_width=1 --disk_parity_num=0 " \
          "--node_parity_num=0 --total_bytes=100 --dir_slice_num=1 --chunk_size=4096 " \
          "--obj_size=67108864"
    check_result5 = nas_common.create_volume(name="volume", storage_pool_id=2,
                                             is_simple_conf="true", min_throughput="0", max_throughput="100",
                                             min_iops="0", max_iops="100", replica_num=1, stripe_width=1,
                                             disk_parity_num=0,
                                             node_parity_num=0, total_bytes=100, dir_slice_num=1, chunk_size=4096,
                                             obj_size=67108864)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result5))
    msg5 = check_result5
    if msg5["err_msg"] != "" or msg5["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result5))
        raise Exception('%s create_volume!!!' % node_ip)
    """
    # 3> 检查目录并creat file
    log.info("\t[ create_file ]")
    # cmd = 'folder="/mnt/volume/nas" && if [ ! -d "$folder"]; then mkdir "$folder" fi'
    # rc, stdout, stderr = shell.ssh(node_ip, cmd)
    # if rc != 0:
    #     log.info("rc = %s" % (rc))
    #     log.info("WARNING: \ncmd = %s\nstdout = %s\nstderr = %s" % (cmd, stdout, stderr))
    # log.info(stdout)

    global nfs_path
    nfs_path = nas_common.ROOT_DIR + "nfs_dir_16_0_4_83"
    global NAS_PATH
    NAS_PATH = get_config.get_one_nas_test_path() + "/nfs_dir_16_0_4_83"
    cmd = "create_file"
    check_result6 = nas_common.create_file(path=nfs_path, posix_permission="rwxr-xr-x")
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result6))
    msg6 = check_result6
    if msg6["err_msg"] != "" or msg6["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result6))
        raise Exception('%s create_file failed!!!' % node_ip)

    # 4> 检查file是否创建成功
    log.info("\t[ get_file_list ]")
    cmd = "get_file_list "
    check_result7 = nas_common.get_file_list(path=nfs_path)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result7))
    msg7 = check_result7
    if msg7["err_msg"] != "" or msg7["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result7))
        raise Exception('%s get_file_list failed!!!' % node_ip)

    return msg7


#######################################################
# 3.executing_case3
# @function：在az1上创建nfs共享，输入正确的名称和共享路径
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：满足一定格式的创建ftp共享
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps: create_nfs_export
#######################################################
def executing_case3():
    log.info("\t[ create_nfs_export ]")
    cmd = "create_nfs_export "
    check_result1 = nas_common.create_nfs_export(access_zone_id=access_zone_id_16_0_4_83, export_name="nfs_exp_test",
                                                 export_path=nfs_path)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
    msg1 = check_result1
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        raise Exception('%s create_nfs_export failed!!!' % node_ip)
    global nfs_export_id_16_0_4_83
    nfs_export_id_16_0_4_83 = msg1["result"]
    return


#######################################################
# 4.executing_case4
# @function：查看nfs共享路径配置成功，信息是否与配置信息匹配
# @parameter：
#       node_ip：执行cmd命令的节点ip
#       cmd：查看nfs共享路径配置
# @return：
#       check_result —— 执行create命令的字典格式返回值
# @steps:
# 1> get_nfs_exports
# 2> 对比设置参数

#######################################################
def executing_case4():
    # 1> get_ftp_exports
    log.info("\t[ get_nfs_exports ]")
    cmd = "get_nfs_exports"
    check_result = nas_common.get_nfs_exports(ids=nfs_export_id_16_0_4_83)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result))
    msg = check_result
    if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result))
        raise Exception('%s get_nfs_exports failed!!!' % node_ip)

    # 2> 对比设置参数
    access_zone_id = check_result["result"]["exports"][0]["access_zone_id"]
    export_name = check_result["result"]["exports"][0]["export_name"]
    export_path = check_result["result"]["exports"][0]["export_path"]
    if access_zone_id != access_zone_id_16_0_4_83:
        raise Exception('%s creat and get_nfs_exports failed1!!!' % node_ip)
    if export_name != 'nfs_exp_test':
        raise Exception('%s creat and get_nfs_exports failed2!!!' % node_ip)
    if export_path != nfs_path:
        raise Exception('%s creat and get_nfs_exports failed3!!!' % node_ip)
    return msg


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
    check_result1 = nas_common.delete_nfs_exports(ids=nfs_export_id_16_0_4_83)
    log.info('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
    msg1 = check_result1
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        log.error('node_ip = %s, cmd = %s, check_result = %s' % (node_ip, cmd, check_result1))
        raise Exception('%s delete_nfs_export failed!!!' % node_ip)

    '''2> 删除目录'''
    log.info("\t[ 删除目录 ]")
    cmd = 'rm -rf %s' % NAS_PATH
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
    executing_case4()
    clearing_environment()
    prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)