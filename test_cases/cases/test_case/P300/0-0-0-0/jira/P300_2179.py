# -*-coding:utf-8 -*
import os
import time

import utils_path
import common
import snap_common
import log
import shell
import get_config
import prepare_clean
import random
import nas_common
import json
"""
author 梁晓昱
date 2018-07-31
@summary：
     缺陷自动化：配置将AD认证服务,查看某个属于两个组的特定用户信息。（查看副组信息）
@steps:
    1、添加ad认证服务器
    2、确定测试用户（同时在两个组）和组信息期望值
    3、获取AD用户以验证
    4、比较是否有两个组信息

@changelog：
    最后修改时间：
    修改内容：
    todo_
           在nas完全交付后，完整访问区的添加、删除操作；
"""
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
MAX_WAIT_TIME = 600


def get_add_one_ad(case_ip, ad_info_add):
    """
    author：LiangXiaoyu
    function:检查集群中的AD数量，若存在，取第一个；若不存在，添加一个nas_common里的251
    :param case_ip集群内ip； ad_info_add:添加的ad认证服务器信息列表，如ad_info_add = ["ad_test", nas_common.AD_DOMAIN_NAME, nas_common.AD_DNS_ADDRESSES,
                   nas_common.AD_USER_NAME, nas_common.AD_PASSWORD,
                   "NONE", "2000-3000"]
    :return: AD认证服务器配置命令的字典类型标准输出
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
        if 0 == int(add_ad_final):
            msd_get_ad = nas_common.get_auth_providers_ad(None)
            log.info("add ad sever success")
        else:
            log.error("add ad failed:%s\nunix range is right?%s,ntp:%s)" %
                      (msd_get_ad, ad_info_add, msg_set_ntp))
            raise Exception("case failed!!!")

    '''不止一个ad,只取第一个'''
    sys_ad_id_org = msd_get_ad["result"]["auth_providers"][0]["id"]
    log.info("ad_system:%d OK" % sys_ad_id_org)
    return msd_get_ad


def random_choose_node(ob_node):
    """
        name  :      delete_disk_random_beta
        parameter:   common库中的node类
        author:      LiangXiaoyu
        date  :      2018.07.13
        Description: 返回一个随机得到的node_id和IP
        @changelog：
    """
    nodeid_list = ob_node.get_nodes_id()
    '''随机选一个节点'''
    fault_node_id = random.choice(nodeid_list)
    return fault_node_id


def case():
    log.info("case begin")
    '''随机节点'''
    reult_test = 0
    ob_node = common.Node()
    case_node_id = 1
    case_ip = ob_node.get_node_ip_by_id(case_node_id)
    ad_info_add = ["ad_test", nas_common.AD_DOMAIN_NAME, nas_common.AD_DNS_ADDRESSES,
                   nas_common.AD_USER_NAME, nas_common.AD_PASSWORD,
                   "NONE", "2000-3000"]

    """添加ad认证服务器，获取用户，比较adusertest"""
    ad_group_user_test = ["adusertest", "Domain Users", "Domain Admins"]
    msg_get_ad = get_add_one_ad(case_ip, ad_info_add)

    if "" != msg_get_ad["detail_err_msg"]:
        log.error("update AD online cmd failed")
        raise Exception("case failed!!!")
    id_ad = msg_get_ad["result"]["auth_providers"][0]["id"]
    rc, msg_get_users_ad = nas_common.get_auth_users(id_ad)
    msg_get_nephew = msg_get_users_ad["result"]["auth_users"]
    log.info("test user:%s" % ad_group_user_test[0])
    for name in msg_get_nephew:
        enter_cmp = cmp(ad_group_user_test[0], str(name["name"]))
        if 0 == enter_cmp:
            log.info("Found：%s" % name)
            null_cmp = cmp("[]", str(name["secondary_groups"]))
            if 0 == null_cmp:
                log.error("secondary_groups of %s is null:%s" % (name["name"], name["secondary_groups"]))
                raise Exception("case failed!!!")
            else:
                sec_grp_cmp = cmp(ad_group_user_test[2], str(name["secondary_groups"]))
                if 0 != sec_grp_cmp:
                    log.error("%s second group is wrong:%s" % (name["name"], name["secondary_groups"]))
                    raise Exception("case failed!!!")
                first_grp_cmp = cmp(ad_group_user_test[1], str(name["primary_group_name"]))
                if 0 != first_grp_cmp:
                    log.error("%s first group is wrong:%s" % (name["name"], name["primary_group_name"]))
                    raise Exception("case failed!!!")

    log.info("case succeed!")
    return


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    case()
    prepare_clean.nas_test_clean()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
