# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-7

'''
测试内容:业务过程中磁盘异常
测试步骤：
1）配置访问区，创建逻辑卷映射至主机
2）在主机端进行读写业务，监控网卡流量，使网卡流量占用率到到95%以上
5）修改逻辑卷
检查项：
1）访问区配置成功
2）逻辑卷可成功修改

'''

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


def vdb_test():
    log.info("vdbench 进行读写业务")
    lun_name = env_manage.osan.ls_scsi_dev(client_ip=client_ip1)
    if len(lun_name) > 10:
        lun_name = lun_name[:10]
    log.info("主机端扫描到的逻辑卷：%s" % (lun_name))
    vdb_file = env_manage.com2_osan.gen_vdb_xml(lun=lun_name, xfersize="4k", rdpct="100")
    env_manage.com2_osan.run_vdb(client_ip=client_ip1, vdb_xml=vdb_file, output=node_ip1, time=180)


def vdb_result():
    log.info("保存vdb测试结果")
    env_manage.osan.save_vdb_log(c_ip=client_ip1, f_name="vdbtest")


def case():
    log.info("step:1.创建逻辑卷，随机选取一个数据盘,创建lun map")
    env_manage.create_lun()  # 创建lun
    env_manage.create_lun_map()
    log.info("step:2.ISCSI 登录")
    env_manage.create_iscsi_login(client_ip1)
    log.info("step:3.vdbench测试（目的提高网络利用率）过程中将磁盘拔掉")
    env_manage.create_lun(node_ip1, "LUN2")  # 创建lun
    threads = []
    t1 = threading.Thread(target=vdb_test)  # vdbench自动测试
    threads.append(t1)
    t2 = threading.Thread(target=env_manage.update_luns)  # 同时进行拔盘
    threads.append(t2)
    for i in threads:
        i.start()
    for i in threads:
        i.join()
    env_manage.osan.iscsi_logout_all(client_ip1)


def main():
    env_manage.clean_test_env()
    setup()
    case()
    log.info("step:5.检查清理测试环境")
    env_manage.clean_lun_map()
    env_manage.clean_lun()
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)
