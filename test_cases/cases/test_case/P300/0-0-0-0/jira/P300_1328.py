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
Author:liangxy
date 2018-08-22
@summary：
     缺陷自动化——导出nfs后，使用update_nfs_export_auth_client更新参数anonuid与anongid失败
@steps:
    1、创建访问分区
    2、导出nfs
    3、创建nfs客户端
    4、更新nfs客户端的anonuid与anongid为新的值
    5、检查anonuid与anongid参数值；
    6、在nfs客户端创建文件，检查文件的属主和属组信息是否符合anonuid与anongid
    7、清理环境，返回结果
@changelog：todo_
           disable nas 后最少需要6分钟（经验值）才可完全生效; delete path
"""
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
MAX_WAIT_TIME = 1801
MAX_WAIT_MTIME = 30


def get_client_date_ip(client_ip):
    """
    :author :             chenjy1
    :date:                2018.08.24
    :description:         获取一个客户端的所有数据网IP
    :param client_ip:    (str)客户端IP
    :return:
    """
    client_date_ip_lst = []
    ob_node = common.Node()
    node_id_lst = ob_node.get_nodes_id()
    sys_node_ip = ob_node.get_node_ip_by_id(node_id_lst[0])
    eth_list, data_ip_list, ip_mask_lst = ob_node.get_node_eth(node_id_lst[0])
    clientnode_all_ip_lst = []

    cmd = 'ip addr | grep "inet "'
    rc, stdout = common.run_command(client_ip, cmd)
    common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    lines = stdout.strip().split('\n')
    for line in lines:
        ip = line.split()[1].split('/')[0]
        clientnode_all_ip_lst.append(ip)

    for sys_date_ip in data_ip_list:
        for ip in clientnode_all_ip_lst:
            if ip != "127.0.0.1":
                cmd = "ping -c 2 -I %s %s" % (sys_date_ip, ip)
                rc, stdout = common.run_command(sys_node_ip, cmd, timeout=5)
                if rc == 0:
                    client_date_ip_lst.append(ip)
                    break
    return client_date_ip_lst


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
    msg_get_az = nas_common.get_access_zones(None, case_ip)
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

        msg_get_az = nas_common.get_access_zones(None, case_ip)
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


def nfs_mount_stat(client_ip, export_ip, export_path, str_ax=None):
    """

    :param client_ip: (str)挂载nfs的客户端ip
    :param export_ip: (str)导出nfs的集群（数据网）ip
    :param export_path: (str)导出目录
    :param str_ax: (str)区分touch文件的文件名
    :return:filename(str), std_stat_uid(str), std_stat_gid(str)
    """

    mount_point = "/mnt/%s_m_nfs" % FILE_NAME

    cmd_mkdir = "mkdir %s" % mount_point
    log.info("timeout=%s" % str(MAX_WAIT_MTIME))
    (rc_mkdir, std_mk) = common.run_command(node_ip=client_ip, cmd=cmd_mkdir, timeout=MAX_WAIT_MTIME)
    common.judge_rc(rc_mkdir, 0, "mkdir info:" + std_mk, False)
    mount_name = "%s:%s" % (export_ip, export_path)
    log.info("will execute mount cmd between %s:%s to %s" % (export_ip, export_path, mount_point))

    cmd_mnt = "mount -t nfs %s %s" % (mount_name, mount_point)
    log.info("timeout=%s" % str(MAX_WAIT_MTIME))

    (rc_mnt, std_mnt) = common.run_command(node_ip=client_ip, cmd=cmd_mnt, timeout=MAX_WAIT_MTIME)
    common.judge_rc(rc_mnt, 0, "mount rc:" + str(rc_mnt) + "info:" + std_mnt, False)
    # cmd_df = "df | grep nfs"
    # log.info("timeout=%s" % str(MAX_WAIT_MTIME))
    #
    # (rc_df, std_df) = common.run_command(node_ip=client_ip, cmd=cmd_df, timeout=MAX_WAIT_MTIME)
    # if rc_mnt != 0:
    #     if mount_point in std_df:
    #         log.info("mount suceed!")
    #     else:
    #         log_df_info = "mount failed!"
    #         common.except_exit(log_df_info)
    filename = FILE_NAME + "_" + str_ax
    cmd_touch = "touch %s/%s" % (mount_point, filename)
    (rc_touch, std_touch) = common.run_command(client_ip, cmd_touch)
    common.judge_rc(rc_touch, 0, "touch info:" + std_touch)
    # stat check_core_2.5.py | grep Uid | awk -F/ '{print $2}' | awk '{print $NF}'
    # stat check_core_2.5.py | grep Uid | awk -F/ '{print $3}' | awk '{print $NF}'
    cmd_ls_uid = "ls -n %s/%s" % (mount_point, filename)
    (rc_ls_uid, std_ls_n) = common.run_command(client_ip, cmd_ls_uid)
    std_ls_n_lst = std_ls_n.split()
    return filename, std_ls_n_lst[2], std_ls_n_lst[3]


def case():
    log.info("case begin")
    ob_node = common.Node()
    case_node_id = random.choice(ob_node.get_nodes_id())
    case_ip = ob_node.get_node_ip_by_id(case_node_id)
    case_client_ip_m = random.choice(get_config.get_allclient_ip())
    # 换到20网段
    #case_client_ip_s = case_client_ip_m.split('.')
    #case_client_ip_s[0] = '20'
    #case_client_ip = ".".join(case_client_ip_s)
    case_client_ip = get_client_date_ip(case_client_ip_m)[0]
    cmd_ping = "ping -c 4 %s" % case_client_ip
    (rc_ping, std_ping) = common.run_command(case_ip, cmd_ping)
    ping_info = "from %s ping %s" % (case_ip, case_client_ip)
    common.judge_rc(rc_ping, 0, ping_info)
    test_value_uid = 10000
    test_value_gid = 10001
    log.info("1> 创建访问分区,清理客户端mount")

    mount_point = "/mnt/%s_m_nfs" % FILE_NAME
    ls_cmd = "ls %s" % mount_point
    for client_ip in ob_node.get_external_client_ips():
        (rc_ls, rc_std) = common.run_command(client_ip, ls_cmd, True, MAX_WAIT_MTIME)
        if rc_ls == 0:
            cmd_umount = "umount -f %s" % mount_point
            log.info("timeout=%s" % str(MAX_WAIT_MTIME))
            time_start = time.time()
            while True:
                time_t = time.time() - time_start
                if time_t > MAX_WAIT_MTIME:
                    common.except_exit("umount too long time")
                (rc_umount, std_umount) = common.run_command(node_ip=client_ip, cmd=cmd_umount)
                log.info("std_umount is :%s " % std_umount)
                if rc_umount == 0 or 'not mounted' in std_umount:
                    log.info("umount succeed")
                    break

    msg_get_az = nas_common.get_access_zones(None, case_ip)
    az_total_num_org = msg_get_az["result"]["total"]
    if 0 != int(az_total_num_org):
        for left_azs in msg_get_az["result"]["access_zones"]:
            log.error("nas_cleaning failed,left access zone:%s to delete" % left_azs["id"])
            msg_clean_az = nas_common.delete_access_zone(left_azs["id"])
            common.judge_rc(msg_clean_az, 0, "clean access zone:%s after nas_cleaning() failed" % left_azs["id"])
    msg_add_az = nas_common.create_access_zone(case_node_id, FILE_NAME + "_az")
    common.judge_rc(msg_add_az["err_no"], 0, "add az info:" + msg_add_az["detail_err_msg"])
    id_az = msg_add_az["result"]
    log.info("access zone(%s) is ok" % id_az)
    log.info("2> 创建导出nfs，注意nas状态")
    nas_state_change(case_ip, True)
    nfs_export_volume_path = nas_common.ROOT_DIR + FILE_NAME + "_nfs"
    msg_crt_file = nas_common.create_file(nfs_export_volume_path)
    common.judge_rc(msg_crt_file["err_no"], 0, "create file info:" + msg_crt_file["detail_err_msg"])
    msg_export_nfs_dir = nas_common.create_nfs_export(id_az, FILE_NAME + "_nfs_ex", nfs_export_volume_path)
    common.judge_rc(msg_export_nfs_dir["err_no"], 0, "export nfs dir info:" + msg_export_nfs_dir["detail_err_msg"])
    id_nfs = msg_export_nfs_dir["result"]
    """
    参数：export_id, name, permission_level, write_mode=None, port_constraint=None, permission_constraint=None, anonuid=None,
    #  anongid=None, node_ip=RANDOM_NODE_IP
    """
    msg_add_nfs_auth = nas_common.add_nfs_export_auth_clients(export_id=id_nfs, name=case_client_ip,
                                                              permission_level="rw")
    common.judge_rc(msg_add_nfs_auth["err_no"], 0, "add nfs auth info:" + msg_add_nfs_auth["detail_err_msg"])
    nfs_client_id = msg_add_nfs_auth["result"][0]
    msg_get_nfs_auth = nas_common.get_nfs_export_auth_clients(export_ids=id_nfs)
    common.judge_rc(msg_get_nfs_auth["err_no"], 0, "get nfs info:" + msg_get_nfs_auth["detail_err_msg"])
    # nfs_client_id是否是顺序累加？nfs_export_auth_clients字段后的排序0是回退的还是不一致的？
    log.info("3> 获取默认的uid和gid")
    fault_uid = msg_get_nfs_auth["result"]["nfs_export_auth_clients"][0]["anonuid"]
    fault_gid = msg_get_nfs_auth["result"]["nfs_export_auth_clients"][0]["anongid"]
    log.info("3-1> 更新前执行touch和stat命令")
    abs_path = nas_common.NAS_PATH + "/" + FILE_NAME + "_nfs"
    msg_get_nodes = nas_common.get_nodes(ids=case_node_id)
    common.judge_rc(msg_get_nodes["err_no"], 0, "get nodes info:" + msg_get_nodes["detail_err_msg"])
    date_ip = msg_get_nodes["result"]["nodes"][0]["data_ips"][0]["ip_address"]
    get_nodes_info = "get nodes --ids unaffctive,total:%s(should be 1),get data ip failed" % str(msg_get_nodes["result"]["total"])
    common.judge_rc(msg_get_nodes["result"]["total"], 1, get_nodes_info)
    log.info("case id:%s,case ip:%s,data ip:%s,client ip:%s" % (str(case_node_id), case_ip, date_ip, case_client_ip))
    (filename_ft, uid_ft, gid_ft) = nfs_mount_stat(case_client_ip, date_ip, abs_path, "default")

    log.info("4> 更新nfs导出用户的为uid(%s)和gid(%s)" % (test_value_uid, test_value_gid))
    msg_update_nfs_auth = nas_common.update_nfs_export_auth_client(auth_client_id=nfs_client_id,
                                                                   anonuid=test_value_uid, anongid=test_value_gid)
    common.judge_rc(msg_update_nfs_auth["err_no"], 0, "update nfs info:" + msg_update_nfs_auth["detail_err_msg"])
    msg_get_nfs_auth_up = nas_common.get_nfs_export_auth_clients(export_ids=id_nfs)
    common.judge_rc(msg_get_nfs_auth_up["err_no"], 0, "get nfs info updated:" + msg_get_nfs_auth_up["detail_err_msg"])
    update_uid = msg_get_nfs_auth_up["result"]["nfs_export_auth_clients"][0]["anonuid"]
    update_gid = msg_get_nfs_auth_up["result"]["nfs_export_auth_clients"][0]["anongid"]
    # client check point
    log.info("4-1> 更新后执行touch和stat命令验证")
    (filename_new, uid_new, gid_new) = nfs_mount_stat(case_client_ip, date_ip, abs_path, "update")
    log.info("5> 清理环境，返回结果")
    ls_cmd = "ls %s" % mount_point
    (rc_ls, rc_std) = common.run_command(case_client_ip, ls_cmd, True, MAX_WAIT_MTIME)
    if rc_ls == 0:
        cmd_umount = "umount -f %s" % mount_point
        log.info("timeout=%s" % str(MAX_WAIT_MTIME))
        time_start = time.time()
        while True:
            time_t = time.time() - time_start
            if time_t > MAX_WAIT_MTIME:
                common.except_exit("umount too long time")
            (rc_umount, std_umount) = common.run_command(node_ip=case_client_ip, cmd=cmd_umount)
            log.info("std_umount is :%s " % std_umount)
            if rc_umount == 0 or 'not mounted' in std_umount:
                log.info("umount succeed")
                break
    prepare_clean.nas_test_clean()
    log.info("default (uid,gid):(%s,%s)\ndefault (uid,gid):(%s,%s) by ls -n cmd\n" % (fault_uid, fault_gid, uid_ft, gid_ft))
    log.info("new (uid,gid):(%s,%s)\nnew (uid,gid):(%s,%s) by stat cmd\n" % (update_uid, update_gid, uid_new, gid_new))
    if update_uid == test_value_uid and update_gid == test_value_gid:
        log.info("update is active:test value == update value")
    if uid_new == test_value_uid and gid_new == test_value_gid:
        log.info("stat check is pass:test value == uid_new")
    else:

        common.judge_rc(int(update_uid), int(test_value_uid), "uid failed:test-> %s,fault-> %s" % (test_value_uid, update_uid))
        common.judge_rc(int(update_gid), int(test_value_gid), "gid failed:test-> %s,fault-> %s" % (test_value_gid, update_gid))
        common.judge_rc(int(uid_new), int(test_value_uid), "uid failed:test-> %s,ls -n-> %s" % (test_value_uid, uid_new))
        common.judge_rc(int(gid_new), int(test_value_gid), "gid failed:test-> %s,ls -n-> %s" % (test_value_gid, gid_new))
    log.info("case succeed!")

    return


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    case()
    log.info('%s finished!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)