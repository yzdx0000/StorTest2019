# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time

import utils_path
import common
import log
import tool_use
import get_config
import prepare_clean
#################################################################
#
# Author: chenjy1
# Date: 2018-08-16
# @summary：
#    跑vdbench同时节点轮流运维下线上线
# @steps:
#    1.子进程跑vdbench
#    2.重复三次节点轮流运维下线上线
#
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]          # 本脚本名字
VDBENCH_PATH = os.path.join(prepare_clean.DEFECT_PATH, FILE_NAME)    # /mnt/parastor/defect_path/vdb_shutdown_startup
N = 3  # 运维上下线循环次数
FAIL_CNT = 10  # 运维下线允许失败的次数(因为有可能某个进程未准备好)

ONLINE_FAIL_CNT = 1  # 决定运维上线允许失败的等待时间(1个数1分钟)


def case():
    log.info("case begin")
    log.info("1> 子进程跑vdbench")
    '''获取集群节点信息'''
    ob_node = common.Node()
    node_id_lst = ob_node.get_nodes_id()
    client_ip_lst = get_config.get_allclient_ip()
    p1 = Process(target=tool_use.vdbench_run, args=(VDBENCH_PATH, client_ip_lst[0], client_ip_lst[1]),
                 kwargs={'run_create': True, 'run_check_write': True})
    p1.daemon = True
    p1.start()

    log.info("2> 节点轮流运维上下线")
    obj_node = common.Node()
    for i in range(N):
        for nodeid in node_id_lst:
            start_time = time.time()
            """节点运维下线"""
            for cnt in range(FAIL_CNT+1):
                rc, stdout = common.make_node_offline(nodeid)
                if rc == 0:
                    log.info("nodeid : %s make_node_offline finish" % nodeid)
                    break
                elif cnt == FAIL_CNT:
                    common.judge_rc(rc, 0, "make_node_offline id=%s failed" % nodeid)
                else:
                    time.sleep(60)
                    exist_time = int(time.time() - start_time)
                    m, s = divmod(exist_time, 60)
                    h, m = divmod(m, 60)
                    log.info('retry make_node_offline exist %dh:%dm:%ds' % (h, m, s))

            time.sleep(30)
            """节点运维上线"""
            for cnt in range(ONLINE_FAIL_CNT):
                rc, stdout = common.make_nodes_online(nodeid)
                if rc == 0:
                    log.info("nodeid : %s make_nodes_online finish" % nodeid)
                    break
                elif cnt == FAIL_CNT:
                    common.judge_rc(rc, 0, "make_nodes_online id=%s failed" % nodeid)
                else:
                    time.sleep(60)
                    exist_time = int(time.time() - start_time)
                    m, s = divmod(exist_time, 60)
                    h, m = divmod(m, 60)
                    log.info('retry make_nodes_online exist %dh:%dm:%ds' % (h, m, s))

            """获取节点状态"""
            start_time = time.time()
            flag_node_healthy = False
            while True:
                getnodeinfo = obj_node.get_nodes()
                for node in getnodeinfo['result']['nodes']:
                    if node['node_id'] == nodeid:
                        if "NODE_STATE_HEALTHY" == node['state']:
                            log.info("node : %s NODE_STATE_HEALTHY" % nodeid)
                            flag_node_healthy = True
                            break
                if flag_node_healthy:
                    break
                time.sleep(10)
                exist_time = int(time.time() - start_time)
                m, s = divmod(exist_time, 60)
                h, m = divmod(m, 60)
                log.info('wait NODE_STATE_HEALTHY state %dh:%dm:%ds' % (h, m, s))
            log.info("nodeid : %s state is NODE_STATE_HEALTHY " % nodeid)

            """获取集群服务状态"""
            start_time = time.time()
            while True:
                rc = common.check_service_state()
                if rc:
                    break
                time.sleep(10)
                exist_time = int(time.time() - start_time)
                m, s = divmod(exist_time, 60)
                h, m = divmod(m, 60)
                log.info('wait check_service_state %dh:%dm:%ds' % (h, m, s))
            log.info("check_service_state ok ")

    p1.join()
    common.judge_rc(p1.exitcode, 0, "vdbench run failed")
    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
