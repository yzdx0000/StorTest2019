# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-10
'''
测试内容：日志组业务节点数据网异常时映射
测试步骤：
1）创建访问区，配置访问区
2）创建逻辑卷
3）将逻辑卷映射至主机，映射过程中将日志组业务节点数据网断开
4）主机端检查映射逻辑卷数量与逻辑卷数量一至

检查项：
1）访问区配置成功
2）逻辑卷创建成功
3）映射成功

'''

# testlink case: 1000-34287
import os
import time
import threading
import utils_path
import log
import common
import ReliableTest
import prepare_x1000
import env_manage
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
    node_ip1 = env_manage.get_inter_ids()[0]  # 业务节点IP
    node_ip2 = env_manage.get_inter_ids()[-1]  # 非业务节点IP
    client_ip1 = env_manage.client_ips[0]


def case():
    subnet_eth = env_manage.com_lh.get_vip_eth_name(node_ip2)
    log.info("step:1.创建逻辑卷")
    env_manage.create_luns()
    log.info("step:2.创建lun map过程中网卡闪断")
    threads = []
    t1 = threading.Thread(target=env_manage.create_lun_map, args=(node_ip1,))
    threads.append(t1)
    t2 = threading.Thread(target=env_manage.com_lh.net_flash_test, args=(node_ip2, subnet_eth))
    threads.append(t2)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    log.info("step:3.ISCSI 登录")
    env_manage.create_iscsi_login()
    lun_name = env_manage.osan.ls_scsi_dev(client_ip=client_ip1)
    lun_ids = env_manage.osan.get_lun()
    if len(lun_name) == len(lun_ids):
        log.info("host get lun numbers right")
    else:
        log.error("check xstor disk is not equal 10 ,find disk is %s" % (len(lun_name)))
        exit(1)


def main():
    env_manage.clean_test_env()
    setup()
    case()
    log.info("step:4.检查清理测试环境")
    env_manage.osan.iscsi_logout_all(client_ip1)
    env_manage.clean_lun_map()
    env_manage.clean_lun()
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)
