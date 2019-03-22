# -*- coding:utf-8 -*-

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-x-x 创建smb共享规格测试
#######################################################

import os

import utils_path
import log
import nas_common
import time
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


def executing_case():
    """
    1、使用脚本创建达到规格上限的smb共享；[1、smb共享的规格是65536个；]
    :return:
    """
    log.info("（2）executing_case")

    '''1> 创建3节点访问分区az1，启动nas服务'''
    """同步NTP"""
    exe_info = nas_common.set_ntp(is_enabled='true',
                                  ntp_servers=nas_common.AD_DNS_ADDRESSES,
                                  sync_period=5)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('set ntp failed !!!')

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

    # """启动nas服务"""
    # exe_info = nas_common.enable_nas(access_zone_id)
    # if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
    #     log.error('enable nas failed !!!')
    #     raise Exception('enable nas failed !!!')

    num = 65537

    start_time = time.time()
    for i in range(num):
        count = i + 1
        print "count = %s" % count

        dir_name = "nas_16-0-4-46_dir" + "_%s" % count
        create_file_path = nas_common.ROOT_DIR + dir_name
        export_name = "nas_16_0_4_46_smb_export_name" + "_%s" % count

        check_result1 = nas_common.create_file(path=create_file_path)
        if check_result1["detail_err_msg"] != "":
            log.info("%s" % check_result1["detail_err_msg"])

        if count < num:
            check_result2 = nas_common.create_smb_export(access_zone_id=access_zone_id,
                                                         export_name=export_name,
                                                         export_path=create_file_path)
            if check_result2["detail_err_msg"] != "":
                log.error(("%s Failed") % FILE_NAME)
                raise Exception(("%s Failed") % FILE_NAME)
            # result = check_result2["result"]

            # check_result3 = nas_common.get_smb_exports(ids=result)
            # if check_result3["detail_err_msg"] != "":
            #     log.error(("%s Failed") % FILE_NAME)
            #     raise Exception(("%s Failed") % FILE_NAME)
            # exports = check_result3["result"]["exports"]
            # for export in exports:
            #     if cmp(export, {
            #             "access_zone_id": int("%s" % access_zone_id),
            #             "allow_create_ntfs_acl": True,
            #             "clients": [],
            #             "enable_alternative_datasource": False,
            #             "enable_dos_attributes": True,
            #             "enable_guest": False,
            #             "enable_ntfs_acl": True,
            #             "enable_oplocks": True,
            #             "enable_os2style_ex_attrs": False,
            #             "export_name": export_name,
            #             "export_path": create_file_path,
            #             "id": int("%s" % result),
            #             "key": int("%s" % result),
            #             "version": 0
            #             }) != 0:
            #         log.error(("%s Failed") % FILE_NAME)
            #         raise Exception(("%s Failed") % FILE_NAME)
        elif count == num:  # 第65537次循环，创建失败
            check_result4 = nas_common.create_smb_export(access_zone_id=access_zone_id,
                                                         export_name=export_name,
                                                         export_path=create_file_path)
            if check_result4["detail_err_msg"].find("has reached the limit:65536") == -1:
                log.error(("%s Failed") % FILE_NAME)
                raise Exception(("%s Failed") % FILE_NAME)

    end_time = time.time()
    run_time = int(end_time - start_time)
    (m, s) = divmod(run_time, 60)
    (h, m) = divmod(m, 60)
    time_str = "%dh:%dm:%ds" % (h, m, s)
    log.info(time_str)

    """启动nas服务"""
    exe_info = nas_common.enable_nas(access_zone_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('enable nas failed !!!')
        raise Exception('enable nas failed !!!')

    return


def nas_main():
    """脚本入口函数
    :return:无
    """
    prepare_clean.nas_test_prepare(FILE_NAME, env_check=False)
    executing_case()
    if nas_common.DEBUG != 'on':
        prepare_clean.nas_test_clean()
    return


if __name__ == '__main__':
    common.case_main(nas_main)
