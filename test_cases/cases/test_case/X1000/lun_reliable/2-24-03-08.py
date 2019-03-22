# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-9

'''
测试内容:SVIP和VIP在同一节点上能被扫描LUN
测试步骤：
1、配置节点池含3节点，设置副本数为3
2、创建存储池，使用全部磁盘
3、创建一个访问区，包含4个节点
4、给访问区添加1个IP地址池，至少包含3个IP
5、启动iSCSI，创建一条LUN和对应的映射
6、主机下发业务中，从访问区中删除一个节点过程中，主oJNL节点数据网故障，1分钟后恢复
检查项：
6、节点删除成功，业务无报错，日志组仅包含访问区中剩余2节点，该删除节点上的vip切换到日志组其他节点

'''

# testlink case: 1000-34210
import os
import time
import random
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


def setup():
    '''获取业务节点IP和非业务节点IP'''
    global node_ip1
    global node_ip2
    global client_ip1
    node_ip1 = env_manage.deploy_ips[0]  # 业务节点IP
    node_ip2 = env_manage.deploy_ips[1]  # 非业务节点IP
    client_ip1 = env_manage.client_ips[0]


def create_iscsi_login(ips, cli_ips, svip):
    env_manage.osan.discover_scsi_list(client_ip=cli_ips, svip=svip)  # 进行一下discovery，真正的tag从xstor中拿
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


def update_access(s_ip):
    env_manage.update_access(s_ip, id_list="1,2,3")


def check_node_vip():
    node_list = []
    vips = env_manage.com2_osan.analysis_vip(env_manage.vips)
    for vip in vips:
        mgr_ip = env_manage.com2_osan.get_node_by_vip(vip)
        node_list.append(mgr_ip)
    log.info("get vip node list:%s" % (node_list))
    if env_manage.deploy_ips[2] in node_list:
        log.info("old node have vip")
        os._exit(1)
    else:
        log.error("old node have not vip")
        return


def os_down_osan(ip, name):
    time.sleep(30)
    log.info("will down network and update access")
    new_ip_list = []
    for s_ip in env_manage.deploy_ips:
        if ip == s_ip:
            log.info("master orole IP is :%s, will out it" % (ip))
        else:
            new_ip_list.append(s_ip)  # 取差集那到正常节点IP
    log.info("get the new ip list:%s" % (new_ip_list))
    threads = []
    threads.append(threading.Thread(target=update_access, args=(new_ip_list[0],)))
    threads.append(threading.Thread(target=env_manage.down_network, args=(ip, name)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def case():
    svip1 = env_manage.svip[0]
    svip2 = env_manage.from_xml_get_svip2()[0]
    vip1 = env_manage.vips[0]
    vip2 = env_manage.from_xml_get_vip2()[0]
    master_id = env_manage.com_lh.get_opara_jnl()
    master_ip = env_manage.deploy_ips[int(master_id)-1]
    data_net = env_manage.com_lh.get_eth_name(master_ip)[1]
    log.info("step:1.创建访问区")
    az_id1 = env_manage.create_access(ips=node_ip1, node_ids="1,2,3,4", access_name="accesszone1")
    log.info("step:2.启动scsi")
    env_manage.enable_san()
    sub_id1 = env_manage.create_subnet(s_ip=node_ip1, svip=svip1, a_z_id=az_id1, access_name="sub1")
    env_manage.create_vip(s_ip=node_ip1, subnet_id=sub_id1, vip_name="vip1.com", vip_pool=vip1)
    env_manage.create_host_group()
    env_manage.create_host()
    env_manage.create_add_initiator()
    env_manage.create_lun(ips=node_ip1, name="LUN1", access_id=az_id1)
    env_manage.create_lun_map(node_ip1)
    create_iscsi_login(ips=node_ip1, cli_ips=client_ip1, svip=svip1)
    log.info("step:3.停止scsi过程中，主oPmgr节点掉电")
    threads = []
    threads.append(threading.Thread(target=vdb_test))
    threads.append(threading.Thread(target=os_down_osan, args=(master_ip, data_net)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    env_manage.up_network(master_ip, data_net)
    log.info("step:5.检查节点运行状态，检查服务恢复情况。")
    env_manage.com_lh.get_os_status(node_ip2)
    # env_manage.com_lh.multi_check_part_lun_uniform_by_ip()  # 比较数据一致性


def main():
    access_env.check_env()
    setup()
    case()
    log.info("step:6.检查清理测试环境")
    env_manage.clean_access_zone(node_ip1)
    log.info("The case finished!!!")


if __name__ == '__main__':
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=5)
    common.case_main(main)
