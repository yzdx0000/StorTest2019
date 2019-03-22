# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import common
import log
import shell
import get_config
import prepare_clean
import tool_use
import commands
#################################################################
#
# Author: chenjy1
# Date: 2018-07-14
# @summary：
#        3节点物理机，跑空文件mdtest，一个节点上出现oStor的core
# @steps:
#        1、3节点物理机，跑空文件mdtest
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
IOZONE_FILE_PATH = os.path.join(prepare_clean.DEFECT_PATH, FILE_NAME)
MACHINES_PATH = '/tmp/machines'


def mdtest_large_data(exe_ip):
    """
    :author :             chenjy1
    :date:                2018.07.30
    :description:         运行mdtest
    :param exe_ip:       执行命令的ip
    :return:
    """
    cmd = 'mpirun -hostfile %s -np 20 -allow-run-as-root mdtest -z 2 -b 3 -I 10 -C -i 1 -d %s' % (MACHINES_PATH, IOZONE_FILE_PATH)
    # cmd = 'mpirun -hostfile %s -np 20 -allow-run-as-root mdtest -z 5 -b 5 -I 10 -C -i 10 -d %s'% (MACHINES_PATH, IOZONE_FILE_PATH)
    rc, stdout = common.run_command(exe_ip, cmd)
    common.judge_rc(rc, 0, "mdtest execution is failed!!!!!!")

    return


def case():
    log.info("case begin")
    client_ip_lst = get_config.get_allclient_ip()
    common.rm_exe(client_ip_lst[0],MACHINES_PATH)
    cmd = 'echo "%s slots=10\n%s slots=10" > %s' % (client_ip_lst[0], client_ip_lst[1], MACHINES_PATH)
    common.run_command(client_ip_lst[0], cmd)
    log.info("1> 3节点物理机，跑空文件mdtest")
    mdtest_large_data(client_ip_lst[0])

    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)