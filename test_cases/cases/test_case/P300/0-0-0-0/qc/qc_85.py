# -*-coding:utf-8 -*
import os
import time
import random

import utils_path
import common
import log
import tool_use
import get_config
import prepare_clean
import shell

#################################################################
#
# Author: chenjy1
# Date: 2017-07-24
# @summary：
#    虚拟机，6节点集群，4个客户端，运行vdbench脚本创建文件后，umount客户端，4个客户端，有两个出现crash
# @steps:
#    1.vdbench读写
#    2.vdbench完成后，获取所有客户端，并umount
#    3.检查是否恢复挂载（本脚本测试的环境在部署时已经选择了自动挂载了）
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
VDBENCH_PATH = os.path.join(prepare_clean.DEFECT_PATH, FILE_NAME)


def vdbench_run(anchor_path, journal_path, *args):
    """
    :author :             chenjy1
    :date:                2018.07.30
    :description:         跑vdbench
    :param anchor_path:  vdbench anchor目录
    :param journal_path: journal目录
    :param args:         跑vdbench节点IP
    :return:
    """
    vdb = tool_use.Vdbenchrun(elapsed=30)

    rc = vdb.run_create(VDBENCH_PATH, VDBENCH_PATH, *args)
    common.judge_rc(rc, 0, "vdbench run_create failed!!!!!!")

    rc = vdb.run_check_write(anchor_path, journal_path, *args)
    common.judge_rc(rc, 0, "vdbench run_check_write failed!!!!!!")
    return


def case():
    log.info("case begin")
    """获取客户端节点"""
    client_ip_list = get_config.get_allclient_ip()
    log.info("1> vdbench读写")
    vdbench_run(VDBENCH_PATH, VDBENCH_PATH, client_ip_list[0])

    time.sleep(10)

    log.info("2> vdbench完成后，获取所有客户端，并umount")
    """获取所有挂载目录"""
    mnt_path_list = get_config.get_mount_paths()

    log.info('type')
    log.info(mnt_path_list[0])
    log.info(type(mnt_path_list[0]))

    client_ip = client_ip_list[0]
    log.info(client_ip)
    log.info(type(client_ip))

    """umount"""
    for client_ip in client_ip_list:
        for i in range(len(mnt_path_list)):
            cmd = "umount %s -f" % mnt_path_list[i]
            #log.info("umount %s  %s") % (client_ip, mnt_path_list[i])
            rc, stdout, stderr = shell.ssh(client_ip, cmd)
            if 0 != rc:
                raise Exception(
                    "IP : %s execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (client_ip,cmd, stdout, stderr))
    log.info('wait ')
    time.sleep(10)

    log.info("3> 检查是否恢复挂载（本脚本测试的环境在部署时已经选择了自动挂载了）")
    ret_lst = common.wait_df_find_volume(client_ip_list, get_config.get_one_volume_name(), 300, 1800)
    log.info(client_ip_list)
    log.info(ret_lst)
    flag_get_volume_ok = True
    for i, val in enumerate(ret_lst):
        if val == 0:
            log.info('IP : %s can find volume %s' % (client_ip_list[i], FILE_NAME))
        if val == -1:
            flag_get_volume_ok = False
            log.info('IP : %s ssh failed' % (client_ip_list[i]))
        if val == -2:
            flag_get_volume_ok = False
            log.info('IP :%s df block up' % (client_ip_list[i]))
        if val == -3:
            flag_get_volume_ok = False
            log.info('IP : %s can not find volume %s after wait %d s' % (client_ip_list[i], FILE_NAME, 1800))
    if flag_get_volume_ok == False:
        common.except_exit("some node get volume failed")

    log.info("case succeed!")
    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)
