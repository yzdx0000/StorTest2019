# -*-coding:utf-8 -*
import os
import time

import utils_path
import common
import nas_common
import log
import get_config
import quota_common
import prepare_clean

####################################################################################
#
# Author: liyao
# date 2018-06-07
# @summary：
#    nfs目录inode数配额硬阈值
# @steps:
#    1、创建ad访问分区，创建访问分区，启动NAS
#    2、创建共享目录，导出并授权某个用户的导出权限
#    3、针对目录配置inode数为100硬阈值的配额
#    4、通过nfs客户端先写入100个文件
#    5、尝试继续写入文件，检查配额是否生效
#    6、删除配额及所创建的文件
#    7、删除nfs_export_auth_clients, nfs_exports, 访问分区及ad认证服务器，清理环境
#
# @changelog：
####################################################################################
VOLUME_NAME = get_config.get_one_volume_name()
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0].replace('-', '_')                 # 本脚本名字
NAS_PATH = get_config.get_one_nas_test_path()                            # /mnt/volume/nas_test_dir
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)             # /mnt/volume/nas_test_dir/nas_16_6_0_16
BASE_NAS_PATH = os.path.dirname(NAS_PATH)                                # /mnt/volume
NAS_PATH_BASENAME = os.path.basename(NAS_PATH)                           # nas_test_dir
SYSTEM_IP_0 = get_config.get_parastor_ip(0)
SYSTEM_IP_1 = get_config.get_parastor_ip(1)
SYSTEM_IP_2 = get_config.get_parastor_ip(2)


def umount(auth_name_ip, local_path):
    cmd = 'umount %s' % local_path
    rc, stdout = common.run_command(auth_name_ip, cmd)
    return rc


