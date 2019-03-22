# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-10
'''
测试内容：日志组业务节点数据网异常时映射
测试步骤：
1、创建节点池和存储池
2、创建访问分区
3、启动iSCSI过程中，oPmgr主所在节点数据网故障，1分钟后恢复

检查项：
1、节点池和存储池创建成功
2、访问分区创建成功
3、访问分区iSCSI启动成功

'''

# testlink case: 1000-34203
import os
import time
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


def setup():
    '''获取业务节点IP和非业务节点IP'''
    global node_ip1
    global node_ip2
    global client_ip1
    node_ip1 = env_manage.deploy_ips[0]  # 业务节点IP
    node_ip2 = env_manage.deploy_ips[1]  # 非业务节点IP
    client_ip1 = env_manage.client_ips[0]


def case():
    orole_master_ip = env_manage.com_lh.get_master_oRole(node_ip1)
    data_net = env_manage.com_lh.get_eth_name(orole_master_ip)[1]
    new_ip_list = []
    for ip in env_manage.deploy_ips:
        if orole_master_ip == ip:
            log.info("master orole IP is :%s, will out it" % (orole_master_ip))
        else:
            new_ip_list.append(ip)  # 取差集那到正常节点IP
    log.info("get the New ip_list:%s" % (new_ip_list))
    node_id_list = []
    for ip in new_ip_list:
        id = env_manage.com2_osan.get_access_zone_id(ip)
        new_ip_list.append(id)
    log.info("step:1.create access zone")
    env_manage.create_access(node_ids=node_id_list)
    log.info("step:2.激活san过程中断开网卡")
    threads = []
    t1 = threading.Thread(target=env_manage.enable_san, args=(new_ip_list[0],))
    threads.append(t1)
    t2 = threading.Thread(target=env_manage.down_network, args=(orole_master_ip, data_net))
    threads.append(t2)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    time.sleep(10)
    log.info("检查san 协议是否开启成功")
    san_status = env_manage.com_lh.get_san_state(node_ip1)
    if all(san_status) is True:
        log.info("check all san is active, all san status:%s" % (san_status))
        os._exit(1)
    else:
        log.info("check san status is :%s" % (san_status))
    env_manage.up_network(orole_master_ip, data_net)


def main():
    access_env.check_env()
    setup()
    case()
    log.info("step:5.清理检查环境")
    access_env.check_env()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=5)
    common.case_main(main)
