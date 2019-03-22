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
# Date: 2018-07-28
# @summary：
#    5节点集群跑vdbench，一段时间后没有读写了
# @steps:
#    1、开启子进程跑vdbench
#    2、检查客户端挂载情况
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
VDBENCH_PATH = os.path.join(prepare_clean.DEFECT_PATH, FILE_NAME, "vdbench")


def case():
    log.info("case begin")

    client_ip_lst = get_config.get_allclient_ip()

    log.info("1> 开启子进程跑vdbench")
    p1 = Process(target=tool_use.vdbench_run, args=(VDBENCH_PATH, client_ip_lst[0], client_ip_lst[1]),
                 kwargs={'run_create': True, 'run_check_write': True})
    p1.start()

    log.info('wait 30s')
    time.sleep(30)

    '''获取跑vdbench的目录所在卷名'''
    tools_run_volume = os.path.basename(os.path.dirname(prepare_clean.DEFECT_PATH))

    '''循环：1.判断所有独立客户端节点是否卡住或者掉了，2.判断进程是否跑完了'''
    '''如1出现，则脚本失败，如2出现，则往下走。'''
    log.info(" 2> 检查客户端挂载情况")
    while True:
        res = common.check_client_state_by_list(get_config.get_allclient_ip(), tools_run_volume, timeout=300)
        if -1 == res:
            raise Exception('ssh failed !!!  please check node!!!')
        elif -2 == res:
            p1.terminate()
            p1.join()
            raise Exception('client is blockup !!!')
        elif -3 == res:
            p1.terminate()
            p1.join()
            raise Exception('not found volume !!!')
        if False == p1.is_alive():
            break

    p1.join()

    '''进行检查'''
    if p1.exitcode != 0:
        raise Exception("vdbench is failed!!!!!!")

    return

def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)
