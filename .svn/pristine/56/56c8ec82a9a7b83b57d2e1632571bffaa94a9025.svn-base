# -*-coding:utf-8 -*
import os

import utils_path
import common
import log
import prepare_clean

####################################################################################
#
# Author: baorb
# Date: 2018-08-08
# @summary：
#      检查集群节点的系统时间是否一致
# @steps:
#     1、获取集群节点的时间；
#     2、检查节点的时间是否一致；
#
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字


def case():
    log.info("1> 获取集群所有节点的时间")
    obj_node = common.Node()
    node_ip_lst = obj_node.get_nodes_ip()
    time_lst = []
    cmd = 'date +%s'
    for node_ip in node_ip_lst:
        rc, node_time = common.run_command(node_ip, cmd)
        time_lst.append(int(node_time.strip()))

    log.info("2> 检查集群所有节点的时间是否相差大于10s")
    time_compare = time_lst[0]
    for time_tmp in time_lst:
        if abs(time_compare - time_tmp) > 10:
            raise Exception("ntp time is not same, time_compare:%s  time_tmp:%s" % (time_compare, time_tmp))
    log.info("ntp time is right!")


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)
    return


if __name__ == '__main__':
    common.case_main(main)