# -*- coding:utf-8 -*-

######################################################
# Author: jiangxiaoguang
# Date: 2018-08-07
# @summary：
#   add_smb_export_auth_clients的name参数为user name，type参数为USER，run_as_root参数为true，用户存在，使用export_name登录
# @steps:
#   1、create_smb_export 导出目录；
#   pscli --command=create_smb_export --access_zone_id=x --export_name=export_name --export_path=volume:/export/dir
#   2、add_smb_export_auth_clients指定name为存在的user name，type为USER，run_as_root为true；
#   pscli --command=add_smb_export_auth_clients --export_id=x --name=exist_user_name --type=USER --run_as_root=true
#   3、update_smb_global_config配置home_dir；
#   pscli --command=update_smb_global_config --id=x --home_dir=volume:/homedir
#   4、mstsc到某windows设备，使用export_name进行挂载，在弹出的登录框中输入存在的用户名和密码；
#   5、通过nas客户端写入数据，观察写入数据的属性是否正确；
#   6、尝试删除使用中的用户；
#   7、尝试删除导出的目录；
#   8、尝试删除导出的策略；
# @changelog：
#   None
######################################################

import os
import time

import utils_path
import log
import common
import nas_common

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]     # 脚本名称


def executing_case():
    """测试执行
    :return:无
    """
    log.info('（2）executing_case')

    # for add_auth_provider_ad
    auth_provider_name = 'nas_16_0_7_22_ad_auth_name'
    domain_name = nas_common.AD_DOMAIN_NAME
    dns_addresses = nas_common.AD_DNS_ADDRESSES
    username = nas_common.AD_USER_NAME
    ad_password = nas_common.AD_PASSWORD
    services_for_unix = 'NONE'
    unix_id_range = [3000, 3099]
    # for create_access_zone
    node_ids = '1,2,3'
    access_zone_name = 'nas_16_0_7_22_access_zone_name'
    # for create_file
    dir_name = 'nas_16-0-7-22_dir'
    create_file_path = nas_common.ROOT_DIR + dir_name
    create_home_dir_file_path = nas_common.ROOT_DIR + 'nas_16_0_7_22_homedir'
    # for create_smb_export，不配authorization_ip即允许所有ip
    export_name = 'nas_16_0_7_22_smb_export_name'
    export_path = create_file_path
    # for add_smb_export_auth_clients
    auth_clients_name = nas_common.AD_USER_1
    auth_clients_type = 'USER'
    run_as_root = 'true'
    # for windows端smb挂载
    ip_and_port = nas_common.DEFAULT_SMB_CLIENT_IP_AND_PORT
    disk_symbol = 'x:'
    mount_path = '\\\\10.2.40.49\\' + export_name
    user_passwd = nas_common.AD_USER_PW
    user = 'adtest\\' + auth_clients_name
    # for 写数据
    filename = 'file_16-0-7-22'

    """增加鉴权服务器"""
    msg = nas_common.add_auth_provider_ad(name=auth_provider_name,
                                          domain_name=domain_name,
                                          dns_addresses=dns_addresses,
                                          username=username,
                                          password=ad_password,
                                          services_for_unix=services_for_unix,
                                          unix_id_range='%s-%s' % (unix_id_range[0],
                                                                   unix_id_range[1]))
    if msg['detail_err_msg'] != '':
        raise Exception('%s Failed' % FILE_NAME)
    auth_provider_id = msg['result']

    """创建访问区"""
    msg = nas_common.create_access_zone(node_ids=node_ids,
                                        name=access_zone_name,
                                        auth_provider_id=auth_provider_id)
    if msg['detail_err_msg'] != '':
        raise Exception('%s Failed' % FILE_NAME)
    access_zone_id = msg['result']

    """使能访问区"""
    msg = nas_common.enable_nas(access_zone_id=access_zone_id)
    if msg['detail_err_msg'] != '':
        raise Exception('%s Failed' % FILE_NAME)

    """创建目录"""
    msg = nas_common.create_file(path=create_file_path)
    if msg['detail_err_msg'] != '':
        log.info('%s' % msg['detail_err_msg'])
    msg = nas_common.create_file(path=create_home_dir_file_path)
    if msg['detail_err_msg'] != '':
        log.info('%s' % msg['detail_err_msg'])

    """导出目录"""
    msg = nas_common.create_smb_export(access_zone_id=access_zone_id,
                                       export_name=export_name,
                                       export_path=export_path)
    if msg['detail_err_msg'] != '':
        raise Exception('%s Failed' % FILE_NAME)
    export_id = msg['result']

    """添加认证用户"""
    msg = nas_common.add_smb_export_auth_clients(export_id=export_id,
                                                 name=auth_clients_name,
                                                 user_type=auth_clients_type,
                                                 run_as_root=run_as_root)
    if msg['detail_err_msg'] != '':
        raise Exception('%s Failed' % FILE_NAME)

    """update_smb_global_config"""
    msg = nas_common.update_smb_global_config(smb_global_config_id=access_zone_id,
                                              home_dir=create_home_dir_file_path)
    if msg['detail_err_msg'] != '':
        raise Exception('%s Failed' % FILE_NAME)

    """windows端smb挂载(需要客户端提前运行run_remote.py脚本)，预期挂载成功"""
    time.sleep(10)
    retcode, output = nas_common.smb_mount(disk_symbol, mount_path, user_passwd, user)
    log.info(output)
    common.judge_rc(retcode, 0, 'smb_mount failed')

    """挂载结果查询"""
    retcode, output = nas_common.get_smb_mount_info(ip_and_port)
    common.judge_rc(retcode, 0, 'get_smb_mount_info')
    output_lines = output.split('\n')
    flag = False
    for line in output_lines:
        if mount_path in line:
            flag = True
            log.info('smb_mount succeed')

    if flag is False:
        raise Exception('%s Failed' % FILE_NAME)

    """写数据"""
    retcode = nas_common.create_file_by_smb_client(disk_symbol, filename)
    if retcode != 0:
        raise Exception('create_file_by_smb_client Failed.')

    # todo：校验数据，需先解决windows端进入盘符时，run_command_shot_time函数报错问题

    return


def preparing_environment():
    """测试条件准备
    :return:无
    """
    log.info('（1）preparing_environment')

    return


def nas_main():
    """脚本入口函数
    :return:无
    """

    # 初始化日志
    nas_common.nas_log_init(FILE_NAME)

    nas_common.cleaning_environment()
    preparing_environment()
    executing_case()
    if nas_common.DEBUG != "on":
        nas_common.cleaning_environment()

    return


if __name__ == '__main__':
    common.case_main(nas_main)
