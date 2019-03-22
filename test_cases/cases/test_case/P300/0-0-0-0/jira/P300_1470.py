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
date 2018-08-22
@summary：
     缺陷自动化——两种方式查看ad用户的副组失败
@steps:
    1、添加ad服务器
    2、创建访问分区
    3、检查nas启动状态下的ad特定用户的状态
    4、检查结果，清理环境
@changelog：
    最后修改时间：
    修改内容：
"""
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
MAX_WAIT_TIME = 1800
# nas30分钟——chengqiang


def nas_state_change(case_ip, flag=False):
    """
    author：LiangXiaoyu
    function:改变访问区中的nas，根据参数开启或关闭nas
    :param case_ip(str):访问区所在节点ip；
    :param flag(bool):开启（True）或关闭（False）nas
    :return:
    @changelog：
    """
    class_action = "disable"
    if flag is True:
        class_action = "enable"
    log.info("change nas status,flag:%s---%s" % (flag, class_action))
    msg_get_az = nas_common.get_access_zones(None)
    time_start = time.time()
    if flag is True:
        msg_nas = nas_common.enable_nas(msg_get_az["result"]["access_zones"][0]["id"])
    else:
        msg_nas = nas_common.disable_nas(msg_get_az["result"]["access_zones"][0]["id"])
    time_end = time.time()
    if time_end - time_start > MAX_WAIT_TIME:
        raise Exception("wait nas command:%d s" % (time_end - time_start))
    log.info("wait nas command:%d s" % (time_end - time_start))
    action_nas_rst = msg_nas["detail_err_msg"]
    judge_info = "%s nas action :%s" % (class_action, action_nas_rst)
    common.judge_rc(msg_nas["err_no"], 0, judge_info)
    time_count = 0
    while True:

        msg_get_az = nas_common.get_access_zones(None)
        nas_status_active = msg_get_az["result"]["access_zones"][0]["nas_service_enabled"]
        cmp_nas_status_active = cmp(flag, nas_status_active)

        log.info("wait for %d s(flag:%s,status:%s)" % (time_count, flag, nas_status_active))
        if 0 != int(cmp_nas_status_active):
            if MAX_WAIT_TIME < time_count:
                raise Exception("wait for nas %s active too long:%d s" %
                                (class_action, time_count))
            log.info("%s  nas not active yet,waiting:%d" % (class_action, time_count))
            time.sleep(30)
            time_count += 30
            log.info("%d s" % time_count)
        else:
            log.info("changed to %s,used %d s" % (class_action, time_count))
            break
    return


def delete_add_one_ad(case_ip, ad_info_add):
    """
    author：
    function:检查集群中的AD数量，若存在，删除；若不存在，添加一个nas_common里的ad(方可测试固定的用户)
    :param case_ip(str)集群内ip；
    :param ad_info_add(list):添加的ad认证服务器信息列表，
                    如ad_info_add = ["ad_test", nas_common.AD_DOMAIN_NAME, nas_common.AD_DNS_ADDRESSES,
                    nas_common.AD_USER_NAME, nas_common.AD_PASSWORD, "NONE", "2000-3000"]
    :return: AD认证服务器配置命令的字典类型标准输出
    @changelog：
    """
    '''get,获取ad和az状态'''
    msd_get_ad = nas_common.get_auth_providers_ad(None)
    ad_total_sys_org = msd_get_ad["result"]["total"]

    '''没有ad就添加ad'''

    if 0 != int(ad_total_sys_org):
        log.info("ad_total is not zero!!!cleaning environment second")
        for delete_id in msd_get_ad["result"]["auth_providers"]:
            msg_delete_ad = nas_common.delete_auth_providers(delete_id["id"])
            common.judge_rc(msg_delete_ad["err_no"], 0,
                            "delete ad when cleaning func failed:" + msg_delete_ad["detail_err_msg"])

    msg_add_ad = nas_common.add_auth_provider_ad(ad_info_add[0], ad_info_add[1],
                                                 ad_info_add[2], ad_info_add[3],
                                                 ad_info_add[4], ad_info_add[5])
    msg_set_ntp = nas_common.set_ntp("true", ad_info_add[2], 5)
    add_ad_result = msg_add_ad["err_no"]
    set_ntp_rst = msg_set_ntp["err_no"]
    add_ad_final = set_ntp_rst + add_ad_result
    inf_p = "add ad result:add ad " + str(msg_add_ad["err_no"]) + ";ntp" + str(msg_set_ntp["err_no"])
    common.judge_rc(add_ad_final, 0, inf_p)

    '''不止一个ad,只取第一个'''
    msd_get_ad = nas_common.get_auth_providers_ad(None)

    return msd_get_ad


def case():
    log.info("case begin")
    ob_node = common.Node()
    case_node_id_lst = ob_node.get_nodes_id()
    case_id = random.choice(case_node_id_lst)
    case_ip = ob_node.get_node_ip_by_id(case_id)
    add_ad_info = [FILE_NAME + "_ad", nas_common.AD_DOMAIN_NAME, nas_common.AD_DNS_ADDRESSES,
                   nas_common.AD_USER_NAME, nas_common.AD_PASSWORD,
                   "NONE", "2000-3000"]
    rc_pscli_get_user = 1
    rc_gent_winbind = 1
    log.info(">1 添加ad服务器")
    msg_add_ad = delete_add_one_ad(case_ip, add_ad_info)
    ad_id = msg_add_ad["result"]["auth_providers"][0]["id"]
    log.info("ad add succeed:%s" % ad_id)

    log.info(">2 创建访问分区")
    msg_crt_az = nas_common.create_access_zone(case_id, FILE_NAME + "az", ad_id)
    common.judge_rc(msg_crt_az["err_no"], 0, "create access zone:" + str(msg_crt_az["detail_err_msg"]))
    az_id = msg_crt_az["result"]
    log.info("ad add succeed:%s" % az_id)

    log.info(">3 检查nas启动状态下的特定ad用户:%s，%s，%s" %
             (nas_common.AD_USER_4, nas_common.AD_USER_1st_GROUP, nas_common.AD_USER_2nd_GROUP))
    nas_state_change(case_ip, True)
    msg_check_ad = nas_common.check_auth_provider(ad_id)
    common.judge_rc(msg_check_ad["err_no"], 0, "check ad:" + str(msg_check_ad["detail_err_msg"]))
    log.info("ad check succeed:%s" % ad_id)
    rc, msg_get_ad = nas_common.get_auth_users(ad_id)
    common.judge_rc(msg_get_ad["err_no"], 0, "p300 get ad user:" + str(msg_get_ad["detail_err_msg"]))
    get_winbind_cmd = "getent passwd -s winbind"
    (rc_get, std_get) = common.run_command(case_ip, get_winbind_cmd)
    common.judge_rc(rc_get, 0, "rc of \"getent passwd -s winbind\" is:" + str(rc_get))
    get_winbind_cmd_total = get_winbind_cmd + " | wc -l"
    (rc_get_total, std_get_total) = common.run_command(case_ip, get_winbind_cmd_total)
    common.judge_rc(rc_get_total, 0, "std of \"getent passwd -s winbind | wc -l\" is:" + str(std_get_total))
    info_cmp_user = ("p300 get user total:%s,result of getent winbind is %s" %
                     (msg_get_ad["result"]["total"], std_get_total))
    common.judge_rc(msg_get_ad["result"]["total"], int(std_get_total) - 1, info_cmp_user)

    rc, msg_get_ad_user = nas_common.get_auth_users(ad_id)
    user_para_lst = []
    for user in msg_get_ad_user["result"]["auth_users"]:
        for secondary_group in user['secondary_groups']:
            if "id" in secondary_group:
                log.info("Found user in p300:%s" % user)
                user_para_lst.append(user['name'])
            # break
    if user_para_lst:
        log.info("not empty")
    else:
        rc_pscli_get_user = 0
    # user_para = "%s%s%s" % ('\"', nas_common.AD_USER_4, '\"')
    log.info("choose user")
    user_choice = str(random.choice(user_para_lst))
    log.info("choose: %s" % user_choice)
    user_para = "%s%s%s" % ('\"', user_choice, '\"')

    find_winbind_cmd = "getent passwd -s winbind | grep %s | wc -l" % user_para
    (rc_find_winbind, std_find) = common.run_command(case_ip, find_winbind_cmd)

    if rc_find_winbind != 0:
        rc_gent_winbind = int(find_winbind_cmd)
        log.info("failed:can not find by \'%s\'" % find_winbind_cmd)

    log.info(">4 检查结果，清理环境")
    log.info("ad user: %s is the choice" % nas_common.AD_USER_4)
    info_a = "result is (p300){},(gentwind){}".format(rc_pscli_get_user, rc_gent_winbind)
    common.judge_rc_unequal((rc_gent_winbind * int(rc_pscli_get_user)), 0, info_a)
    log.info("case succeed!")
    return


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    case()
    log.info("%s succeed!" % FILE_NAME)
    # prepare_clean.nas_test_clean()


if __name__ == '__main__':
    common.case_main(main)