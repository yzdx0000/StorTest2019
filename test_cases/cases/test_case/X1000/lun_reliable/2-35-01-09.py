# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-9

'''
测试内容:SVIP和VIP在同一节点上能被扫描LUN
测试步骤：
1、创建存储池和访问分区，业务子网和对应的SVIP和VIP地址池（至少每个节点一个VIP），并创建6条LUN，LUN1-LUN6
2、创建主机组，添加主机，并将主机组映射到LUN1-LUN6上
3、在主机端使用SVIP登录主机映射的LUN
4、修改SVIP
5、在主机端注销所有iscsi会话后使用SVIP重新登录主机映射的LUN
检查项：
1、步骤3，使用SVIP登录扫描6条LUN成功,；
2、步骤4，修改SVIP成功；
3、步骤5，主机iscsi会话注销成功；使用新SVIP登录扫描LUN成功

'''

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


def pro_test():
    orole_master_ip = env_manage.com_lh.get_master_oRole(s_ip=node_ip1)
    env_manage.com_lh.kill_thread(s_ip=orole_master_ip, p_name="oRole", t_name="pmgr")
    log.info("kill opmgr finished")
    return


def create_iscsi_login(cli_ips, svip):
    env_manage.osan.discover_scsi_list(client_ip=cli_ips, svip=svip[0])  # 进行一下discovery，真正的tag从xstor中拿
    target_list = env_manage.osan.get_map_target(node_ip1)
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


def update_access():
    env_manage.update_access(node_ip1, id_list="1,2,3,4")


def os_down_osan():
    time.sleep(30)
    threads = []
    threads.append(threading.Thread(target=update_access))
    threads.append(threading.Thread(target=pro_test))
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def update_subnet(sub_ip):
    # new_svip = get_svip()[1]
    subnet_id = env_manage.osan.get_subnet_id(node_ip1)
    for id in subnet_id:
        cmd = ("ssh %s \"pscli --command=update_subnet --id=%s --svip=%s --subnet_mask=%s\"" % (
            node_ip1, id, sub_ip, "255.0.0.0"))
        rc, output = commands.getstatusoutput(cmd)
        if rc != 0:
            log.info("update svip failed")
        else:
            log.info(output)


def create_luns():
    for i in range(6):
        lun_name = "LUN" + str(i)
        env_manage.create_lun(node_ip1, lun_name)


def case():
    svip1 = env_manage.svip[0]
    svip2 = env_manage.from_xml_get_svip2()[0]
    vip1 = env_manage.vips[0]
    vip2 = env_manage.from_xml_get_vip2()[0]
    log.info("step:1.创建逻辑卷")
    create_luns()
    create_iscsi_login(cli_ips=client_ip1, svip=svip1)
    log.info("step:2.扫描主机端lun数量")
    lun_name1 = env_manage.com2_osan.ls_scsi_dev(client_ip1)
    log.info("step:3.修改svip")
    update_subnet(svip2)
    env_manage.com2_osan.iscsi_logout_all()
    create_iscsi_login(cli_ips=client_ip1, svip=svip2)
    log.info("step:4.扫描主机端lun数量")
    lun_name2 = env_manage.com2_osan.ls_scsi_dev(client_ip1)
    if lun_name1 == lun_name2:
        log.info("check lun success")
    else:
        log.error("check lun failed")


def main():
    access_env.check_env()
    setup()
    case()
    log.info("step:6.检查清理测试环境")
    env_manage.clean_access_zone(node_ip1)
    log.info("The case finished!!!")


if __name__ == '__main__':
    env_manage.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=5)
    common.case_main(main)