def case():
    '''函数执行主体'''
    '''1> 创建3节点访问分区az1，不启动nas服务'''
    """创建AD认证"""
    log.info("\t[ 2.add_auth_provider_ad ]")
    ad_server_name = 'ad_server_' + FILE_NAME
    exe_info = nas_common.add_auth_provider_ad(ad_server_name, nas_common.AD_DOMAIN_NAME, nas_common.AD_DNS_ADDRESSES,
                                               nas_common.AD_USER_NAME, nas_common.AD_PASSWORD,
                                               services_for_unix="NONE")
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('add auth provider ad %s failed !!!' % ad_server_name)
        raise Exception('add auth provider ad %s failed !!!' % ad_server_name)
    ad_server_id = exe_info['result']

    """get_auth_providers_ad"""
    log.info("\t[ 3.get_auth_provider_ad ]")
    exe_info = nas_common.get_auth_providers_ad(ad_server_id)
    ad_server = exe_info['result']['auth_providers'][0]
    if ad_server['name'] == ad_server_name and ad_server['domain_name'] == nas_common.AD_DOMAIN_NAME and \
            ad_server['id'] == ad_server_id and ad_server['name'] == ad_server_name:
        log.info('params of auth provider are correct !')
    else:
        log.error('params of auth provider are wrong !!!')
        raise Exception('params of auth provider are wrong !!!')

    """check_auth_provider"""
    nas_common.check_auth_provider(ad_server_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('check auth provider failed !!!')
        raise Exception('check auth provider failed !!!')

    """创建访问分区"""
    obj_node = common.Node()
    nodes_id_list = obj_node.get_nodes_id()
    nodes_id_str = ','.join(str(p) for p in nodes_id_list)
    access_zone_name = 'az_' + FILE_NAME
    exe_info = nas_common.create_access_zone(nodes_id_str, access_zone_name, ad_server_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('create access zone %s failed !!!' % access_zone_name)
        raise Exception('create access zone %s failed !!!' % access_zone_name)
    access_zone_id = exe_info['result']

    """启动nas服务"""
    exe_info = nas_common.enable_nas(access_zone_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('enable nas failed !!!')
        raise Exception('enable nas failed !!!')

    '''2> 创建共享目录并授权某个用户的导出权限'''
    """检查NAS_PATH是否存在"""
    cmd = 'ls %s' % NAS_PATH
    rc, stdout = common.run_command(SYSTEM_IP_1, cmd)
    if rc != 0:
        cmd = 'mkdir -p %s' % NAS_TRUE_PATH
        common.run_command(SYSTEM_IP_1, cmd)
    else:
        cmd = 'mkdir %s' % NAS_TRUE_PATH
        common.run_command(SYSTEM_IP_1, cmd)

    """在存储卷里创建目录并导出共享目录"""
    log.info('waiting for 15s')
    time.sleep(15)

    export_name = 'nfs_exp_test'
    create_export_path = VOLUME_NAME + ':/' + os.path.join(NAS_PATH_BASENAME, FILE_NAME)
    export_sys_ip = SYSTEM_IP_2
    exe_info = nas_common.create_nfs_export(access_zone_id, export_name, create_export_path)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('create nfs export failed !!!')

    exe_info = nas_common.get_nfs_exports()
    nfs_info = exe_info['result']['exports']
    for mem in nfs_info:
        if mem['export_name'] == export_name:
            export_id = mem['id']
            break
    else:
        common.except_exit('nfs export information is wrong !!!')

    """授权某个用户的导出权限"""
    permission_level = 'rw'
    auth_name_ip = nas_common.CLIENT_IP_1
    exe_info = nas_common.add_nfs_export_auth_clients(export_id, auth_name_ip, permission_level)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('add nfs export auth clients failed !!!')
    export_auth_id = exe_info['result'][0]
    log.info('waiting for 15s')
    time.sleep(15)

    """nfs客户端挂载"""
    mount_path = SYSTEM_IP_1 + ':/' + NAS_TRUE_PATH
    local_path = os.path.join('/home/local', FILE_NAME)
    cmd = 'mkdir -p %s' % local_path
    common.run_command(auth_name_ip, cmd)

    rc = umount(auth_name_ip, local_path)   # 检查本地路径是否已经mount
    if rc != 0:
        log.info('local path did not mount')

    log.info("\t[ 2-2> 客户端mount共享路径 ]")
    begin_time = time.time()
    rc = 1
    while rc != 0:
        cmd = "mount -t nfs %s %s" % (mount_path, local_path)
        rc, stdout = common.run_command(auth_name_ip, cmd)
        print stdout
        last_time = time.time()
        during_time = last_time - begin_time
        if int(during_time) >= 15:
            common.except_exit('mount time exceeded 15s !!!')
        time.sleep(5)

    exe_info = nas_common.get_nfs_export_auth_clients(export_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('mount nfs failed !!!')

    '''3> 针对目录配置inode数为100的硬阈值配额'''
    quota_path = create_export_path
    rc, check_result = quota_common.create_one_quota(path=quota_path,
                                                     filenr_quota_cal_type='QUOTA_LIMIT',
                                                     filenr_hard_threshold=100)
    common.judge_rc(rc, 0, "create quota failed", exit_flag=False)

    rc, quota_id = quota_common.get_one_quota_id(path=quota_path,
                                                 u_or_g_type=quota_common.TYPE_CATALOG)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    '''4> 通过nfs客户端先写入100个文件'''
    for i in range(100):
        file_name = 'test' + str(i)
        file_path = os.path.join(local_path, file_name)
        cmd = 'echo 111 > %s' % file_path
        common.run_command(auth_name_ip, cmd)

    '''5> 尝试继续写入文件，检查配额是否生效'''
    file_create_again_name = 'test_again'
    file_create_again_path = os.path.join(local_path, file_create_again_name)
    cmd = 'echo 222 > %s' % file_create_again_path
    rc, stdout = common.run_command(auth_name_ip, cmd)
    common.judge_rc_unequal(rc, 0, 'quota did not work well !!!')

    '''6> 删除配额及文件'''
    rc = umount(auth_name_ip, local_path)
    common.judge_rc(rc, 0, 'umount %s failed !!!' % local_path)

    rc, stdout = quota_common.delete_one_quota(quota_id)
    common.judge_rc(rc, 0, 'delete quota failed !!!')

    deleted_file_path = os.path.dirname(local_path)
    deleted_file_path = os.path.join(deleted_file_path, '*')
    common.rm_exe(auth_name_ip, deleted_file_path)

    '''7> 删除访问分区，删除ad认证服务器'''
    exe_info = nas_common.disable_nas(access_zone_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('disable nas failed !!!')

    exe_info = nas_common.delete_nfs_exports(export_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('delete nfs exports failed !!!')

    exe_info = nas_common.delete_access_zone(access_zone_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('delete access zone %s failed !!!' % access_zone_name)

    exe_info = nas_common.delete_auth_providers(ad_server_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('delete auth provider %s failed !!!' % ad_server_name)

    delete_sys_path = os.path.join(NAS_PATH, '*')
    common.rm_exe(export_sys_ip, delete_sys_path)


def nas_main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    prepare_clean.nas_test_clean()
    # nas_common.cleaning_environment()
    case()
    prepare_clean.nas_test_clean()
    log.info('%s succeed!' % FILE_NAME)

    return


if __name__ == '__main__':
    nas_main()