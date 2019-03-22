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
date 2018-07-26
@summary：
     缺陷自动化：将AD认证服务器配置到访问分区后，在线update访问分区的认证服务器，获取AD用户
@steps:
    1、没有访问区就添加
    2、先disable_nas；确定AD认证有没有，没有就添加
    3、enable_nas,在线更新访问区的认证服务器administrator信息
    4、获取AD用户以验证

@changelog：todo_
           disable nas 后最少需要6分钟（经验值）才可完全生效
"""
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
MAX_WAIT_TIME = 600


def nas_state_change(case_ip, flag=False):
    """
    author：LiangXiaoyu
    function:改变访问区中的nas，根据参数开启或关闭nas
    :param case_ip:访问区所在节点ip；
    :param flag:开启（True）或关闭（False）nas
    :return:
    @changelog：
    """
    class_action = "disable"
    if flag is True:
        class_action = "enable"
    log.info("change nas status,flag:%s---%s" % (flag, class_action))
    msg_get_az = nas_common.get_access_zones(None, case_ip)

    if flag is True:
        msg_nas = nas_common.enable_nas(msg_get_az["result"]["access_zones"][0]["id"])
    else:
        msg_nas = nas_common.disable_nas(msg_get_az["result"]["access_zones"][0]["id"])
    action_nas_rst = msg_nas["detail_err_msg"]
    if "" != action_nas_rst:
        log.error("%s nas action failed and exit:\n%s" % (class_action, action_nas_rst))
        raise Exception("case failed!!!")
    else:
        time_count = 0
        while True:
            msg_get_az = nas_common.get_access_zones(None, case_ip)
            nas_status_active = msg_get_az["result"]["access_zones"][0]["nas_service_enabled"]
            cmp_nas_status_active = cmp(flag, nas_status_active)

            if 0 != int(cmp_nas_status_active):

                if MAX_WAIT_TIME < time_count:
                    log.error("wait for nas %s active too long:%d s" % (class_action, time_count))
                    raise Exception("case failed!!!")
                log.info("%s  nas not active yet,waiting:" % class_action)
                time.sleep(20)
                time_count += 20
                log.info("%d s" % time_count)
            else:
                log.info("%s nas done" % class_action)
                break
    return


def get_add_one_ad(case_ip, ad_info_add):
    """
    author：LiangXiaoyu
    function:检查集群中的AD数量，若存在，取第一个；若不存在，添加一个nas_common里的251
    :param case_ip(str)集群内ip；
    :param ad_info_add:(str)添加的ad认证服务器信息列表，如ad_info_add = ["ad_test", nas_common.AD_DOMAIN_NAME, nas_common.AD_DNS_ADDRESSES,
                   nas_common.AD_USER_NAME, nas_common.AD_PASSWORD,
                   "NONE", "2000-3000"]
    :return: 配置好的AD认证服务器id
    @changelog：
    """
    '''get,获取ad和az状态'''
    msd_get_ad = nas_common.get_auth_providers_ad(None, case_ip)
    ad_total_sys_org = msd_get_ad["result"]["total"]
    if 0 != int(ad_total_sys_org):
        ad_faile_log_info = ("nas clean function failed, left ad server:%s" % str(msd_get_ad["result"]))
        common.except_exit(ad_faile_log_info)
    msg_add_ad = nas_common.add_auth_provider_ad(ad_info_add[0], ad_info_add[1], ad_info_add[2], ad_info_add[3], ad_info_add[4], ad_info_add[5])
    msg_set_ntp = nas_common.set_ntp("true", ad_info_add[2], 5, nas_common.RANDOM_NODE_IP)
    add_ad_result = msg_add_ad["err_no"]
    set_ntp_rst = msg_set_ntp["err_no"]
    add_ad_final = set_ntp_rst + add_ad_result
    if 0 == int(add_ad_final):
        msd_get_ad = nas_common.get_auth_providers_ad(None, case_ip)
        log.info("add ad sever success")
    else:
        log.error("add ad failed:%s\nunix range is right?%s,ntp:%s)" % (msd_get_ad, ad_info_add, msg_set_ntp))
        raise Exception("case failed!!!")

    '''不止一个ad,只取第一个'''
    sys_ad_id_org = msg_add_ad["result"]
    log.info("ad_system OK")
    return sys_ad_id_org


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
    ob_node = common.Node()
    case_node_id = random_choose_node(ob_node)
    case_ip = ob_node.get_node_ip_by_id(case_node_id)

    ad_info_add = ["ad_test", nas_common.AD_DOMAIN_NAME, nas_common.AD_DNS_ADDRESSES,
                   nas_common.AD_USER_NAME, nas_common.AD_PASSWORD,
                   "NONE", "2000-3000"]
    log.info("1> 创建访问区")
    msg_get_az = nas_common.get_access_zones(None, case_ip)
    az_total_num_org = msg_get_az["result"]["total"]
    if 0 != az_total_num_org:
        for az in msg_get_az["result"]["access_zones"]:
            msg_clean_az = nas_common.delete_access_zone(az["id"])
            common.judge_rc(msg_clean_az["err_no"], 0, "clean az by hand:" + msg_clean_az["detail_err_msg"])
    msg_crt_az = nas_common.create_access_zone(case_node_id, FILE_NAME + "_az")
    common.judge_rc(msg_crt_az["err_no"], 0, "create access zone info:" + msg_crt_az["detail_err_msg"])

    '''
    确定nas状态,disable
    '''
    nas_state_change(case_ip, False)
    '''
    配置含错误信息ad_info_add[3]到ad认证服务器
    '''
    ad_info_add[3] = "admini"
    update_provider_id = get_add_one_ad(case_ip, ad_info_add)
    msg_get_az = nas_common.get_access_zones(None, case_ip)
    log.info("new provider id will be:%d" % update_provider_id)
    '''
    配置AD到访问分区
    '''
    id_az = msg_crt_az["result"]
    msg_up_provider = nas_common.update_access_zone(access_zone_id=id_az, auth_provider_id=update_provider_id)
    if "" != msg_up_provider["detail_err_msg"]:
        log.error("update_access_zone failed ")
        raise Exception("case failed!!!")
    log.info("update access zone done with wrong info:%s!" % ad_info_add[3])
    '''
    确定nas状态,enable
    '''
    nas_state_change(case_ip, True)
    '''
    核心操作，update认证服务器，get_user
    '''
    ad_info_add[3] = nas_common.AD_USER_NAME
    msg_get_ad = nas_common.get_auth_providers_ad(case_node_id, case_ip)
    id_ad = update_provider_id
    # msg_get_ad["result"]["auth_providers"][0]["id"]
    msg_online_up_ad = nas_common.update_auth_provider_ad(provider_id=id_ad, username=ad_info_add[3])

    if 0 != msg_online_up_ad["err_no"]:
        log.error("update AD online cmd failed")
        raise Exception("case failed!!!")
    rc, msg_get_users_ad = nas_common.get_auth_users(id_ad)
    if 0 != msg_get_users_ad["err_no"]:
        log.error("get_auth_users 1st failed(expect failed),type:AD\nadd info:%s" % ad_info_add)
        log.error("nas bug in reworking,wait for 300s to update again")
        time.sleep(300)
        msg_online_up_ad = nas_common.update_auth_provider_ad(provider_id=id_ad, username=ad_info_add[3])
        if "" != msg_online_up_ad["detail_err_msg"]:
            log.error("update AD online 2nd failed")
            raise Exception("case failed!!!")
        rc, msg_get_users_ad = nas_common.get_auth_users(id_ad)
        if "" != msg_get_users_ad["detail_err_msg"]:
            log.error("get_auth_users 2nd failed,type:AD\nadd info:%s" % ad_info_add)
            raise Exception("case failed!!!")
    if 0 == msg_get_users_ad["result"]["total"]:
        log.error("get_auth_users filed:AD\nadd info:%s" % ad_info_add)
        raise Exception("case failed!!!")
    log.info("case succeed!")
    return


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    case()
    prepare_clean.nas_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
