# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-9

'''
测试内容:SVIP和VIP在同一节点上能被扫描LUN
测试步骤：
1、创建节点池和存储池
2、创建访问分区
3、启动iSCSI过程中，oPmgr主所在节点掉电
检查项：
1、节点池和存储池创建成功
2、访问分区创建成功
3、访问分区iSCSI启动成功

'''

# testlink case: 1000-34183
import os
import time
import random
import commands
import threading
import utils_path
import log
import common
import ReliableTest
import prepare_x1000
import env_manage
import access_env
import decorator_func

'''初始化'''
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log

infos = []
os_types = []


def setup():
    '''获取业务节点IP和非业务节点IP'''
    global node_ip1
    global node_ip2
    global client_ip1
    node_ip1 = env_manage.deploy_ips[0]  # 业务节点IP
    node_ip2 = env_manage.deploy_ips[1]  # 非业务节点IP
    client_ip1 = env_manage.client_ips[0]


def os_down(node_ip):
    log.info("step:2.1 will down oRole master node")
    os_type = env_manage.get_os_type(node_ip)
    info = env_manage.down_node(node_ip, os_type)
    os_types.append(os_type)
    infos.append(info)
    log.info("Down master oPmgr node finished. Get the node type: %s ,info: %s" % (os_type, info))
    return


def case():
    log.info("******************* case start **********************")
    log.info("step:1.Start the scsi protocol of access zone ")
    orole_ip = env_manage.com_lh.get_master_oRole(node_ip1)
    node_id = env_manage.com_lh.get_node_id_by_ip(orole_ip)  # 拿到主orole id
    nodes_id = env_manage.osan.get_nodes(node_ip1)  # 获取全部ID
    nodes_id.remove(node_id)   # 移除主oRole ID
    create_ids = nodes_id[:4]
    ids = [str(i) for i in create_ids]
    create_ids = ','.join(ids)
    log.info("create access zone ids:%s, node_down ids:%s" % (create_ids, node_id))
    env_manage.create_access(ips=node_ip1, node_ids=create_ids, access_name="accesszone1")
    log.info("step:2.shutdown oRole master node when start scsi protocol of access zone")
    threads = []
    threads.append(threading.Thread(target=env_manage.enable_san))
    threads.append(threading.Thread(target=os_down, args=(orole_ip,)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    log.info("step:3.check if the scsi protocol is open success")
    san_status = env_manage.com_lh.get_san_state(node_ip1)
    if all(san_status) is True:
        log.info("step:4.check all san is active, all san status:%s" % (san_status))
    else:
        log.info("step:4.check san status is :%s, will exit" % (san_status))
        os._exit(1)
    log.info("step:4.%s 节点开机 节点类型%s,节点ID or IPMI IP: %s" % (node_ip2, os_types[0], infos[0]))
    env_manage.up_node(infos[0], os_types[0])
    log.info("step:5.检查节点运行状态，检查服务恢复情况。")
    env_manage.com_lh.get_os_status(node_ip2)
    log.info("******************* case end ************************")


def main():
    log.info("step: checking the test environment")
    access_env.check_env()
    log.info("step: initialize node ip")
    setup()
    case()
    log.info("step:5.检查清理测试环境")
    # env_manage.disable_san()
    # env_manage.clean_access_zone(node_ip1)
    access_env.init_access_env()
    log.info("The case finished!!!")


if __name__ == '__main__':
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=5)
    common.case_main(main)
