# -*-coding:utf-8 -*
import os
import time
import sys

import utils_path
import common
import nas_common
import log
import get_config
import quota_common
import prepare_clean
####################################################################################
#
# Author: liyi
# date 2018-11-15
# @summary：
#    nfs目录在删除操作后，inode嵌套配额是否生效
# @steps:
#    1、创建ad访问分区，创建访问分区，启动NAS
#    2、创建共享目录，导出并授权某个用户的导出权限
#    3、对父目录配置inode硬阈值120;子目录inode软阈值：100
#    4、通过nfs客户端在子目录下写入120个文件，预计100个
#    5、删除子目录下文件
#    6、子目录nesting1_1下写120数据，预计119个（父配额120）
# @changelog：
####################################################################################
VOLUME_NAME = get_config.get_one_volume_name()
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0].replace('-', '_')                 # 本脚本名字
NAS_PATH = get_config.get_one_nas_test_path()                            # /mnt/volume/nas_test_dir
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)             # /mnt/volume/nas_test_dir/quota_nas_4
BASE_NAS_PATH = os.path.dirname(NAS_PATH)                                # /mnt/volume
NAS_PATH_BASENAME = os.path.basename(NAS_PATH)                           # nas_test_dir
SYSTEM_IP_0 = get_config.get_parastor_ip(0)
SYSTEM_IP_1 = get_config.get_parastor_ip(1)
SYSTEM_IP_2 = get_config.get_parastor_ip(2)
local_path = os.path.join('/home/local', FILE_NAME)


def umount(auth_name_ip, local_path):
    cmd = 'umount %s' % local_path
    rc, stdout = common.run_command(auth_name_ip, cmd)
    return rc


