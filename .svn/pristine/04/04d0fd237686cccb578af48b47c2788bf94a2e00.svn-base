#-*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-x-x 描述信息边界值测试
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
        1、创建一个描述信息长度为1的FTP共享；
        2、创建一个描述信息长度为255的FTP共享；
        3、创建一个描述信息长度为256的FTP共享；
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
                                               services_for_unix="NONE", node_ip=SYSTEM_IP_0)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('add auth provider ad %s failed !!!' % ad_server_name)
        raise Exception('add auth provider ad %s failed !!!' % ad_server_name)
    ad_server_id = exe_info['result']

    """get_auth_providers_ad"""
    log.info("\t[ 3.get_auth_provider_ad ]")
    exe_info = nas_common.get_auth_providers_ad(ad_server_id, node_ip=SYSTEM_IP_1)
    ad_server = exe_info['result']['auth_providers'][0]
    if ad_server['name'] == ad_server_name and ad_server['domain_name'] == nas_common.AD_DOMAIN_NAME and \
            ad_server['id'] == ad_server_id and ad_server['name'] == ad_server_name:
        log.info('params of auth provider are correct !')
    else:
        log.error('params of auth provider are wrong !!!')
        raise Exception('params of auth provider are wrong !!!')

    """check_auth_provider"""
    nas_common.check_auth_provider(ad_server_id, node_ip=SYSTEM_IP_0)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('check auth provider failed !!!')
        raise Exception('check auth provider failed !!!')

    """创建访问分区"""
    obj_node = common.Node()
    nodes_id_list = obj_node.get_nodes_id()
    nodes_id_str = ','.join(str(p) for p in nodes_id_list)
    access_zone_name = 'az_' + FILE_NAME
    exe_info = nas_common.create_access_zone(nodes_id_str, access_zone_name, ad_server_id, node_ip=SYSTEM_IP_1)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('create access zone %s failed !!!' % access_zone_name)
        raise Exception('create access zone %s failed !!!' % access_zone_name)
    access_zone_id = exe_info['result']

    """启动nas服务"""
    exe_info = nas_common.enable_nas(access_zone_id, node_ip=SYSTEM_IP_0)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('enable nas failed !!!')
        raise Exception('enable nas failed !!!')

    create_file_path_1 = nas_common.ROOT_DIR + "nas_16-0-4-140_dir_1"
    create_file_path_2 = nas_common.ROOT_DIR + "nas_16-0-4-140_dir_2"
    create_file_path_3 = nas_common.ROOT_DIR + "nas_16-0-4-140_dir_3"
    create_file_path_list = [create_file_path_1, create_file_path_2, create_file_path_3]
    export_name_1 = "nas_16_0_4_140_ftp_export_name_1"
    export_name_2 = "nas_16_0_4_140_ftp_export_name_2"
    export_name_3 = "nas_16_0_4_140_ftp_export_name_3"
    description_1 = "a"
    description_2 = "b" * 255
    description_3 = "c" * 256

    for create_file_path in create_file_path_list:
        check_result1 = nas_common.create_file(path=create_file_path)
        if check_result1["detail_err_msg"] != "":
            log.info("%s" % check_result1["detail_err_msg"])

    result = 1
    check_result1 = nas_common.create_ftp_export(access_zone_id=access_zone_id,
                                                user_name=nas_common.AD_USER_1,
                                                export_path=create_file_path_1,
                                                description=description_1)
    if check_result1["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    result1 = check_result1["result"]

    check_result2 = nas_common.delete_ftp_exports(ids=result1)
    if check_result2["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)

    check_result3 = nas_common.create_ftp_export(access_zone_id=result,
                                                export_name=export_name_2,
                                                export_path=create_file_path_2,
                                                description=description_2)
    if check_result3["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    result2 = check_result3["result"]

    check_result4 = nas_common.delete_ftp_exports(ids=result2)
    if check_result4["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)

    check_result5 = nas_common.create_ftp_export(access_zone_id=result,
                                                export_name=export_name_3,
                                                export_path=create_file_path_3,
                                                description=description_3)
    if check_result5["detail_err_msg"].find("exceed the max length:255") == -1:
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

    nas_common.cleaning_environment()
    preparing_environment()
    executing_case()
    if nas_common.DEBUG != "on":
        nas_common.cleaning_environment()

    return

class Nas_Class_16_0_x_x():
    def nas_method_16_0_x_x(self):
        nas_main()

if __name__ == '__main__':
    nas_main()
