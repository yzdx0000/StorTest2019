#-*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-x-x 共享名称边界值
#######################################################

import os

import utils_path
import log
import get_config
import common
import prepare_clean
import nas_common

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
        1、创建一个共享名以字母开头的含数字和下划线的长度超过31位的smb共享；
        2、创建一个共享名以字母开头的，除了含数字和下划线还含有其他字符的smb共享（用户名长度在1-31之间）；
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

    # export_name边界值检查
    illegal_name = "nas_16_0_4_28_export_name00000000000000000000000000000000000000000000000000000081"
    legal_name = "nas_16_0_4_28_export_name0000000000000000000000000000000000000000000000000000080"

    dir_name = "nas_16-0-4-28_dir"
    create_file_path = nas_common.ROOT_DIR + dir_name
    get_file_list_path = nas_common.ROOT_DIR

    check_result1 = nas_common.create_file(path=create_file_path, posix_permission="rwxrwxrwx")
    if check_result1["detail_err_msg"] != "":
        log.info("%s" % check_result1["detail_err_msg"])

    check_result2 = nas_common.get_file_list(path=get_file_list_path, display_details="true")
    if check_result2["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    files = check_result2["result"]["detail_files"]
    for file in files:
        if file["path"] == create_file_path:
            if file["name"] != "%s" % dir_name \
                    or file["path"] != "%s" % create_file_path \
                    or file["posix_permission"] != "rwxrwxrwx" \
                    or file["type"] != "DIR":
                log.error(("%s Failed") % FILE_NAME)
                raise Exception(("%s Failed") % FILE_NAME)

    check_result3 = nas_common.create_smb_export(access_zone_id=access_zone_id,
                                                 export_name=illegal_name,
                                                 export_path=create_file_path)
    if check_result3["detail_err_msg"].find("exceed the max length:80") == -1:
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)

    check_result4 = nas_common.create_smb_export(access_zone_id=access_zone_id,
                                                 export_name=legal_name,
                                                 export_path=create_file_path)
    if check_result4["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    result = check_result4["result"]

    check_result5 = nas_common.get_smb_exports(ids=result)
    if check_result5["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    exports = check_result5["result"]["exports"]
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
            "export_name": legal_name,
            "export_path": create_file_path,
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
