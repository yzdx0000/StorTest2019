# -*-coding:utf-8 -*
import os
import time
import re

import utils_path
import common
import nas_common
import log
import get_config
import json
import random
import quota_common
import prepare_clean

####################################################################################
#
# Author: liyao
# date 2018-06-07
# @summary：
#    ftp目录inode数配额硬阈值
# @steps:
#    1、创建3节点访问分区az1，启动nas服务
#    2、在az1上创建业务子网，配置正确的az1 ID、svip、掩码、网关，与接口信息
#    3、通过pscli --command=get_subnets命令查看业务子网信息
#    4、添加vip池，输入正确的vip地址、掩码等参数
#    5、客户端进行域名解析，并添加主机路由表，检查vip池的域名是否可以ping通
#    6、创建共享目录并授权某个用户的导出权限
#    7、针对目录配置inode数为100的硬阈值配额
#    8、客户端上传文件
#    9、进入ftp共享目录，查看配额是否生效
#    10、清理环境
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
    '''1> 创建3节点访问分区az1，启动nas服务'''
    """同步NTP"""
    cmd = 'pscli --command=set_ntp --is_enabled=true --ntp_servers=%s' % nas_common.AD_DNS_ADDRESSES
    rc, stdout = common.run_command(SYSTEM_IP_0, cmd)
    common.judge_rc(rc, 0, 'set ntp failed !!!')

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

    '''2> 在az1上创建业务子网，配置正确的az1 ID、svip、掩码、网关，与接口信息'''
    subnet_name = 'subnet_' + FILE_NAME
    ip_family = 'IPv4'
    exe_info = nas_common.create_subnet(access_zone_id=access_zone_id, name=subnet_name, ip_family=ip_family,
                                        svip=nas_common.SUBNET_SVIP, subnet_mask=nas_common.SUBNET_MASK,
                                        subnet_gateway=nas_common.SUBNET_GATEWAY,
                                        network_interfaces=nas_common.SUBNET_NETWORK_INTERFACES)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('create subnet %s failed !!!' % subnet_name)
        raise Exception('create subnet %s failed !!!' % subnet_name)
    subnet_id = exe_info['result']

    '''3> 通过pscli --command=get_subnets命令查看业务子网信息'''
    exe_info = nas_common.get_subnets(subnet_id)
    subnet = exe_info['result']['subnets'][0]
    if subnet['id'] == subnet_id and subnet['name'] == subnet_name and subnet['svip'] == nas_common.SUBNET_SVIP and \
            subnet['subnet_mask'] == int(nas_common.SUBNET_MASK) and subnet[
        'subnet_gateway'] == nas_common.SUBNET_GATEWAY \
            and subnet['network_interfaces'][0] == nas_common.SUBNET_NETWORK_INTERFACES:
        log.info('subnet params are correct !')
    else:
        log.error('subnet params are wrong !!! ')
        raise Exception('subnet params are wrong !!!')

    '''4> 添加vip池，输入正确的vip地址、掩码等参数'''
    allocation_method_list = ['DYNAMIC']
    used_protocol = 'NAS'
    used_method = random.choice(allocation_method_list)
    exe_info = nas_common.add_vip_address_pool(subnet_id, nas_common.VIP_DOMAIN_NAME, nas_common.VIP_ADDRESSES,
                                               used_protocol, used_method)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('add vip address pool failed !!!')
        raise Exception('add vip address pool failed !!!')
    vip_pool_id = exe_info['result']

    '''5> 客户端进行域名解析，并添加主机路由表，检查vip池的域名是否可以ping通'''
    """域名解析"""
    nameserver_conf_ip = nas_common.FTP_1_CLIENT_IP
    add_nameserver_path = '/etc/resolv.conf'
    resolv_file_bak = '/etc/resolv.conf.bak'
    cmd = 'cp %s %s' % (add_nameserver_path, resolv_file_bak)   # 备份域名解析文件
    rc, stdout = common.run_command(nameserver_conf_ip, cmd)
    common.judge_rc(rc, 0, 'resolve file backup failed !!!')

    cmd = 'echo "nameserver %s" > %s' % (nas_common.SUBNET_SVIP, add_nameserver_path)
    rc, stdout = common.run_command(nameserver_conf_ip, cmd)
    common.judge_rc(rc, 0, 'resolve domain name failed !!!')

    """客户端添加主机路由表"""
    vip_ip_parts = re.split('[.-]', nas_common.VIP_ADDRESSES)
    vip_start_part = vip_ip_parts[3]
    vip_end_part = vip_ip_parts[4]
    diff_num = int(vip_end_part) - int(vip_start_part)  # vip地址之间的差距，用于后续路由表的循环添加
    typical_vip_ip = []
    typical_eth = nas_common.SUBNET_NETWORK_INTERFACES.split(',')[0]
    for i in range(0, diff_num + 1):
        tmp_vip_ip = vip_ip_parts[0] + '.' + vip_ip_parts[1] + '.' + vip_ip_parts[2] + '.' + str(
            int(vip_ip_parts[3]) + i)
        typical_vip_ip.append(tmp_vip_ip)
        cmd = 'route add -host %s dev %s' % (tmp_vip_ip, typical_eth)
        common.run_command(nameserver_conf_ip, cmd)

    log.info('waiting for 10s')
    time.sleep(10)

    '''6> 创建共享目录并授权某个用户的导出权限'''
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
    create_export_path = VOLUME_NAME + ':/' + os.path.join(NAS_PATH_BASENAME, FILE_NAME)
    export_sys_ip = SYSTEM_IP_2
    exe_info = nas_common.create_ftp_export(access_zone_id, nas_common.AD_USER_1, create_export_path,
                                            enable_upload="true")
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('create ftp export failed !!!')
    ftp_export_id = exe_info['result']

    """get_auth_user查看导出是否成功"""
    rc, exe_info = nas_common.get_auth_users(ad_server_id)
    auth_users = exe_info['result']['auth_users']
    name_list = []
    for user in auth_users:
        name_list.append(user['name'])
    if nas_common.AD_USER_1 not in name_list:
        common.except_exit('get auth user information is wrong !!!')

    '''7> 针对目录配置inode数为100的硬阈值配额'''
    quota_path = create_export_path
    quota_file_num = 100
    rc, check_result = quota_common.create_one_quota(path=quota_path,
                                                     filenr_quota_cal_type='QUOTA_LIMIT',
                                                     filenr_hard_threshold=quota_file_num)
    common.judge_rc(rc, 0, "create quota failed", exit_flag=False)

    rc, quota_id = quota_common.get_one_quota_id(path=quota_path,
                                                 u_or_g_type=quota_common.TYPE_CATALOG)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    """本地创建150个文件"""
    local_path = os.path.join('/home/local', FILE_NAME)
    cmd = 'mkdir -p %s' % local_path
    rc, stdout = common.run_command(nas_common.FTP_1_CLIENT_IP, cmd)
    common.judge_rc(rc, 0, 'mkdir %s failed !!!' % local_path)
    for i in range(150):
        file_name = 'test' + str(i)
        file_path = os.path.join(local_path, file_name)
        cmd = 'echo 111 > %s' % file_path
        common.run_command(nas_common.FTP_1_CLIENT_IP, cmd)
    total_file = 'test*'

    '''8> 客户端上传文件'''
    ftp_client_ip = nas_common.FTP_1_CLIENT_IP
    execution_file = os.path.join(local_path, 'ftp.sh')
    cmd = "echo "" > %s &&" \
          "echo '#!/bin/bash' >> %s &&" \
          "echo 'ftp -nv << EOF' >> %s &&" \
          "echo 'prompt' >> %s &&" \
          "echo 'open %s' >> %s &&" \
          "echo 'user %s 111111' >> %s &&" \
          "echo 'mput %s /' >> %s &&" \
          "echo 'close' >> %s &&" \
          "echo 'bye' >> %s &&" \
          "echo 'EOF' >> %s &&" \
          "echo 'sleep 2' >> %s " % (execution_file, execution_file, execution_file, execution_file,
                                     nas_common.VIP_DOMAIN_NAME, execution_file, nas_common.AD_USER_1, execution_file,
                                     total_file, execution_file, execution_file, execution_file, execution_file,
                                     execution_file)
    rc, stdout = common.run_command(ftp_client_ip, cmd)
    common.judge_rc(rc, 0, 'edit file failed !!!')

    cmd = "cd %s ;sh %s" % (local_path, execution_file)
    rc, stdout = common.run_command(ftp_client_ip, cmd)
    common.judge_rc(rc, 0, '%s execution failed !!!' % execution_file)

    '''9> 进入ftp共享目录，查看配额是否生效'''
    """获取共享目录下的文件数"""
    cmd = 'cd %s; ls -lR |grep "^-" |wc -l' % NAS_TRUE_PATH
    rc, file_num = common.run_command(export_sys_ip, cmd)
    common.judge_rc(rc, 0, 'get file number failed !!!')

    cmd = 'cd %s; ls -lR |grep "^d" |wc -l' % NAS_TRUE_PATH
    rc, dir_num = common.run_command(export_sys_ip, cmd)
    common.judge_rc(rc, 0, 'get directory failed !!!')

    total_num = int(file_num) + int(dir_num)
    if total_num > quota_file_num:
        common.except_exit('quota did not work well !!!')

    """删除配额及文件"""
    rc, stdout = quota_common.delete_one_quota(quota_id)
    common.judge_rc(rc, 0, 'delete quota failed !!!')

    deleted_file_path = os.path.dirname(local_path)
    deleted_file_path = os.path.join(deleted_file_path, '*')
    common.rm_exe(nas_common.FTP_1_CLIENT_IP, deleted_file_path)

    '''10> 清理环境'''
    """将域名解析文件恢复原状"""
    cmd = 'mv %s %s' % (resolv_file_bak, add_nameserver_path)
    rc, stdout = common.run_command(nameserver_conf_ip, cmd)
    common.judge_rc(rc, 0, 'resolv file recovery failed !!!')

    """从客户端删除已经添加的路由表"""
    for i in range(0, diff_num + 1):
        cmd = 'route delete -host %s dev %s' % (typical_vip_ip[i], typical_eth)
        common.run_command(nameserver_conf_ip, cmd)

    """disable nas 服务"""
    exe_info = nas_common.disable_nas(access_zone_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('disable nas failed !!!')
        raise Exception('disable nas failed !!!')

    """删除vip_pool"""
    exe_info = nas_common.delete_vip_address_pool(vip_pool_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('delete vip address pool failed !!!')

    """删除业务子网"""
    exe_info = nas_common.delete_subnet(subnet_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('delete subnet failed !!!')

    """删除ftp导出"""
    exe_info = nas_common.delete_ftp_exports(ftp_export_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('delete ftp exports failed !!!')

    """删除访问分区"""
    exe_info = nas_common.delete_access_zone(access_zone_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('delete access zone failed !!!')

    """删除AD认证服务器"""
    exe_info = nas_common.delete_auth_providers(ad_server_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('delete ad provider failed !!!')

    delete_sys_path = os.path.join(NAS_PATH, '*')
    common.rm_exe(export_sys_ip, delete_sys_path)
    return


def nas_main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    case()
    prepare_clean.nas_test_clean()
    log.info('%s succeed!' % FILE_NAME)
    return


if __name__ == '__main__':
    nas_main()