#-*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-x-x 开启NTLMv2
#######################################################

import os

import utils_path
import log
import nas_common
import common
import get_config
import prepare_clean

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
        1、开启enable_send_ntlmv2；
        pscli --command=update_smb_global_config --id=x --enable_send_ntlmv2=true
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

    num = 5
    smb_ids = []

    for count in range(num):
        print "count = %s" % (count + 1)

        create_file_path = nas_common.ROOT_DIR + "nas_16-0-4-59_dir" + "_%s" % (count + 1)
        export_name = "nas_16_0_4_59_smb_export_name" + "_%s" % (count + 1)

        check_result1 = nas_common.create_file(path=create_file_path)
        if check_result1["detail_err_msg"] != "":
            log.info("%s" % check_result1["detail_err_msg"])

        check_result2 = nas_common.create_smb_export(access_zone_id=access_zone_id,
                                                     export_name=export_name,
                                                     export_path=create_file_path)
        if check_result2["detail_err_msg"] != "":
            log.error(("%s Failed") % FILE_NAME)
            raise Exception(("%s Failed") % FILE_NAME)
        result = check_result2["result"]
        smb_ids.append(result)

        check_result3 = nas_common.get_smb_exports(ids=result)
        if check_result3["detail_err_msg"] != "":
            log.error(("%s Failed") % FILE_NAME)
            raise Exception(("%s Failed") % FILE_NAME)
        exports = check_result3["result"]["exports"]
        for export in exports:
            if cmp(export, {
                "access_zone_id": int("%s" % access_zone_id),
                "allow_create_ntfs_acl": True,
                "clients": [],
                "enable_alternative_datasource": False,
                "enable_dos_attributes": True,
                "enable_guest": False,
                "enable_ntfs_acl": True,
                "enable_oplocks": True,
                "enable_os2style_ex_attrs": False,
                "export_name": export_name,
                "export_path": create_file_path,
                "id": int("%s" % result),
                "key": int("%s" % result),
                "version": 0
            }) != 0:
                log.error(("%s Failed") % FILE_NAME)
                raise Exception(("%s Failed") % FILE_NAME)

    check_result1 = nas_common.get_smb_global_configs()
    if check_result1["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    config = check_result1["result"]["configs"][0]  # 只update第一个
    allow_create_ntfs_acl = config["allow_create_ntfs_acl"]
    enable_alternative_datasource = config["enable_alternative_datasource"]
    enable_change_notify = config["enable_change_notify"]
    enable_dos_attributes = config["enable_dos_attributes"]
    enable_guest = config["enable_guest"]
    enable_ntfs_acl = config["enable_ntfs_acl"]
    enable_oplocks = config["enable_oplocks"]
    enable_os2style_ex_attrs = config["enable_os2style_ex_attrs"]
    enable_send_ntlmv2 = config["enable_send_ntlmv2"]
    id = config["id"]
    if allow_create_ntfs_acl != True \
            or enable_alternative_datasource != False \
            or enable_change_notify != True \
            or enable_dos_attributes != True \
            or enable_guest != False \
            or enable_ntfs_acl != True \
            or enable_oplocks != True \
            or enable_os2style_ex_attrs != False \
            or enable_send_ntlmv2 != False:
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)

    check_result2 = nas_common.update_smb_global_config(smb_global_config_id=id,
                                                        enable_send_ntlmv2="true")
    if check_result2["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)

    check_result3 = nas_common.get_smb_global_configs()
    if check_result3["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    config = check_result3["result"]["configs"][0]  # 只update第一个
    allow_create_ntfs_acl = config["allow_create_ntfs_acl"]
    enable_alternative_datasource = config["enable_alternative_datasource"]
    enable_change_notify = config["enable_change_notify"]
    enable_dos_attributes = config["enable_dos_attributes"]
    enable_guest = config["enable_guest"]
    enable_ntfs_acl = config["enable_ntfs_acl"]
    enable_oplocks = config["enable_oplocks"]
    enable_os2style_ex_attrs = config["enable_os2style_ex_attrs"]
    enable_send_ntlmv2 = config["enable_send_ntlmv2"]
    if allow_create_ntfs_acl != True \
            or enable_alternative_datasource != False \
            or enable_change_notify != True \
            or enable_dos_attributes != True \
            or enable_guest != False \
            or enable_ntfs_acl != True \
            or enable_oplocks != True \
            or enable_os2style_ex_attrs != False \
            or enable_send_ntlmv2 != True:
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    else:
        log.info(("%s Succeed") % FILE_NAME)

    # 把环境恢复，enable_send_ntlmv2="false"
    log.info("\n")
    log.info(">>> cleaning_environment start <<<")
    check_result4 = nas_common.update_smb_global_config(smb_global_config_id=id,
                                                        enable_send_ntlmv2="false")
    if check_result4["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    log.info(">>> cleaning_environment end <<<")

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
    log.info("%s succeed!" % FILE_NAME)
    return

class Nas_Class_16_0_x_x():
    def nas_method_16_0_x_x(self):
        nas_main()

if __name__ == '__main__':
    nas_main()
