#!/usr/bin/python
# -*- encoding:utf8 -*-

import sys
import random
import utils_path
import log
import common
import fence_common
import make_fault
import time
import check_if_nextcase
import prepare_clean
#
# Author: liuyzhb
# date 2019/03/15
# @summary：
#           故障zk主节点除了zk进程之外的所有进程，zk主节点不切换
# @steps:
#           1、获取zk主节点id
#           2、故障zk主节点之外的节点，故障是断部分数据网10次
#           3、再次获取zk主节点的id
#           4、如果id和步骤1一致，则成功
def prepare():
    prepare_clean.test_prepare(sys.argv[0])
def main():
    log_file_path = log.get_log_path(sys.argv[0])
    log.init(log_file_path, True)
    fence = fence_common.Fence()

    prepare()
    log.info("0> 进行环境准备")
    fence.fence_prepare()
    log.info("1> 获取zk主节点的id")
    rc, before_zkmaster_id= fence.get_master_of_zk()
    common.judge_rc(rc, 0, "get master of zk failed!!!")
    node = common.Node()
    master_ip = node.get_node_ip_by_id(before_zkmaster_id)

    log.info("2> 选定一个集群中一个非主节点的id")
    node = common.Node()
    node_list = node.get_nodes_id()
    log.info('node_list is %s' % node_list)
    log.info('before_zkmaster_id is %s' % before_zkmaster_id)
    node_list.remove(before_zkmaster_id)
    log.info('slave_node_list to down_net is %s' % node_list)
    slave_node_id = random.sample(node_list, 1)[0]
    log.info('slave_node_id to down_net is %d' %slave_node_id)

    log.info("3> 将选定的非主节点执行断部分数据网操作10次")
    rc = make_fault.part_net_down(slave_node_id, 1, 10, 300)
    common.judge_rc(rc, 0, "down and up net on node_id %d failed!!!"%slave_node_id)
    # 重命名失败了怎么办

    log.info("4> 再次查询zk主节点的id")
    rc, after_zkmaster_id = fence.get_master_of_zk()
    common.judge_rc(rc, 0, "get master of zk failed!!!")

    log.info("5> 判断zk的主节点有没有更换")
    if before_zkmaster_id == after_zkmaster_id:
        log.info('case %s finish success!!!!!' %sys.argv[0])
    else:
        log.error('case %s finish failed,after fault,zk master have been changed,tha is wrong' % sys.argv[0])
        except_exit(None, 1)

    log.info('fence_enable case %s finish success!!!!!' % sys.argv[0])




if __name__=="__main__":
    common.case_main(main)
