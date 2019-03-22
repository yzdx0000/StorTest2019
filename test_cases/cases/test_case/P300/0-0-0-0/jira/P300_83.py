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
date: 2018-08-07
@summary：
     缺陷自动化——快照回滚开始时间错误
@steps:
    1、在卷目录下创建测试目录，在其中创建文件FILE_NAME
    2、创建快照
    3、重命名文件FILE_NAME
    4、执行revert命令，恢复快照，ssh在同一客户端节点上记录执行revert操作的时间开始结束点
    5、pscli命令查看回滚时间
    6、若落在开始结束点构成的区间，返回成功，否则失败；清理环境
@changelog：
    
"""
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)


def case():
    log.info("case begin")
    """随机客户端节点"""
    ob_node = common.Node()
    case_ip_lst = ob_node.get_nodes_ip()
    case_ip = random.choice(case_ip_lst)

    """使用iozone创建1个文件"""
    test_file = os.path.join(SNAP_TRUE_PATH, "aaa")
    cmd = ("iozone -s 1m -i 0 -f %s -w" % test_file)
    rc, stdout = common.run_command(case_ip, cmd)
    err_str = "Execute command: \"%s\". \nstdout: %s " % (cmd, stdout)
    common.judge_rc(rc, 0, err_str)
    """创建快照"""
    name1 = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(name1, path)
    err_str = "create_snapshot %s" % (name1, )
    common.judge_rc(rc, 0, err_str)
    """快照回滚"""
    cmd_lt = "date +%s"
    # todo 拿集群点时间
    rc_lt, stdout_lt = common.run_command(case_ip, cmd_lt)
    err_str = "get time by shell,id {}!!!".format(case_ip)
    common.judge_rc(rc_lt, 0, err_str)
    time_space_left = int(stdout_lt)

    rc_revert, std_revert = snap_common.revert_snapshot_by_name(name1)
    cmd_rt = "date +%s"
    rc_rt, stdout_rt = common.run_command(case_ip, cmd_rt)
    err_str = "get time by shell,id {}!!!".format(case_ip)
    common.judge_rc(rc_lt, 0, err_str)
    time_space_right = int(stdout_rt)
    err_str = "revert:snap name %s!!!" % (name1, )
    common.judge_rc(rc_revert, 0, err_str)
    """获取回滚时间"""
    rc_get, msg_get_snap = snap_common.get_revert_snapshot()
    time_get_revert = msg_get_snap["result"]["revertSnapshots"][0]["revert_start_time"]
    err_str = "get revert time:snap name {},time {}".format(name1, time_get_revert)
    common.judge_rc(rc_get, 0, err_str)

    if time_get_revert >= time_space_left or time_get_revert <= time_space_right:
        info = ("case succeed!!!pscli = %d in [%d,%d]" % (time_get_revert, time_space_left, time_space_right))
        case_flag = 0
    else:
        info = ("case:pscli = %d ,range[%d,%d]" % (time_get_revert, time_space_left, time_space_right))
        case_flag = -2
    common.judge_rc(case_flag, 0, info)
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
