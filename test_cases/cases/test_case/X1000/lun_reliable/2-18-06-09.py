# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-9

'''
测试内容:SVIP和VIP在同一节点上能被扫描LUN
测试步骤：
1、配置节点池含3节点，设置副本数为3
2、创建存储池
3、创建访问区
4、创建业务子网和VIP地址池，并启动iSCSI
5、创建LUN
6、修改vip地址池中有LUN关联的VIP过程中，oPmgr主节点掉电
7、创建LUN映射
8、主机端使用SVIP扫描登录并访问LUN
检查项：
6、节点添加到访问区成功，该节点成为日志服务节点；业务正常，故障节点VIP切换到新添加节点

'''

# testlink case: 1000-34201
import os
import time
import random
import json
import commands
import threading
import utils_path
import log
import xml
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
current_path = os.path.dirname(os.path.abspath(__file__))


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
    log.info("kill opmgr finished")
    return


def change_vip():
    new_vips = env_manage.from_xml_get_vip2()
    vip_pool_list = env_manage.com2_osan.analysis_vip(new_vips)
    log.info("修改（删除）vip")
    vip_pool_id = env_manage.com2_osan.get_vip_address_pools_id(node_ip1)
    env_manage.osan.update_vip_address_pool(vip_id=vip_pool_id[0], s_ip=node_ip1, vip_addresses=new_vips[0])
    log.info("update success,will check it")
    env_manage.check_new_vip_status(vip_pool_list)


def case():
    log.info("step:1 创建lun")
    env_manage.create_lun(ips=node_ip1, name="LUN1")
    log.info("step:2. 修改vip过程中杀进程")
    threads = []
    threads.append(threading.Thread(target=change_vip))
    threads.append(threading.Thread(target=pro_test))
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    env_manage.create_lun_map(node_ip1)
    env_manage.create_iscsi_login()
    lun_name = env_manage.osan.ls_scsi_dev(client_ip=client_ip1)
    log.info("from host get xstor lun %s" % (lun_name))
    log.info("step:5.检查节点运行状态，检查服务恢复情况。")
    env_manage.com_lh.get_os_status(node_ip2)
    # env_manage.com_lh.multi_check_part_lun_uniform_by_ip()  # 比较数据一致性


def main():
    env_manage.clean_test_env()
    setup()
    case()
    log.info("step:6.检查清理测试环境")
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == '__main__':
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)
