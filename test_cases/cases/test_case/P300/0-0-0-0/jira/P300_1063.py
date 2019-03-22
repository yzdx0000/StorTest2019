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
date 2018-08-23
@summary：
     缺陷自动化——导出nfs后，在集群节点使用rm命令可删除导出目录（预期防御rm，不可删除）
@steps:
    1、创建访问分区
    2、导出nfs
    3、授权nfs客户端
    4、在集群节点上使用rm删除目录（预期不可删除）
    5、清理环境，返回结果
@changelog：todo_
           disable nas 后最少需要6分钟（经验值）才可完全生效
"""
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
MAX_WAIT_TIME = 1801


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


def case():
    log.info("case begin")
    ob_node = common.Node()
    case_node_id = random.choice(ob_node.get_nodes_id())
    case_ip = ob_node.get_node_ip_by_id(case_node_id)
    case_client_ip = random.choice(ob_node.get_client_ips())
    log.info("1> 创建访问分区")
    msg_get_az = nas_common.get_access_zones(None)
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
    log.info("3> 授权nfs客户端")
    msg_add_nfs_auth = nas_common.add_nfs_export_auth_clients(export_id=id_nfs, name=case_client_ip,
                                                              permission_level="rw")
    common.judge_rc(msg_add_nfs_auth["err_no"], 0, "add nfs auth info:" + msg_add_nfs_auth["detail_err_msg"])
    msg_get_nfs_auth = nas_common.get_nfs_export_auth_clients(export_ids=id_nfs)
    common.judge_rc(msg_get_nfs_auth["err_no"], 0, "get nfs info:" + msg_get_nfs_auth["detail_err_msg"])

    abs_path = nas_common.NAS_PATH + "/" + FILE_NAME + "_nfs"
    (rc_rm, std_rm) = common.rm_exe(case_ip, abs_path)
    log.info("5> 清理环境，返回结果")
    prepare_clean.nas_test_clean()
    log.info("should not exec pass, rm std:" + std_rm + "rc:" + str(rc_rm))
    common.judge_rc_unequal(rc_rm, 0, " ")
    log.info('case ok!')
    return


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    case()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
