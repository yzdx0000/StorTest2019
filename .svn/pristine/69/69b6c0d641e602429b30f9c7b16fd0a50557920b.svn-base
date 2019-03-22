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
date 2018-09-08
@summary：
    基本功能list——nfs客户端目录dac_setadvacl各权限的设置验证
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
    case_id = 1  # random.choice(case_node_id_lst)
    case_ip = ob_node.get_node_ip_by_id(case_id)

    client_ip = nas_common.NFS_3_CLIENT_IP   # random.choice(get_config.get_nfs_client_ip())
    bin_path = "/home/parastor/tools/client"
    user_name = "u1_%s" % FILE_NAME
    grp_name = "g1_%s" % FILE_NAME
    log.info(">1-1 挂载文件nfs文件系统，创建服务端和客户端相同本地用户，用于验证权限")
    for ip in (case_ip, client_ip):
        # 防止脚本未运行完中断引起的usr name或group name已经存在
        log.info("clear user and group for abort")
        cmd_del_user = "userdel -rf %s" % user_name
        (rc_del_uesr, std_del_user) = common.run_command(ip, cmd_del_user)
        # "userdel -r %s_g1"
        common.judge_rc_unequal(rc_del_uesr, 0, "should not need to del user at start ", False)
        cmd_del_grp = "groupdel  %s" % grp_name
        (rc_del_grp, std_del_grp) = common.run_command(ip, cmd_del_grp)
        # "userdel -r %s_g1"
        common.judge_rc_unequal(rc_del_grp, 0, "should not need to del group at start ", False)
    uid_1 = 901
    cmd_tail_passwd = "tail -n 1 /etc/passwd"
    (rc_wd, std_wd) = common.run_command(case_ip, cmd_tail_passwd)
    common.judge_rc(rc_wd, 0, "get last uid by shell command ")
    get_passwd_node = std_wd.strip().split(':')[2]
    (rc_wd, std_wd) = common.run_command(client_ip, cmd_tail_passwd)
    common.judge_rc(rc_wd, 0, "get last uid by shell command ")
    get_passwd_client = std_wd.strip().split(':')[2]
    log.info("node last user:{}, client last user:{}".format(get_passwd_node, get_passwd_client))

    add_time = 0
    while int(get_passwd_node) >= int(uid_1) or int(get_passwd_client) >= int(uid_1):
        uid_1 = int(uid_1) + 1
        add_time += 1
        log.info("node last user:{}, client last user:{}".format(get_passwd_node, get_passwd_client))
        log.info("find uid_1 No.{} time, uid_1 = {}".format(add_time, uid_1))
    log.info("user_id found:{}".format(uid_1))

    for ip in (case_ip, client_ip):
        log.info("add user and group")
        cmd_add_grp = "groupadd -g %d %s" % (uid_1, grp_name)
        (rc_add_grp, std_add_grp) = common.run_command(ip, cmd_add_grp)
        common.judge_rc(rc_add_grp, 0, "add group by shell command ")

        cmd_add_user = "useradd -g %s -u %d %s" % (grp_name, uid_1, user_name)
        (rc_add_uesr, std_add_user) = common.run_command(ip, cmd_add_user)
        # "userdel -r %s_g1"
        common.judge_rc(rc_add_uesr, 0, "add user by shell command ")

    mount_path = '/mnt/' + FILE_NAME
    cmd_df_grep = 'mount | grep %s' % FILE_NAME
    (rc_df, std_df) = common.run_command(node_ip=client_ip, cmd=cmd_df_grep, timeout=wait_time_th)
    path_top = nas_common.NAS_PATH_ABSPATH + "/" + FILE_NAME
    if rc_df == 0:
        cmd_umount = "umount -f {}".format(mount_path)
        rc_umount = 1
        umount_times = 0
        while rc_umount != 0:
            (rc_umount, std_umount) = common.run_command(node_ip=client_ip, cmd=cmd_umount, timeout=wait_time_th)
            umount_times += 1
            log.info("umount times: %d" % umount_times)
            if umount_times > 100:
                exit_info = "umount more than 100 times,exit"
                common.except_exit(exit_info, -2)
        log.info("umount succeed")

    log.info(">2 节点导出nfs:{}，客户端挂载nfs".format(case_ip, client_ip))
    msg_crt_az = nas_common.create_access_zone(case_id, FILE_NAME + "_az")
    common.judge_rc(msg_crt_az["err_no"], 0, "create access zone: " + msg_crt_az["detail_err_msg"])
    az_id = msg_crt_az["result"]
    msg_file = nas_common.create_file(nas_common.ROOT_DIR + FILE_NAME)
    common.judge_rc(msg_file["err_no"], 0, "create file: " + msg_file["detail_err_msg"])

    msg_nfs_export = nas_common.create_nfs_export(az_id, FILE_NAME, nas_common.ROOT_DIR + FILE_NAME)
    common.judge_rc(msg_nfs_export["err_no"], 0, "create nfs: " + msg_nfs_export["detail_err_msg"])
    msg_add_nfs_client = nas_common.add_nfs_export_auth_clients(export_id=msg_nfs_export["result"], name=str(client_ip), permission_level='rw', permission_constraint='no_root_squash')
    common.judge_rc(msg_add_nfs_client["err_no"], 0, "add nfs client: " + msg_add_nfs_client['detail_err_msg'])
    msg_rc_nas = nas_common.enable_nas(az_id)
    common.judge_rc(msg_rc_nas["err_no"], 0, "enable_nas: " + msg_rc_nas["detail_err_msg"])
    log.info("等nas启动5s")
    time.sleep(wait_time_th)

    common.mkdir_path(client_ip, mount_path)

    cmd_mount = 'mount -t nfs {}:{} {}'.format(case_ip, path_top, mount_path)
    (rc_mt, std_mt) = common.run_command(client_ip, cmd_mount)
    common.judge_rc(rc_mt, 0, "mount nfs: " + std_mt)
    (rc_df, std_df) = common.run_command(node_ip=client_ip, cmd=cmd_df_grep, timeout=wait_time_th)
    log.info("ready: " + std_df)

    log.info(">3 权限设置(node:%s;client:%s)" % (case_ip, client_ip))

    set_list = "rwpxdDaARWcCoS"

    complite_path = path_top + "/" + "dir_advacl"
    #
    # # sss = nas_common.VOLUME_NAME
    common.mkdir_path(case_ip, complite_path)
    #
    set_value = "r"
    dac_adv_set_get(case_ip, set_value, bin_path, user_name, complite_path)
    log.info(">检查%s 是否生效" % set_value)

    ls_std_set = "let_it_be"
    cmd_been = "touch %s/%s" % (complite_path, ls_std_set)
    (rc_been, std_been) = common.run_command(client_ip, cmd_been)
    common.judge_rc(rc_been, 0, "touch for ls: ")
    cmd_do = "su - %s -c \"ls %s\"" % (user_name, complite_path)
    (rc_do, std_do) = common.run_command(client_ip, cmd_do)
    common.judge_rc(rc_do, 0, "action: " + std_do)
    log.info(std_do)

    if ls_std_set.strip() != std_do.strip():
        do_cmp = "ls should show:%s, not:%s" % (ls_std_set, std_do)
        rc_dict[sys._getframe().f_lineno] = do_cmp
        # common.except_exit(do_cmp, cmp(ls_std_set, std_do))
    log.info("**********ace:%s passed!**********" % set_value)

    set_value = "wx"
    dac_adv_set_get(case_ip, set_value, bin_path, user_name, complite_path)
    log.info(">检查%s 是否生效(目录写文件)" % set_value)
    ls_std_set = "let_%s" % str(time.time())
    cmd_been = "su - %s -c \"touch %s/%s\"" % (user_name, complite_path, ls_std_set)
    (rc_been, std_been) = common.run_command(client_ip, cmd_been)
    common.judge_rc(rc_been, 0, "touch for w: ")
    cmd_do = "ls %s " % complite_path
    (rc_do, std_do) = common.run_command(client_ip, cmd_do)
    common.judge_rc(rc_do, 0, "action: " + std_do)
    log.info(std_do)
    if ls_std_set not in std_do:
        do_cmp = "ls should show:%s, not %s" % (ls_std_set, std_do)
        rc_dict[sys._getframe().f_lineno] = do_cmp
        # common.except_exit(do_cmp, 2)
    file_w = "%s/%s" % (complite_path, ls_std_set)
    (rc_rm_w, std_rm_w) = common.rm_exe(case_ip, file_w)
    if 0 != rc_rm_w:
        do_check = "con't rm file(with ace 'w'):%s, not %s" % (user_name, file_w)
        rc_dict[sys._getframe().f_lineno] = do_check
    del_path = complite_path + ls_std_set
    if '/mnt/' in del_path:
        cmd_been = "su - %s -c \"rm -f %s\"" % (user_name, del_path)
        (rc_been, std_been) = common.run_command(client_ip, cmd_been)
    log.info("**********ace:%s passed!**********" % set_value)

    set_value = "x"
    dac_adv_set_get(case_ip, set_value, bin_path, user_name, complite_path)
    log.info(">检查%s 是否生效" % set_value)
    # common.judge_rc(rc_been, 0, "cd && pwd for x: ")
    cmd_do = "cd %s && pwd " % complite_path
    (rc_do, std_do) = common.run_command(client_ip, cmd_do)
    common.judge_rc(rc_do, 0, "action: " + std_do)
    log.info(std_do)
    if rc_do != 0:
        do_cmp = "cd should :%s" % (complite_path, )
        rc_dict[sys._getframe().f_lineno] = do_cmp
        # common.except_exit(do_cmp, 2)
    log.info("**********ace:%s passed!**********" % set_value)

    if rc_dict != {}:
        log.info(rc_dict)
        for rci in rc_dict:
            log.info("some check point failed in %s,info:%s" % (rci, rc_dict[rci]))
        common.except_exit("failed in some check points, focus on first on", -9)

    log.info(">4 检查报错信息，清理环境")
    cmd_umount = "umount -f {}".format(mount_path)
    rc_umount = 1
    umount_times = 0
    while rc_umount != 0:
        (rc_umount, std_umount) = common.run_command(node_ip=client_ip, cmd=cmd_umount, timeout=wait_time_th)
        umount_times += 1
        log.info("umount times: %d" % umount_times)
        if umount_times > 100:
            exit_info = "umount more than 100 times,exit"
            common.except_exit(exit_info, -2)
    log.info("umount succeed")

    for ip in (case_ip, client_ip):
        cmd_del_user = "userdel -rf %s" % user_name
        (rc_del_uesr, std_del_user) = common.run_command(ip, cmd_del_user)
        # "userdel -r %s_g1"
        common.judge_rc(rc_del_uesr, 0, "del user by shell command ")
        cmd_del_grp = "groupdel  %s" % grp_name
        (rc_del_grp, std_del_grp) = common.run_command(ip, cmd_del_grp)
        # "userdel -r %s_g1"
        common.judge_rc(rc_del_grp, 0, "del group by shell command ")
    log.info("case passed")
    return


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    case()
    prepare_clean.nas_test_clean(FILE_NAME)
    log.info("%s succeed!" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
