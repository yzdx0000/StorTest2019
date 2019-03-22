#-*-coding:utf-8 -*
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
date 2018-08-09
@summary：
     缺陷自动化——导出smb目录命令的description参数上限不是255
@steps:
    1、添加ad认证、设置ntp
    2、创建访问区FILE_NAME
    3、创建导出目录
    4、使用pscli命令导出smb协议目录，添加长于255的description，检查报错信息
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
    :param case_ip集群内ip； ad_info_add:添加的ad认证服务器信息列表，如ad_info_add = ["ad_test", nas_common.AD_DOMAIN_NAME, nas_common.AD_DNS_ADDRESSES,
                   nas_common.AD_USER_NAME, nas_common.AD_PASSWORD,
                   "NONE", "2000-3000"]
    :return: 配置好的AD认证服务器id
    @changelog：
    """
    '''get,获取ad和az状态'''
    msd_get_ad = nas_common.get_auth_providers_ad(None)
    ad_total_sys_org = msd_get_ad["result"]["total"]

    '''没有ad就添加ad'''
    if 0 == int(ad_total_sys_org):

        msg_add_ad = nas_common.add_auth_provider_ad(ad_info_add[0], ad_info_add[1], ad_info_add[2], ad_info_add[3],
                                                     ad_info_add[4], ad_info_add[5])
        msg_set_ntp = nas_common.set_ntp("true", ad_info_add[2], 5)
        add_ad_result = msg_add_ad["err_no"]
        set_ntp_rst = msg_set_ntp["err_no"]
        add_ad_final = set_ntp_rst + add_ad_result
        add_info = "add ad and set"
        msd_get_ad = nas_common.get_auth_providers_ad(None,)
        common.judge_rc(add_ad_final, 0, add_info)
        log.info("add ad sever success")
    '''不止一个ad,只取第一个'''
    sys_ad_id_org = msd_get_ad["result"]["auth_providers"][0]["id"]
    msg_check_ad = nas_common.check_auth_provider(sys_ad_id_org)
    err_che_ad = "check ad:%d" % int(sys_ad_id_org)
    common.judge_rc(msg_check_ad["err_no"], 0, err_che_ad)
    log.info("ad_system OK:%d" % int(sys_ad_id_org))
    return sys_ad_id_org


def case():
    log.info("case begin")
    """节点列表"""
    ob_node = common.Node()
    case_node_id_lst = ob_node.get_nodes_id()

    """handle->节点id、客户端ip；添加后要删除的访问区"""
    case_id = random.choice(case_node_id_lst)
    case_ip = ob_node.get_node_ip_by_id(case_id)
    imp_info_lst = []
    """添加ad认证服务器，启动ntp，check ad"""
    log.info(">1 添加ad认证服务器、ntp、check ad认证服务器")
    ad_info_add = ["ad_test", nas_common.AD_DOMAIN_NAME, nas_common.AD_DNS_ADDRESSES,
                   nas_common.AD_USER_NAME, nas_common.AD_PASSWORD,
                   "NONE", "2000-3000"]
    provider_id = get_add_one_ad(case_ip, ad_info_add)
    imp_info_lst.append(provider_id)
    '''
    在选定节点添加上访问分区
    '''
    log.info(">2 创建访问分区")
    msg_add_az = nas_common.create_access_zone(node_ids=case_id, name=FILE_NAME + "az", auth_provider_id=provider_id)
    common.judge_rc(msg_add_az["err_no"], 0, "create az" + msg_add_az["detail_err_msg"])

    id_az = msg_add_az["result"]
    imp_info_lst.append(id_az)
    log.info("az id created： %d" % id_az)
    """创建目录"""
    log.info(">3 创建目录")

    get_volume_lst = get_config.get_volume_names()
    case_volume = random.choice(get_volume_lst)
    path_create = case_volume + ":/" + FILE_NAME
    msg_get_file = nas_common.get_file_list(case_volume + ":/")
    common.judge_rc(msg_get_file["err_no"], 0, "get file list" + msg_get_file["detail_err_msg"])
    for files in msg_get_file["result"]["files"]:
        if FILE_NAME == files["name"]:
            file_dele_p = nas_common.delete_file(path_create)
            common.judge_rc(file_dele_p["err_no"], 0, "first dele:" + FILE_NAME + file_dele_p["detail_err_msg"])
    msg_add_file = nas_common.create_file(path_create)
    common.judge_rc(msg_add_file["err_no"], 0, "create file" + msg_add_file["detail_err_msg"])
    """创建smb导出"""
    log.info(">4 创建smb导出")
    descrp_smb = "a" * 256
    msg_crt_export_smb = nas_common.create_smb_export(access_zone_id=id_az,
                                                      export_name=FILE_NAME+"smb", export_path=path_create,
                                                      description=descrp_smb)
    id_smb = msg_crt_export_smb["result"]
    imp_info_lst.append(id_smb)
    """删除本脚本创建的资源"""
    log.info(">5 删除访问区 %d，清理环境" % id_az)
    az_dele = nas_common.delete_access_zone(id_az)

    file_dele = nas_common.delete_file(path_create)
    """检查修改结果"""
    log.info(">6 验证结果，若创建成功或者字符长度限制为255，测试成功；否则，失败")
    common.judge_rc_unequal(msg_crt_export_smb["err_no"], 0, "wrong name" + msg_crt_export_smb["detail_err_msg"])
    string_lonth_limit = "255"
    flag_get_num = string_lonth_limit in msg_crt_export_smb["detail_err_msg"]
    if False is flag_get_num:
        err_len = "lenth limit of description :%s" % msg_crt_export_smb["detail_err_msg"]
        common.judge_rc(-2, 0, err_len)
    common.judge_rc(file_dele["err_no"], 0, "delete file" + file_dele["detail_err_msg"])
    common.judge_rc(az_dele["err_no"], 0, "delete az" + az_dele["detail_err_msg"])
    log.info("case succeed!\n%s (lenth:%d) is illegal" % (descrp_smb, len(descrp_smb)))
    return


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    case()
    prepare_clean.nas_test_clean()
    log.info("%s succeed!" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
