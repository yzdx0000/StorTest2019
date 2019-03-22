# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-9

'''
测试内容:SVIP和VIP在同一节点上能被扫描LUN
测试步骤：
1、创建2个访问区，分别启动两个访问分区iSCSI
2、分别创建两个访问区对应的子网，VIP地址池
3、分别创建两个访问区的LUN和LUN映射
4、主机登录访问区1的LUN，并下发大小快混合的读写业务
5、停止访问区2的iSCSI
6、再次启动访问区2iSCSI过程中，oPmgr主所在节点掉电
检查项：
1、节点池和存储池创建成功
2、访问分区创建成功
3、访问分区iSCSI启动成功

'''

# testlink case: 1000-34185
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
import xml
import decorator_func


'''初始化'''
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
current_path = os.path.dirname(os.path.abspath(__file__))

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


def os_down():
    node_ip = env_manage.com_lh.get_master_oRole(node_ip1)
    os_type = env_manage.get_os_type(node_ip)
    info = env_manage.down_node(node_ip, os_type)
    os_types.append(os_type)
    infos.append(info)
    log.info("Down master oPmgr node finished. Get the node type: %s ,info: %s" % (os_type, info))
    return


def create_iscsi_login(ips=node_ip1, cli_ips=client_ip1, svip=None):
    env_manage.osan.discover_scsi_list(client_ip=cli_ips, svip=svip[0])  # 进行一下discovery，真正的tag从xstor中拿
    target_list = env_manage.osan.get_map_target(ips)
    log.info("Get Info:\nSvip list:%s \nTarget list:%s" % (svip, target_list))
    for tag in target_list:
        log.info("主机发现存储target：%s,主机 %s 将进行SCSI登录" % (tag, cli_ips))
        env_manage.osan.iscsi_login(client_ip=cli_ips, iqn=tag)


def vdb_test():
    lun_name = env_manage.osan.ls_scsi_dev(client_ip=client_ip1)
    if len(lun_name) > 10:
        lun_name = lun_name[:10]
    vdb_file = env_manage.com2_osan.gen_vdb_xml(lun=lun_name, xfersize="4k", rdpct="50")
    log.info("vdbench 进行读写业务")
    env_manage.com2_osan.run_vdb(client_ip=client_ip1, vdb_xml=vdb_file, output=node_ip1, jn_jro="jn", time=600)


def os_down_osan(access_id):
    time.sleep(30)
    env_manage.osan.disable_san(node_ip1, access_id)
    threads = []
    threads.append(threading.Thread(target=env_manage.osan.enable_san, args=(node_ip1, access_id)))
    threads.append(threading.Thread(target=os_down))
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def case():
    log.info("******************* case start **********************")
    svip1 = env_manage.svip[0]
    svip2 = env_manage.from_xml_get_svip2()[0]
    vip1 = env_manage.vips[0]
    vip2 = env_manage.from_xml_get_vip2()[0]
    log.info("step:1.创建访问区")
    az_id1 = env_manage.create_access(ips=node_ip1, node_ids="1,2,3", access_name="accesszone1")
    az_id2 = env_manage.create_access(ips=node_ip1, node_ids="4,5,6", access_name="accesszone2")
    log.info("step:2.启动scsi")
    env_manage.enable_san()
    log.info("step:3.分别创建两个svip")
    sub_id1 = env_manage.create_subnet(s_ip=node_ip1, svip=svip1, a_z_id=az_id1, access_name="sub1")
    sub_id2 = env_manage.create_subnet(s_ip=node_ip1, svip=svip2, a_z_id=az_id2, access_name="sub2")
    log.info("step:4.创建vip池")
    env_manage.create_vip(s_ip=node_ip1, subnet_id=sub_id1, vip_name="vip1.com", vip_pool=vip1)
    env_manage.create_vip(s_ip=node_ip1, subnet_id=sub_id2, vip_name="vip2.com", vip_pool=vip2)
    log.info("step:5.创建lun")
    env_manage.create_host_group()
    env_manage.create_host()
    env_manage.create_add_initiator()
    env_manage.create_lun(ips=node_ip1, name="LUN1", access_id=az_id1)
    env_manage.create_lun(ips=node_ip1, name="LUN2", access_id=az_id2)
    create_iscsi_login(ips=node_ip1, cli_ips=client_ip1, svip=svip1)
    log.info("step:6.运行vdbench停止访问区2的iSCSI,再次启动访问区2iSCSI过程中，oPmgr主所在节点掉电")
    threads = []
    threads.append(threading.Thread(target=vdb_test))
    threads.append(threading.Thread(target=os_down_osan))
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    log.info("检查san 协议是否开启成功")
    san_status = env_manage.com_lh.get_san_state(node_ip1)
    if all(san_status) is True:
        log.info("check all san is active, all san status:%s" % (san_status))
    else:
        log.info("check san status is :%s" % (san_status))
        os._exit(1)
    log.info("step:7.%s 节点开机 节点类型%s,节点ID or IPMI IP: %s" % (node_ip2, os_types[0], infos[0]))
    env_manage.up_node(infos[0], os_types[0])
    log.info("step:8.检查节点运行状态，检查服务恢复情况。")
    env_manage.com_lh.get_os_status(node_ip2)
    log.info("******************* case end ************************")


def main():
    log.info("step: checking the test environment")
    access_env.check_env()
    log.info("step: initialize node ip")
    setup()
    case()
    log.info("step:9.检查清理测试环境")
    access_env.check_env()
    log.info("The case finished!!!")


if __name__ == '__main__':
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=7)
    common.case_main(main)
