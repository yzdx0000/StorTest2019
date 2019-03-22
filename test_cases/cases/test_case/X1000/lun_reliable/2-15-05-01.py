# -*-coding:utf-8 -*-
# !/usr/bin/python

'''
测试步骤：
1）配置访问区，将逻辑卷映射主机
2）制造磁盘池异常，使逻辑卷不能正常工作。
3）主机端扫描磁盘，无异常
4）主机端重启，无异常
5）测试windows/linux系统
检查项：
卷异常不会导致主机异常
'''

# testlink case: 1000-33690
import os
import time
import commands
import threading
import utils_path
import log
import common
import ReliableTest
import env_manage
import decorator_func
 

'''初始化'''
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
scripts_path = os.path.dirname(os.path.abspath(__file__))


def setup():
    '''获取业务节点IP和非业务节点IP'''
    global node_ip1
    global node_ip2
    global client_ip1
    global client_ip2
    node_ip1 = env_manage.deploy_ips[0]
    node_ip2 = env_manage.deploy_ips[1]
    client_ip1 = env_manage.client_ips[0]
    client_ip2 = env_manage.client_ips[1]


def get_dsik(id):  # 这样写的语法不好，需要优化
    # data_disks = []
    s_disk, d_disk = env_manage.com_disk.get_share_monopoly_disk_names(id)
    # data_disks.append(d_disk)
    return d_disk


def remove_disk(node_ip, disk_id):
    time.sleep(50)
    log.info("%s 移除硬盘 %s" % (node_ip, disk_id))
    for id in disk_id:
        cmd = 'ssh %s \"echo scsi remove-single-device %s > /proc/scsi/scsi\"' % (node_ip, id)
        rc, stdout = commands.getstatusoutput(cmd)
        if 0 != rc:
            log.error('node %s remove disk %s fault!!!' % (node_ip, disk_id))


def insert_disk(node_ip, disk_id):
    time.sleep(60)
    log.info("%s 节点插入硬盘 %s " % (node_ip, disk_id))
    cmd = 'ssh %s \"echo scsi add-single-device %s > /proc/scsi/scsi\"' % (node_ip, disk_id)
    rc, stdout = commands.getstatusoutput(cmd)
    if 0 != rc:
        log.info('node %s add disk %s fault!!!' % (node_ip, disk_id))
    time.sleep(5)
    cmd = 'ssh %s \"lsscsi\"' % node_ip
    rc, stdout = commands.getstatusoutput(cmd)
    log.info("硬盘列表 ：\n %s" % (stdout))
    return


def create_lun_map(ips):
    map_ids = []
    # lun_ids = osan.get_lun(s_ip=ips)
    lun_ids = env_manage.com_lh.get_unmap_lun(s_ip=ips)
    host_group_id = env_manage.osan.get_host_groups(s_ip=ips)
    log.info("Get Info:\nGet unmap lun ids:%s \nGet host_group_id:%s" % (lun_ids, host_group_id))
    for id in lun_ids:
        log.info("in the node %s make the lun ID %s be aassigned to %s" % (ips, id, host_group_id[0]))
        map_id = env_manage.osan.map_lun(s_ip=ips, lun_ids=id, hg_id=host_group_id[1])
        map_ids.append(map_id)
    return map_ids


def case():
    log.info("step:1.创建逻辑卷，创建lun map，映射主机")
    env_manage.create_lun()
    create_lun_map(node_ip1)
    env_manage.create_iscsi_login(client_ip2)
    log.info("step:2.将磁盘池所有硬盘拔出，让存储池不能正常工作")
    for ip in env_manage.deploy_ips:
        node_id = env_manage.com_lh.get_node_id_by_ip(ip)
        node_disk = get_dsik(node_id)
        log.info("node %s get data disk:%s" % (ip, node_disk))
        remove_disk(ip, node_disk)
    log.info("step3.将主机重启")
    os_type = env_manage.get_os_type(client_ip2)
    env_manage.down_node(client_ip2, os_type, "init 6")
    log.info("step:4.检查主机运行情况")
    rc = env_manage.com_lh.get_os_status_1(client_ip2)
    if rc == 0:
        for ip in env_manage.deploy_ips:
            env_manage.down_node(ip, "VM")
        for ip in env_manage.deploy_ips:
            env_manage.up_node(ip, "VM")
        install_cmd1 = ("ssh %s \"/usr/bin/python -u /home/StorTest/scripts/Auto_install.py\"" % (client_ip1))
        commands.getstatusoutput(install_cmd1)
        return


def main():
    setup()
    env_manage.clean_test_env()
    case()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)
