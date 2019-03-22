#-*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-4-25 正常创建smb共享（全测试默认值）
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
        1、创建3节点访问分区az1，启动nas服务；
        2、创建共享路径volume:/nas/smb_dir
        pscli --command=create_file --path=volume:/nas/smb_dir
        3、在az1上创建smb共享，输入正确的名称和共享路径；
        pscli --command=create_smb_export --access_zone_id=x --export_name=smb_exp_test --export_path=volume:/nas/smb_dir
        4、查看smb共享路径配置成功，信息是否与配置信息匹配；
        pscli --command=get_smb_exports
    :return:
    """
    log.info("（2）executing_case")

    '''1> 创建3节点访问分区az1，启动nas服务'''
    """同步NTP"""
    nas_common.set_ntp(is_enabled="true", ntp_servers=nas_common.AD_DNS_ADDRESSES)
    # cmd = 'pscli --command=set_ntp --is_enabled=true --ntp_servers=%s' % nas_common.AD_DNS_ADDRESSES
    # rc, stdout = common.run_command(SYSTEM_IP_0, cmd)
    # common.judge_rc(rc, 0, 'set ntp failed !!!')

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

    dir_name1 = "nas_16-0-4-25_dir"
    dir_name2 = "dir"
    dir_name_list = [dir_name1, dir_name2]
    create_file_path1 = nas_common.ROOT_DIR + dir_name1
    create_file_path2 = create_file_path1 + "/" + dir_name2
    create_file_path_list = [create_file_path1, create_file_path2]
    get_file_list_path1 = nas_common.ROOT_DIR
    get_file_list_path2 = create_file_path1
    get_file_list_path_list = [get_file_list_path1, get_file_list_path2]

    for i in range(len(dir_name_list)):
        check_result1 = nas_common.create_file(path=create_file_path_list[i])
        if check_result1["detail_err_msg"] != "":
            log.info("%s" % check_result1["detail_err_msg"])

        check_result2 = nas_common.get_file_list(path=get_file_list_path_list[i])
        if check_result2["detail_err_msg"] != "":
            log.error(("%s Failed") % FILE_NAME)
            raise Exception(("%s Failed") % FILE_NAME)
        files = check_result2["result"]["files"]
        for file in files:
            if file["path"] == create_file_path_list[i]:
                if cmp(file, {
                    "auth_provider_id": 0,
                    "name": "%s" % dir_name_list[i],
                    "path": "%s" % create_file_path_list[i],
                    "type": "DIR"
                }) != 0:
                    log.error(("%s Failed") % FILE_NAME)
                    raise Exception(("%s Failed") % FILE_NAME)

    check_result3 = nas_common.create_smb_export(access_zone_id=access_zone_id,
                                                 export_name="nas_16_0_4_25_smb_export_name",
                                                 export_path=create_file_path2)
    if check_result3["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    result = check_result3["result"]

    check_result4 = nas_common.get_smb_exports(ids=result)
    if check_result4["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    exports = check_result4["result"]["exports"]
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
            "export_name": "nas_16_0_4_25_smb_export_name",
            "export_path": create_file_path2,
            "id": int("%s" % result),
            "key": int("%s" % result),
            "version": 0
        }) != 0:
            log.error(("%s Failed") % FILE_NAME)
            raise Exception(("%s Failed") % FILE_NAME)
        else:
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
    1、创建3节点访问分区az1，启动nas服务；
    2、创建共享路径volume:/nas/smb_dir；
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

class Nas_Class_16_0_4_25():
    def nas_method_16_0_4_25(self):
        nas_main()

if __name__ == '__main__':
    nas_main()