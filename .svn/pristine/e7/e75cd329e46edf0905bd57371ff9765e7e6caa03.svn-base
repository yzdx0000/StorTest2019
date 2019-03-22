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
date: 2018-08-09
@summary：
     缺陷自动化——set_export_dir设置目录为导出目录后，仍可进行rename操作（预期不可rename）
@steps:
    1、在卷目录下创建测试目录，在其中创建文件FILE_NAME
    2、使用parastor工具set_export_dir设置目录export属性为1
    3、重命名目录
    4、判断结果，预期无法重命名
    5、清理环境
@changelog：
    
"""
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
FILE_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)    # /mnt/volume1/snap/P300_1889
CREATE_FILE_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)     # snap/P300_1889
SYSTOOLS_PATH = "/home/parastor/tools/set_dir_export"
"""目前只有一个脚本调用且不会变化"""


def case():
    log.info("case begin")
    """随机确定集群节点"""
    log.info(">1 随机选择一个集群节点执行测试")
    ob_node = common.Node()
    case_id_lst = ob_node.get_nodes_id()
    case_id = random.choice(case_id_lst)
    case_ip = ob_node.get_node_ip_by_id(node_id=case_id)
    """使用iozone创建1个文件"""
    log.info(">2 在目标目录下创建1M文件")
    test_file = os.path.join(FILE_TRUE_PATH, "aaa")
    cmd = ("iozone -s 1m -i 0 -f %s -w" % test_file)
    rc, stdout = common.run_command(case_ip, cmd)
    err_str = "iozone create file"
    common.judge_rc(rc, 0, err_str)
    """工具修改为导出目录"""
    log.info(">3 使用set_export_dir工具修改为导出目录")
    cmd_set = "%s -d %s -s 1" % (SYSTOOLS_PATH, FILE_TRUE_PATH)
    rc, stdout = common.run_command(case_ip, cmd_set)
    err_str = "set %s export path" % FILE_TRUE_PATH
    common.judge_rc(rc, 0, err_str)
    """mv目标路径"""
    log.info("mv 目标路径")
    cmd_mv = "mv -f %s %s" % (FILE_TRUE_PATH, FILE_TRUE_PATH + "_bak")
    rc_mv, std_mv = common.run_command(case_ip, cmd_mv)
    """预期失败，检查结果并返回，环境清理可由主函数中的snap_test_clean完成"""
    info = ("set %s export path,move it:" % FILE_TRUE_PATH)
    common.judge_rc_unequal(rc_mv, 0, info)
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
