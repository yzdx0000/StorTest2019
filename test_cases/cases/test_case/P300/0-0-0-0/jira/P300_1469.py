# -*-coding:utf-8 -*
import os
import time
import sys

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
Author:liangxy
date 2018-08-29
@summary：
     缺陷自动化——将AD认证服务器配置到访问分区后，su登录ad用户失败
@steps:
    1、添加ad认证服务器
    2、配置ad认证服务器到新建的访问区中
    3、enable_nas,选择ad用户执行su命令
    4、清理环境，返回结果

@changelog：todo_
           disable nas 后最少需要6分钟（经验值）才可完全生效
"""
reload(sys)
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
MAX_WAIT_TIME = 600


def nas_state_change(case_ip, flag=False):
    """
    author：LiangXiaoyu
    function:改变访问区中的nas，根据参数开启或关闭nas
    :param  case_ip(str):访问区所在节点ip；
    :param  flag(bool):开启（True）或关闭（False）nas
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
    function:检查集群中的AD数量，若存在，报错退出，说明未调用nas的prepare函数，或函数失败；添加nas_common里的251
    :param case_ip(str)集群内ip；
    :param ad_info_add:添加的ad认证服务器信息列表，如ad_info_add = ["ad_test", nas_common.AD_DOMAIN_NAME, nas_common.AD_DNS_ADDRESSES,
                   nas_common.AD_USER_NAME, nas_common.AD_PASSWORD,
                   "NONE", "2000-3000"]
    :return: 配置好的AD认证服务器id
    @changelog：
    """
    msd_get_ad = nas_common.get_auth_providers_ad(None, case_ip)
    ad_total_sys_org = msd_get_ad["result"]["total"]
    ad_faile_log_info = ("nas clean function failed, left ad server:%s" % str(msd_get_ad["result"]))
    common.judge_rc(int(ad_total_sys_org), 0, ad_faile_log_info)
    msg_add_ad = nas_common.add_auth_provider_ad(ad_info_add[0], ad_info_add[1], ad_info_add[2], ad_info_add[3], ad_info_add[4], ad_info_add[5])
    msg_set_ntp = nas_common.set_ntp("true", ad_info_add[2], 5, nas_common.RANDOM_NODE_IP)
    add_ad_result = msg_add_ad["err_no"]
    set_ntp_rst = msg_set_ntp["err_no"]
    add_ad_final = set_ntp_rst + add_ad_result
    common.judge_rc(add_ad_final, 0, "add ad and set ntp info:")
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
    ob_node = common.Node()
    case_node_id = random_choose_node(ob_node)
    case_ip = ob_node.get_node_ip_by_id(case_node_id)

    ad_info_add = ["ad_test", nas_common.AD_DOMAIN_NAME, nas_common.AD_DNS_ADDRESSES,
                   nas_common.AD_USER_NAME, nas_common.AD_PASSWORD,
                   "NONE", "2000-3000"]
    log.info("1> 添加ad认证")
    ad_id = get_add_one_ad(case_ip, ad_info_add)
    log.info("2> 创建访问区")
    msg_get_az = nas_common.get_access_zones(None, case_ip)
    az_total_num_org = msg_get_az["result"]["total"]
    if 0 != az_total_num_org:
        for az in msg_get_az["result"]["access_zones"]:
            msg_clean_az = nas_common.delete_access_zone(az["id"])
            common.judge_rc(msg_clean_az["err_no"], 0, "clean az by hand:" + msg_clean_az["detail_err_msg"])
    msg_crt_az = nas_common.create_access_zone(node_ids=case_node_id, name=FILE_NAME + "_az", auth_provider_id=ad_id)
    az_id = msg_crt_az["result"]
    common.judge_rc(msg_crt_az["err_no"], 0, "create access zone info:" + msg_crt_az["detail_err_msg"])

    log.info("3> 选择ad用户执行su命令")
    nas_state_change(case_ip, True)
    rc, msg_get_user = nas_common.get_auth_users(ad_id)
    common.judge_rc(msg_get_user["err_no"], 0, "get user info:" + msg_get_user["detail_err_msg"])
    user_lst = []
    for user in msg_get_user["result"]["auth_users"]:
        check_ch = user["name"].decode('utf-8')[0]
        if (u'\u4e00' > check_ch) or (check_ch > u'\u9fff'):
            user_lst.append(user["name"])
            log.info("%s not Chinese" % user["name"])

    test_user = random.choice(user_lst)
    cmd_su = "su %s" % str(test_user)
    (rc_su, std_su) = common.run_command(case_ip, cmd_su)
    common.judge_rc(rc_su, 0, "result stdout:" + std_su)
    log.info("case succeed!")
    return


def main():

    prepare_clean.nas_test_prepare(FILE_NAME)
    case()
    prepare_clean.nas_test_clean()
    log.info('%s succeed!\n*********************该缺陷目前被否决*********************' % FILE_NAME)


if __name__ == '__main__':
    # common.case_main(main)
    print("*********************该缺陷目前被否决，暂行保留脚本*********************")