# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import json
import random

import utils_path
import common
import log
import get_config
import prepare_clean
import make_fault
import tool_use
import uninstall

####################################################################################
#
# author 刘俊鑫
# date 2019-1-23
# @summary：
#   客户端业务过程中所有数据网故障
# @steps:
#   step1: 客户端授权、安装、挂载
#   step2: 客户端业务跑起来
#   step3: 客户端间隔5分钟轮询断所有数据网
#   ps.需要将客户端安装包解压后放到配置文件中的client_install_path
#
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
PACKAGE_PATH = get_config.get_client_install_path()
CLIENT_IP = get_config.get_allclient_ip()
SERVER_IP = get_config.get_allparastor_ips()
VDBENCH_PATH = get_config.get_mount_paths()[0] + '/data'
VDBENCH_JN_PATH = get_config.get_mount_paths()[0] + '/jn'
# testlink case: 3.0-55152


def grab_client_global(client_ip):
    '''获取私有客户端数据网'''
    node_obj = common.Node()
    sys_node_id_lst = node_obj.get_nodes_id()
    eth_list, data_ip_list, ip_mask_lst = node_obj.get_node_eth(sys_node_id_lst[0])
    cmd = 'ssh %s ip addr | grep global | grep inet' % client_ip
    rc, stdout = common.run_command(client_ip, cmd)
    line_lst = stdout.splitlines()

    data_ips_part = []
    '''获取集群节点数据网IP的前两部分'''
    for ip in data_ip_list:
        ip_part_dist1 = ip.split('.')[0]
        ip_part_dist2 = ip.split('.')[1]
        ip_part = [ip_part_dist1, ip_part_dist2]
        ip_specific = '.'.join(ip_part)
        data_ips_part.append(ip_specific)

    eth_name_lst = []
    ip_mask_lst = []
    for line in line_lst:
        external_client_ip = line.split()[1].split('/')[0]
        eth_name = line.split()[-1]
        ip_mask = line.split()[1]
        ip_part_dist1 = external_client_ip.split('.')[0]
        ip_part_dist2 = external_client_ip.split('.')[1]
        ip_part = [ip_part_dist1, ip_part_dist2]
        client_ip_part = '.'.join(ip_part)
        if client_ip_part in data_ips_part:
            eth_name_lst.append(eth_name)
            ip_mask_lst.append(ip_mask)
    return eth_name_lst, ip_mask_lst


def down_net(node_ip, eth_name_lst, ip_mask_lst):

        make_fault.down_eth(node_ip, eth_name_lst)
        sleep_time = random.randint(1, 50)
        log.info('**************BEGIN DOWN NET**************')
        log.info('wait %ss for up %s' %(sleep_time, eth_name_lst))
        time.sleep(sleep_time)
        make_fault.up_eth(node_ip, eth_name_lst, ip_mask_lst)


def case():
    cmd = 'mkdir -p %s' % VDBENCH_PATH
    rc, stdout = common.run_command(SERVER_IP[0],cmd)
    common.judge_rc(rc, 0, '\t[command %s excuted faield, stdout=%s]' %(cmd, stdout))

    cmd = 'mkdir -p %s' % VDBENCH_JN_PATH
    rc, stdout = common.run_command(SERVER_IP[0], cmd)
    common.judge_rc(rc, 0, '\t[command %s excuted faield, stdout=%s]' % (cmd, stdout))

    '''客户端授权'''
    volume = common.Volume()
    volume_name = get_config.get_volume_names()
    volume_id = volume.get_volume_id(volume_name[0])
    rc, stdout = common.create_client_auth(CLIENT_IP[0], volume_id, auto_mount='true',
                                           atime='false', acl='false', user_xattr='true', sync='false')
    common.judge_rc(rc, 0, '\t[create_client_auth failed, stdout = %s]' % stdout)
    result = common.json_loads(stdout)
    client_auth_id = result['result']['ids'][0]

    '''客户端安装'''
    install_cmd = PACKAGE_PATH + '/install.py --ips=%s' % SERVER_IP[0]
    rc, stdout = common.run_command(CLIENT_IP[0], install_cmd)
    common.judge_rc(rc, 0, '\t[Install client failed, stdout=%s]' % stdout)

    ret_list = common.wait_df_find_volume([CLIENT_IP[0]], get_config.get_volume_names()[0], 1800, 1800)
    common.judge_rc(ret_list[0], 0, 'can not file volume in 600 seconds')

    vdbench = tool_use.Vdbenchrun(elapsed=300)
    vdbench.run_create(VDBENCH_PATH, VDBENCH_JN_PATH, CLIENT_IP[0])

    eth_name_lst, ip_mask_lst = grab_client_global(CLIENT_IP[0])
    p1 = Process(target=vdbench.run_check_write, args=(VDBENCH_PATH, VDBENCH_JN_PATH, CLIENT_IP[0]))
    p2 = Process(target=down_net, args=(CLIENT_IP[0], eth_name_lst, ip_mask_lst))
    p3 = Process(target=vdbench.run_check_write, args=(VDBENCH_PATH, VDBENCH_JN_PATH, CLIENT_IP[0]))
    p1.start()
    p1.join()
    p2.start()
    p2.join()
    if p2.exitcode != 0:
        common.except_exit('vdbench check_write failed before net fault')
    time.sleep(100)
    ret_list = common.wait_df_find_volume([CLIENT_IP[0]], get_config.get_volume_names()[0], 1800, 1800)
    common.judge_rc(ret_list[0], 0, 'can not file volume in 600 seconds')
    log.info('*********restart check_write after net fault*********')
    p3.start()
    p3.join()

    if p3.exitcode != 0:
        common.except_exit('vdbench check_write failed after net fault')


    rc, stdout = common.delete_client_auth(client_auth_id)
    common.judge_rc(rc, 0, 'delete client auth failed')


def case_clean():

    cmd = 'rm -rf %s/*' % get_config.get_mount_paths()[0]
    rc, stdout = common.run_command(SERVER_IP[0], cmd)
    common.judge_rc(rc, 0, 'rm failed')


def main():
    prepare_clean.test_prepare(FILE_NAME)
    uninstall.case()
    case()
    case_clean()
    prepare_clean.test_clean()


if __name__ == '__main__':
    common.case_main(main)