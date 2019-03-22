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
date 2018-09-04
@summary：
    基本功能list——私有客户端目录扩展属性各字段的增、查、删
@steps:
    1、用户信息获取与检查
    2、扩展属性设置
    3、检查报错信息，清理环境，返回结果
@changelog：
    最后修改时间：
    修改内容：
"""

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
wait_time_th = 5


def setfattr_with_ns(exe_ip, namespace, target):
    """

    :param exe_ip: (str)执行的ip
    :param namespace: (str)命名空间
    :param target: (str)包含路径的设置对象
    :return：
    """
    tim = time.time().__str__()
    value = tim.split(".")[0]
    name = namespace + "." + value
    cmd_set = "setfattr -n %s -v %s %s" % (name, value, target)
    (rc, std) = common.run_command(exe_ip, cmd_set)

    return rc, std, value


def case():
    log.info("case begin")
    ob_node = common.Node()
    case_ip_lst = ob_node.get_nodes_ip()
    case_node_id_lst = ob_node.get_nodes_id()
    client_ip_lst = get_config.get_allclient_ip()
    
    log.info(">1 随机选择执行节点（独立客户端设置，集群节点查看）")
    case_id = random.choice(case_node_id_lst)
    case_ip = ob_node.get_node_ip_by_id(case_id)
    client_ip = random.choice(client_ip_lst)
    xattr_stat = common.get_param_current("oApp", "xattr_enable")
    update_times = 0
    while 1 != int(xattr_stat):
        common.update_param("oApp", "xattr_enable", "1")
        xattr_stat = common.get_param_current("oApp", "xattr_enable")
        update_times += 1
        if 3 < update_times:
            log_info = ("update xattr_enable %d time, with %s,exit" % (update_times, xattr_stat))
            common.except_exit(log_info, 2)

    log.info(">2 扩展属性设置(node:%s;client:%s)" % (case_ip, client_ip))
    # security， trusted， user
    ns_list = ["security", "trusted", "user"]
    path_top = os.path.join(prepare_clean.DEFECT_PATH, FILE_NAME)
    complite_path = path_top

    for ns in ns_list:
        (rc_set, std_set, value) = setfattr_with_ns(client_ip, ns, complite_path)
        log.info("path and name is:%s" % complite_path)
        common.judge_rc(rc_set, 0, "setfattr :" + std_set)
        name_s = ns + '.' + value
        gt = name_s + "=" + "\"" + value + "\""
        wait_info = "wait %f s(%d ms)" % (wait_time_th, wait_time_th*1000)
        log.info(wait_info)
        time.sleep(wait_time_th)
        cmd_getfattr = "getfattr -n %s %s" % (name_s, complite_path)
        (rc_get, std_get) = common.run_command(case_ip, cmd_getfattr)
        common.judge_rc(rc_get, 0, "getfattr:" + std_get)
        # std_get.split('\n')[1]这个1是有风险的，需要添加一个、删除一个，如果失败就不是1了，所以一直在检查异常
        if '' == std_get:
            common.except_exit("command get fattr is passed,but fattr should be %s,not Empty" % gt)
        if gt != std_get.split('\n')[1]:
            common.except_exit("gt and getattr is: %s != %s" % (gt, std_get.split('\n')[1]))

        log.info("Will delete attr")
        log.info("Execute get command(after delete):should failed")
        cmd_deleattr = "setfattr -x %s %s" % (name_s, complite_path)
        (rc_dele, std_dele) = common.run_command(client_ip, cmd_deleattr)
        common.judge_rc(rc_dele, 0, "dele fattr:" + std_dele)

        (null_get, std_get_d) = common.run_command(case_ip, cmd_getfattr)
        common.judge_rc_unequal(null_get, 0, "getfattr after dele:" + std_get_d)

        if 'No such attribute' not in std_get_d:
            common.except_exit("command delete fattr is passed,but fattr should be empty,not %s" % std_get_d)

    log.info("case succeed!")
    log.info(">3 检查报错信息，清理环境")
    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed!" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
