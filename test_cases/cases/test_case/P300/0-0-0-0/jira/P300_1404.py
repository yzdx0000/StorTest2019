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
import quota_common
"""
Author:liangxy
date 2018-08-21
@summary：
     缺陷自动化——为ldap用户创建目录配额失败
@steps:
    1、添加ldap服务器
    2、创建访问分区
    3、检查nas启动状态下的ldap用户状态
    4、选取一个ldap用户，创建目录配额
    5、检查结果，清理环境
@changelog：
    最后修改时间：
    修改内容：
"""
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
MAX_WAIT_TIME = 1800
# 30分钟——chengqiang
QUOTA_TH = 2000


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


def quota_config(auth_provider_id, quota_user):
    """

    :param auth_provider_id(str):认证服务器id
    :return:
    """
    quota_common.creating_dir(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH)
    rc, stdout = common.create_quota("%s:/%s" % (quota_common.VOLUME_NAME, quota_common.QUOTA_PATH_BASENAME),
                                     auth_provider_id=auth_provider_id, filenr_quota_cal_type='QUOTA_LIMIT',
                                     filenr_hard_threshold=QUOTA_TH, user_type='USERTYPE_USER',
                                     user_or_group_name=quota_user)
    check_rst = common.json_loads(stdout)

    return check_rst


def case():

    log.info("case begin")
    ob_node = common.Node()
    case_node_id_lst = ob_node.get_nodes_id()
    case_id = random.choice(case_node_id_lst)
    case_ip = ob_node.get_node_ip_by_id(case_id)
    case_id = nas_common.get_node_ids()

    log.info(">1 添加ldap服务器")
    msg_add_ldap = nas_common.add_auth_provider_ldap(FILE_NAME + "_ldap", nas_common.LDAP_BASE_DN, nas_common.LDAP_IP_ADDRESSES)
    common.judge_rc(msg_add_ldap["err_no"], 0, "add ldap:" + msg_add_ldap["detail_err_msg"])
    ldap_id = msg_add_ldap["result"]
    log.info("ldap add succeed:%s" % ldap_id)

    log.info(">2 创建访问分区")
    msg_crt_az = nas_common.create_access_zone(case_id, FILE_NAME + "az", ldap_id)
    common.judge_rc(msg_crt_az["err_no"], 0, "create access zone:" + msg_crt_az["detail_err_msg"])
    az_id = msg_crt_az["result"]
    log.info("ldap add succeed:%s" % az_id)

    log.info(">3 检查nas启动状态下的ldap用户状态")
    nas_state_change(case_ip, True)
    msg_check_ldap = nas_common.check_auth_provider(ldap_id)
    common.judge_rc(msg_check_ldap["err_no"], 0, "check ldap:" + msg_check_ldap["detail_err_msg"])
    log.info("ldap check succeed:%s" % ldap_id)
    rc, msg_get_ldap_user = nas_common.get_auth_users(ldap_id)
    common.judge_rc(msg_get_ldap_user["err_no"], 0, "p300 get ldap user:" + msg_get_ldap_user["detail_err_msg"])
    time.sleep(15)
    get_winbind_cmd = "getent passwd -s ldap"
    (rc_get, std_get) = common.run_command(case_ip, get_winbind_cmd)
    common.judge_rc(rc_get, 0, "rc of \"getent passwd -s ldap\" is:" + str(rc_get))
    get_winbind_cmd_total = get_winbind_cmd + " | wc -l"
    (rc_get_total, std_get_total) = common.run_command(case_ip, get_winbind_cmd_total)
    common.judge_rc(rc_get_total, 0, "std of \"getent passwd -s ldap | wc -l\" is:" + str(std_get_total))

    info_cmp_user = "p300 get user total:%s,result of getent ldap is %s" % (msg_get_ldap_user["result"]["total"], std_get_total)
    common.judge_rc(msg_get_ldap_user["result"]["total"], int(std_get_total), info_cmp_user)

    log.info(">4 选取一个ldap用户，创建目录配额")
    ldap_user_name_lst = []

    for ldap_info in msg_get_ldap_user["result"]["auth_users"]:
        ldap_user_name_lst.append(ldap_info["name"])
    test_ldap_name = ldap_user_name_lst[0]  # random.choice(ldap_user_name_lst)
    # quota_common.cleaning_environment()
    check_rst = quota_config(ldap_id, test_ldap_name)
    common.judge_rc(check_rst["err_no"], 0, "Config quota result:" + check_rst["detail_err_msg"])

    quota_common.creating_files_by_designated_user_or_group(node_ip=quota_common.NOTE_IP_1, quota_path=quota_common.QUOTA_PATH,
                                                            file_size=1, file_count=(QUOTA_TH + 100), file_name_identifier=1, designated_user=test_ldap_name)

    log.info(">5 检查结果，清理环境")
    log.info("ldap user: %s is the choice\ncreate its quota" % test_ldap_name)

    total_inodes = quota_common.user_total_inodes(quota_common.CLIENT_IP_2, quota_common.QUOTA_PATH,
                                                  test_ldap_name)
    common.judge_rc(int(total_inodes), int(QUOTA_TH), "quota result:")
    quota_common.cleaning_environment()
    log.info("case succeed!")

    return


def main():

    prepare_clean.nas_test_prepare(FILE_NAME)
    quota_common.cleaning_environment()
    case()
    prepare_clean.nas_test_clean()
    log.info("%s succeed!" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
