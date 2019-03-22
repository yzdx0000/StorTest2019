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
date 2018-08-20
@summary：
     缺陷自动化--kill oCnas进程后系统没有自动拉起
@steps:
    1、创建访问区
    2、disable nas，enable nas
    3、kill oCnas进程
    4、在限制的时间内get nodes 检查nas服务状态是否启动
    5、输出结果，清理环境
@changelog：
    todo enable nas 超时bug
    最后修改时间：
    修改内容：2018-12-17在步骤三和步骤四之间加了一个延时（liyi）
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


def get_pid_and_time(case_ip):
    '''
    Author:LiangXiaoyu
    date:2018-08-20
    description：在指定ip上获取oCnas的pid和oCnas进程开始时间
    :param case_ip(str):执行命令的ip
    :return: oCnas的pid和oCnas进程开始时间
    '''
    cmd_pidof = "pidof oCnas"
    (rc_p, std_p) = common.run_command(case_ip, cmd_pidof)
    std_p = std_p.strip()
    get_pid_info = "pidof with rc:%s, result:%s" % (rc_p, std_p)
    common.judge_rc(rc_p, 0, get_pid_info)
    cmd_lstart = "ps -o lstart %s | awk \'{ print $4 }\' | sed 1d" % std_p
    (rc_start_time, std_start) = common.run_command(case_ip, cmd_lstart)
    std_start = std_start.strip()
    info_lstart = "get start time of the process with rc:%s,start:time:%s" % (rc_start_time, std_start)
    common.judge_rc(rc_start_time, 0, info_lstart)
    return int(std_p), std_start


def case():
    log.info("case begin")
    ob_node = common.Node()
    case_node_id = random.choice(ob_node.get_nodes_id())
    case_ip = ob_node.get_node_ip_by_id(case_node_id)
    rst_enable_nas = 1
    change_nas_time = 10
    node_ids = nas_common.get_node_ids()
    log.info(">1 添加访问分区")
    msg_add_az = nas_common.create_access_zone(node_ids, FILE_NAME+"az")
    az_id = msg_add_az["result"]
    add_az_result = msg_add_az["detail_err_msg"]
    # msg_get_az["result"]["access_zones"][0]["id"]
    common.judge_rc(msg_add_az["err_no"], 0, ("add access_zone %s" % add_az_result))

    log.info(">2 确定nas状态,disable-enable nas 10次，保证以enable状态退出")
    for i in range(0, change_nas_time):
        nas_state_change(case_ip, False)
        nas_state_change(case_ip, True)

    rc_check_before = nas_common.check_nas_status(MAX_WAIT_TIME, case_node_id)

    log.info(">3 查询oCnas进程号，kill oCnas，再次pidof拿到新的oCnas进程号应不同")
    (std_pid_killing, std_start_before_kill) = get_pid_and_time(case_ip)
    log.info("std_pid_killing:%s,time:%s" % (std_pid_killing, std_start_before_kill))
    cmd_kill = "kill -9 %s" % std_pid_killing
    (rc_kill, std_kill) = common.run_command(case_ip, cmd_kill)
    info_kill = "result of kill oCnas on node_%s:%s" % (case_node_id, rc_kill)
    common.judge_rc(rc_kill, 0, info_kill)
    time.sleep(20)
    (std_pid_killed, std_start_after_kill) = get_pid_and_time(case_ip)
    log.info("std_pid_killed:%s,time:%s" % (std_pid_killed, std_start_after_kill))
    time.sleep(20)
    log.info(">4 通过get_nodes查询nas状态")
    rst_enable_nas = nas_common.check_nas_status(MAX_WAIT_TIME, case_node_id)
    if std_pid_killed == "":
        rst_enable_nas = -1
    if std_start_after_kill == std_start_before_kill:
        rst_enable_nas = -2
    log.info(">5 输出测试结果，清理环境")
    rst_info_before = "restult of nas service check(before kill):%s" % rc_check_bef ore
    common.judge_rc(rc_check_before, 0, rst_info_before)
    prepare_clean.nas_test_clean()
    rst_info = "restult of kill oCnas pid(based on nas service check):%s" % rst_enable_nas
    common.judge_rc(rst_enable_nas, 0, rst_info)
    return


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    case()
    prepare_clean.nas_test_clean()
    log.info("%s succeed!" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
