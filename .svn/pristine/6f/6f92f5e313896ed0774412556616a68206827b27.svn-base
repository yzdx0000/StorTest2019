# -*-coding:utf-8 -*
import os
import time

import utils_path
import common
import snap_common
import log
import get_config
import prepare_clean
import nas_common
import shell
import random
import json
"""
Author:liangxy
date 2018-08-28
@summary：
     缺陷自动化——导出smb目录的访问权限不是777（从而导致挂载失败）
@steps:
    1、添加ad认证、设置ntp
    2、创建访问区FILE_NAME
    3、新建导出目录
    4、使用pscli命令导出smb协议目录，检查目录访问权限
    5、清理环境，返回结果
@changelog：
    最后修改时间：
    修改内容：
"""

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]


def get_add_one_ad(case_ip, ad_info_add):
    """
    author：LiangXiaoyu
    function:检查集群中的AD数量，若存在，取第一个；若不存在，添加一个nas_common里的251
    :param case_ip(str)集群内ip；
    :param ad_info_add:(list)添加的ad认证服务器信息列表，如ad_info_add = ["ad_test", nas_common.AD_DOMAIN_NAME, nas_common.AD_DNS_ADDRESSES,
                   nas_common.AD_USER_NAME, nas_common.AD_PASSWORD,
                   "NONE", "2000-3000"]
    :return: 配置好的AD认证服务器id
    @changelog：
    """
    '''get,获取ad和az状态'''
    msd_get_ad = nas_common.get_auth_providers_ad(None)
    ad_total_sys_org = msd_get_ad["result"]["total"]
    if 0 != int(ad_total_sys_org):
        ad_faile_log_info = ("nas clean function failed, left ad server:%s" % str(msd_get_ad["result"]))
        common.except_exit(ad_faile_log_info)
    msg_add_ad = nas_common.add_auth_provider_ad(ad_info_add[0], ad_info_add[1], ad_info_add[2], ad_info_add[3], ad_info_add[4], ad_info_add[5])
    msg_set_ntp = nas_common.set_ntp("true", ad_info_add[2], 5)
    add_ad_result = msg_add_ad["err_no"]
    set_ntp_rst = msg_set_ntp["err_no"]
    add_ad_final = set_ntp_rst + add_ad_result
    if 0 == int(add_ad_final):
        msd_get_ad = nas_common.get_auth_providers_ad(None)
        log.info("add ad sever success")
    else:
        log.error("add ad failed:%s\nunix range is right?%s,ntp:%s)" % (msd_get_ad, ad_info_add, msg_set_ntp))
        raise Exception("case failed!!!")
    sys_ad_id_org = msg_add_ad["result"]
    log.info("ad_system OK")
    return sys_ad_id_org


def case():
    log.info("case begin")
    ob_node = common.Node()
    case_node_id_lst = ob_node.get_nodes_id()
    case_id = random.choice(case_node_id_lst)
    case_ip = ob_node.get_node_ip_by_id(case_id)

    log.info(">1 添加ad认证服务器、ntp、check ad认证服务器")
    ad_info_add = ["ad_test", nas_common.AD_DOMAIN_NAME, nas_common.AD_DNS_ADDRESSES,
                   nas_common.AD_USER_NAME, nas_common.AD_PASSWORD,
                   "NONE", "2000-3000"]
    provider_id = get_add_one_ad(case_ip, ad_info_add)

    log.info(">2 创建访问分区")
    msg_add_az = nas_common.create_access_zone(node_ids=case_id, name=FILE_NAME + "az", auth_provider_id=provider_id)
    common.judge_rc(msg_add_az["err_no"], 0, "create az" + msg_add_az["detail_err_msg"])
    id_az = msg_add_az["result"]
    log.info("az id created： %d" % id_az)
    log.info(">3 创建目录")
    case_volume = nas_common.VOLUME_NAME
    path_create = case_volume + ":/" + FILE_NAME
    msg_get_file = nas_common.get_file_list(case_volume + ":/")
    common.judge_rc(msg_get_file["err_no"], 0, "get file list" + msg_get_file["detail_err_msg"])
    for files in msg_get_file["result"]["files"]:
        if FILE_NAME == files["name"]:
            file_dele_p = nas_common.delete_file(path_create)
            common.judge_rc(file_dele_p["err_no"], 0, "first dele:" + FILE_NAME + file_dele_p["detail_err_msg"])
    msg_add_file = nas_common.create_file(path_create)
    common.judge_rc(msg_add_file["err_no"], 0, "create file" + msg_add_file["detail_err_msg"])
    log.info(">4 创建smb导出")
    descrp_smb = "check-777"
    msg_crt_export_smb = nas_common.create_smb_export(access_zone_id=id_az,
                                                      export_name=FILE_NAME+"_smb", export_path=path_create,
                                                      description=descrp_smb)
    common.judge_rc(msg_crt_export_smb["err_no"], 0, "smb export" + msg_crt_export_smb["detail_err_msg"])

    id_smb = msg_crt_export_smb["result"]

    """检查修改结果"""
    log.info(">6 验证结果，为rwxrwxrwx，测试成功；否则，失败")
    msg_get_file_detail = nas_common.get_file_list(path=case_volume + ":/", display_details="true")
    common.judge_rc(msg_get_file_detail["err_no"], 0, "get faile detail" + msg_get_file_detail["detail_err_msg"])
    get_mode = "init_liangxy"

    for files in msg_get_file_detail["result"]["detail_files"]:
        if FILE_NAME == files["name"]:
            get_mode = files["posix_permission"]
    if get_mode == "init_liangxy":
        err_info = "get file detail by name failed"
        common.except_exit(err_info, 2)
    expect_mode = "rwxrwxrwx"

    if expect_mode != get_mode:
        err_len = "mode :%s, expect mode:%s" % (str(get_mode), expect_mode)
        common.except_exit(err_len, 3)

    log.info("case succeed!")
    return


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    case()
    prepare_clean.nas_test_clean()
    log.info("%s succeed!" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
