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
6、修改业务子网的SVIP和子网掩码过程中，oPmgr主节点掉电
7、创建LUN映射
8、主机端使用修改后SVIP扫描登录并访问LUN
检查项：
6、节点添加到访问区成功，该节点成为日志服务节点；业务正常，故障节点VIP切换到新添加节点

'''

# testlink case: 1000-34192
import os
import time
import random
import json
import xml
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
current_path = os.path.dirname(os.path.abspath(__file__))

infos = []
os_types = []
down_node = []


def setup():
    '''获取业务节点IP和非业务节点IP'''
    global node_ip1
    global node_ip2
    global client_ip1
    node_ip1 = env_manage.deploy_ips[0]  # 业务节点IP
    node_ip2 = env_manage.deploy_ips[1]  # 非业务节点IP
    client_ip1 = env_manage.client_ips[0]


def os_down(node_ip):
    os_type = env_manage.get_os_type(node_ip)
    info = env_manage.down_node(node_ip, os_type)
    os_types.append(os_type)
    infos.append(info)
    down_node.append(node_ip)
    log.info("Down master oPmgr node finished. Get the node type: %s ,info: %s" % (os_type, info))
    return


def update_subnet(s_ip, new_svip):
    subnet_id = env_manage.osan.get_subnet_id(s_ip)
    for id in subnet_id:
        cmd = ("ssh %s \"pscli --command=update_subnet --id=%s --svip=%s --subnet_mask=%s\"" % (
            s_ip, id, new_svip, "255.0.0.0"))
        log.info(cmd)
        rc, output = commands.getstatusoutput(cmd)
        if rc != 0:
            log.info("update svip failed")
        else:
            log.info("update success,will check it")
            rc = ReliableTest.check_ping(new_svip)
            if rc == True:
                log.info("svip chanage success")
            else:
                log.error("chanage svip failed")
                os._exit(1)


def case():
    log.info("******************* start case **********************")
    svip = env_manage.svip[0]
    new_svip = env_manage.from_xml_get_svip2()[0]
    log.info("step:1.创建 lun")
    env_manage.create_lun(ips=node_ip1, name="LUN1")
    node_ip = env_manage.com_lh.get_master_oRole(node_ip1)
    new_ip_list = []
    for ip in env_manage.deploy_ips:
        if node_ip == ip:
            log.info("master orole IP is :%s, will out it" % (node_ip))
        else:
            new_ip_list.append(ip)  # 取差集那到正常节点IP
    log.info("get the new ip list:%s" % (new_ip_list))
    log.info("step:2.修改svip过程中节点关机")
    threads = []
    threads.append(threading.Thread(target=update_subnet, args=(new_ip_list[0], new_svip,)))
    threads.append(threading.Thread(target=os_down, args=(node_ip,)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    log.info("step:3.创建 lun map")
    env_manage.create_lun_map(node_ip1)
    log.info("step:4.iscsi 登录")
    env_manage.create_iscsi_login()
    lun_name = env_manage.osan.ls_scsi_dev(client_ip=client_ip1)
    log.info("from host get xstor lun %s" % (lun_name))
    log.info("step:5.%s 节点开机 节点类型%s,节点ID or IPMI IP: %s" % (node_ip2, os_types[0], infos[0]))
    env_manage.up_node(infos[0], os_types[0])
    log.info("step:6.检查节点运行状态，检查服务恢复情况。")
    env_manage.com_lh.get_os_status(node_ip2)
    log.info("step:7.还原svip")
    update_subnet(new_ip_list[0], svip)
    # env_manage.com_lh.multi_check_part_lun_uniform_by_ip()  # 比较数据一致性
    log.info("******************* case end ************************")


def main():
    log.info("step: checking the test environment")
    env_manage.clean_test_env()
    log.info("step: initialize node ip")
    setup()
    case()
    log.info("step:8.检查清理测试环境")
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == '__main__':
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    # log.init(log_file_path, True)
    common.case_main(main)
