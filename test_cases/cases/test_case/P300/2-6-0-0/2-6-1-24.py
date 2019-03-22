#!/usr/bin/python
# -*- encoding:utf8 -*-

import sys
import utils_path
import log
import common
import fence_common
#
# Author: liuyzhb
# date 2019/03/15
# @summary：
#           故障zk主节点除了zk进程之外的所有进程，zk主节点不切换
# @steps:
#           1、获取zk主节点id
#           2、故障zk主节点除了zk进程之外的所有进程，zk主节点不切换
#           3、再次获取zk主节点的id
#           4、如果id和步骤1一致，则成功
def main():
    log_file_path = log.get_log_path(sys.argv[0])
    log.init(log_file_path, True)
    fence = fence_common.Fence()

    log.info("0> 进行环境准备")
    fence.fence_prepare()
    log.info("1> 获取zk主节点的id")
    rc, before_zkmaster_id= fence.get_master_of_zk()
    common.judge_rc(rc, 0, "get master of zk failed!!!")

    log.info("2> 故障主节点除了zk之外的其他所有进程")
    process_list = ["oJmgs","oRole","oJob","oPara","oStor","oMgcd","oCnas","ctdb","oJmv","oOms","oOss"]
    node = common.Node()
    node_ip = node.get_node_ip_by_id(int(before_zkmaster_id))
    log.info('ip of zk master is %s' %node_ip)
    for process in process_list:
        fence.kill_process_and_rename(node_ip, process,10)
    # 重命名失败了怎么办

    log.info("3> 再次查询zk主节点的id")
    rc, after_zkmaster_id = fence.get_master_of_zk()
    common.judge_rc(rc, 0, "get master of zk failed!!!")

    log.info("4> 判断zk的主节点有没有更换")
    if before_zkmaster_id == after_zkmaster_id:
        log.info('case %s finish success!!!!!' %sys.argv[0])
    else:
        log.error('case %s finish failed,after fault,zk master have been changed,tha is wrong' % sys.argv[0])
        except_exit(None, 1)

    log.info("5> 等待2min等环境恢复")
    time.sleep(120)




if __name__=="__main__":
    common.case_main(main)
