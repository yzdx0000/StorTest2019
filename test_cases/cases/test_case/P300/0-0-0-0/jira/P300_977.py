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
date 2018-08-14
@summary：
     缺陷自动化——添加ldap命令的base_dn参数未对特殊字符进行检查
@steps:
    1、生成特殊字符列表(首字符不为#和空格，尾字符不为空格，须用""引住)
    2、添加ldap认证
    3、获取、检查、汇总返回信息
    4、清理环境，返回结果
@changelog：
    最后修改时间：
    修改内容：
"""

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]


def dele_add_one_wrong_dn_ldap(case_ip, name, dn, ip_ldap, bind_dn=None):
    """
    author：LiangXiaoyu
    function:检查集群中的LDAP数量，若存在则删除后添加指定的LDAP；若不存在，则直接添加
    :param case_ip(str)集群内ip；
    :param name(str):添加的ad认证服务器名
    :param dn(str):添加的ad认证服务器base dn名
    :param ip_ldap(str):添加的ad认证服务器ip地址
    :param bind_dn(str):添加的ad认证服务器bind dn名
    :return:msg_add_ldap(dict)：字典类型，参数和错误信息
    @changelog：
    """
    '''get,获取ldap'''
    msd_get_ldap = nas_common.get_auth_providers_ldap(None)
    ldap_total_sys_org = msd_get_ldap["result"]["total"]

    '''删除已有的ldap'''
    if 0 != int(ldap_total_sys_org):
        for ldap_i in msd_get_ldap["result"]["auth_providers"]:
            msg_ldap_dele = nas_common.delete_auth_providers(ids=ldap_i["id"])
            common.judge_rc(msg_ldap_dele["err_no"], 0, "dele ldap:" + msg_ldap_dele["detail_err_msg"])
    if bind_dn is None:
        msg_add_ldap = nas_common.add_auth_provider_ldap(name, dn, ip_ldap)
    else:
        msg_add_ldap = nas_common.add_auth_provider_ldap(name=name, base_dn=dn, ip_addresses=ip_ldap, bind_dn=bind_dn)
    return msg_add_ldap


def generate_wrongstr_para_lst(org_para, wrong_sp):
    """
    Author：LiangXiaoyu
    :param org_para(str):正确的参数
    :param wrong_sp(str):非法字符
    :return: wrongstr_para_lst(list):生成的错误参数（字符串组成的）列表,空格和#分别添加到每个值首字符，空格也添加到每个值尾字符
    """
    wrongstr_para_lst = []
    b_split = org_para.split(",")
    for i in range(len(b_split)):
        b_org = b_split[i]
        for wrong_s in wrong_sp:
            # 值首字符
            b_split[i] = b_split[i].replace("=", "=" + wrong_s)
            b_join = ",".join(b_split)
            wrongstr_para_lst.append(b_join)
            # 只替换一个值，故应还原
            b_split[i] = b_org
        # 尾字符
        b_split[i] = b_split[i] + " "
        b_join = ",".join(b_split)
        wrongstr_para_lst.append(b_join)
        # 只替换一个值，故应还原
        b_split[i] = b_org
    return wrongstr_para_lst


def case():
    log.info("case begin")
    """节点列表"""
    ob_node = common.Node()
    case_node_id_lst = ob_node.get_nodes_id()

    """handle->节点id"""
    case_id = random.choice(case_node_id_lst)
    case_ip = ob_node.get_node_ip_by_id(case_id)
    log.info(">1 构建参数测试名")
    wrong_sp = "# "
    replaced_s = "="
    wrong_ldap_name_bs_lst = []
    wrong_ldap_name_bi_lst = []
    err_msg_add_ldap_unit = []
    err_detail_msg_unit = []
    id_ldap_lst = []
    wrong_ldap_name_bs_lst = generate_wrongstr_para_lst(nas_common.LDAP_BASE_DN, wrong_sp)
    wrong_ldap_name_bi_lst = generate_wrongstr_para_lst(nas_common.LDAP_BIND_DN, wrong_sp)
    log.info(">2 添加ad认证服务器")
    for wrong_ldap_name in wrong_ldap_name_bs_lst:
        msg_crt_ldap_nu = dele_add_one_wrong_dn_ldap(case_ip, FILE_NAME + "ldap", "\"" + wrong_ldap_name + "\"",
                                                     nas_common.LDAP_IP_ADDRESSES)
        err_detail_con = "LDAP base dn %s is invalid, format: xxx=yyy, separated by commas (,)." % wrong_ldap_name
        err_detail_cmp = cmp(err_detail_con, str(msg_crt_ldap_nu["detail_err_msg"]))
        dict_detail_err = {(wrong_ldap_name,): [err_detail_cmp, msg_crt_ldap_nu["detail_err_msg"], err_detail_con]}
        err_detail_msg_unit.append(dict_detail_err)
        dict_add_ldap = {(wrong_ldap_name,): msg_crt_ldap_nu["err_no"]}
        err_msg_add_ldap_unit.append(dict_add_ldap)
    for wrong_ldap_bi_name in wrong_ldap_name_bi_lst:
        msg_crt_ldap_nu = dele_add_one_wrong_dn_ldap(case_ip, FILE_NAME + "ldap", nas_common.LDAP_BASE_DN,
                                                     nas_common.LDAP_IP_ADDRESSES, "\"" + wrong_ldap_bi_name + "\"")
        err_detail_con = "LDAP bind dn %s is invalid, format: xxx=yyy, separated by commas (,)." % wrong_ldap_bi_name
        err_detail_cmp = cmp(err_detail_con, str(msg_crt_ldap_nu["detail_err_msg"]))
        dict_detail_err = {(wrong_ldap_bi_name,): [err_detail_cmp, msg_crt_ldap_nu["detail_err_msg"], err_detail_con]}
        err_detail_msg_unit.append(dict_detail_err)
        dict_add_ldap = {(wrong_ldap_bi_name,): msg_crt_ldap_nu["err_no"]}
        err_msg_add_ldap_unit.append(dict_add_ldap)
    """删除本脚本创建的资源"""
    log.info(">3 可能创建的ldap认证 %s，清理环境" % id_ldap_lst)
    """检查修改结果"""
    log.info(">4 验证结果，特殊字符应无法创建")
    # 若base dn和bind dn两个一起错，一定是报base dn的错
    # LDAP base dn dc=#test,dc=#com is invalid, format: xxx=yyy, separated by commas (,).
    # LDAP bind dn cn=#root,dc=#test,dc=#com is invalid, format: xxx=yyy, separated by commas (,).
    for err_dict in err_msg_add_ldap_unit:
        log.info("add rst:%s" % err_dict)
    for detail_dict in err_detail_msg_unit:
        log.info("detail:{}\n".format(detail_dict))
    for err_dict in err_msg_add_ldap_unit:
        common.judge_rc_unequal(err_dict.values()[0], 0, "wrong name: " + err_dict.keys()[0].__str__())
    for detail_dict in err_detail_msg_unit:
        info_rc = "\nwrong info: " + detail_dict.values()[0][1].__str__() + "\nexpect info: " + detail_dict.values()[0][2].__str__()
        common.judge_rc(detail_dict.values()[0][0], 0, info_rc)
    log.info("case succeed!\n%s are illegal" % (wrong_sp, ))
    return


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    case()
    prepare_clean.nas_test_clean()
    log.info("%s succeed!" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
