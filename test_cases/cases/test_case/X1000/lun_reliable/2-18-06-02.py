# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-9

'''
测试内容:SVIP和VIP在同一节点上能被扫描LUN
测试步骤：
1、创建节点池和存储池
2、创建访问分区
3、启动i该访问分区SCSI
4、停止该访问分区iSCSI过程中，oPmgr主所在节点掉电
检查项：
1、节点池和存储池创建成功
2、访问分区创建成功
3、访问分区iSCSI启动成功
4、访问分区iSCSI停止成功

'''

# testlink case: 1000-34194
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


def setup():
    '''获取业务节点IP和非业务节点IP'''
    global node_ip1
    global node_ip2
    global client_ip1
    node_ip1 = env_manage.deploy_ips[0]  # 业务节点IP
    node_ip2 = env_manage.deploy_ips[1]  # 非业务节点IP
    client_ip1 = env_manage.client_ips[0]


def pro_test():
    orole_master_ip = env_manage.com_lh.get_master_oRole(s_ip=node_ip1)
    env_manage.com_lh.kill_thread(s_ip=orole_master_ip, p_name="oRole", t_name="pmgr")
    log.info("node %s kill opmgr finished" % (orole_master_ip))
    return


def case():
    log.info("step:1.创建访问区")
    env_manage.create_access(ips=node_ip1, node_ids="1,2,3", access_name="accesszone1")
    log.info("step:2.启动scsi")
    env_manage.enable_san()
    log.info("step:3.停止scsi过程中，kill主oPmgr")
    threads = []
    threads.append(threading.Thread(target=env_manage.disable_san))
    threads.append(threading.Thread(target=pro_test))
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    log.info("检查san 协议是否开启成功")
    san_status = env_manage.com_lh.get_san_state(node_ip1)
    if all(san_status) is True:  # san仍然是开启状态说明disable失败。退出
        log.info("check all san is active, all san status:%s" % (san_status))
        os._exit(1)
    else:
        log.info("check san status is :%s" % (san_status))
    log.info("step:4.检查节点运行状态，检查服务恢复情况。")
    env_manage.com_lh.get_os_status(node_ip2)


def main():
    access_env.check_env()
    setup()
    case()
    log.info("step:6.检查清理测试环境")
    access_env.check_env()
    log.info("The case finished!!!")


if __name__ == '__main__':
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)
