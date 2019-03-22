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
# Date: 2018-8-8
# @summary：
#        卸载独立的私有客户端，卡住了
# @steps:
#       1、跑vdbench占用卷
#       2、卸载客户端，判断是否卡在了卸载命令
#       3、安装客户端
#       4、等待直到df发现存储卷
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
VDBENCH_PATH = os.path.join(prepare_clean.DEFECT_PATH, FILE_NAME)           # /mnt/parastor/P300-2468
# /root/ofs3.0/client/uninstall.py  and  /root/ofs3.0/client/install.py --ips=%s
UNINSTALL_CLIENT_CMD = os.path.join(get_config.get_client_install_path(), "uninstall.py")
INSTALL_CLIENT_CMD = os.path.join(get_config.get_client_install_path(), "install.py"
                                  + " --ips=%s" % common.SYSTEM_IP)
TOOLS_RUN_VOLUME = os.path.basename(os.path.dirname(prepare_clean.DEFECT_PATH))
BLOCK_RC_VAL = 255  # 卡住的返回值在common中暂定为255


def un_or_install_client(clientip, cmd):
    """
    :author：               chenjy1
    :date:                  2018.08.08
    :param clientip:       要安装或卸载的client_IP
    :param uninstall_cmd:  安装卸载命令
    :return:
    """
    rc, stdout = common.run_command(clientip, 'pwd')
    common.judge_rc(rc, 0, 'ssh failed !!!  please check node!!! ')
    rc, stdout = common.run_command(clientip, cmd, timeout=180)
    exit(rc)  # 让主进程知道子进程的返回状态，在主进程中进行相应的处理


def case():
    log.info("case begin")

    client_ip_lst = get_config.get_allclient_ip()

    log.info("1> 跑vdbench占用卷")
    p1 = Process(target=tool_use.vdbench_run, args=(VDBENCH_PATH, VDBENCH_PATH, client_ip_lst[0],))
    p1.start()
    log.info("wait 30s")
    time.sleep(30)

    log.info("2> 卸载客户端")
    process_variable_name_list = []
    for i, client_ip in enumerate(client_ip_lst):
        process_variable_name = 'p' + str(i+2)  # 从p2开始
        process_variable_name_list.append(process_variable_name)
        locals()[process_variable_name] = Process(target=un_or_install_client, args=(client_ip, UNINSTALL_CLIENT_CMD, ))

    for i in range(len(process_variable_name_list)):
        locals()[process_variable_name_list[i]].start()

    p1.terminate()
    p1.join()

    """判断卸载返回值"""
    fail_client = []  # 卸载失败的客户端
    block_client = []  # 卸载卡住的客户端
    for i in range(len(process_variable_name_list)):
        locals()[process_variable_name_list[i]].join()
        if locals()[process_variable_name_list[i]].exitcode != 0:
            if locals()[process_variable_name_list[i]].exitcode != BLOCK_RC_VAL:  # 判断卸载卡住
                fail_client.append(i)
            else:
                block_client.append(i)

    """通过判断两个列表有没有内容来判断卸载过程有无异常"""
    if fail_client != [] or block_client != []:
        for i in fail_client:
            log.info('IP: %s uninsall client failed' % client_ip_lst[i])
        for i in block_client:
            log.info('IP: %s uninsall client block up' % client_ip_lst[i])
        common.except_exit(info='some client uninstall failed or block up')

    """看挂载目录是否已经掉了"""
    uninstall_client_list = []
    log.info("wait 20s")
    time.sleep(20)
    for i, ip in enumerate(client_ip_lst):
        res = common.check_client_state(ip, TOOLS_RUN_VOLUME)
        if res != -3:
            uninstall_client_list.append(ip)
    if uninstall_client_list != []:
        for ip in uninstall_client_list:
            common.except_exit('IP : %s volume still in df stdout'% ip)

    log.info("3> 安装客户端")
    process_variable_name_list = []

    for i, client_ip in enumerate(client_ip_lst):
        process_variable_name = 'p' + str(i + 2)
        process_variable_name_list.append(process_variable_name)
        locals()[process_variable_name] = Process(target=un_or_install_client, args=(client_ip, INSTALL_CLIENT_CMD,))

    for i in range(len(process_variable_name_list)):
        locals()[process_variable_name_list[i]].start()

    fail_client = []  # 失败的客户端
    block_client = []  # 卡住的客户端
    for i in range(len(process_variable_name_list)):
        locals()[process_variable_name_list[i]].join()
        if locals()[process_variable_name_list[i]].exitcode != 0:
            if locals()[process_variable_name_list[i]].exitcode != BLOCK_RC_VAL:
                fail_client.append(i)
            else:
                block_client.append(i)

    """通过判断两个列表有没有内容来判断卸载过程有无异常"""
    if fail_client != [] or block_client != []:
        for i in fail_client:
            log.info('IP: %s insall client failed' % client_ip_lst[i])
        for i in block_client:
            log.info('IP: %s insall client block up' % client_ip_lst[i])
        common.except_exit(info='some client install failed or block up')

    log.info("4> 等待集群所有节点df发现卷 %s"%TOOLS_RUN_VOLUME)
    flag_ip_volume = 1
    for i in range(len(client_ip_lst) - 1):
        flag_ip_volume = (flag_ip_volume << 1) + 1  # 111
    res_ip_volume = flag_ip_volume  # 111
    start_time = time.time()
    while True:
        for i, ip in enumerate(client_ip_lst):
            if (flag_ip_volume & (1 << i)) != 0:  # 仅看还未发现卷的节点
                res = common.check_client_state(ip, TOOLS_RUN_VOLUME)  # 使用判断客户端超时的函数
                if 0 == res:
                    flag_ip_volume &= (res_ip_volume ^ (1 << i))  # 将i对应的标志位置0
                elif -1 == res:
                    common.except_exit(info='ssh failed !!!  please check node!!!')
                elif -2 == res:
                    common.except_exit(info='client is blockup !!!')
                else:
                    log.info('still waiting %s' % ip)
        if flag_ip_volume & res_ip_volume == 0:  # 全0则通过
            break
        time.sleep(10)
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        log.info('not found volume exist %dh:%dm:%ds' % (h, m, s))
    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)