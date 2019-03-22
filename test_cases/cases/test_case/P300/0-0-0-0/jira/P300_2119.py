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
date 2018-08-24
@summary：
     缺陷自动化——存在两个（多个）访问分区，同一ad，关闭其中一个nas服务，获取ad用户数量错误
@steps:
    1、添加ad服务器
    2、创建两个访问分区
    3、在访问区0nas关闭、访问区1（nas启动）两种状态下get ad用户的数量：数据库方式和pscli方式应相差一个
    4、检查结果，清理环境
@changelog：
    最后修改时间：
    修改内容：修订多个访问分区的nas启停函数，传入访问分区id作为执行参数
"""
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
MAX_WAIT_TIME = 1800
NUMBERS = 2
# nas30分钟——chengqiang


def nas_state_change(az_id, flag=False):
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
    msg_get_az = nas_common.get_access_zones(az_id)
    time_start = time.time()
    if flag is True:
        msg_nas = nas_common.enable_nas(az_id)
    else:
        msg_nas = nas_common.disable_nas(az_id)
    time_end = time.time()
    if time_end - time_start > MAX_WAIT_TIME:
        raise Exception("wait nas command:%d s" % (time_end - time_start))
    log.info("wait nas command:%d s" % (time_end - time_start))
    action_nas_rst = msg_nas["detail_err_msg"]
    judge_info = "%s nas action :%s" % (class_action, action_nas_rst)
    common.judge_rc(msg_nas["err_no"], 0, judge_info)
    time_count = 0
    while True:

        msg_get_az = nas_common.get_access_zones(az_id)
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
    :param ad_info_add(list):添加的ad认证服务器信息列表，如ad_info_add = ["ad_test", nas_common.AD_DOMAIN_NAME, nas_common.AD_DNS_ADDRESSES,
                   nas_common.AD_USER_NAME, nas_common.AD_PASSWORD,
                   "NONE", "2000-3000"]
    :return: AD认证服务器配置命令的字典类型标准输出
    @changelog：
    """

    msd_get_ad = nas_common.get_auth_providers_ad(None)
    ad_total_sys_org = msd_get_ad["result"]["total"]

    '''存在ad先删除'''

    if 0 != int(ad_total_sys_org):
        log.info("ad_total is not zero!!!cleaning environment second")
        for delete_id in msd_get_ad["result"]["auth_providers"]:
            msg_delete_ad = nas_common.delete_auth_providers(delete_id["id"])
            common.judge_rc(msg_delete_ad["err_no"], 0, "delete ad when cleaning func failed:" + msg_delete_ad["detail_err_msg"])

    msg_add_ad = nas_common.add_auth_provider_ad(ad_info_add[0], ad_info_add[1], ad_info_add[2], ad_info_add[3], ad_info_add[4], ad_info_add[5])
    # , ad_info_add[6])
    msg_set_ntp = nas_common.set_ntp("true", ad_info_add[2], 5)
    add_ad_result = msg_add_ad["err_no"]
    set_ntp_rst = msg_set_ntp["err_no"]
    add_ad_final = set_ntp_rst + add_ad_result
    common.judge_rc(add_ad_final, 0, "add ad result:" + str(msg_add_ad["err_no"]) + str(msg_set_ntp["err_no"]))

    msd_get_ad = nas_common.get_auth_providers_ad(None)

    return msd_get_ad


