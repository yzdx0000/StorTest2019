# -*-coding:utf-8 -*
import os

import utils_path
import log
import common
import get_config
import prepare_clean

##########################################
#
# Author: baorb
# date 2018-11-13
# @summary：
#    测试大文件单流的读写性能。
# @steps:
#    1，单客户端跑iozone测试性能
#
# @changelog：
##########################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
PROPERTY_TRUE_PATH = os.path.join(prepare_clean.PROPERTY_PATH, FILE_NAME)   # /mnt/volume1/mini_case/3_0014_data_test
File_Size = '600G'


def case():
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

    log.info("case succeed!")
    return


def main():
    prepare_clean.preperty_test_prepare(FILE_NAME)
    case()
    prepare_clean.preperty_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)