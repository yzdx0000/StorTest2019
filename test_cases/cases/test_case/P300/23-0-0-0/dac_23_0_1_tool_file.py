# -*-coding:utf-8 -*
import os
import time
import sys

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
date 2018-09-06
@summary：
    基本功能list——私有客户端文件dac_setadvacl各权限的设置验证
@steps:
    1、用户信息获取与检查
    2、权限设置
    3、检查报错信息，清理环境，返回结果
@changelog：
    最后修改时间：
    修改内容：
"""

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
wait_time_th = 5


def clear_user_grp(case_ip, user_name, grp_name):
    cmd_del_user = "userdel -rf %s" % user_name
    (rc_del_uesr, std_del_user) = common.run_command(case_ip, cmd_del_user)
    # "userdel -r %s_g1"
    common.judge_rc(rc_del_uesr, 0, "del user by shell command ")
    cmd_del_grp = "groupdel  %s" % grp_name
    (rc_del_grp, std_del_grp) = common.run_command(case_ip, cmd_del_grp)
    # "userdel -r %s_g1"
    common.judge_rc(rc_del_grp, 0, "del group by shell command ")
    return


def dac_adv_set_get(case_ip, set_value, bin_path, user_name, complite_path):
    log.info("**********set并get权限位：%s************" % set_value)
    cmd_set = "%s/dac_setadvacl -s u:%s:%s::allow %s" % (bin_path, user_name, set_value, complite_path)
    (rc_set, std_set) = common.run_command(case_ip, cmd_set)
    common.judge_rc(rc_set, 0, "dac_setadvacl: " + std_set)
    cmd_get = "%s/dac_getadvacl  --full %s" % (bin_path, complite_path)
    (rc_get, std_get) = common.run_command(case_ip, cmd_get)
    common.judge_rc(rc_get, 0, "dac_getadvacl: " + std_get)
    log.info("get stdio info: %s" % std_get)
    return


def case():
    log.info("case begin")
    ob_node = common.Node()
    case_ip_lst = ob_node.get_nodes_ip()
    case_node_id_lst = ob_node.get_nodes_id()
    client_ip_lst = get_config.get_allclient_ip()
    # client_ip_lst = ob_node.get_external_client_ips()
    rc_dict = {}
    log.info(">1 随机选择执行节点")
    case_id = random.choice(case_node_id_lst)
    case_ip = ob_node.get_node_ip_by_id(case_id)
    # 舍弃独立客户端
    client_ip = case_ip
    bin_path = "/home/parastor/tools/client"
    user_name = "u1_%s" % FILE_NAME
    grp_name = "g1_%s" % FILE_NAME

    log.info(">1-1 创建系统本地用户，用于验证权限")
    # msg_get_local_pro = nas_common.get_auth_providers_local(case_id)
    # common.judge_rc(msg_get_local_pro["err_no"], 0, "<get local provider>")
    #
    # local_provider_id = msg_get_local_pro["result"]
    # gid = nas_common.create_auth_group(local_provider_id, FILE_NAME + "_grp")
    # msg_auth_user = nas_common.create_auth_user(local_provider_id, FILE_NAME + "_user", "111111", gid)
    cmd_del_user = "userdel -rf %s" % user_name
    (rc_del_uesr, std_del_user) = common.run_command(case_ip, cmd_del_user)
    # "userdel -r %s_g1"
    # common.judge_rc(rc_del_uesr, 0, "del user by shell command ")
    cmd_del_grp = "groupdel  %s" % grp_name
    (rc_del_grp, std_del_grp) = common.run_command(case_ip, cmd_del_grp)
    # "userdel -r %s_g1"
    # common.judge_rc(rc_del_grp, 0, "del group by shell command ")

    uid_1 = 950

    cmd_tail_passwd = "tail -n 1 /etc/passwd"
    (rc_wd, std_wd) = common.run_command(case_ip, cmd_tail_passwd)
    common.judge_rc(rc_wd, 0, "get last uid by shell command ")
    if user_name in std_wd:
        clear_user_grp(case_ip, user_name, grp_name)
    get_passwd = std_wd.strip().split(':')[2]
    if int(get_passwd) >= uid_1:
        uid_1 = int(get_passwd) + 10
    cmd_add_grp = "groupadd -g %d %s" % (uid_1, grp_name)
    (rc_add_grp, std_add_grp) = common.run_command(case_ip, cmd_add_grp)
    common.judge_rc(rc_add_grp, 0, "add group by shell command ")

    cmd_add_user = "useradd -g %s -u %d %s" % (grp_name, uid_1, user_name)
    (rc_add_uesr, std_add_user) = common.run_command(case_ip, cmd_add_user)
    # "userdel -r %s_g1"
    common.judge_rc(rc_add_uesr, 0, "add user by shell command ")

    log.info(">2-1 权限设置(node:%s;client:%s)" % (case_ip, client_ip))

    set_list = "rwpxdDaARWcCoS"
    path_top = os.path.join(prepare_clean.DEFECT_PATH, FILE_NAME)
    complite_path = path_top

    # sss = nas_common.VOLUME_NAME
    common.mkdir_path(case_ip, complite_path)

    set_value = "rx"

    # ssh u1@ip ''
    # cmd_do = "ssh %s@%s \"ls %s\"" % (user_name, client_ip, complite_path)
    # (rc_do, std_do) = common.run_command_shot_time(cmd_do)
    #
    # common.judge_rc(rc_do, 0, "action: " + std_do)
    ls_std_set = "let_it_be"
    org_context = "echo 111"
    cmd_been = "echo \"%s\" > %s/%s" % (org_context, complite_path, ls_std_set)
    (rc_been, std_been) = common.run_command(client_ip, cmd_been)
    common.judge_rc(rc_been, 0, "echo rsl: ")

    dac_adv_set_get(case_ip, set_value, bin_path, user_name, complite_path)
    dac_adv_set_get(case_ip, "r", bin_path, user_name, complite_path + "/" + ls_std_set)

    log.info(">检查%s 是否生效(读目录下的文件)" % set_value)
    # 变成完整目录才能cat
    cmd_do = "su - %s -c \"cat %s/%s\"" % (user_name, complite_path, ls_std_set)
    (rc_do, std_do) = common.run_command(client_ip, cmd_do)
    common.judge_rc(rc_do, 0, "action: " + std_do)

    if "111" not in std_do.strip():
        do_cmp = "[line]cat should show:%s, not:%s" % ("111", std_do)
        rc_dict[sys._getframe().f_lineno] = do_cmp
        # common.except_exit(do_cmp, cmp(ls_std_set, std_do))

    log.info("**********ace:%s passed!**********" % set_value)

    set_value = "w"
    context = "pwd"
    dac_adv_set_get(case_ip, "x", bin_path, user_name, complite_path)
    dac_adv_set_get(case_ip, set_value, bin_path, user_name, complite_path + "/" + ls_std_set)
    log.info(">检查%s 是否生效(写文件)" % set_value)
    # ls_std_set = "let_%s" % str(time.time())
    cmd_been = "su - %s -c \"echo \"%s\" > %s/%s\"" % (user_name, context, complite_path, ls_std_set)
    (rc_been, std_been) = common.run_command(client_ip, cmd_been)
    common.judge_rc(rc_been, 0, "echo for w: ")
    cmd_do = "cat %s/%s " % (complite_path, ls_std_set)
    (rc_do, std_do) = common.run_command(client_ip, cmd_do)
    common.judge_rc(rc_do, 0, "echo: " + std_do)
    
    if context not in std_do:
        do_cmp = "[line]cat should include(echo value):%s, not %s" % (context, std_do)
        rc_dict[sys._getframe().f_lineno] = do_cmp
        # common.except_exit(do_cmp, 2)

    log.info("**********ace:%s passed!**********" % set_value)

    set_value = "x"
    dac_adv_set_get(case_ip, set_value, bin_path, user_name, complite_path + "/" + ls_std_set)
    log.info(">检查%s 是否生效" % set_value)

    cmd_do = "%s/%s" % (complite_path, ls_std_set)
    (rc_do, std_do) = common.run_command(client_ip, cmd_do)
    if rc_do != 0:
        do_info = "[line]exec should not return:%d" % (rc_do, )
        rc_dict[sys._getframe().f_lineno] = do_info
        # common.except_exit(do_cmp, 2)
    log.info("**********ace:%s passed!**********" % set_value)

    if rc_dict != {}:
        log.info(rc_dict)
        for rci in rc_dict:
            log.info("some check point failed in %s,info:%s" % (rci, rc_dict[rci]))
        common.except_exit("failed in some check points, focus on first on", -9)

    log.info(">3 检查报错信息，清理环境")
    clear_user_grp(case_ip, user_name, grp_name)

    log.info("case passed")
    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info("%s succeed!" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
