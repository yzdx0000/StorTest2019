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
date 2018-08-31
@summary：
     缺陷自动化——get_auth_user未对参数名的合法性进行检查
@steps:
    1、生成参数列表
    2、添加ad认证服务器
    3、使用get_auth_user命令对查询错误参数
    4、检查报错信息，清理环境，返回结果
@changelog：
    最后修改时间：
    修改内容：
"""

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]


def get_add_one_ad(case_ip, ad_info_add):
    """
    author：LiangXiaoyu
    function:检查集群中的AD数量，若存在，报错退出，说明未调用nas的prepare函数，或函数失败；添加nas_common里的251
    :param case_ip(str)集群内ip；
    :param ad_info_add:添加的ad认证服务器信息列表，如ad_info_add = ["ad_test", nas_common.AD_DOMAIN_NAME,
                nas_common.AD_DNS_ADDRESSES,nas_common.AD_USER_NAME, nas_common.AD_PASSWORD,"NONE"]
    :return: 配置好的AD认证服务器id
    @changelog：
    """
    msd_get_ad = nas_common.get_auth_providers_ad(None)
    ad_total_sys_org = msd_get_ad["result"]["total"]
    ad_faile_log_info = ("nas clean function failed, left ad server:%s" % str(msd_get_ad["result"]))
    common.judge_rc(int(ad_total_sys_org), 0, ad_faile_log_info)
    msg_add_ad = nas_common.add_auth_provider_ad(ad_info_add[0], ad_info_add[1], ad_info_add[2], ad_info_add[3],
                                                 ad_info_add[4], ad_info_add[5])
    msg_set_ntp = nas_common.set_ntp("true", ad_info_add[2], 5)
    add_ad_result = msg_add_ad["err_no"]
    set_ntp_rst = msg_set_ntp["err_no"]
    add_ad_final = set_ntp_rst + add_ad_result
    common.judge_rc(add_ad_final, 0, "add ad and set ntp info:")
    sys_ad_id_org = msg_add_ad["result"]
    log.info("ad_system OK")
    return sys_ad_id_org


def case():
    log.info("case begin")
    ob_node = common.Node()
    case_node_id_lst = ob_node.get_nodes_id()
    case_id = random.choice(case_node_id_lst)
    case_ip = ob_node.get_node_ip_by_id(case_id)

    log.info(">1 指定参数")
    get_auth_para_lst = ["group_id", "start", "limit"]
    err_dict = {}
    err_dict_lst = []
    log.info(">2 添加ad认证")
    ad_info_add = ["ad_test", nas_common.AD_DOMAIN_NAME, nas_common.AD_DNS_ADDRESSES,
                   nas_common.AD_USER_NAME, nas_common.AD_PASSWORD,
                   "NONE"]
    ad_id = get_add_one_ad(case_ip, ad_info_add)
    log.info("add AD server: %d sccessful" % ad_id)
    log.info(">3 使用错误参数列表执行命令")
    for err in get_auth_para_lst:
        err_msg = "%saaa" % err
        # err_para = " --auth_provider_id=%d %s=1111" % (ad_id, err_msg)
        # cmd_err = cmd_get + err_para
        rc_err, std_err = common.run_pscli(command='get_auth_users', print_flag=True, fault_node_ip=None,
                                           auth_provider_id=ad_id, err_msg='11111')
        # (rc_err, std_err) = common.pscli_run_command(cmd_err)
        msg_err_locate = std_err.find("ArgumentValidateException")
        msg_err = std_err[msg_err_locate:]
        err_dict = {(err_msg,): [rc_err, msg_err]}
        err_dict_lst.append(err_dict)

    log.info(">4 结果返回，清理环境")
    faild_flag = 0
    for rst in err_dict_lst:
        if rst.values()[0][0] == 0:
            log.info("error result print:%s" % rst)
            faild_flag = 1
    common.judge_rc(faild_flag, 0, "check flag!!!!")
    log.info("case succeed!")
    return


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed!" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
