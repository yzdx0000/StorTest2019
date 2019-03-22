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
date 2018-08-15
@summary：
     缺陷自动化——ldap命令设置bind_dn参数后check失败(预期成功)
@steps:
    1、选择测试节点
    2、有bind_dn参数添加ldap认证
    3、无bind_dn参数添加ldap认证
    4、清理环境，汇总返回信息返回结果
@changelog：
    最后修改时间：
    修改内容：
"""

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]


def dele_add_one_wrong_dn_ldap(case_ip, name, dn, ip_ldap, bind_dn=None, bind_ps=None):
    """
    author：LiangXiaoyu
    function:检查集群中的LDAP数量，若存在，取第一个；若不存在，添加一个nas_common
    :param case_ip集群内ip；
    :param name:添加的ad认证服务器名
    :param dn:添加的ad认证服务器dn名
    :param ip_ldap:添加的ad认证服务器ip地址
    :return: rc_add_ldap:命令执行的返回值；msg_add_ldap：字典类型，参数和错误信息
    @changelog：
    """
    '''get,获取ldap和az状态'''
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
        msg_add_ldap = nas_common.add_auth_provider_ldap(name=name, base_dn=dn, ip_addresses=ip_ldap, bind_dn=bind_dn,
                                                         bind_password=bind_ps,domain_password=nas_common.LDAP_DOMAIN_PASSWORD)
    common.judge_rc(msg_add_ldap['err_no'], 0, msg_add_ldap['detail_err_msg'])
    return msg_add_ldap


def case():
    log.info("case begin")
    """节点列表"""
    ob_node = common.Node()
    case_node_id_lst = ob_node.get_nodes_id()
    log.info(">1 选择测试节点")
    case_id = random.choice(case_node_id_lst)
    case_ip = ob_node.get_node_ip_by_id(case_id)

    err_msg_add_ldap_unit = []
    id_ldap_lst = []
    log.info(">2 添加ad认证服务器")
    msg_crt_ldap_nu = dele_add_one_wrong_dn_ldap(case_ip, FILE_NAME + "ldap",  nas_common.LDAP_BASE_DN,
                                                 nas_common.LDAP_IP_ADDRESSES)
    msg_check_ldap = nas_common.check_auth_provider(msg_crt_ldap_nu["result"])
    dict_add_ldap = {(msg_crt_ldap_nu["result"], nas_common.LDAP_BASE_DN): [msg_check_ldap["err_no"], msg_check_ldap["detail_err_msg"]]}
    err_msg_add_ldap_unit.append(dict_add_ldap)
    id_ldap_lst.append(msg_crt_ldap_nu["result"])
    msg_crt_ldap_nu = dele_add_one_wrong_dn_ldap(case_ip, FILE_NAME + "ldap", nas_common.LDAP_BASE_DN,
                                                 nas_common.LDAP_IP_ADDRESSES, nas_common.LDAP_BIND_DN,
                                                 nas_common.LDAP_BIND_PASSWORD)
    print str(msg_crt_ldap_nu["result"])
    msg_check_ldap = nas_common.check_auth_provider(str(msg_crt_ldap_nu["result"]))
    dict_add_ldap = {(msg_crt_ldap_nu["result"], nas_common.LDAP_BIND_PASSWORD): [msg_check_ldap["err_no"], msg_check_ldap["detail_err_msg"]]}
    err_msg_add_ldap_unit.append(dict_add_ldap)
    id_ldap_lst.append(msg_crt_ldap_nu["result"])
    """删除本脚本创建的资源"""
    log.info(">3 可能创建的ldap认证 %s，清理环境" % id_ldap_lst)

    """检查修改结果"""
    log.info(">4 验证结果，check ldap 预期可以通过")
    for err_dict in err_msg_add_ldap_unit:
        log.info("test rst:%s" % err_dict)

    for err_dict in err_msg_add_ldap_unit:
        common.judge_rc(err_dict.values()[0][0], 0,
                        err_dict.keys()[0].__str__() + "check wrong: " + err_dict.values()[0][1].__str__())

    log.info("case succeed!")
    return


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    case()
    prepare_clean.nas_test_clean()
    log.info("%s succeed!" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
