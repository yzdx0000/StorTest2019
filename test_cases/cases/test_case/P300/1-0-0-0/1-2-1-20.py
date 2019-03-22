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
# date 2019-1-24
# @summary：
#   单客户端性能测试（单流带宽，聚合带宽，聚合iops）
# @steps:
#   step1: 客户端授权、安装、挂载
#   step2: 性能测试

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
PROPERTY_TRUE_PATH = os.path.join(prepare_clean.PROPERTY_PATH, FILE_NAME)
File_Size = '500G'
# testlink case: 3.0-55153


def single_bw():
    cmd = 'mkdir -p %s' % PROPERTY_TRUE_PATH
    common.run_command(CLIENT_IP[0], cmd)
    log.info("清除缓存")
    obj_node = common.Node()
    parastor_node_lst = obj_node.get_nodes_ip()
    client_node_lst = get_config.get_allclient_ip()
    all_node_lst = parastor_node_lst + client_node_lst
    cmd = "echo 3 > /proc/sys/vm/drop_caches"
    for node_ip in all_node_lst:
        common.run_command(node_ip, cmd)

    log.info("获取大文件单流写的性能")
    client_ip = get_config.get_client_ip()
    write_cmd = "iozone -t 1 -s %s -r 4m -i 0 -+n -w -F %s" % (File_Size, os.path.join(PROPERTY_TRUE_PATH, 'iozone.0'))
    rc, stdout = common.run_command(client_ip, write_cmd)
    line_lst = stdout.splitlines()
    preperty_write = ''
    for line in line_lst:
        if 'Avg throughput per process' in line:
            preperty_write = line.split('=')[-1]
            break

    log.info("清除缓存")
    obj_node = common.Node()
    parastor_node_lst = obj_node.get_nodes_ip()
    client_node_lst = get_config.get_allclient_ip()
    all_node_lst = parastor_node_lst + client_node_lst
    cmd = "echo 3 > /proc/sys/vm/drop_caches"
    for node_ip in all_node_lst:
        common.run_command(node_ip, cmd)

    log.info("获取大文件单流读的性能")
    read_cmd = "iozone -t 1 -s %s -r 4m -i 1 -+n -F %s" % (File_Size, os.path.join(PROPERTY_TRUE_PATH, 'iozone.0'))
    rc, stdout = common.run_command(client_ip, read_cmd)
    line_lst = stdout.splitlines()
    preperty_read = ''
    for line in line_lst:
        if 'Avg throughput per process' in line:
            preperty_read = line.split('=')[-1]
            break

    log.info("***********************************************")
    log.info("大文件单流写平均性能是: %s" % preperty_write)
    log.info("大文件单流读平均性能是: %s" % preperty_read)
    log.info("***********************************************")
    cmd = 'rm -rf %s' % PROPERTY_TRUE_PATH
    common.run_command(CLIENT_IP[0], cmd)

    return preperty_write, preperty_read


def multi_bw():
    cmd = 'mkdir -p %s' % PROPERTY_TRUE_PATH
    common.run_command(CLIENT_IP[0], cmd)
    log.info("清除缓存")
    obj_node = common.Node()
    parastor_node_lst = obj_node.get_nodes_ip()
    client_node_lst = get_config.get_allclient_ip()
    all_node_lst = parastor_node_lst + client_node_lst
    cmd = "echo 3 > /proc/sys/vm/drop_caches"
    for node_ip in all_node_lst:
        common.run_command(node_ip, cmd)

    log.info("获取大文件聚合写的性能")
    client_ip = get_config.get_client_ip()
    write_cmd = "iozone -t 20 -s %s -r 4m -i 0 -+n -w -F %s" % (File_Size, os.path.join(PROPERTY_TRUE_PATH, 'iozone.0'))
    rc, stdout = common.run_command(client_ip, write_cmd)
    line_lst = stdout.splitlines()
    preperty_write = ''
    for line in line_lst:
        if 'Children see throughput for 10 initial writers' in line:
            preperty_write = line.split('=')[-1]
            break

    log.info("清除缓存")
    obj_node = common.Node()
    parastor_node_lst = obj_node.get_nodes_ip()
    client_node_lst = get_config.get_allclient_ip()
    all_node_lst = parastor_node_lst + client_node_lst
    cmd = "echo 3 > /proc/sys/vm/drop_caches"
    for node_ip in all_node_lst:
        common.run_command(node_ip, cmd)

    log.info("获取大文件聚合读的性能")
    read_cmd = "iozone -t 20 -s %s -r 4m -i 1 -+n -F %s" % (File_Size, os.path.join(PROPERTY_TRUE_PATH, 'iozone.0'))
    rc, stdout = common.run_command(client_ip, read_cmd)
    line_lst = stdout.splitlines()
    preperty_read = ''
    for line in line_lst:
        if 'Children see throughput for 10 initial writers' in line:
            preperty_read = line.split('=')[-1]
            break

    log.info("***********************************************")
    log.info("大文件聚合写平均性能是: %s" % preperty_write)
    log.info("大文件聚合读平均性能是: %s" % preperty_read)
    log.info("***********************************************")
    cmd = 'rm -rf %s' % PROPERTY_TRUE_PATH
    common.run_command(CLIENT_IP[0], cmd)

    return preperty_write, preperty_read





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

    # todo: 性能测试
    '''单流带宽'''
    single_bw()



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