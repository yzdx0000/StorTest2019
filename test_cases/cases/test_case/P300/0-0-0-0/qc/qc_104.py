# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import subprocess

import utils_path
import common
import snap_common
import log
import shell
import get_config
import prepare_clean
import tool_use


####################################################################################
#
# Author: chenjy1
# Date: 2018-07-12
# @summary：
#    3节点物理机跑4k mdtest和iozone，一段时间后无法读写
# @steps:
#    1、同时进行：1、iozone  2、mdtest
#    2、检查客户端挂载情况
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
MDTEST_PATH = os.path.join(prepare_clean.DEFECT_PATH, FILE_NAME, "mdtest")
IOZONE_PATH = os.path.join(prepare_clean.DEFECT_PATH, FILE_NAME, "iozone")
MACHINES_PATH = '/tmp/machines'


def mdtest_large_data(exe_ip):
    cmd = 'mpirun -hostfile %s -np 20 -allow-run-as-root mdtest -z 2 -b 3 -I 10 -i 1 -w 4096 -d %s'% (MACHINES_PATH, MDTEST_PATH)
    rc, stdout = common.run_command(exe_ip, cmd)
    if rc != 0:
        raise Exception("mdtest execution is failed!!!!!!")
    return


def case():
    log.info("case begin")

    client_ip_lst = get_config.get_allclient_ip()

    """准备mdtest的配置文件"""
    common.rm_exe(client_ip_lst[0], MACHINES_PATH)
    cmd = 'echo "%s slots=10\n%s slots=10" > %s' % (client_ip_lst[0], client_ip_lst[1], MACHINES_PATH)
    rc, stdout = common.run_command(client_ip_lst[0], cmd)
    if rc != 0:
        raise Exception('mdtest configure file failed !!!')

    """准备iozone的路径"""
    cmd = "mkdir %s" % IOZONE_PATH
    rc, stdout = common.run_command(client_ip_lst[0], cmd)
    if rc != 0:
        raise Exception('iozone path failed !!!')

    log.info("1> 同时进行：1、iozone  2、mdtest")
    p1 = Process(target=tool_use.iozone_run, args=(3, 4, IOZONE_PATH, 12, '10M', '1M',))
    p2 = Process(target=mdtest_large_data, args=(client_ip_lst[0],))
    p1.daemon = True
    p2.daemon = True
    p1.start()
    p2.start()

    log.info('wait 30s')
    time.sleep(30)

    tools_run_volume = os.path.basename(os.path.dirname(prepare_clean.DEFECT_PATH))

    '''循环：1.判断所有独立客户端节点是否卡住或者掉了，2.判断俩进程是否全跑完了'''
    '''如1出现，则脚本失败，如2出现，则往下走。'''
    log.info("2> 检查客户端挂载情况")
    while True:
        res = common.check_client_state_by_list(get_config.get_allclient_ip(), tools_run_volume, timeout=300)
        if -1 == res:
            raise Exception('ssh failed !!!  please check node!!!')
        elif -2 == res:
            p2.terminate()
            p1.terminate()
            p1.join()
            p2.join()
            raise Exception('client is blockup !!!')
        elif -3 == res:
            p2.terminate()
            p1.terminate()
            p1.join()
            p2.join()
            raise Exception('not found volume !!!')
        if False == p1.is_alive() and False == p2.is_alive():
            break

    p1.join()
    p2.join()

    "检查"
    if p1.exitcode != 0:
        raise Exception("iozone is failed!!!!!!")

    if p2.exitcode != 0:
        raise Exception("mdtest is failed!!!!!!")

    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)
