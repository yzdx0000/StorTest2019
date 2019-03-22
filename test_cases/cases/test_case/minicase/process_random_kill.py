# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import common
import log
import tool_use
import make_fault
import get_config
import prepare_clean

#################################################################
#
# Author: baorb
# date 2017-08-21
# @summary：
#    本测试主要测试随机kill进程测试。
# @steps:
#    1，运行vdbench进行数据创建和校验
#    2，同时并行每隔2分钟kill同一个节点的进程
#
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                # 本脚本名字
MINI_TRUE_PATH = os.path.join(prepare_clean.MINICASE_PATH, FILE_NAME)      # /mnt/volume1/mini_case/3_0015_truncate_test

session_list = ['oJmgs', 'oMgcd', 'oPara', 'oStor', 'oJob', 'oRole', 'zk']


def kill_process(node_ip, pro_lst):
    """
    进行kill 进程故障
    :param node_ip:
    :return:
    """
    time.sleep(10)
    while True:
        '''随机选取进程'''
        ran_num = random.randint(1, len(pro_lst))
        tem_session_lst = random.sample(pro_lst, ran_num)
        for session in tem_session_lst:
            make_fault.kill_process(node_ip, session)
        time.sleep(120)


def case():
    log.info("----------case----------")
    '''随机获取集群内的一个节点，对其进行故障'''
    ob_node = common.Node()
    node_ip_list = ob_node.get_nodes_ip()
    node_ip = random.choice(node_ip_list)
    node_id = ob_node.get_node_id_by_ip(node_ip)
    rc, service_lst = ob_node.get_node_all_services(node_id=node_id)
    pro_lst = list(set(service_lst).intersection(set(session_list)))
    client_ip_lst = get_config.get_allclient_ip()

    p1 = Process(target=tool_use.vdbench_run, args=(MINI_TRUE_PATH, client_ip_lst[0], client_ip_lst[1]),
                 kwargs={'run_create': True, 'run_check_write': True})
    p2 = Process(target=kill_process, args=(node_ip, pro_lst))

    p1.start()
    p2.start()

    p1.join()
    p2.terminate()
    p2.join()

    common.judge_rc(p1.exitcode, 0, 'vdbench_run')

    '''不断检查坏对象是否修复'''
    count = 0
    log.info("wait 60 seconds")
    time.sleep(60)
    while True:
        count += 1
        log.info("the %d times check badjobnr" % count)
        log.info("wait 10 seconds")
        time.sleep(10)
        if common.check_badjobnr():
            break

    '''再跑检查数据的正确性'''
    tool_use.vdbench_run(MINI_TRUE_PATH, client_ip_lst[0], client_ip_lst[1], run_check=True)

    """不断检查进程是否起来"""
    while True:
        log.info("wait 60 s")
        time.sleep(60)
        for process in pro_lst:
            if not make_fault.check_process(node_ip, process):
                log.info('node %s process %s is not normal!!!' % (node_ip, process))
                break
        else:
            break

    '''检查系统'''
    common.ckeck_system()
    log.info("case succeed!")


def main():
    prepare_clean.minicase_test_prepare(FILE_NAME)
    case()
    prepare_clean.minicase_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)
    return


if __name__ == '__main__':
    common.case_main(main)