def case():
    log.info("1>创建访问分区")
    rc_lst = {}
    """同步NTP"""
    cmd = 'pscli --command=set_ntp --is_enabled=true --ntp_servers=%s' % nas_common.AD_DNS_ADDRESSES
    rc, stdout = common.run_command(SYSTEM_IP_0, cmd)
    common.judge_rc(rc, 0, 'set ntp failed !!!')

    log.info("1.1>创建认证服务")
    ad_server_name = 'ad_server_' + FILE_NAME
    exe_info = nas_common.add_auth_provider_ad(ad_server_name, nas_common.AD_DOMAIN_NAME, nas_common.AD_DNS_ADDRESSES,
                                               nas_common.AD_USER_NAME, nas_common.AD_PASSWORD,
                                               services_for_unix="NONE")
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('add auth provider ad %s failed !!!' % ad_server_name)
        raise Exception('add auth provider ad %s failed !!!' % ad_server_name)
    ad_server_id = exe_info['result']

    log.info("1.2>查询认证服务")
    exe_info = nas_common.get_auth_providers_ad(ad_server_id)
    ad_server = exe_info['result']['auth_providers'][0]
    if ad_server['name'] == ad_server_name and ad_server['domain_name'] == nas_common.AD_DOMAIN_NAME and \
            ad_server['id'] == ad_server_id and ad_server['name'] == ad_server_name:
        log.info('params of auth provider are correct !')
    else:
        log.error('params of auth provider are wrong !!!')
        raise Exception('params of auth provider are wrong !!!')

    log.info("1.3>检查认证服务可连接性")
    nas_common.check_auth_provider(ad_server_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('check auth provider failed !!!')
        raise Exception('check auth provider failed !!!')

    log.info("1.4>创建访问分区")
    obj_node = common.Node()
    nodes_id_list = obj_node.get_nodes_id()
    nodes_id_str = ','.join(str(p) for p in nodes_id_list)
    access_zone_name = 'az_' + FILE_NAME
    exe_info = nas_common.create_access_zone(nodes_id_str, access_zone_name, ad_server_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('create access zone %s failed !!!' % access_zone_name)
        raise Exception('create access zone %s failed !!!' % access_zone_name)
    access_zone_id = exe_info['result']

    log.info("1.5>启动nas服务")
    exe_info = nas_common.enable_nas(access_zone_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('enable nas failed !!!')
        raise Exception('enable nas failed !!!')

    log.info("2> 创建共享目录并授权某个用户的导出权限")
    """检查NAS_PATH是否存在"""
    cmd = 'ls %s' % NAS_PATH
    rc, stdout = common.run_command(SYSTEM_IP_1, cmd)
    if rc != 0:
        cmd = 'mkdir -p %s' % NAS_TRUE_PATH
        common.run_command(SYSTEM_IP_1, cmd)
    else:
        cmd = 'mkdir %s' % NAS_TRUE_PATH
        common.run_command(SYSTEM_IP_1, cmd)

    log.info("2.1> 在存储卷里创建目录")
    log.info('waiting for 15s')
    time.sleep(15)

    export_name = 'nfs_exp_test'
    create_export_path = VOLUME_NAME + ':/' + os.path.join(NAS_PATH_BASENAME, FILE_NAME)
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

    log.info("2.2> 授权某个用户的导出权限")
    permission_level = 'rw'
    auth_name_ip = nas_common.CLIENT_IP_1
    exe_info = nas_common.add_nfs_export_auth_clients(export_id, auth_name_ip, permission_level)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('add nfs export auth clients failed !!!')
    log.info('waiting for 15s')
    time.sleep(15)

    log.info("2.3> nfs客户端挂载")
    mount_path = SYSTEM_IP_1 + ':/' + NAS_TRUE_PATH
    cmd = 'mkdir -p %s' % local_path
    common.run_command(auth_name_ip, cmd)
    rc = umount(auth_name_ip, local_path)   # 检查本地路径是否已经mount
    if rc != 0:
        log.info('local path did not mount')

    log.info("2.4> 客户端mount共享路径")
    begin_time = time.time()
    rc = 1
    while rc != 0:
        cmd = "mount -t nfs %s %s" % (mount_path, local_path)
        rc, stdout = common.run_command(auth_name_ip, cmd)
        last_time = time.time()
        during_time = last_time - begin_time
        if int(during_time) >= 15:
            common.except_exit('mount time exceeded 15s !!!')
        time.sleep(5)

    exe_info = nas_common.get_nfs_export_auth_clients(export_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('mount nfs failed !!!')

    log.info("3> 对父目录配置inode硬阈值120；子目录inode软阈值100")
    dir1_1 =  os.path.join(NAS_TRUE_PATH, 'nesting1_1')
    cmd = 'mkdir -p %s' % dir1_1
    common.run_command(auth_name_ip, cmd)
    cmd = 'chmod 777 %s' % dir1_1
    common.run_command(auth_name_ip, cmd)
    quota_path = create_export_path
    create_quota_dir1_1 = os.path.join(create_export_path, 'nesting1_1')

    log.info("3.1> 创建父目录配额，inode硬阈值120，等待配额生效")
    rc, check_result = quota_common.create_one_quota(path=quota_path,
                                                     filenr_quota_cal_type='QUOTA_LIMIT',
                                                     filenr_hard_threshold=120)
    common.judge_rc(rc, 0, "create quota failed", exit_flag=False)
    rc, quota_id = quota_common.get_one_quota_id(path=quota_path,
                                                 u_or_g_type=quota_common.TYPE_CATALOG)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("3.2> 创建子目录配额，inode软阈值100（60s），等待配额生效")
    rc, check_result = quota_common.create_one_quota(path=create_quota_dir1_1,
                                                     filenr_quota_cal_type='QUOTA_LIMIT',
                                                     filenr_soft_threshold=100,
                                                     filenr_grace_time=60)
    common.judge_rc(rc, 0, "create quota failed", exit_flag=False)
    rc, quota_id = quota_common.get_one_quota_id(path=quota_path,
                                                 u_or_g_type=quota_common.TYPE_CATALOG)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info("4> 通过nfs客户端先在目录中写入110个文件;延时60s，无法写入")
    for i in range(110):
        file_name = 'test' + str(i)
        local_path_dir1_1 = os.path.join(local_path, 'nesting1_1')
        file_path = os.path.join(local_path_dir1_1, file_name)
        cmd = 'echo 111 > %s' % file_path
        common.run_command(auth_name_ip, cmd)
    dir_inode = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, dir1_1)
    if dir_inode != 110:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir1_1, dir_inode)

    log.info("延时70s")
    time.sleep(70)
    log.info("子目录nesting1_1下预计无法继续写入；预计共110")
    file_name = 'test' + "_overtime"
    local_path_dir1_1 = os.path.join(local_path, 'nesting1_1')
    file_path = os.path.join(local_path_dir1_1, file_name)
    cmd = 'echo 111 > %s' % file_path
    common.run_command(auth_name_ip, cmd)

    dir_inode = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, dir1_1)
    if dir_inode != 110:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir1_1, dir_inode)

    log.info("5> 删除子目录下文件")
    rm_dir = os.path.join(local_path_dir1_1, '*')
    rc, stdout = common.rm_exe(nas_common.CLIENT_IP_1, rm_dir)
    common.judge_rc(rc, 0, 'rm failed!!')

    log.info("6> 子目录nesting1_1下写120数据，预计119个（父配额120）")
    for i in range(120):
        file_name = 'test' + str(i)
        local_path_dir1_1 = os.path.join(local_path, 'nesting1_1')
        file_path = os.path.join(local_path_dir1_1, file_name)
        cmd = 'echo 111 > %s' % file_path
        common.run_command(auth_name_ip, cmd)

    dir_inode = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, dir1_1)
    if dir_inode != 119:
        rc_lst[sys._getframe().f_lineno] = 'dir: %s total_inode: %s ' % (dir1_1, dir_inode)

    """判断rc_lst"""
    if rc_lst != {}:
        log.info(rc_lst)
        for i in rc_lst:
            log.info("check point in line : %s is about :%s " % (i, rc_lst[i]))
        log.info('If there are many lines, you may only need to look at the first line.')
        common.except_exit("some check point failed")


def clean_mount_path(auth_name_ip,local_path):
    """
    author:liyi
    date: 2018-11-15
    description:清理nfs客户端文件以及挂载目录
    :param auth_name_ip: nfs客户端所在节点
    :param local_path: nfs客户端共享路径
    :return:
    """
    rm_local_path  = os.path.join(local_path,'*')
    common.rm_exe(auth_name_ip, rm_local_path)

    rc = umount(auth_name_ip, local_path)
    common.judge_rc(rc, 0, 'umount %s failed !!!' % local_path, exit_flag=False)

    deleted_file_path = os.path.dirname(local_path)
    deleted_file_path = os.path.join(deleted_file_path, '*')
    common.rm_exe(auth_name_ip, deleted_file_path)

    return


def nas_main():
    prepare_clean.quota_test_prepare(FILE_NAME)
    try:
        case()
    finally:
        clean_mount_path(quota_common.CLIENT_IP_1,local_path)
        prepare_clean.quota_test_prepare(FILE_NAME)
        log.info('%s succeed!' % FILE_NAME)
    return


if __name__ == '__main__':
    nas_main()