#-*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-x-x 显示SMB用户用户组信息正确性测试
#######################################################

import os

import utils_path
import log
import nas_common
import common
import prepare_clean
import get_config

# 当前脚本名称
VOLUME_NAME = get_config.get_one_volume_name()
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0].replace('-', '_')                 # 本脚本名字
NAS_PATH = get_config.get_one_nas_test_path()                            # /mnt/volume/nas_test_dir
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)             # /mnt/volume/nas_test_dir/nas_16_6_0_16
BASE_NAS_PATH = os.path.dirname(NAS_PATH)                                # /mnt/volume
NAS_PATH_BASENAME = os.path.basename(NAS_PATH)                           # nas_test_dir
SYSTEM_IP_0 = get_config.get_parastor_ip(0)
SYSTEM_IP_1 = get_config.get_parastor_ip(1)
SYSTEM_IP_2 = get_config.get_parastor_ip(2)

#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def executing_case():
    """
        1、连接AD认证服务器；
        pscli --command=add_auth_provider_ad --name=adtest --domain_name=adtest.com --dns_addresses=10.2.41.251 --username=administrator --password=Ly111111 --services_for_unix=NONE --unix_id_range=5000-6000
        2、添加AD用户/用户组到NAS客户端的smb用户/用户组；
        pscli --command=add_smb_export_auth_clients --name=u1 --export_id=x --type=USER --run_as_root=true
        pscli --command=add_smb_export_auth_clients --name=g1 --export_id=x --type=GROUP --run_as_root=true
        3、查询NAS客户端的smb用户/用户组信息；
        pscli --command=get_smb_export_auth_clients
    :return:
    """
    log.info("（2）executing_case")

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

    # add_auth_provider_ad
    auth_provider_ad_name = "nas_16_0_4_69_ad_auth_name"
    unix_id_range_list = [10001,11000]
    # create_file
    create_file_path = nas_common.ROOT_DIR + "nas_16-0-4-69_dir"
    # create_smb_export
    export_name = "nas_16_0_4_69_smb_export_name"
    # add_smb_export_auth_clients
    smb_export_auth_clients_name_1 = "nas_16-0-4-69_user_1"
    smb_export_auth_clients_name_2 = "nas_16-0-4-69_group"

    """
    check_result1 = nas_common.add_auth_provider_ad(name=auth_provider_ad_name,
                                                    domain_name=nas_common.AD_DOMAIN_NAME,
                                                    dns_addresses=nas_common.AD_DNS_ADDRESSES,
                                                    username=nas_common.AD_USER_NAME,
                                                    password=nas_common.AD_PASSWORD,
                                                    services_for_unix="NONE",
                                                    unix_id_range="%s-%s" % (unix_id_range_list[0],
                                                                             unix_id_range_list[1]))
    
                                                                             
    if check_result1["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    """

    check_result2 = nas_common.create_file(path=create_file_path)
    if check_result2["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        #raise Exception(("%s Failed") % FILE_NAME)

    check_result3 = nas_common.create_smb_export(access_zone_id=access_zone_id,
                                                 export_name=export_name,
                                                 export_path=create_file_path)
    if check_result3["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    result1 = check_result3["result"]

    check_result4 = nas_common.add_smb_export_auth_clients(export_id=result1,
                                                           name=smb_export_auth_clients_name_1,
                                                           user_type="USER",
                                                           run_as_root="true")
    if check_result4["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    result2 = check_result4["result"][0]

    check_result5 = nas_common.add_smb_export_auth_clients(export_id=result1,
                                                           name=smb_export_auth_clients_name_2,
                                                           user_type="GROUP",
                                                           run_as_root="true")
    if check_result5["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    result3 = check_result5["result"][0]

    check_result6 = nas_common.get_smb_export_auth_clients(export_ids=result1)
    smb_export_auth_clients = check_result6["result"]["smb_export_auth_clients"]
    if check_result6["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)

    for smb_export_auth_client in smb_export_auth_clients:
        if smb_export_auth_client["type"] == "GROUP":
            if smb_export_auth_client != {
                "export_id": int(result1),
                "id": int(result3),
                "key": int(result3),
                "name": "%s" % smb_export_auth_clients_name_2,
                "permission_level": "full_control",
                "run_as_root": True,
                "type": "GROUP",
                "version": 0
            }:
                log.error(("%s Failed") % FILE_NAME)
                raise Exception(("%s Failed") % FILE_NAME)
        elif smb_export_auth_client["type"] == "USER":
            if smb_export_auth_client != {
                "export_id": int(result1),
                "id": int(result2),
                "key": int(result2),
                "name": "%s" % smb_export_auth_clients_name_1,
                "permission_level": "full_control",
                "run_as_root": True,
                "type": "USER",
                "version": 0
            }:
                log.error(("%s Failed") % FILE_NAME)
                raise Exception(("%s Failed") % FILE_NAME)

    log.info(("%s Succeed") % FILE_NAME)

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
    file_name = os.path.basename(__file__)
    file_name = os.path.splitext(file_name)[0]
    log_file_path = log.get_log_path(file_name)
    stream = log.init(log_file_path, True)

    prepare_clean.nas_test_prepare(FILE_NAME)
    preparing_environment()
    executing_case()
    if nas_common.DEBUG != "on":
        prepare_clean.nas_test_clean()

    return

class Nas_Class_16_0_x_x():
    def nas_method_16_0_x_x(self):
        nas_main()

if __name__ == '__main__':
    nas_main()
