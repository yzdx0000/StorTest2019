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
author@liangxy
date: 2018-08-02
@summary：
     缺陷自动化：快照回滚命令超时
@steps:
    1、在卷目录下创建测试目录，在其中创建文件FILE_NAME
    2、创建快照
    3、重命名文件FILE_NAME
    4、执行revert命令，恢复快照（预期不成功）
@changelog：
    
"""
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)


def case():
    log.info("case begin")
    """随机节点"""
    ob_node = common.Node()
    case_ip_lst = get_config.get_allclient_ip()
    # ob_node.get_external_client_ips()
    case_ip = random.choice(case_ip_lst)

    """使用iozone创建1个文件"""
    test_file = os.path.join(SNAP_TRUE_PATH, "aaa")
    cmd = ("iozone -s 1m -i 0 -f %s -w" % test_file)
    rc, stdout = common.run_command(case_ip, cmd)
    if rc != 0:
        raise Exception(
                "Execute command: \"%s\" failed. \nstdout: %s " % (cmd, stdout))
    """创建快照"""
    name1 = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH + "/" + "aaa"
    rc, stdout = snap_common.create_snapshot(name1, path)
    if 0 != rc:
        raise Exception('create_snapshot %s failed!!!' % name1)
    """重命名原文件"""

    cmd_mv = ("mv %s %s" % (test_file, test_file+"_bak"))
    rc_mv, std_mv = common.run_command(case_ip, cmd_mv)
    if 0 != rc_mv:
        raise Exception("case file:mv failed")
    """快照回滚"""
    rc_revert, std_revert = snap_common.revert_snapshot_by_name(name1)
    if 0 == rc_revert:
        raise Exception("case file:revert should not succeed")
    log.info("case succeed")
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
