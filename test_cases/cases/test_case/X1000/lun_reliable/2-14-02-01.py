# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-7

'''
测试内容:日志组业务节点+日志组非业务节点在业务过程中异常
测试步骤：
1）配置访问区等设置，创建逻辑卷，映射至主机
2）主机端对逻辑卷进行读写业务，过程中将磁盘中的一块磁盘拔出
3）检查业务不中断
检查项：
业务不中断


'''

# testlink case: 1000-33681
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
    global node_ip3
    global node_ip4
    global node_ip5
    global client_ip1
    node_ip1 = env_manage.get_inter_ids()[0]
    node_ip2 = env_manage.get_inter_ids()[-1]
    node_ip3 = env_manage.get_inter_ids()[1]
    node_ip4 = env_manage.get_inter_ids()[2]
    node_ip5 = env_manage.get_inter_ids()[3]
    client_ip1 = env_manage.client_ips[0]


infos1 = []
types1 = []
infos2 = []
types2 = []


def vdb_test():
    lun_name = env_manage.osan.ls_scsi_dev(client_ip=client_ip1)
    if len(lun_name) > 10:
        lun_name = lun_name[:10]
    vdb_file = env_manage.com2_osan.gen_vdb_xml(lun=lun_name, xfersize="4k", rdpct="50")
    log.info("vdbench 进行读写业务")
    env_manage.com2_osan.run_vdb(client_ip=client_ip1, vdb_xml=vdb_file, output=node_ip1, jn_jro="jn", time=600)
    env_manage.com2_osan.run_vdb(client_ip=client_ip1, vdb_xml=vdb_file, output=node_ip1, jn_jro="jro")


def vdb_result():
    env_manage.osan.save_vdb_log(c_ip=client_ip1, f_name="vdbtest")


def os_test():
    time.sleep(30)
    type1 = env_manage.get_os_type(node_ip1)
    info1 = env_manage.down_node(node_ip1, type1, "init 0")
    infos1.append(info1)
    types1.append(type1)
    type2 = env_manage.get_os_type(node_ip2)
    info2 = env_manage.down_node(node_ip2, type2, "init 0")
    infos2.append(info2)
    types2.append(type2)


def case():
    log.info("step:1.创建逻辑卷，创建lun map")
    env_manage.create_lun()  # 创建lun
    env_manage.create_lun_map()
    log.info("step:2.ISCSI 登录")
    env_manage.create_iscsi_login(client_ip1)
    threads = []
    t1 = threading.Thread(target=vdb_test)  # vdbench自动测试
    threads.append(t1)
    t2 = threading.Thread(target=os_test)  # 同时进行拔盘
    threads.append(t2)
    for i in threads:
        i.start()
    for i in threads:
        i.join()
    log.info("step:3.检查vdbench结果")
    vdb_result()
    log.info("step:4.节点开机")
    env_manage.up_node(infos1[0], types1[0])
    env_manage.up_node(infos2[0], types2[0])
    rc1 = env_manage.com_lh.get_os_status(node_ip1)
    rc2 = env_manage.com_lh.get_os_status(node_ip2)
    if rc1 == 0 and rc2 == 0:
        return


def main():
    env_manage.clean_test_env()
    setup()
    case()
    log.info("step:5.检查清理测试环境")
    env_manage.osan.iscsi_logout_all(client_ip1)
    env_manage.clean_lun_map()
    env_manage.clean_lun()
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == '__main__':
    env_manage.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=5)
    common.case_main(main)