def nas_stat_ad_diff_one(case_ip, ad_id, nas_flag):
    """

    :param case_ip:(str)执行命令的（访问区）节点ip
    :param ad_id:(str)配置到访问区里的ad
    :param nas_flag:(bool)nas状态标志位
    :return:rst_dict:(为字典)获取和计算用户数量的结果
    """
    # rst_dict = {}
    # 注意多个访问区，不能直接取字典数组中的第0个作为待操作访问区的id
    az_id = -1
    node_id = common.Node().get_node_id_by_ip(case_ip)
    msg_find_id = nas_common.get_access_zones()
    common.judge_rc(msg_find_id["err_no"], 0, "get az all info:" + msg_find_id["detail_err_msg"])
    for az_info in msg_find_id["result"]["access_zones"]:
        if node_id in az_info["node_ids"]:
            az_id = az_info["id"]
    common.judge_rc_unequal(az_id, -1, "get az_id from ip,info: " + str(msg_find_id["result"]))
    nas_state_change(az_id, nas_flag)
    msg_get_az = nas_common.get_access_zones(az_id)
    common.judge_rc(msg_get_az["err_no"], 0, "get az by id info:" + msg_get_az["detail_err_msg"])

    nas_status_active = msg_get_az["result"]["access_zones"][0]["nas_service_enabled"]
    if nas_flag != nas_status_active:
        log_exit_info = "err:nas_status_active:%s should be :%s" % (nas_status_active, nas_flag)
        common.except_exit(log_exit_info)
    msg_check_ad = nas_common.check_auth_provider(ad_id)
    common.judge_rc(msg_check_ad["err_no"], 0, "check ad:" + str(msg_check_ad["detail_err_msg"]))
    log.info("ad check succeed:%s" % ad_id)
    rc, msg_get_ad = nas_common.get_auth_users(ad_id)
    common.judge_rc(msg_get_ad["err_no"], 0, "p300 get ad user(az1):" + msg_get_ad["detail_err_msg"])
    get_winbind_cmd = "getent passwd -s winbind"
    get_winbind_cmd_total = get_winbind_cmd + " | wc -l"
    (rc_get_total, std_get_total) = common.run_command(case_ip, get_winbind_cmd_total)
    common.judge_rc(rc_get_total, 0, "std of \"getent passwd -s winbind | wc -l\" is:" + str(std_get_total))
    rst_diff = int(std_get_total) - msg_get_ad["result"]["total"]

    rst_dict = {(nas_flag, case_ip): [rst_diff, msg_get_ad["result"]["total"], int(std_get_total)]}
    info_cmp_user = "on %s p300 get user total:%s should less 1 than result of getent winbind is %s" % (case_ip, msg_get_ad["result"]["total"], std_get_total)
    log.info(info_cmp_user)

    return rst_dict


def case():
    log.info("case begin")
    ob_node = common.Node()
    case_node_id_lst = ob_node.get_nodes_id()
    # lst中0是先enable后disable nas，1是enable nas去检查
    case_id_lst = random.sample(case_node_id_lst, NUMBERS)
    case_ip_lst = []
    for case_id in case_id_lst:
        case_ip = ob_node.get_node_ip_by_id(case_id)
        case_ip_lst.append(case_ip)
    add_ad_info = [FILE_NAME + "_ad", nas_common.AD_DOMAIN_NAME, nas_common.AD_DNS_ADDRESSES,
                   nas_common.AD_USER_NAME, nas_common.AD_PASSWORD,
                   "NONE", "2000-3000"]
    if NUMBERS > len(case_ip_lst):
        exit_info = "%s set too big,should not bigger than total nodes %s" % (NUMBERS, len(case_ip_lst))
        common.except_exit(exit_info)
    az_id_lst = []
    rst_dict_lst = []
    log.info(">1 添加ad服务器")
    msg_add_ad = delete_add_one_ad(case_ip_lst[0], add_ad_info)
    ad_id = msg_add_ad["result"]["auth_providers"][0]["id"]
    log.info("ad add succeed:%s" % ad_id)

    log.info(">2 创建两个访问分区")
    for i in range(NUMBERS):
        az_name = FILE_NAME + "_az" + str(i)
        msg_crt_az = nas_common.create_access_zone(case_id_lst[i], az_name, ad_id)
        common.judge_rc(msg_crt_az["err_no"], 0, "create access zone:" + msg_crt_az["detail_err_msg"])
        az_id = msg_crt_az["result"]
        log.info("ad add succeed:%s" % az_id)
        az_id_lst.append(az_id)

    log.info(">3 在两个访问区nas关闭(%s)+nas启动状态下(%s)检查ad用户的数量，数据库方式和pscli方式应相差一个"
             % (az_id_lst[0], az_id_lst[1]))
    log.info(case_ip_lst[0])
    rst_dict = nas_stat_ad_diff_one(case_ip_lst[0], ad_id, True)
    rst_dict_lst.append(rst_dict)
    log.info(case_ip_lst[0])
    rst_dict = nas_stat_ad_diff_one(case_ip_lst[0], ad_id, False)
    rst_dict_lst.append(rst_dict)
    log.info(case_ip_lst[1])
    rst_dict_test = nas_stat_ad_diff_one(case_ip_lst[1], ad_id, True)
    rst_dict_lst.append(rst_dict_test)

    log.info(">4 检查结果，清理环境")
    log.info("ad user: %s is the choice" % nas_common.AD_USER_4)

    prepare_clean.nas_test_clean()

    # for res in rst_dict_lst:
    rst_info = ("nas stat:%s on %s(nas is %s on %s)\nresult on %s:%s(except diff:1,psl,getent)" %
                (rst_dict_test.keys()[0][0], rst_dict_test.keys()[0][1], rst_dict.keys()[0][0], rst_dict.keys()[0][1], rst_dict_test.keys()[0][1], rst_dict_test.values()[0]))
    common.judge_rc(rst_dict_test.values()[0][0], 1, rst_info)
    log.info("%s\ncase succeed!" % rst_info)
    return


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    case()
    log.info("%s succeed!" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
