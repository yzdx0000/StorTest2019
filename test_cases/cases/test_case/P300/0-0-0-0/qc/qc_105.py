# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time

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
#    3节点物理机，4k mdtest和iozone，出现oPara的core
# @steps:
#    1、同时进行：1、iozone  2、mdtest
#    2、进行检查
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 #本脚本名字
MDTEST_PATH = os.path.join(prepare_clean.DEFECT_PATH, FILE_NAME,"mdtest")
IOZONE_PATH = os.path.join(prepare_clean.DEFECT_PATH, FILE_NAME,"iozone")
MACHINES_PATH = '/tmp/machines'


def mdtest_large_data(exe_ip):
    """
    :author :             chenjy1
    :date:                2018.07.30
    :description:         运行mdtest
    :param exe_ip:       执行命令的ip
    :return:
    """
    cmd = 'mpirun -hostfile %s -np 20 -allow-run-as-root mdtest -z 2 -b 3 -I 10 -C -i 1 -w 4096 -d %s' % (MACHINES_PATH, MDTEST_PATH)
    #cmd = 'mpirun -hostfile %s -np 20 -allow-run-as-root mdtest -z 5 -b 5 -I 10 -C -i 10 -w 4096 -d %s'% (MACHINES_PATH, MDTEST_PATH)
    rc, stdout = common.run_command(exe_ip, cmd)
    common.judge_rc(rc, 0, "mdtest execution is failed!!!!!!")
    return


def case():
    log.info("case begin")

    client_ip_lst = get_config.get_allclient_ip()

    """准备mdtest的配置文件"""
    common.rm_exe(client_ip_lst[0], MACHINES_PATH)
    cmd = 'echo "%s slots=10\n%s slots=10" > %s' % (client_ip_lst[0], client_ip_lst[1], MACHINES_PATH)
    rc, stdout = common.run_command(client_ip_lst[0], cmd)
    common.judge_rc(rc, 0, 'mdtest configure file failed !!!')

    """准备iozone的路径"""
    cmd = "mkdir %s" % IOZONE_PATH
    rc, stdout = common.run_command(client_ip_lst[0], cmd)
    common.judge_rc(rc, 0, 'iozone path failed !!!')

    log.info("1> 同时进行：1、iozone  2、mdtest")
    p1 = Process(target=tool_use.iozone_run, args=(2, 2, IOZONE_PATH, 2, '10m', '64k',))
    #p1 = Process(target=tool_use.iozone_run, args=(3, 4, IOZONE_PATH, 12, '10G', '4M',))
    p2 = Process(target=mdtest_large_data, args=(client_ip_lst[0],))

    p1.start()
    p2.start()

    log.info('wait 30s')
    time.sleep(30)

    p1.join()
    p2.join()

    log.info("2> 进行检查")
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
