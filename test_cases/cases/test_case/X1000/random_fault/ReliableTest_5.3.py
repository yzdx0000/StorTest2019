#!/usr/bin/python
# -*- encoding=utf8 -*-

import time
import json
import random
import sys
import logging
import os
import re
import traceback
import subprocess
from multiprocessing import Process
import xml.dom.minidom
from optparse import OptionParser

global OPERATION      # 执行的故障
global NUMBERS        # 故障执行的次数
global FAULTDISKTYPE  # 做故障磁盘的类型
global FAULTDISKNUM   # 做故障磁盘的数目
global LOCALNODEFLAG  # 执行脚本的节点是否是集群节点的标志，True:是集群节点，False:非集群节点
global LOCALNODEIP    # 本节点ip
global ZKNUM          # 集群创建时的zk数量（参数中获取）
global MIXFAULT       # 混合故障标志，True:混合故障; Fault:不做混合故障
global CORESTOP       # 环境有core停止脚本的标志


global NODE_IP_LST        # 集群节点的管理ip，当执行脚本的节点不是集群节点时使用，列表
global NODE_DATA_IP_LST   # 集群节点的数据ip，当执行脚本的节点不是集群节点时使用，列表

global FAULT_NODE_IP_LST  # 综合集群zk个数和当前zk节点个数，可以做网络和节点故障的节点ip(管理网ip)列表

CHECKBADOBJ_WAIT_TIME = 300    # 故障完成后到检查坏对象的等待时间, 单位:s

wait_times = {'down_disk': [1, 300], 'del_disk': [300, 600],
              'down_net': [1, 300], 'del_node': [600, 1200]}


'''
提供给管理网和数据网复用的环境使用。
1、如果管理网和数据网分开的，这个字典不用填写。
2、如果管理网和数据网复用的环境，需要填写每个节点的一个非管理网的ip（可以ping通）
数据类型是字典，键是节点的管理网ip，值是空闲的ip
举例：FREE_IP_DIR = {"10.2.40.1":"20.10.10.1", "10.2.40.2":"20.10.10.2"}
"10.2.40.1"是管理网ip，"20.10.10.1"是数据网没有使用的ip，需要填写所有集群ip
'''
FREE_IP_DIR = {}

global MGR_DATA_IP_SAME    # 管理网和数据网是否复用的标志


'''***********************************   日志记录   ***********************************'''


##############################################################################
# ##name  :      log_init
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 日志模块初始化
##############################################################################
def log_init():
    file_path = os.path.split(os.path.realpath(__file__))[0]
    file_name = os.path.basename(__file__)
    file_name = file_name[:-3]
    now_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    file_name = now_time + '_' + file_name + '.log'
    file_name = os.path.join(file_path, file_name)
    print file_name
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(levelname)s][%(asctime)s]%(lineno)d:  %(message)s',
                        datefmt='%y-%m-%d %H:%M:%S',
                        filename=file_name,
                        filemode='a')

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s][%(asctime)s]   %(message)s', '%y-%m-%d %H:%M:%S')
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)
    return

'''***********************************   down disk   ***********************************'''


##############################################################################
# ##name  :      get_share_monopoly_disk_ids
# ##parameter:   node_id:节点id
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 获取本节点的所有共享硬盘和数据硬盘
##############################################################################
def get_share_monopoly_disk_ids(node_id):
    cmd = ("pscli --command=get_disks --node_ids=%s" % node_id)
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        msg = json_loads(stdout)
        share_disk_names = []
        monopoly_disk_names = []
        disks_pool = msg['result']['disks']
        for disk in disks_pool:
            if disk['usage'] == 'SHARED' and disk['usedState'] == 'IN_USE' and disk['state'] == 'DISK_STATE_HEALTHY':
                share_disk_names.append(disk['devname'])
            elif disk['usage'] == 'DATA' and disk['usedState'] == 'IN_USE' and disk['state'] == 'DISK_STATE_HEALTHY':
                monopoly_disk_names.append(disk['devname'])

    return share_disk_names, monopoly_disk_names


##############################################################################
# ##name  :      get_physicalid_by_name
# ##parameter:   node_ip:节点ip
# ##             disk_name:硬盘名字
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 获取某个节点的一个硬盘的物理id （2:0:0:1）
##############################################################################
def get_physicalid_by_name(node_ip, disk_name):
    cmd = 'lsscsi'
    rc, stdout = command(cmd, node_ip)
    if 0 != rc:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        list_stdout = stdout.strip().split('\n')
        for mem in list_stdout:
            if disk_name in mem:
                list_mem = mem.split()
                id = list_mem[0]
                id = id[1:-1]
                return id
    return None


##############################################################################
# ##name  :      remove_disk
# ##parameter:   node_ip:节点ip
# ##             disk_id:硬盘物理id
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 拔出某个节点的一个硬盘
##############################################################################
def remove_disk(node_ip, disk_id, disk_usage):
    cmd = 'echo scsi remove-single-device %s > /proc/scsi/scsi' % disk_id
    logging.info('node %s remove disk %s, disk usage is %s' % (node_ip, disk_id, disk_usage))
    rc, stdout = command(cmd, node_ip)
    if 0 != rc:
        logging.error('node %s remove disk %s fault!!!' % (node_ip, disk_id))
    return


##############################################################################
# ##name  :      insert_disk
# ##parameter:   node_ip:节点ip
# ##             disk_id:硬盘物理id
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 插入某个节点的一个硬盘
##############################################################################
def insert_disk(node_ip, disk_id, disk_usage):
    cmd = 'echo scsi add-single-device %s > /proc/scsi/scsi' % disk_id
    logging.info('node %s insert disk %s, disk usage is %s' % (node_ip, disk_id, disk_usage))
    rc, stdout = command(cmd, node_ip)
    if 0 != rc:
        logging.error('node %s add disk %s fault!!!' % (node_ip, disk_id))
    time.sleep(5)
    cmd = 'lsscsi'
    rc, stdout = command(cmd, node_ip)
    logging.info(stdout)
    return


##############################################################################
# ##name  :      choose_node_and_disk
# ##parameter:
# ##return:      fault_disk_lst:故障的磁盘，类型:列表，[node_ip, disk_name ]
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 按照参数-f的值随机选择f个要故障的磁盘
##############################################################################
def choose_node_and_disk():
    # 获取所有节点管理网
    node_ip_lst = get_nodes_ip()
    share_disk_lst = []
    monopoly_disk_lst = []
    for node_ip in node_ip_lst:
        node_id = get_node_id_by_ip(node_ip)

        # 获取节点中的硬盘
        share_disk_names, monopoly_disk_names = get_share_monopoly_disk_ids(node_id)
        for share_disk_name in share_disk_names:
            tmp_lst = [node_ip, share_disk_name]
            share_disk_lst.append(tmp_lst)
        for monopoly_disk_name in monopoly_disk_names:
            tmp_lst = [node_ip, monopoly_disk_name]
            monopoly_disk_lst.append(tmp_lst)

    all_disk_lst = share_disk_lst + monopoly_disk_lst

    # 根据参数随机获取一块磁盘
    disk_names_dir = {'all': all_disk_lst,
                      'data': monopoly_disk_lst,
                      'meta': share_disk_lst}

    """如果元数据盘小于等于副本数,则不做元数据盘故障"""
    if check_share_disk_fault(len(share_disk_lst)) is False:
        if FAULTDISKTYPE == 'meta':
            logging.warn("share disk num < replica num, can't make meta disk fault!!!")
            return -1, None
        else:
            tem_disk_lst = disk_names_dir.get('data')
    else:
        tem_disk_lst = disk_names_dir.get(FAULTDISKTYPE)

    # 如果磁盘总个数小于配置的-n，则报错退出
    if len(tem_disk_lst) < FAULTDISKNUM:
        logging.warn("The %s disk num is %d, less than -n %d" % (FAULTDISKTYPE, len(tem_disk_lst), FAULTDISKNUM))
        return -1, None

    if FAULTDISKTYPE == 'meta':
        fault_disk_lst = random.sample(tem_disk_lst, 1)
    elif FAULTDISKTYPE == 'all':
        for i in range(10):
            fault_disk_lst = random.sample(tem_disk_lst, FAULTDISKNUM)
            num = 0
            for fault_disk in fault_disk_lst:
                if fault_disk in share_disk_lst:
                    num += 1
            if num <= 1:
                break
        else:
            logging.warn("share can't fail more than 1 disk")
            return -1, None
    else:
        fault_disk_lst = random.sample(tem_disk_lst, FAULTDISKNUM)

    for fault_disk in fault_disk_lst:
        if fault_disk in share_disk_lst:
            start_time = time.time()
            while True:
                fault_node_ip = fault_disk[0]
                fault_node_id = get_node_id_by_ip(fault_node_ip)
                flag = check_metanode(fault_node_id)
                if flag is True:
                    logging.info("the node %s jnl is OK!" % (fault_node_ip))
                    break
                else:
                    exist_time = int(time.time() - start_time)
                    m, s = divmod(exist_time, 60)
                    h, m = divmod(m, 60)
                    logging.info("the node %s jnl is not OK %dh:%dm:%ds!!! can't fault!!!" % (fault_node_ip, h, m, s))
                    logging.info("wait 30s")
                    time.sleep(30)

    return 0, fault_disk_lst


##############################################################################
# ##name  :      run_down_disk
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 执行拔盘故障
##############################################################################
def run_down_disk_no_wait():
    # 随机选择故障节点和故障磁盘
    # 修改磁盘超时参数
    cmd = "pscli --command=update_param --section=MGR --name=disk_isolate2rebuild_timeout --current=18000000"
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.error('update param failed!!!')
        return False

    rc, fault_disk_lst = choose_node_and_disk()
    if rc != 0:
        logging.warn("can't select meta disk!!!")
        return

    fault_disk_info_lst = []
    for fault_disk in fault_disk_lst:
        fault_node_ip = fault_disk[0]
        fault_disk_name = fault_disk[1]
        fault_disk_phy_id = get_physicalid_by_name(fault_node_ip, fault_disk_name)
        fault_node_id = get_node_id_by_ip(fault_node_ip)
        fault_disk_usage = get_disk_usage_by_name(fault_node_id, fault_disk_name)
        fault_disk_uuid = get_disk_uuid_by_name(fault_node_id, fault_disk_name)

        tmp_dic = {"fault_node_ip": fault_node_ip,
                   "fault_node_id": fault_node_id,
                   "fault_disk_name": fault_disk_name,
                   "fault_disk_phy_id": fault_disk_phy_id,
                   "fault_disk_usage": fault_disk_usage,
                   "fault_disk_uuid": fault_disk_uuid
                   }
        fault_disk_info_lst.append(tmp_dic)

    # 拔盘
    for fault_disk_info in fault_disk_info_lst:
        fault_node_ip = fault_disk_info["fault_node_ip"]
        fault_disk_phy_id = fault_disk_info["fault_disk_phy_id"]
        fault_disk_usage = fault_disk_info["fault_disk_usage"]

        remove_disk(fault_node_ip, fault_disk_phy_id, fault_disk_usage)

    wait_time('down_disk')

    # 插盘
    for fault_disk_info in fault_disk_info_lst:
        fault_node_ip = fault_disk_info["fault_node_ip"]
        fault_disk_phy_id = fault_disk_info["fault_disk_phy_id"]
        fault_disk_usage = fault_disk_info["fault_disk_usage"]

        insert_disk(fault_node_ip, fault_disk_phy_id, fault_disk_usage)

    # 共享盘需要删除
    for fault_disk_info in fault_disk_info_lst:
        fault_node_ip = fault_disk_info["fault_node_ip"]
        fault_disk_usage = fault_disk_info["fault_disk_usage"]
        fault_node_id = fault_disk_info["fault_node_id"]
        fault_disk_uuid = fault_disk_info["fault_disk_uuid"]
        fault_disk_name = fault_disk_info["fault_disk_name"]
        if fault_disk_usage == 'SHARED':
            logging.info(
                'node %s delete disk %s, disk usage is %s' % (fault_node_ip, fault_disk_name, fault_disk_usage))
            fault_disk_id_old = get_disk_id_by_uuid(fault_node_id, fault_disk_uuid)
            delete_disk(fault_disk_id_old)
            logging.info('node %s delete disk %s success' % (fault_node_ip, fault_disk_name))

    logging.info("wait 30s")
    time.sleep(30)

    # 共享盘需要添加
    for fault_disk_info in fault_disk_info_lst:
        fault_node_ip = fault_disk_info["fault_node_ip"]
        fault_node_id = fault_disk_info["fault_node_id"]
        fault_disk_name = fault_disk_info["fault_disk_name"]
        fault_disk_usage = fault_disk_info["fault_disk_usage"]
        fault_disk_uuid = fault_disk_info['fault_disk_uuid']
        if fault_disk_usage == 'SHARED':
            logging.info(
                'node %s add disk %s, disk usage is %s' % (fault_node_ip, fault_disk_name, fault_disk_usage))
            add_disk(fault_node_id, fault_disk_uuid, fault_disk_usage)
            logging.info('node %s add disk %s success' % (fault_node_ip, fault_disk_name))
    return


##############################################################################
# ##name  :      down_disk_no_wait
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 拔盘故障入口函数(不等数据修复)
##############################################################################
def down_disk_no_wait():
    logging.info("***************** 1 down_disk_no_wait begin *****************")
    run_down_disk_no_wait()
    return


##############################################################################
# ##name  :      run_down_disk_wait
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 执行拔盘故障
##############################################################################
def run_down_disk_wait():
    # 修改磁盘超时参数
    cmd = "pscli --command=update_param --section=MGR --name=disk_isolate2rebuild_timeout --current=30000"
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.error('update param failed!!!')
        return False

    # 随机选择故障节点和故障磁盘
    rc, fault_disk_lst = choose_node_and_disk()
    if rc != 0:
        logging.warn("can't select meta disk!!!")
        return

    # 用字典记录磁盘信息
    fault_disk_info_lst = []
    for fault_disk in fault_disk_lst:
        fault_node_ip = fault_disk[0]
        fault_disk_name = fault_disk[1]
        fault_disk_phy_id = get_physicalid_by_name(fault_node_ip, fault_disk_name)
        fault_node_id = get_node_id_by_ip(fault_node_ip)
        fault_disk_uuid = get_disk_uuid_by_name(fault_node_id, fault_disk_name)
        fault_disk_usage = get_disk_usage_by_name(fault_node_id, fault_disk_name)
        tmp_dic = {"fault_node_ip": fault_node_ip,
                   "fault_node_id": fault_node_id,
                   "fault_disk_name": fault_disk_name,
                   "fault_disk_phy_id": fault_disk_phy_id,
                   "fault_disk_uuid": fault_disk_uuid,
                   "fault_disk_usage": fault_disk_usage}
        fault_disk_info_lst.append(tmp_dic)

        # 拔盘
        remove_disk(fault_node_ip, fault_disk_phy_id, fault_disk_usage)

    logging.info("waiting 60s")
    time.sleep(60)

    # 检查坏对象
    check_badobj()

    # 检查重建任务是否存在
    start_time = time.time()
    while True:
        if check_rebuild_job() is False:
            logging.info('rebuild job finish!!!')
            break
        time.sleep(20)
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        logging.info('rebuild job exist %dh:%dm:%ds' % (h, m, s))

    for fault_disk_info in fault_disk_info_lst:
        # 插盘
        fault_node_ip = fault_disk_info['fault_node_ip']
        fault_disk_phy_id = fault_disk_info['fault_disk_phy_id']
        fault_disk_usage = fault_disk_info["fault_disk_usage"]
        insert_disk(fault_node_ip, fault_disk_phy_id, fault_disk_usage)

    time.sleep(60)

    # 删除磁盘
    for fault_disk_info in fault_disk_info_lst:
        fault_node_id = fault_disk_info['fault_node_id']
        fault_disk_uuid = fault_disk_info['fault_disk_uuid']
        fault_node_ip = fault_disk_info['fault_node_ip']
        fault_disk_name = fault_disk_info['fault_disk_name']
        fault_disk_usage = fault_disk_info["fault_disk_usage"]
        fault_disk_id_old = get_disk_id_by_uuid(fault_node_id, fault_disk_uuid)
        storage_pool_id = get_storage_pool_id_by_diskid(fault_node_id, fault_disk_id_old)
        fault_disk_info['storage_pool_id'] = storage_pool_id

        logging.info('node %s delete disk %s, disk usage is %s' % (fault_node_ip, fault_disk_name, fault_disk_usage))
        delete_disk(fault_disk_id_old)
        logging.info('node %s delete disk %s success' % (fault_node_ip, fault_disk_name))

    time.sleep(300)

    # 加入磁盘
    for fault_disk_info in fault_disk_info_lst:
        fault_node_ip = fault_disk_info['fault_node_ip']
        fault_node_id = fault_disk_info['fault_node_id']
        fault_disk_name = fault_disk_info['fault_disk_name']
        fault_disk_uuid = fault_disk_info['fault_disk_uuid']
        fault_disk_usage = fault_disk_info['fault_disk_usage']
        logging.info('node %s add disk %s, disk usage is %s' % (fault_node_ip, fault_disk_name, fault_disk_usage))
        add_disk(fault_node_id, fault_disk_uuid, fault_disk_usage)
        logging.info('node %s add disk %s success' % (fault_node_ip, fault_disk_name))

        # 加入存储池
        if 'SHARED' != fault_disk_usage:
            fault_disk_id_new = get_disk_id_by_uuid(fault_node_id, fault_disk_uuid)
            storage_pool_id = fault_disk_info['storage_pool_id']
            logging.info('node %s add disk %s to storage_pool %s' % (fault_node_ip, fault_disk_name, storage_pool_id))
            expand_disk_2_storage_pool(storage_pool_id, fault_disk_id_new)
            logging.info('node %s add disk %s to storage_pool %s success'
                         % (fault_node_ip, fault_disk_name, storage_pool_id))

    # 恢复磁盘超时参数
    cmd = "pscli --command=update_param --section=MGR --name=disk_isolate2rebuild_timeout --current=18000000"
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.error('update param failed!!!')
        return False

    return


##############################################################################
# ##name  :      down_disk_no_wait
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 拔盘故障入口函数(等待数据修复)
##############################################################################
def down_disk_wait():
    logging.info("***************** 5 down_disk_wait begin *****************")
    run_down_disk_wait()
    return


'''***********************************   del disk   ***********************************'''


##############################################################################
# ##name  :      get_diskid_by_name
# ##parameter:   node_id:节点id
# ##             disk_name:硬盘名字
# ##return:      disk id
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 根据磁盘名字获取磁盘id
##############################################################################
def get_diskid_by_name(node_id, disk_name):
    cmd = "pscli --command=get_disks --node_ids=%s" % node_id
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        result = json_loads(stdout)
        disk_list = result['result']['disks']
        for disk in disk_list:
            if disk['devname'] == disk_name:
                return disk['id']
    return None


##############################################################################
# ##name  :      get_disk_id_by_uuid
# ##parameter:   node_id:节点id
# ##             disk_uuid：硬盘uuid
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 通过磁盘的uuid获取磁盘的id
##############################################################################
def get_disk_id_by_uuid(node_id, disk_uuid):
    cmd = "pscli --command=get_disks --node_ids=%s" % node_id
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        result = json_loads(stdout)
        disk_list = result['result']['disks']
        for disk in disk_list:
            if disk['uuid'] == disk_uuid:
                return disk['id']
    return None


##############################################################################
# ##name  :      get_disk_uuid_by_name
# ##parameter:   node_id:节点id
# ##             disk_name：硬盘名字
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 获取磁盘的uuid
##############################################################################
def get_disk_uuid_by_name(node_id, disk_name):
    cmd = "pscli --command=get_disks --node_ids=%s" % node_id
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        result = json_loads(stdout)
        disk_list = result['result']['disks']
        for disk in disk_list:
            if disk['devname'] == disk_name:
                return disk['uuid']
    return None


##############################################################################
# ##name  :      get_disk_usage_by_name
# ##parameter:   node_id:节点id
# ##             disk_name：硬盘名字
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 获取磁盘的usage
##############################################################################
def get_disk_usage_by_name(node_id, disk_name):
    cmd = "pscli --command=get_disks --node_ids=%s" % node_id
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        result = json_loads(stdout)
        disk_list = result['result']['disks']
        for disk in disk_list:
            if disk['devname'] == disk_name:
                return disk['usage']
    return None


##############################################################################
# ##name  :      delete_disk
# ##parameter:   disk_id:磁盘id
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 删盘
##############################################################################
def delete_disk(disk_id):
    cmd = "pscli --command=remove_disks --disk_ids=%s" % disk_id
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    return


##############################################################################
# ##name  :      delete_disk_noquery
# ##parameter:   disk_id:磁盘id
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 删盘(后台运行)
##############################################################################
def delete_disk_noquery(disk_id):
    cmd = "pscli --command=remove_disks --disk_ids=%s --auto_query=false" % disk_id
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    return


##############################################################################
# ##name  :      cancel_delete_disk
# ##parameter:   disk_id:磁盘id
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 取消删盘
##############################################################################
def cancel_delete_disk(disk_id):
    cmd = "pscli --command=cancel_remove_disks --disk_ids=%s" % disk_id
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    return


##############################################################################
# ##name  :      add_disk
# ##parameter:   node_ids:节点id
# ##             uuid:磁盘的uuid
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 加盘
##############################################################################
def add_disk(node_id, uuid, usage):
    cmd = ("pscli --command=add_disks --node_ids=%s --disk_uuids=%s --usage=%s" % (node_id, uuid, usage))
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    return


##############################################################################
# ##name  :      run_del_disk_no_wait
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 删除磁盘
##############################################################################
def run_del_disk_no_wait():
    # 随机选择故障节点和故障磁盘
    rc, fault_disk_lst = choose_node_and_disk()
    if rc != 0:
        logging.warn("can't select meta disk!!!")
        return

    fault_disk_info_lst = []
    for fault_disk in fault_disk_lst:
        fault_node_ip = fault_disk[0]
        fault_disk_name = fault_disk[1]
        fault_node_id = get_node_id_by_ip(fault_node_ip)
        fault_disk_id = get_diskid_by_name(fault_node_id, fault_disk_name)
        fault_disk_uuid = get_disk_uuid_by_name(fault_node_id, fault_disk_name)
        fault_disk_usage = get_disk_usage_by_name(fault_node_id, fault_disk_name)
        tmp_dic = {"fault_node_ip": fault_node_ip,
                   "fault_node_id": fault_node_id,
                   "fault_disk_name": fault_disk_name,
                   "fault_disk_id": fault_disk_id,
                   "fault_disk_uuid": fault_disk_uuid,
                   "fault_disk_usage": fault_disk_usage}
        fault_disk_info_lst.append(tmp_dic)

    for fault_disk_info in fault_disk_info_lst:
        # 删盘
        fault_node_ip = fault_disk_info['fault_node_ip']
        fault_disk_id = fault_disk_info['fault_disk_id']
        fault_disk_name = fault_disk_info['fault_disk_id']
        fault_node_id = fault_disk_info['fault_node_id']
        storage_pool_id = get_storage_pool_id_by_diskid(fault_node_id, fault_disk_id)
        fault_disk_info['storage_pool_id'] = storage_pool_id
        logging.info('delete node %s disk %s' % (fault_node_ip, fault_disk_name))
        delete_disk_noquery(fault_disk_id)

    wait_time('del_disk')

    # 检查盘是否存在
    for fault_disk_info in fault_disk_info_lst:
        fault_node_ip = fault_disk_info['fault_node_ip']
        fault_disk_id = fault_disk_info['fault_disk_id']
        fault_disk_name = fault_disk_info['fault_disk_id']
        fault_disk_uuid = fault_disk_info['fault_disk_uuid']
        fault_disk_usage = fault_disk_info['fault_disk_usage']
        if 0 == get_diskid_by_name(fault_node_id, fault_disk_name):
            logging.info('add node %s disk %s' % (fault_node_ip, fault_disk_name))
            add_disk(fault_node_id, fault_disk_uuid, fault_disk_usage)
            if 'SHARED' != fault_disk_usage:
                storage_pool_id = fault_disk_info['storage_pool_id']
                fault_disk_id_new = get_disk_id_by_uuid(fault_node_id, fault_disk_uuid)
                logging.info('add node %s disk %s to storage_pool %s' %
                             (fault_node_ip, fault_disk_name, storage_pool_id))
                expand_disk_2_storage_pool(storage_pool_id, fault_disk_id_new)
        else:
            logging.info('cancel delete node %s disk %s' % (fault_node_ip, fault_disk_name))
            cancel_delete_disk(fault_disk_id)

    return


##############################################################################
# ##name  :      del_disk_no_wait
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 删除磁盘入口函数(不等待数据迁移完成)
##############################################################################
def del_disk_no_wait():
    logging.info("***************** 2 del_disk_no_wait begin *****************")
    run_del_disk_no_wait()
    return


def run_del_disk_wait():
    # 随机选择故障节点和故障磁盘
    rc, fault_disk_lst = choose_node_and_disk()
    if rc != 0:
        logging.warn("can't select meta disk!!!")
        return

    # 用字典记录磁盘信息
    fault_disk_info_lst = []
    for fault_disk in fault_disk_lst:
        fault_node_ip = fault_disk[0]
        fault_disk_name = fault_disk[1]
        fault_node_id = get_node_id_by_ip(fault_node_ip)
        fault_disk_id_old = get_diskid_by_name(fault_node_id, fault_disk_name)
        fault_disk_uuid = get_disk_uuid_by_name(fault_node_id, fault_disk_name)
        fault_disk_usage = get_disk_usage_by_name(fault_node_id, fault_disk_name)
        storage_pool_id = get_storage_pool_id_by_diskid(fault_node_id, fault_disk_id_old)
        tmp_dic = {"fault_node_ip": fault_node_ip,
                   "fault_node_id": fault_node_id,
                   "fault_disk_name": fault_disk_name,
                   "fault_disk_uuid": fault_disk_uuid,
                   "fault_disk_usage": fault_disk_usage,
                   "fault_disk_id_old": fault_disk_id_old,
                   "storage_pool_id": storage_pool_id
                   }
        fault_disk_info_lst.append(tmp_dic)

    # 删盘
    for fault_disk_info in fault_disk_info_lst:
        fault_node_ip = fault_disk_info['fault_node_ip']
        fault_disk_name = fault_disk_info['fault_disk_name']
        fault_disk_id_old = fault_disk_info['fault_disk_id_old']
        fault_disk_usage = fault_disk_info["fault_disk_usage"]
        logging.info('delete node %s disk %s, disk usage is %s' % (fault_node_ip, fault_disk_name, fault_disk_usage))
        delete_disk_noquery(fault_disk_id_old)

    start_time = time.time()
    for fault_disk_info in fault_disk_info_lst:
        fault_node_ip = fault_disk_info['fault_node_ip']
        fault_node_id = fault_disk_info['fault_node_id']
        fault_disk_name = fault_disk_info['fault_disk_name']
        # 检查磁盘是否删除
        while True:
            if 0 == get_diskid_by_name(fault_node_id, fault_disk_name):
                logging.info('node %s disk %s delete success!!!' % (fault_node_ip, fault_disk_name))
                break
            time.sleep(20)
            exist_time = int(time.time() - start_time)
            m, s = divmod(exist_time, 60)
            h, m = divmod(m, 60)
            logging.info('node %s disk %s delete %dh:%dm:%ds' % (fault_node_ip, fault_disk_name, h, m, s))

    # 检查重建任务是否存在
    while True:
        if check_rebuild_job() is False:
            logging.info('rebuild job finish!!!')
            break
        time.sleep(20)
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        logging.info('rebuild job exist %dh:%dm:%ds' % (h, m, s))

    # 添加磁盘
    time.sleep(300)
    for fault_disk_info in fault_disk_info_lst:
        fault_node_ip = fault_disk_info['fault_node_ip']
        fault_node_id = fault_disk_info['fault_node_id']
        fault_disk_name = fault_disk_info['fault_disk_name']
        fault_disk_uuid = fault_disk_info['fault_disk_uuid']
        fault_disk_usage = fault_disk_info['fault_disk_usage']
        storage_pool_id = fault_disk_info['storage_pool_id']
        logging.info('add node %s disk %s, disk usage is %s' % (fault_node_ip, fault_disk_name, fault_disk_usage))
        add_disk(fault_node_id, fault_disk_uuid, fault_disk_usage)

        # 添加磁盘到存储池
        if 'SHARED' != fault_disk_usage:
            fault_disk_id_new = get_disk_id_by_uuid(fault_node_id, fault_disk_uuid)
            logging.info('add node %s disk %s to storage_pool %s' % (fault_node_ip, fault_disk_name, storage_pool_id))
            expand_disk_2_storage_pool(storage_pool_id, fault_disk_id_new)

    return


def del_disk_wait():
    logging.info("***************** 6 del_disk_wait begin *****************")
    run_del_disk_wait()


'''***********************************   down net   ***********************************'''


##############################################################################
# ##name  :      exchange_maskint
# ##parameter:   mask_int: int型的掩码
# ##return:      *.*.*.*型的掩码
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 将int掩码转换成str掩码
##############################################################################
def exchange_maskint(mask_int):
    bin_arr = ['0'] * 32
    for i in range(mask_int):
        bin_arr[i] = '1'
    tmpmask = [''.join(bin_arr[i * 8:i * 8 + 8]) for i in range(4)]
    tmpmask = [str(int(tmpstr, 2)) for tmpstr in tmpmask]
    return '.'.join(tmpmask)


##############################################################################
# ##name  :      get_net_eth
# ##parameter:
# ##return:      eth_list:列表，成员是字典{"eth":"eth1", "ip":"10.2.41.101", "mask":"255.255.252.0"}
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 获取一个节点所有数据网的网卡名字、ip和掩码
##############################################################################
def get_net_eth(node_id, node_ip):
    '''获取本节点的数据网的eth名字'''
    cmd = "pscli --command=get_nodes --ids=%s" % node_id

    data_ip_list = []
    rc, stdout = run_command(cmd)
    if 0 != rc:
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        result = json_loads(stdout)
        data_ips = result['result']['nodes'][0]['data_ips']
        for data_ip in data_ips:
            ip = data_ip['ip_address']
            data_ip_list.append(ip)

    eth_list = []
    for ip in data_ip_list:
        tem_dic = {}
        cmd1 = 'ip addr | grep %s' % ip
        rc, stdout = command(cmd1, node_ip)
        if 0 != rc:
            raise Exception(
                "Execute command: \"%s\" failed. \nstdout: %s" % (cmd1, stdout))
        else:
            eth_name = stdout.split()[-1]
            mask = stdout.split()
            tem_dic["eth"] = eth_name

        cmd2 = 'ifconfig | grep %s' % ip
        rc, stdout = command(cmd2, node_ip)
        if 0 != rc:
            raise Exception(
                "Execute command: \"%s\" failed. \nstdout: %s" % (cmd2, stdout))
        else:
            mask = stdout.strip().split()[3]
            tem_dic["dataip"] = ip
            tem_dic["mgrip"] = node_ip
            tem_dic["mask"] = mask

        eth_list.append(tem_dic)
    return eth_list


##############################################################################
# ##name  :      run_down_net
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: ifdown一个节点的所有数据eth
##############################################################################
def run_down_net(node_ip, eth_lst):
    for eth in eth_lst:
        cmd = 'ifdown %s' % eth
        logging.info("node %s ifdown %s" % (node_ip, eth))
        rc, stdout = command(cmd, node_ip)
        if 0 != rc:
            logging.warn("node %s  ifdown %s failed!!!" % (node_ip, eth))
    return


##############################################################################
# ##name  :      run_up_net
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: ifup一个节点的所有数据eth
##############################################################################
def run_up_net(node_ip, eth_lst):
    for eth in eth_lst:
        cmd = 'ifup %s' % eth
        logging.info("node %s ifup %s" % (node_ip, eth))
        rc, stdout = command(cmd, node_ip)
        if 0 != rc:
            logging.warn("node %s ifup %s failed!!!" % (node_ip, eth))
    return


##############################################################################
# ##name  :      net_fault
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 做网络故障
##############################################################################
def net_fault_no_wait():
    # 获取集群所有节点的管理ip
    if len(NODE_IP_LST) == 1 and LOCALNODEIP in NODE_IP_LST:
        logging.error("one node system can't down net!!!")
        raise Exception("one node system can't down net!!!")

    # 修改节点isolate参数
    cmd = 'pscli --command=update_param --section=MGR --name=node_isolate_timeout --current=86400000'
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.warn("update param failed!!!")

    while True:
        fault_node_ip = random.choice(NODE_IP_LST)
        if fault_node_ip != LOCALNODEIP:
            break

    fault_node_id = get_node_id_by_ip(fault_node_ip)

    start_time = time.time()
    while True:
        flag = check_metanode(fault_node_id)
        if flag is True:
            logging.info("the node %s jnl is OK!" % (fault_node_ip))
            break
        else:
            exist_time = int(time.time() - start_time)
            m, s = divmod(exist_time, 60)
            h, m = divmod(m, 60)
            logging.info("the node %s jnl is not OK %dh:%dm:%ds!!! can't fault!!!" % (fault_node_ip, h, m, s))
            logging.info("wait 30s, re select node")
            time.sleep(30)

    eth_info_lst = get_net_eth(fault_node_id, fault_node_ip)
    eth_lst = []
    for tem in eth_info_lst:
        eth_lst.append(tem['eth'])

    if MGR_DATA_IP_SAME is True:
        fault_node_free_ip = FREE_IP_DIR[fault_node_ip]
    else:
        fault_node_free_ip = fault_node_ip

    # down所有数据网
    run_down_net(fault_node_free_ip, eth_lst)

    wait_time('down_net')

    # up所有数据网
    run_up_net(fault_node_free_ip, eth_lst)

    time.sleep(30)

    return


##############################################################################
# ##name  :      down_net_no_wait
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 网络故障入口函数(不等数据修复完成，就恢复故障)
##############################################################################
def down_net_no_wait():
    logging.info("***************** 2 down_net_no_wait begin *****************")
    net_fault_no_wait()
    return


def net_fault_wait():
    # 修改节点isolate参数
    cmd = 'pscli --command=update_param --section=MGR --name=node_isolate_timeout --current=120000'
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.warn("update param failed!!!")

    if len(NODE_IP_LST) == 1 and LOCALNODEIP in NODE_IP_LST:
        logging.error("one node system can't down net!!!")
        raise Exception("one node system can't down net!!!")

    fault_node_ip = random.choice(FAULT_NODE_IP_LST)
    fault_node_id = get_node_id_by_ip(fault_node_ip)
    start_time = time.time()
    while True:
        flag = check_metanode(fault_node_id)
        if flag is True:
            logging.info("the node %s jnl is OK!" % (fault_node_ip))
            break
        else:
            exist_time = int(time.time() - start_time)
            m, s = divmod(exist_time, 60)
            h, m = divmod(m, 60)
            logging.info("the node %s jnl is not OK %dh:%dm:%ds!!! can't fault!!!" % (fault_node_ip, h, m, s))
            logging.info("wait 30s, re select node")
            time.sleep(30)

    eth_info_lst = get_net_eth(fault_node_id, fault_node_ip)
    eth_lst = []
    for tem in eth_info_lst:
        eth_lst.append(tem['eth'])

    if MGR_DATA_IP_SAME is True:
        fault_node_free_ip = FREE_IP_DIR[fault_node_ip]
    else:
        fault_node_free_ip = fault_node_ip

    # down所有数据网
    run_down_net(fault_node_free_ip, eth_lst)

    # 检查坏对象是否修复
    logging.info("waiting 150s")
    time.sleep(150)

    check_badobj(fault_ip=fault_node_ip)

    # 检查重建任务是否存在
    start_time = time.time()
    while True:
        if check_rebuild_job(fault_node_ip) is False:
            logging.info('rebuild job finish!!!')
            break
        time.sleep(20)
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        logging.info('rebuild job exist %dh:%dm:%ds' % (h, m, s))

    # up所有数据网
    run_up_net(fault_node_free_ip, eth_lst)

    time.sleep(30)

    # 修改回超时时间的参数
    cmd = "pscli --command=update_param --section=MGR --name=node_isolate_timeout --current=86400000"
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.warn("update param failed!!!")

    # 生成节点的配置文件
    config_file = make_node_xml(fault_node_id)
    # 获取节点所在的节点池的id
    node_pool_id = get_nodepoolid_by_nodeid(fault_node_id)
    # 获取节点中所有磁盘与存储池的对应关系
    relation_lst = get_node_storage_pool_rel(fault_node_id)

    # 删除节点
    del_node(fault_node_id, auto_query=True)

    time.sleep(60)

    # 添加节点
    add_node(config_file)

    time.sleep(60)

    node_id_new = get_node_id_by_ip(fault_node_ip)

    # 添加节点到节点池中
    add_node_2_nodpool(node_pool_id, node_id_new)

    # 启动系统
    startup()

    # 将节点中的所有磁盘添加到对应的存储池
    add_node_disks_2_storagepool(node_id_new, relation_lst)
    return


def down_net_wait():
    logging.info("***************** 7 down_net_wait begin *****************")
    net_fault_wait()
    return


'''***********************************   down node   ***********************************'''


##############################################################################
# ##name  :      get_ipmi_ip
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 获取指定节点的ipmi ip
##############################################################################
def get_ipmi_ip(node_ip):
    cmd = 'ipmitool lan print'
    rc, stdout = command(cmd, node_ip)
    if 0 != rc:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        return None
    else:
        lines_lst = stdout.strip().split('\n')
        for line in lines_lst:
            if 'IP Address  ' in line:
                ip = line.split(':')[-1].strip()
                return ip
        return None


##############################################################################
# ##name  :      run_down_node
# ##parameter:   ipmi_ip:ipmi地址
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 通过ipmi下电节点
##############################################################################
def run_down_node(ipmi_ip):
    cmd1 = 'ipmitool -H %s -I lan -U admin -P admin power off' % ipmi_ip
    cmd2 = 'ipmitool -H %s -I lan -U ADMIN -P ADMIN power off' % ipmi_ip
    rc, stdout = run_command(cmd1)
    if 0 != rc:
        if 'Invalid user name' in stdout:
            rc, stdout = run_command(cmd2)
            if 0 != rc:
                return False
            else:
                return True
        else:
            return False
    else:
        return True


##############################################################################
# ##name  :      run_up_node
# ##parameter:   ipmi_ip:ipmi地址
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 通过ipmi上电节点
##############################################################################
def run_up_node(ipmi_ip):
    cmd1 = 'ipmitool -H %s -I lan -U admin -P admin power on' % ipmi_ip
    cmd2 = 'ipmitool -H %s -I lan -U ADMIN -P ADMIN power on' % ipmi_ip
    rc, stdout = run_command(cmd1)
    if 0 != rc:
        if 'Invalid user name' in stdout:
            rc, stdout = run_command(cmd2)
            if 0 != rc:
                return False
            else:
                return True
        else:
            return False
    else:
        return True


##############################################################################
# ##name  :      down_node_no_wait
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 下电节点入口函数(不等数据修复完成)
##############################################################################
def down_node_no_wait():
    logging.info("***************** 3 down_node_no_wait begin *****************")

    if len(NODE_IP_LST) == 1 and LOCALNODEIP in NODE_IP_LST:
        logging.error("one node system can't down net!!!")
        raise Exception("one node system can't down net!!!")

    while True:
        fault_node_ip = random.choice(NODE_IP_LST)
        if fault_node_ip != LOCALNODEIP:
            break
    fault_node_id = get_node_id_by_ip(fault_node_ip)
    start_time = time.time()
    while True:
        flag = check_metanode(fault_node_id)
        if flag is True:
            logging.info("the node %s jnl is OK!" % (fault_node_ip))
            break
        else:
            exist_time = int(time.time() - start_time)
            m, s = divmod(exist_time, 60)
            h, m = divmod(m, 60)
            logging.info("the node %s jnl is not OK %dh:%dm:%ds!!! can't fault!!!" % (fault_node_ip, h, m, s))
            logging.info("wait 30s, re select node")
            time.sleep(30)

    # 获取ipmi地址
    ipmi_ip = get_ipmi_ip(fault_node_ip)
    if ipmi_ip is None:
        logging.error("ipmi is not exist, can't down node!!!")
        return

    # 检查ipmi是否可以ping通
    if check_ping(ipmi_ip) is False:
        logging.error("ipmi %s ping failed!!!" % ipmi_ip)
        return

    # 下电
    if run_down_node(ipmi_ip) is False:
        logging.error("node %s down failed!!!" % fault_node_ip)
        return
    logging.info('down node %s' % fault_node_ip)

    logging.info("wait 600 s")
    time.sleep(600)

    # 上电
    if run_up_node(ipmi_ip) is False:
        logging.error("node %s up failed!!!" % fault_node_ip)
        return
    logging.info('up node %s' % fault_node_ip)

    return


##############################################################################
# ##name  :      run_down_node_wait
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 执行下电节点(等数据修复完成)
##############################################################################
def run_down_node_wait():
    # 修改节点isolate参数
    cmd = 'pscli --command=update_param --section=MGR --name=node_isolate_timeout --current=120000'
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.warn("update param failed!!!")

    if len(NODE_IP_LST) == 1 and LOCALNODEIP in NODE_IP_LST:
        logging.error("one node system can't down net!!!")
        raise Exception("one node system can't down net!!!")

    fault_node_ip = random.choice(FAULT_NODE_IP_LST)
    fault_node_id = get_node_id_by_ip(fault_node_ip)
    start_time = time.time()
    while True:
        flag = check_metanode(fault_node_id)
        if flag is True:
            logging.info("the node %s jnl is OK!" % (fault_node_ip))
            break
        else:
            exist_time = int(time.time() - start_time)
            m, s = divmod(exist_time, 60)
            h, m = divmod(m, 60)
            logging.info("the node %s jnl is not OK %dh:%dm:%ds!!! can't fault!!!" % (fault_node_ip, h, m, s))
            logging.info("wait 30s, re select node")
            time.sleep(30)

    # 获取ipmi地址
    ipmi_ip = get_ipmi_ip(fault_node_ip)
    if ipmi_ip is None:
        logging.error("ipmi is not exist, can't down node!!!")
        return

    # 检查ipmi是否可以ping通
    if check_ping(ipmi_ip) is False:
        logging.error("ipmi %s ping failed!!!" % ipmi_ip)
        return

    # 下电
    logging.info('down node %s' % fault_node_ip)
    if run_down_node(ipmi_ip) is False:
        logging.error("node %s down failed!!!" % fault_node_ip)
        return

    # 检查坏对象是否修复
    logging.info("waiting 150s")
    time.sleep(150)

    check_badobj()

    # 检查重建任务是否存在
    start_time = time.time()
    while True:
        if check_rebuild_job(fault_node_ip) is False:
            logging.info('rebuild job finish!!!')
            break
        time.sleep(20)
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        logging.info('rebuild job exist %dh:%dm:%ds' % (h, m, s))

    # 上电
    logging.info('up node %s' % fault_node_ip)
    if run_up_node(ipmi_ip) is False:
        logging.error("node %s up failed!!!" % fault_node_ip)
        return

    # 不断ping节点，知道可以ping通
    num = 0
    while True:
        time.sleep(20)
        if check_ping(fault_node_ip) is not False:
            time.sleep(120)
            break
        num += 1
        logging.info('node %s cannot ping pass %ds' % (fault_node_ip, num*20))

    time.sleep(60)

    # 修改回超时时间的参数
    cmd = "pscli --command=update_param --section=MGR --name=node_isolate_timeout --current=86400000"
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.warn("update param failed!!!")

    fault_node_id = get_node_id_by_ip(fault_node_ip)
    # 生成节点的配置文件
    config_file = make_node_xml(fault_node_id)
    # 获取节点所在的节点池的id
    node_pool_id = get_nodepoolid_by_nodeid(fault_node_id)
    # 获取节点中所有磁盘与存储池的对应关系
    relation_lst = get_node_storage_pool_rel(fault_node_id)

    # 删除节点
    del_node(fault_node_id, auto_query=False)

    time.sleep(60)

    # 添加节点
    add_node(config_file)

    time.sleep(60)

    node_id_new = get_node_id_by_ip(fault_node_ip)

    # 添加节点到节点池中
    add_node_2_nodpool(node_pool_id, node_id_new)

    # 启动系统
    startup()

    # 将节点中的所有磁盘添加到对应的存储池
    add_node_disks_2_storagepool(node_id_new, relation_lst)

    return


##############################################################################
# ##name  :      down_node_wait
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 下电节点入口函数(等数据修复完成)
##############################################################################
def down_node_wait():
    logging.info("***************** 8 down_node_wait begin *****************")
    run_down_node_wait()


'''***********************************   move node   ***********************************'''


##############################################################################
# ##name  :      makeEasyTag
# ##parameter:   dom：xml对象
# ##             tagname：元素标签名字
# ##             value：文本节点内容
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 生成元素节点（子节点为文本节点）
##############################################################################
def make_text_tag(dom, tagname, value):
    tag = dom.createElement(tagname)
    text = dom.createTextNode(value)
    tag.appendChild(text)
    return tag


##############################################################################
# ##name  :      make_element_tag
# ##parameter:   dom：xml对象
# ##             parent_tag：父元素标签名字
# ##             child_tagname：子元素标签名字
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 生成元素节点（子节点为元素节点）
##############################################################################
def make_element_tag(dom, parent_tag, child_tagname):
    child_tag = dom.createElement(child_tagname)
    parent_tag.appendChild(child_tag)
    return child_tag


##############################################################################
# ##name  :      get_sysinfo
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 获取系统信息
##############################################################################
def get_sysinfo():
    cmd = 'pscli --command=get_cluster_overview'
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        sys.exit(1)
    else:
        sys_info = json_loads(stdout)
        sys_name = sys_info['result']['name']
        sys_id = sys_info['result']['sysid']
        sys_uuid = sys_info['result']['uuid']
    return sys_name, sys_id, sys_uuid


##############################################################################
# ##name  :      xml_add_sysinfo
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 向xml中添加系统信息
##############################################################################
def xml_add_sysinfo(dom, root):
    sys_name, sys_id, sys_uuid = get_sysinfo()
    uuid = make_text_tag(dom, 'uuid', sys_uuid)
    sysid = make_text_tag(dom, 'sysid', str(sys_id))
    name = make_text_tag(dom, 'name', sys_name)
    package_path = make_text_tag(dom, 'package_path', '')
    root.appendChild(uuid)
    root.appendChild(sysid)
    root.appendChild(name)
    root.appendChild(package_path)
    return


##############################################################################
# ##name  :      xml_add_cache_ratio
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 向xml中添加缓存占比信息
##############################################################################
def xml_add_cache_ratio(dom, root):
    cmd = 'pscli --command=get_params --section=MGR --name=shared_pool_cache_ratio'
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        sys.exit(1)
    else:
        cache_ratio_info = json_loads(stdout)
        cache_ratio_value = cache_ratio_info['result']['parameters'][0]['current']
    cache_ratio = make_text_tag(dom, 'cache_ratio', cache_ratio_value)
    root.appendChild(cache_ratio)
    return


##############################################################################
# ##name  :      xml_add_scenario_id
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 向xml中添加缓存文件系统类型
##############################################################################
def xml_add_scenario_id(dom, root):
    scenario_id_value = '1'
    scenario_id = make_text_tag(dom, 'scenario_id', scenario_id_value)
    root.appendChild(scenario_id)
    return


##############################################################################
# ##name  :      xml_add_eache_set
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 向xml中添加缓存SSD cache
##############################################################################
def xml_add_eache_set(dom, root):
    cache_set_value = '0'
    enable_cache_set = make_text_tag(dom, 'enable_cache_set', cache_set_value)
    root.appendChild(enable_cache_set)
    return


##############################################################################
# ##name  :      get_cabinetinfo
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 获取机柜信息
##############################################################################
def get_cabinetinfo():
    cmd = 'pscli --command=get_cabinets'
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        sys.exit(1)
    else:
        cabinet_lst = []
        cabinet_info = json_loads(stdout)
        cabinets = cabinet_info['result']['cabinets']
        for cabinet in cabinets:
            height = cabinet['height']
            name = cabinet['name']
            cabinet_lst.append([name, height])
    return cabinet_lst


##############################################################################
# ##name  :      xml_add_cabinetinfo
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 向xml中添加机柜信息
##############################################################################
def xml_add_cabinetinfo(dom, root):
    cabinet_lst = get_cabinetinfo()
    xml_cabinets = make_element_tag(dom, root, 'cabinets')
    for cabinet in cabinet_lst:
        name = make_text_tag(dom, 'name', cabinet[0])
        height = make_text_tag(dom, 'height', str(cabinet[1]))
        xml_cabinet = make_element_tag(dom, xml_cabinets, 'cabinet')
        xml_cabinet.appendChild(name)
        xml_cabinet.appendChild(height)

    return


##############################################################################
# ##name  :      xml_add_nodeip
# ##parameter:   type:ip类型('ctl_ips', 'data_ips')
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 向xml中添加节点ip信息
##############################################################################
def xml_add_nodeip(dom, node, node_info, type):
    ctl_ips = make_element_tag(dom, node, type)
    ctl_ips_info = node_info[type]
    for crl_ip_info in ctl_ips_info:
        ip = make_text_tag(dom, 'ip', crl_ip_info['ip_address'])
        ctl_ips.appendChild(ip)
    return


##############################################################################
# ##name  :      xml_add_ipmiinfo
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 向xml中添加节点ipmi信息
##############################################################################
def xml_add_ipmiinfo(dom, node):
    ipmi = make_element_tag(dom, node, 'ipmi')
    ip = make_text_tag(dom, 'ip', '10.0.10.1')
    username = make_text_tag(dom, 'username', 'ipmi_username')
    password = make_text_tag(dom, 'password', 'ipmi_password')
    ipmi.appendChild(ip)
    ipmi.appendChild(username)
    ipmi.appendChild(password)
    return


##############################################################################
# ##name  :      xml_add_nodevs
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 向xml中添加节点nodevs信息
##############################################################################
def xml_add_nodevs(dom, node):
    nvdevs = make_element_tag(dom, node, 'nvdevs')
    device = make_element_tag(dom, nvdevs, 'device')
    sn = make_text_tag(dom, 'sn', 'nvdev1_sn')
    uuid = make_text_tag(dom, 'uuid', 'fdsfssf-42342-322-fsd')
    device.appendChild(sn)
    device.appendChild(uuid)
    return


##############################################################################
# ##name  :      xml_add_zkinfo
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 向xml中添加节点zk信息
##############################################################################
def xml_add_zkinfo(dom, node, node_info):
    zookeeper = make_element_tag(dom, node, 'zookeeper')
    # zk_ip = node_info['zk_ips'][0]
    # zk_id = node_info['zk_id']
    zk_ip = ''
    zk_id = 0
    ip = make_text_tag(dom, 'ip', zk_ip)
    id = make_text_tag(dom, 'id', str(zk_id))
    zookeeper.appendChild(ip)
    zookeeper.appendChild(id)
    return


##############################################################################
# ##name  :      xml_add_service
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 向xml中添加节点服务信息
##############################################################################
def xml_add_service(dom, node, node_info):
    services = make_element_tag(dom, node, 'services')
    services_info = node_info['services']
    for service_info in services_info:
        if service_info['service_type'] in ['oStor', 'oPara']:
            service = make_element_tag(dom, services, 'service')
            type = make_text_tag(dom, 'type', service_info['service_type'])
            service.appendChild(type)
    return


##############################################################################
# ##name  :      xml_add_diskinfo
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 向xml中添加节点硬盘信息
##############################################################################
def xml_add_diskinfo(dom, node, node_info):
    disks = make_element_tag(dom, node, 'disks')
    data_disks_info = node_info['data_disks']
    share_disks_info = node_info['shared_disks']
    disks_info = data_disks_info + share_disks_info
    for disk_info in disks_info:
        disk = make_element_tag(dom, disks, 'disk')
        dev_name = make_text_tag(dom, 'dev_name', disk_info['devname'])
        usage = make_text_tag(dom, 'usage', disk_info['usage'])
        state = make_text_tag(dom, 'state', 'FREE')
        disk.appendChild(dev_name)
        disk.appendChild(usage)
        disk.appendChild(state)
    return


##############################################################################
# ##name  :      xml_add_nodeinfo
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 向xml中添加节点信息
##############################################################################
def xml_add_nodeinfo(dom, root, node_id):
    nodes = make_element_tag(dom, root, 'nodes')
    node = make_element_tag(dom, nodes, 'node')
    cmd = 'pscli --command=get_nodes --ids=%s' % node_id
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        sys.exit(1)
    else:
        node_json = json_loads(stdout)
        node_info = node_json['result']['nodes'][0]

    # 添加节点名
    hostname_value = node_info['node_name']
    hostname = make_text_tag(dom, 'hostname', hostname_value)
    node.appendChild(hostname)

    # 添加节点管理ip
    xml_add_nodeip(dom, node, node_info, 'ctl_ips')

    # 添加节点数据ip
    xml_add_nodeip(dom, node, node_info, 'data_ips')

    # 添加haip
    ha_ips = make_text_tag(dom, 'ha_ips', '')
    node.appendChild(ha_ips)

    # 添加节点机柜信息
    cabinet = make_text_tag(dom, 'cabinet', node_info['cabinet_name'])
    position = make_text_tag(dom, 'position', str(node_info['position']))
    node_model = make_text_tag(dom, 'node_model', node_info['model'])
    node.appendChild(cabinet)
    node.appendChild(position)
    node.appendChild(node_model)

    # 添加ipmi信息
    xml_add_ipmiinfo(dom, node)

    # 添加nvdevs信息
    xml_add_nodevs(dom, node)

    # 添加zk信息
    xml_add_zkinfo(dom, node, node_info)

    # 添加service信息
    xml_add_service(dom, node, node_info)

    # 添加硬盘信息
    xml_add_diskinfo(dom, node, node_info)
    return


def make_node_xml(node_id):
    impl = xml.dom.minidom.getDOMImplementation()
    dom = impl.createDocument(None, 'install_config', None)
    root = dom.documentElement

    # 添加系统信息
    xml_add_sysinfo(dom, root)

    # 添加缓存占比
    xml_add_cache_ratio(dom, root)

    # 添加文件系统
    xml_add_scenario_id(dom, root)

    # 添加ssd cache开关
    xml_add_eache_set(dom, root)

    # 添加机柜信息
    xml_add_cabinetinfo(dom, root)

    # 添加节点信息
    xml_add_nodeinfo(dom, root, node_id)

    # 添加网络检查
    check_network = make_text_tag(dom, 'check_network', '1')
    root.appendChild(check_network)

    # 写到xml文件中
    domcopy = dom.cloneNode(True)
    indent_xml(domcopy, domcopy.documentElement)
    config_file = '/tmp/deploy_config_sample_node1.xml'
    with open(config_file, 'wb') as f:
        # f = file(config_file, 'wb')
        domcopy.writexml(f, encoding='utf-8')
        domcopy.unlink()
    if LOCALNODEFLAG is False:
        for node_ip in NODE_IP_LST:
            cmd = 'scp /tmp/deploy_config_sample_node1.xml root@%s:/tmp' % node_ip
            command(cmd)

    return config_file


##############################################################################
# ##name  :      Indent
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 将xml格式化
##############################################################################
def indent_xml(dom, node, indent=0):
    # Copy child list because it will change soon
    children = node.childNodes[:]
    # Main node doesn't need to be indented
    if indent:
        text = dom.createTextNode('\n' + '    ' * indent)
        node.parentNode.insertBefore(text, node)
    if children:
        # Append newline after last child, except for text nodes
        if children[-1].nodeType == node.ELEMENT_NODE:
            text = dom.createTextNode('\n' + '    ' * indent)
            node.appendChild(text)
        # Indent children which are elements
        for n in children:
            if n.nodeType == node.ELEMENT_NODE:
                indent_xml(dom, n, indent+1)
    return


##############################################################################
# ##name  :      add_node
# ##parameter:   config_file:节点配置文件
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 添加节点
##############################################################################
def add_node(config_file):
    cmd = 'pscli --command=add_nodes --config_file=%s' % config_file
    logging.info('add node')
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    return


##############################################################################
# ##name  :      del_node
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 删除节点
##############################################################################
def del_node(node_id, auto_query=False):
    node_ip = get_node_ip_by_id(node_id)
    if auto_query is False:
        cmd = 'pscli --command=remove_node --id=%s --auto_query=false' % node_id
    else:
        cmd = 'pscli --command=remove_node --id=%s' % node_id
    logging.info('delete node id %s' % node_id)
    rc, stdout = run_command(cmd, fault_node_ip=node_ip)
    if 0 != rc:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    return


##############################################################################
# ##name  :      cancel_del_node
# ##parameter:   node_id:节点id
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 取消删除节点
##############################################################################
def cancel_del_node(node_id):
    cmd = 'pscli --command=cancel_remove_nodes --ids=%s' % node_id
    logging.info('cancel delete node id %s' % node_id)
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    return


##############################################################################
# ##name  :      get_node_storage_pool_rel
# ##parameter:   node_id:节点id
# ##return:      relation_lst:列表，每一项都是列表，元素是磁盘的uuid和存储池的id
# ##             [[uuid1, storage_pool_id1], [uuid2, storage_pool_id2]]
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 获取节点中所有磁盘的uuid和存储池id的关系
##############################################################################
def get_node_storage_pool_rel(node_id):
    cmd = 'pscli --command=get_disks --node_ids=%s' % node_id
    relation_lst = []
    rc, stdout = run_command(cmd)
    if 0 != rc:
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        stdout = json_loads(stdout)
        disks_info = stdout['result']['disks']
        for disk_info in disks_info:
            if disk_info['usage'] != 'DATA' or disk_info['storagePoolId'] == 0:
                continue
            uuid = disk_info['uuid']
            storage_pool_id = disk_info['storagePoolId']
            lst = [uuid, storage_pool_id]
            relation_lst.append(lst)

    return relation_lst


##############################################################################
# ##name  :      add_node_2_nodpool
# ##parameter:   node_pool_id:节点池id
# ##             node_id:节点id
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 将节点加入到节点池
##############################################################################
def add_node_2_nodpool(node_pool_id, node_id):
    cmd = 'pscli --command=get_node_pools --id=%s' % node_pool_id
    node_id_lst = []
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        node_info = json_loads(stdout)
        node_id_lst = node_info['result']['node_pools'][0]['node_ids'][:]
        node_pool_name = node_info['result']['node_pools'][0]['name']

    node_id_lst.append(node_id)
    node_id_str = ','.join(map(str, node_id_lst))

    cmd = 'pscli --command=update_node_pool --node_pool_id=%s --name=%s --node_ids=%s' \
          % (node_pool_id, node_pool_name, node_id_str)
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))

    return


##############################################################################
# ##name  :      add_node_disks_2_storagepool
# ##parameter:   node_id：节点id
# ##             relation_lst:列表，每一项都是列表，元素是磁盘的uuid和存储池的id
# ##             [[uuid1, storage_pool_id1], [uuid2, storage_pool_id2]]
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 添加节点中所有磁盘到对应的存储池
##############################################################################
def add_node_disks_2_storagepool(node_id, relation_lst):
    cmd = 'pscli --command=get_disks --node_ids=%s' % node_id
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        stdout = json_loads(stdout)
        disks_info = stdout['result']['disks']
        for disk_info in disks_info:
            for rel_tem in relation_lst:
                if disk_info['uuid'] == rel_tem[0]:
                    rel_tem.append(disk_info['id'])
                    break

    for rel_tem in relation_lst:
        cmd = 'pscli --command=expand_storage_pool --storage_pool_id=%s --disk_ids=%s' % (rel_tem[1], rel_tem[2])
        rc, stdout = run_command(cmd)
        if 0 != rc:
            logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            raise Exception(
                "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))

    return


##############################################################################
# ##name  :      run_move_node_no_wait
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 执行删除节点(不等重建完成)
##############################################################################
def run_move_node_no_wait():
    if len(NODE_IP_LST) == 1 and LOCALNODEIP in NODE_IP_LST:
        logging.error("one node system can't down net!!!")
        raise Exception("one node system can't down net!!!")

    while True:
        fault_node_ip = random.choice(NODE_IP_LST)
        if fault_node_ip != LOCALNODEIP:
            break
    fault_node_id = get_node_id_by_ip(fault_node_ip)
    start_time = time.time()
    while True:
        flag = check_metanode(fault_node_id)
        if flag is True:
            logging.info("the node %s jnl is OK!" % (fault_node_ip))
            break
        else:
            exist_time = int(time.time() - start_time)
            m, s = divmod(exist_time, 60)
            h, m = divmod(m, 60)
            logging.info("the node %s jnl is not OK %dh:%dm:%ds!!! can't fault!!!" % (fault_node_ip, h, m, s))
            logging.info("wait 30s, re select node")
            time.sleep(30)

    fault_node_id = get_node_id_by_ip(fault_node_ip)

    # 删除节点
    del_node(fault_node_id)

    # 等待一段时间
    wait_time('del_node')

    # 取消删除节点
    cancel_del_node(fault_node_id)


##############################################################################
# ##name  :      move_node_no_wait
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 删除节点入口函数(不等重建完成)
##############################################################################
def move_node_no_wait():
    logging.info("***************** 5 move_node_no_wait begin *****************")
    run_move_node_no_wait()
    return


##############################################################################
# ##name  :      run_move_node_wait
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 执行删除节点(等重建完成)
##############################################################################
def run_move_node_wait():
    if len(NODE_IP_LST) == 1 and LOCALNODEIP in NODE_IP_LST:
        logging.error("one node system can't down net!!!")
        raise Exception("one node system can't down net!!!")

    fault_node_ip = random.choice(FAULT_NODE_IP_LST)
    fault_node_id = get_node_id_by_ip(fault_node_ip)
    start_time = time.time()
    while True:
        flag = check_metanode(fault_node_id)
        if flag is True:
            logging.info("the node %s jnl is OK!" % (fault_node_ip))
            break
        else:
            exist_time = int(time.time() - start_time)
            m, s = divmod(exist_time, 60)
            h, m = divmod(m, 60)
            logging.info("the node %s jnl is not OK %dh:%dm:%ds!!! can't fault!!!" % (fault_node_ip, h, m, s))
            logging.info("wait 30s, re select node")
            time.sleep(30)

    # 生成节点的配置文件
    config_file = make_node_xml(fault_node_id)
    # 获取节点所在的节点池的id
    node_pool_id = get_nodepoolid_by_nodeid(fault_node_id)
    # 获取节点中所有磁盘与存储池的对应关系
    relation_lst = get_node_storage_pool_rel(fault_node_id)

    # 删除节点
    del_node(fault_node_id)

    # 检查节点是否删除
    start_time = time.time()
    while True:
        if check_node_exist(fault_node_id, fault_node_ip) is False:
            logging.info('node %s delete success!!!' % (fault_node_id))
            break
        time.sleep(20)
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        logging.info('node %s delete %dh:%dm:%ds' % (fault_node_id, h, m, s))

    # 检查重建任务是否存在
    while True:
        if check_rebuild_job() is False:
            logging.info('rebuild job finish!!!')
            break
        time.sleep(20)
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        logging.info('rebuild job exist %dh:%dm:%ds' % (h, m, s))

    time.sleep(60)

    # 添加节点
    add_node(config_file)

    time.sleep(60)

    node_id_new = get_node_id_by_ip(fault_node_ip)

    # 添加节点到节点池中
    add_node_2_nodpool(node_pool_id, node_id_new)

    # 启动系统
    startup()

    # 将节点中的所有磁盘添加到对应的存储池
    add_node_disks_2_storagepool(node_id_new, relation_lst)

    return


##############################################################################
# ##name  :      move_node_wait
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 删除节点入口函数(等重建完成)
##############################################################################
def move_node_wait():
    logging.info("***************** 9 move_node_wait begin *****************")
    run_move_node_wait()
    return


'''***********************************   kill process   ***********************************'''


##############################################################################
# ##name  :      run_kill_process
# ##parameter:   node_ip：节点ip
# ##             process：进程
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 在一个节点上kill一个进程
##############################################################################
def run_kill_process(node_ip, process):
    ps_cmd = ('ps -ef | grep %s | grep -v grep' % process)
    rc, stdout = command(ps_cmd, node_ip)
    if '' == stdout:
        return
    logging.info(stdout)
    lines = stdout.strip().split('\n')
    for line in lines:
        vars = line.split()
        pid = vars[1]
        kill_cmd = ('kill -9 %s' % pid)
        logging.info('node %s kill %s' % (node_ip, process))
        rc, stdout = command(kill_cmd, node_ip)
        if 0 != rc:
            logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (kill_cmd, stdout))
    return


##############################################################################
# ##name  :      check_process
# ##parameter:   node_ip：节点ip
# ##             process：进程
# ##return:      True:进程存在
# ##             Flase:进程不存在
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 检查进程是否存在
##############################################################################
def check_process(node_ip, process):
    ps_cmd = ('ps -ef | grep %s | grep -v grep' % process)
    rc, stdout = command(ps_cmd, node_ip)
    if 0 == rc:
        return True
    else:
        return False


##############################################################################
# ##name  :      random_kill_process
# ##parameter:   node_ip：节点ip
# ##return:      fault_process_lst:真正故障的进程
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 在一个节点上随机kill一组进程
##############################################################################
def random_kill_process(node_ip):
    process_lst = ['/home/parastor/bin/oJmgs', '/home/parastor/bin/oMgcd', '/home/parastor/bin/oPara',
                   '/home/parastor/bin/oStor', '/home/parastor/bin/oJob', '/home/parastor/bin/oRole',
                   '/home/parastor/bin/oCnas', '/home/parastor/oss/oOss', '/home/parastor/oms/oOms', 'zk']
    # 随机获取一组进程，检查进程是否存在
    ran_num = random.randint(1, len(process_lst))
    tem_process_lst = random.sample(process_lst, ran_num)
    fault_process_lst = []
    for process in tem_process_lst:
        if check_process(node_ip, process) is True:
            fault_process_lst.append(process)
            run_kill_process(node_ip, process)
    return fault_process_lst


##############################################################################
# ##name  :      kill_process
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 做kill 进程故障
##############################################################################
def kill_process():
    logging.info("***************** 4 kill_process begin *****************")
    # 随机获取一个节点ip
    node_ip = random.choice(NODE_IP_LST)

    # 检查节点是否可以故障
    fault_node_id = get_node_id_by_ip(node_ip)
    start_time = time.time()
    while True:
        flag = check_metanode(fault_node_id)
        if flag is True:
            logging.info("the node %s jnl is OK!" % (node_ip))
            break
        else:
            exist_time = int(time.time() - start_time)
            m, s = divmod(exist_time, 60)
            h, m = divmod(m, 60)
            logging.info("the node %s jnl is not OK %dh:%dm:%ds!!! can't fault!!!" % (node_ip, h, m, s))
            logging.info("wait 30s, re select node")
            time.sleep(30)

    # 随机kill节点的一组进程
    fault_process_lst = random_kill_process(node_ip)

    # 不断检查进程是否起来
    while True:
        logging.info("wait 60 s")
        time.sleep(60)
        for process in fault_process_lst:
            if check_process(node_ip, process) is False:
                logging.info('node %s process %s is not normal!!!' % (node_ip, process))
                break
        else:
            break

    logging.info("all process is OK")
    return

'''***********************************   10 down part net   ***********************************'''


##############################################################################
# ##name  :      get_all_nodes_eths
# ##parameter:
# ##return:   eth_info_lst:举例[[{"eth":"eth1", "mgrip":"10.2.41.101", "dataip":"20.10.11.101", "mask":"255.255.252.0"},
# ##                           {"eth":"eth1", "mgrip":"10.2.41.102", "dataip":"20.10.11.102", "mask":"255.255.252.0"}],
# ##                          [{"eth":"eth2", "mgrip":"10.2.41.101", "dataip":"30.10.11.101", "mask":"255.255.252.0"},
# ##                           {"eth":"eth2", "mgrip":"10.2.41.102", "dataip":"30.10.11.102", "mask":"255.255.252.0"}]]
# ##author:      baoruobing
# ##date  :      2018.5.17
# ##Description: 获取所有节点的所有的数据网的网口
##############################################################################
def get_all_nodes_eths():
    # 获取所有节点的ip
    eth_info_lst = []
    node_ips = get_nodes_ip()
    for node_ip in node_ips:
        node_id = get_node_id_by_ip(node_ip)
        eths_lst = get_net_eth(node_id, node_ip)
        for eth_tem in eths_lst:
            flag = False
            if len(eth_info_lst) == 0:
                temp_lst = [eth_tem]
                eth_info_lst.append(temp_lst)
            else:
                ip1 = eth_tem['dataip']
                mask1 = eth_tem['mask']
                for temp_lst in eth_info_lst:
                    ip2 = temp_lst[0]['dataip']
                    mask2 = temp_lst[0]['mask']
                    if check_ip_route(ip1, mask1, ip2, mask2):
                        temp_lst.append(eth_tem)
                        flag = True
                        break
                if flag is False:
                    temp_lst = [eth_tem]
                    eth_info_lst.append(temp_lst)
    return eth_info_lst


##############################################################################
# ##name  :      check_ip_route
# ##parameter:
# ##return:      True:两个ip的路由相同，False:两个ip的路由不同
# ##author:      baoruobing
# ##date  :      2018.5.17
# ##Description: 检查两个ip的路由是否相同
##############################################################################
def check_ip_route(ip1, mask1, ip2, mask2):
    ip1_lst = ip1.split('.')
    mask1_lst = mask1.split('.')
    ip2_lst = ip2.split('.')
    mask2_lst = mask2.split('.')

    route1_lst = []
    route2_lst = []
    for i in range(4):
        route1_lst.append(str(int(ip1_lst[i]) & int(mask1_lst[i])))
        route2_lst.append(str(int(ip2_lst[i]) & int(mask2_lst[i])))

    route1 = '.'.join(route1_lst)
    route2 = '.'.join(route2_lst)

    if route1 == route2:
        return True
    else:
        return False


##############################################################################
# ##name  :      run_down_part_net
# ##parameter:
# ##author:      baoruobing
# ##date  :      2018.5.17
# ##Description: 每个节点上down部分数据网
##############################################################################
def run_down_part_net():
    # 获取所有节点的数据网，放到字典中，键是管理ip，值是数据网网卡名（列表）
    nodes_eths_info_lst = get_all_nodes_eths()
    log_str = 'all nodes data eth: ', nodes_eths_info_lst
    logging.info(log_str)

    # 随机获取每个点上的部分数据网口，只有数据网大于1才能故障
    if len(nodes_eths_info_lst) <= 1:
        return
    ran_eths_num = random.randint(1, len(nodes_eths_info_lst) - 1)
    fault_node_eths_lst = random.sample(nodes_eths_info_lst, ran_eths_num)

    log_str = 'all nodes fault data eth: ', fault_node_eths_lst
    logging.info(log_str)

    # down每个节点的数据网
    for eths_info_lst in fault_node_eths_lst:
        for node_eth_info in eths_info_lst:
            if MGR_DATA_IP_SAME is True:
                fault_node_free_ip = FREE_IP_DIR[node_eth_info['mgrip']]
            else:
                fault_node_free_ip = node_eth_info['mgrip']

            run_down_net(fault_node_free_ip, [node_eth_info['eth']])

    wait_time('down_net')

    # up每个节点的数据网
    for eths_info_lst in fault_node_eths_lst:
        for node_eth_info in eths_info_lst:
            if MGR_DATA_IP_SAME is True:
                fault_node_free_ip = FREE_IP_DIR[node_eth_info['mgrip']]
            else:
                fault_node_free_ip = node_eth_info['mgrip']

            run_up_net(fault_node_free_ip, [node_eth_info['eth']])

    logging.info('wait 30s')
    time.sleep(30)
    return


##############################################################################
# ##name  :      down_part_net
# ##parameter:
# ##author:      baoruobing
# ##date  :      2018.5.17
# ##Description: 每个节点上down部分数据网(比如3个节点数据网是eth1和eth2，故障每个点上的
# ##             随机一个数据网，比如：1上的eth1,2上eth1,3上的eth2)
##############################################################################
def down_part_net():
    logging.info("***************** 10 down_part_net begin *****************")
    run_down_part_net()
    return


'''***********************************   公共函数   ***********************************'''


##############################################################################
# ##name  :      command
# ##parameter:   node_ip:节点ip
# ##             cmd:要执行的命令
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 执行命令
##############################################################################
def command(cmd, node_ip=None):
    if node_ip:
        cmd1 = 'ssh %s "%s"' % (node_ip, cmd)
    else:
        cmd1 = cmd
    process = subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output, unused_err = process.communicate()
    retcode = process.poll()
    return retcode, output


##############################################################################
# ##name  :      json_loads
# ##parameter:   stdout:需要解析的json格式的字符串
# ##return:      stdout_str:解析的json内容
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 将字符串解析成json
##############################################################################
def json_loads(stdout):
    try:
        # stdout = stdout.replace('\\', '')
        stdout_str = json.loads(stdout, strict=False)
        return stdout_str
    except Exception, e:
        logging.error(stdout)
        raise Exception("Error msg is %s" % e)


##############################################################################
# ##name  :      check_datanet
# ##parameter:   node_ip:节点ip
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 检查节点数据网是否存在
##############################################################################
def check_datanet(node_ip):
    cmd = '"ip addr | grep "inet ""'
    rc, stdout = command(cmd, node_ip)
    if 0 != rc:
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    lines = stdout.strip().split('\n')
    for line in lines:
        ip = line.split()[1].split('/')[0]
        if ip in NODE_DATA_IP_LST:
            return True
    return False


##############################################################################
# ##name  :      check_path
# ##parameter:   node_ip:节点ip path:路径
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 执行命令
##############################################################################
def check_path(node_ip, path):
    cmd = 'ls %s' % path
    rc, stdout = command(cmd, node_ip)
    return rc


##############################################################################
# ##name  :      run_command
# ##parameter:   cmd:要执行的命令
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 执行命令
##############################################################################
def run_command(cmd, fault_node_ip=None):
    if LOCALNODEFLAG is False:
        if (fault_node_ip is not None) and (fault_node_ip in NODE_IP_LST):
            node_ips_list = NODE_IP_LST[:]
            node_ips_list.remove(fault_node_ip)
        else:
            node_ips_list = NODE_IP_LST[:]

        for node_ip in node_ips_list:
            # 判断节点是否可以ping通
            if check_ping(node_ip) is False:
                continue
            # 判断数据网是否正常
            if check_datanet(node_ip) is False:
                continue
            # 判断节点上是否有/home/parastor/conf
            if 0 != check_path(node_ip, '/home/parastor/conf'):
                continue
            # 判断节点上是否有集群
            rc, stdout = command(cmd, node_ip)
            if rc == 127:
                continue
            if (rc != 0) and ('FindMasterError' in stdout):
                num = 1
                logging.warn('%s return "FindMasterError" %d times' % (cmd, num))
                while True:
                    time.sleep(20)
                    num += 1
                    rc, stdout = command(cmd, node_ip)
                    if (rc != 0) and ('FindMasterError' in stdout):
                        logging.warn('%s return "FindMasterError" %d times' % (cmd, num))
                    else:
                        break
            return rc, stdout
    else:
        rc, stdout = command(cmd, LOCALNODEIP)
        if (rc != 0) and ('FindMasterError' in stdout):
            num = 1
            logging.warn('%s return "FindMasterError" %d times' % (cmd, num))
            while True:
                time.sleep(20)
                num += 1
                rc, stdout = command(cmd, LOCALNODEIP)
                if (rc != 0) and ('FindMasterError' in stdout):
                    logging.warn('%s return "FindMasterError" %d times' % (cmd, num))
                else:
                    break
        return rc, stdout


##############################################################################
# ##name  :      run_check_vset
# ##parameter:   node_id:节点id
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 检查某个节点是否可以故障元数据盘
##############################################################################
def run_check_vset():
    mgr_node_id_lst = get_mgr_node_ids()
    for node_id in mgr_node_id_lst:
        cmd = '/home/parastor/tools/nWatch -i %s -t oRole -c oRole#rolemgr_view_dump' % node_id
        rc, stdout = run_command(cmd)
        if 0 != rc or 'failed' in stdout.strip().splitlines()[0]:
            logging.warn("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            continue
        else:
            break
    else:
        return -1
    stdout_lst = stdout.strip().splitlines()
    index = None
    for line in stdout_lst:
        if 'jtype:1 info' in line:
            index = stdout_lst.index(line)
            break
    if index is None:
        logging.warn("get mgrid failed!!!")
        return -1
    stdout_lst1 = stdout_lst[index+1:]
    index = None
    for line in stdout_lst1:
        if 'jtype:' in line:
            index = stdout_lst1.index(line)
            stdout_lst2 = stdout_lst1[:index]
            break
    else:
        stdout_lst2 = stdout_lst1[:]

    index = None
    for line in stdout_lst2:
        if 'grpview info' in line:
            index = stdout_lst2.index(line)
    if index is None:
        logging.warn("get mgrid failed!!!")
        return -1
    stdout_grpview_lst = stdout_lst2[index:]
    """支持多vmgr的场景"""
    node_lnode_lst = []
    lnode_dic = {}
    lnodeid_lst = []
    for line in stdout_grpview_lst:
        if '-->-->--> lnodeid:' not in line:
            if lnode_dic and 'lnode_id' in lnode_dic:
                node_lnode_lst.append(lnode_dic)
            lnode_dic = {}
            lnodeid_lst = []
        if '-->--> node_sn:' in line:
            node_id = line.split(',')[1].split(':')[-1].strip()
            lnode_dic['node_id'] = node_id
        if '-->-->--> lnodeid:' in line:
            lnodeid = line.split(',')[0].split(':')[-1].strip()
            lnodeid_lst.append(lnodeid)
            lnode_dic['lnode_id'] = lnodeid_lst

    for lnode_dic in node_lnode_lst:
        node_id = lnode_dic['node_id']
        lnode_lst = lnode_dic['lnode_id']
        for lnode_id in lnode_lst:
            cmd = '/home/parastor/tools/nWatch -i %s -t oPara -c oPara#vmgr_flattennr_dump -a "vmgrid=%s"' \
                  % (node_id, lnode_id)
            rc, stdout = run_command(cmd)
            if (0 != rc) or ('failed' in stdout) or ('support' in stdout):
                logging.warn("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
                return -1
            vset_num = stdout.strip().split('\n')[-1].split()[2]
            try:
                if int(vset_num) != 0:
                    return 1
                else:
                    logging.info("The current environment all vset is flatten")
                    continue
            except Exception, e:
                logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
                raise Exception("Error msg is %s" % e)

    return 0


##############################################################################
# ##name  :      check_vset
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 每隔一段时间检查一遍是否还有vset没有展平
##############################################################################
def check_vset():
    start_time = time.time()
    while True:
        time.sleep(20)
        rc = run_check_vset()
        if 0 == rc:
            break

        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        if 1 == rc:
            time_str = "vset exist %dh:%dm:%ds" % (h, m, s)
            logging.info(time_str)
    return


##############################################################################
# ##name  :      run_check_ds
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 检查所有ds是否提供服务
##############################################################################
def run_check_ds():
    node_ids = get_nodes_id()
    for node_id in node_ids:
        cmd = '/home/parastor/tools/nWatch -i %s -t oStor -c oStor#get_basicinfo' % node_id
        rc, stdout = run_command(cmd)
        if 0 != rc or 'failed' in stdout.strip().splitlines()[0]:
            logging.warn("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            return -1
        else:
            stdout_lst = stdout.strip().split('\n')
            for line in stdout_lst:
                if 'provide serv' in line:
                    flag = line.split(':')[-1].strip()
                    try:
                        if 1 != int(flag):
                            return 1
                    except Exception, e:
                        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
                        raise Exception("Error msg is %s" % e)

    logging.info("The current environment all ds service is OK")
    return 0


##############################################################################
# ##name  :      check_ds
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 每隔一段时间检查所有ds是否提供服务
##############################################################################
def check_ds():
    start_time = time.time()
    while True:
        time.sleep(20)
        rc = run_check_ds()
        if 0 == rc:
            break
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        if 1 == rc:
            time_str = "ds don't provide service %dh:%dm:%ds" % (h, m, s)
            logging.info(time_str)
    return


##############################################################################
# ##name  :      check_metanode
# ##parameter:   node_id:节点id
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 检查某个节点是否可以故障元数据盘
##############################################################################
def check_metanode(node_id):
    mgr_node_id_lst = get_mgr_node_ids()
    cmd = '/home/parastor/tools/nWatch -t oRole -i %s -c oRole#rolemgr_master_dump' % mgr_node_id_lst[0]
    rc, stdout = run_command(cmd)
    if 0 != rc or 'failed' in stdout.strip().splitlines()[0]:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        return False
    master_node_id = stdout.split(':')[-1].strip()
    cmd1 = '/home/parastor/tools/nWatch -t oRole -i %s -c oRole#rolemgr_slaveready_dump' % master_node_id
    rc, stdout = run_command(cmd1)
    if 0 != rc or 'failed' in stdout.strip().splitlines()[0]:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd1, stdout))
        return False
    stdout_lst = stdout.strip().split('\n')
    for line in stdout_lst:
        if 'nodeid' in line and 'is_takeoverable' in line:
            node_id_tmp = line.split()[-2].split(':')[-1].rstrip(',')
            takeoverable = line.split()[-1].split(':')[-1].strip()
            if node_id_tmp != str(node_id):
                continue
            if takeoverable != '1':
                return False

    return True


##############################################################################
# ##name  :      run_check_badobj
# ##parameter:
# ##return:      False:有坏对象  True:没有坏对象
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 检查是否还有坏对象
##############################################################################
def run_check_badobj(node_id):
    """
    #todo 用oPara还是oJob
    node_id_lst = get_nodes_id()
    badobj_num = 0
    for node_id in node_id_lst:
        cmd = "/home/parastor/tools/nWatch -t oPara -i %d -c RCVR#badobj" % node_id
        rc, stdout = run_command(cmd)
        if 0 != rc:
            logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            raise Exception(
                "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        badobj_num += int(stdout.splitlines()[1].strip().split()[-1].strip())

    if badobj_num != 0:
        logging.info("badobj_num = %d" % (badobj_num))
        return False
    """
    cmd = "/home/parastor/tools/nWatch -t oJob -i %s -c RCVR#jobinfo" % node_id
    rc, stdout = run_command(cmd)
    if 0 != rc or 'failed' in stdout.strip().splitlines()[0]:
        logging.warn("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        return -1
    master_job_id = stdout.split(',')[0].split()[-1]

    cmd = "/home/parastor/tools/nWatch -t oJob -i %s -c RCVR#repairjob" % master_job_id
    rc, result_badobj = run_command(cmd)
    if 0 != rc or 'failed' in stdout.strip().splitlines()[0]:
        logging.warn("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, result_badobj))
        return -1
    result_tmp = result_badobj.split()
    if "0" != result_tmp[-3]:
        logging.info("masterjob = %s, badobj_num = %s" % (master_job_id, result_tmp[-3]))
        return 1

    logging.info("The current environment does not have badobj")
    return 0


##############################################################################
# ##name  :      check_badobj
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 每隔一段时间检查一遍是否还有坏对象
##############################################################################
def check_badobj(waitflag=True, fault_ip=None):
    if waitflag is True:
        # 等待60s
        logging.info("wait %ds" % CHECKBADOBJ_WAIT_TIME)
        time.sleep(CHECKBADOBJ_WAIT_TIME)

    def _check_badjob():
        node_ip_lst_bak = NODE_IP_LST[:]
        if fault_ip:
            if fault_ip in node_ip_lst_bak:
                node_ip_lst_bak.remove(fault_ip)
        for node_ip in node_ip_lst_bak:
            # 检查是否可以ping通
            if check_ping(node_ip) is False:
                continue
            node_id = get_node_id_by_ip(node_ip)
            result = run_check_badobj(node_id)
            if -1 == result:
                continue
            elif 1 == result:
                return 1
            else:
                return 0

    start_time = time.time()
    num = 0
    while True:
        time.sleep(20)
        if LOCALNODEFLAG is False:
            if 0 == _check_badjob():
                num += 1
                if num >= 14:
                    break
                else:
                    logging.info("The %s time badobj is 0, total times is 15" % num)
                    continue
            else:
                num = 0
        else:
            local_node_id = get_node_id_by_ip(LOCALNODEIP)
            if 0 == run_check_badobj(local_node_id):
                num += 1
                if num >= 14:
                    break
                else:
                    logging.info("The %s time badobj is 0, total times is 15" % num)
                    continue
            else:
                num = 0
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        time_str = "badobj exist %dh:%dm:%ds" % (h, m, s)
        logging.info(time_str)
    return


##############################################################################
# ##name  :      check_metadata
# ##parameter:
# ##return:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 检查元数据的正确性
##############################################################################
def check_metadata():
    cmd = 'sh /home/parastor/tools/chkmobjconn.sh'

    def _check_meta(result):
        flag = True
        line_lst = result.strip().splitlines()
        for line in line_lst:
            if 'mobjs not consistant' not in line:
                continue
            else:
                if line.strip().split()[1] != '0':
                    logging.error(line)
                    flag = False

        if flag is False:
            raise Exception('The current environment has bad mobjs!!!')
        else:
            return

    while True:
        rc, result = run_command(cmd)
        if 0 != rc:
            logging.warn("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, result))
            continue
        else:
            _check_meta(result)
            logging.info('The current environment does not have bad mobjs')
            break


##############################################################################
# ##name  :      run_check_core
# ##parameter:   node_ip:节点ip
# ##return:      False:有core  True:没有core
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 检查某个节点是否有core
##############################################################################
def run_check_core(node_ip):
    core_path_lst = ['/home/parastor/log/', '/']
    for core_path in core_path_lst:
        core_path_tmp = os.path.join(core_path, 'core*')
        cmd = 'ls %s' % core_path_tmp
        rc, result = command(cmd, node_ip)
        if 0 != rc:
            return True
        else:
            return False


def get_all_volume_layout():
    """
    :author:      baoruobing
    :date  :      2018.08.15
    :description: 获取所有卷的配比
    :return:      (list)卷的配比信息,[{'disk_parity_num':2,'node_parity_num':1,'replica_num':4}]
    """
    cmd = "pscli --command=get_volumes"
    rc, stdout = run_command(cmd)
    if rc != 0:
        raise Exception("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    volumes_info = json_loads(stdout)
    volumes_lst = volumes_info['result']['volumes']
    layout_lst = []
    for volume in volumes_lst:
        layout_dic = {}
        layout_dic['disk_parity_num'] = volume['layout']['disk_parity_num']
        layout_dic['node_parity_num'] = volume['layout']['node_parity_num']
        layout_dic['replica_num'] = volume['layout']['replica_num']
        layout_lst.append(layout_dic)
    return layout_lst


def check_share_disk_fault(share_disk_num):
    """
    :author:               baoruobing
    :date  :               2018.08.15
    :description:          检查是否可以做元数据盘故障
    :param share_disk_num: 共享盘个数
    :return: 
    """
    """获取所有卷的最大副本数"""
    layout_lst = get_all_volume_layout()
    replica_num = 0
    for layout in layout_lst:
        if layout['disk_parity_num'] != 0:
            replica_num_tmp = layout['disk_parity_num'] + 1
        else:
            replica_num_tmp = layout['replica_num']
        replica_num = replica_num_tmp > replica_num and replica_num_tmp or replica_num

    if share_disk_num > replica_num:
        return True
    else:
        return False


def get_sys_ip():
    sys_ip_lst = []
    cmd = "pscli --command=get_clients"
    rc, result = run_command(cmd)
    if 0 != rc:
        raise Exception("There is not parastor or get nodes ip failed!!!")
    else:
        result = json_loads(result)
        nodes_lst = result['result']
        for node in nodes_lst:
            sys_ip_lst.append(node['ip'])
    return sys_ip_lst


##############################################################################
# ##name  :      check_core
# ##parameter:
# ##return:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 检查环境是否有core
##############################################################################
def check_core():
    flag = True
    core_node_lst = []
    sys_ip_lst = get_sys_ip()
    for node_ip in sys_ip_lst:
        # 先检查是否可以ping通
        if check_ping(node_ip) is False:
            logging.warn('node %s ping failed!!!' % node_ip)
            continue
        else:
            if run_check_core(node_ip) is False:
                flag = False
                core_node_lst.append(node_ip)
    if flag is False:
        core_node = ','.join(core_node_lst)
        logging.warn("These nodes %s has core!!! ", core_node)
        if CORESTOP is True:
            sys.exit(-1)
    else:
        logging.info("The current environment does not have core")

    return


##############################################################################
# ##name  :      get_nodes_ip
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 获取集群中所有节点的管理ip
##############################################################################
def get_nodes_ip():
    cmd = "pscli --command=get_nodes"
    nodes_ips = []
    rc, stdout = run_command(cmd)
    if 0 != rc:
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        node_info = json_loads(stdout)
        nodes = node_info['result']['nodes']
        for node in nodes:
            nodes_ips.append(node['ctl_ips'][0]['ip_address'])

    return nodes_ips


##############################################################################
# ##name  :      get_nodes_id
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 获取集群中所有节点的id
##############################################################################
def get_nodes_id():
    cmd = "pscli --command=get_nodes"
    nodes_ids = []
    rc, stdout = run_command(cmd)
    if 0 != rc:
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        node_info = json_loads(stdout)
        nodes = node_info['result']['nodes']
        for node in nodes:
            nodes_ids.append(node['node_id'])

    return nodes_ids


##############################################################################
# ##name  :      get_nodes_ips_by_ip
# ##parameter:   node_ip:节点ip
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 通过输入的ip获取集群中的所有节点的ip
##############################################################################
def get_nodes_ips_by_ip(node_ip):
    cmd = '"pscli --command=get_nodes"'
    rc, stdout = command(cmd, node_ip)
    if 0 != rc:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        node_ip_lst = []
        node_info = json_loads(stdout)
        nodes = node_info['result']['nodes']
        for node in nodes:
            node_ip_lst.append(node['ctl_ips'][0]['ip_address'])

    return node_ip_lst


##############################################################################
# ##name  :      get_local_node_ip
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 获取本节点的管理ip
##############################################################################
def get_local_node_ip():
    cmd = "pscli --command=get_nodes"
    nodes_ips = []
    rc, stdout = command(cmd)
    if 0 != rc:
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        node_info = json_loads(stdout)
        nodes = node_info['result']['nodes']
        for node in nodes:
            nodes_ips.append(node['ctl_ips'][0]['ip_address'])

    cmd = 'ip addr | grep "inet "'
    rc, stdout = command(cmd)
    if 0 != rc:
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    lines = stdout.strip().split('\n')
    for line in lines:
        ip = line.split()[1].split('/')[0]
        if ip in nodes_ips:
            return ip
    return None


##############################################################################
# ##name  :      get_node_id_by_ip
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 通过节点ip获取节点的id
##############################################################################
def get_node_id_by_ip(node_ip):
    cmd = 'pscli --command=get_nodes'
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        msg = json_loads(stdout)
        nodes_info = msg["result"]["nodes"]
        for node in nodes_info:
            ctl_ip = node["ctl_ips"][0]["ip_address"]
            if node_ip == ctl_ip:
                return node["node_id"]
        logging.info("there is not a node's ip is %s!!!" % node_ip)
        return None


def get_node_ip_by_id(node_id):
    """
    :author:        baoruobing
    :date  :        2018.08.15
    :description:   通过节点id获取节点ip
    :param node_id: (int)节点id
    :return: 
    """
    cmd = "pscli --command=get_nodes --ids=%s" % node_id
    rc, stdout = run_command(cmd)
    if 0 != rc:
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        msg = json_loads(stdout)
        node_info = msg["result"]["nodes"][0]
        node_ip = node_info['ctl_ips'][0]['ip_address']
        return node_ip


##############################################################################
# ##name  :      check_node_exist
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 检查某个节点是否存在
##############################################################################
def check_node_exist(node_id, fault_node_ip=None):
    cmd = 'pscli --command=get_nodes'
    rc, stdout = run_command(cmd, fault_node_ip)
    if 0 != rc:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        msg = json_loads(stdout)
        nodes_info = msg["result"]["nodes"]
        for node in nodes_info:
            if node["node_id"] == node_id:
                return True
        return False


##############################################################################
# ##name  :      get_nodes_data_ip
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 获取集群的所有数据网ip
##############################################################################
def get_nodes_data_ip():
    cmd = 'pscli --command=get_nodes'
    rc, stdout = run_command(cmd)
    if rc != 0:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    data_ip_lst = []
    stdout = json_loads(stdout)
    node_info_lst = stdout['result']['nodes']
    for node_info in node_info_lst:
        for data_ip_info in node_info['data_ips']:
            data_ip_lst.append(data_ip_info['ip_address'])

    return data_ip_lst


##############################################################################
# ##name  :      get_nodes_data_ip_by_ip
# ##parameter:   node_ip:节点ip
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 获取集群的所有数据网ip
##############################################################################
def get_nodes_data_ip_by_ip(node_ip):
    cmd = '"pscli --command=get_nodes"'
    rc, stdout = command(cmd, node_ip)
    if rc != 0:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    data_ip_lst = []
    stdout = json_loads(stdout)
    node_info_lst = stdout['result']['nodes']
    for node_info in node_info_lst:
        for data_ip_info in node_info['data_ips']:
            data_ip_lst.append(data_ip_info['ip_address'])

    return data_ip_lst


##############################################################################
# ##name  :      get_nodepoolid_by_nodeid
# ##parameter:   node_id:节点id
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 通过节点id获取节点所在的节点池的id
##############################################################################
def get_nodepoolid_by_nodeid(node_id):
    cmd = 'pscli --command=get_nodes --ids=%s' % node_id
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        msg = json_loads(stdout)
        node_pool_id = msg["result"]["nodes"][0]['node_pool_id']
        return node_pool_id


##############################################################################
# ##name  :      get_mgr_node_ids
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 获取集群的管理节点id
##############################################################################
def get_mgr_node_ids():
    cmd = 'pscli --command=get_nodes'
    mgr_node_id_lst = []
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        msg = json_loads(stdout)
        nodes_info = msg["result"]["nodes"]
        for node_info in nodes_info:
            for service_info in node_info['services']:
                if service_info['service_type'] == 'oJmgs':
                    mgr_node_id_lst.append(node_info['node_id'])
                    break
    return mgr_node_id_lst


##############################################################################
# ##name  :      get_storage_pool_id_by_diskid
# ##parameter:   node_id:节点id  disk_id:磁盘id
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 通过磁盘id获取磁盘所在的存储池的id
##############################################################################
def get_storage_pool_id_by_diskid(node_id, disk_id):
    cmd = 'pscli --command=get_disks --node_ids=%s' % node_id
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        msg = json_loads(stdout)
        disks_info = msg["result"]["disks"]
        for disk in disks_info:
            if disk['id'] == disk_id:
                return disk['storagePoolId']
        logging.info("there is not a disk's id is %s!!!" % disk_id)
        return None


##############################################################################
# ##name  :      check_rebuild_job
# ##parameter:
# ##return:      True:重建任务存在，Flase:重建任务不存在
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 检查重建任务
##############################################################################
def check_rebuild_job(fault_node_ip=None):
    cmd = 'pscli --command=get_jobengine_state'
    rc, stdout = run_command(cmd, fault_node_ip)
    if 0 != rc:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        msg = json_loads(stdout)
        jobs_info = msg["result"]["job_engines"]
        for job in jobs_info:
            if job['type'] == 'JOB_ENGINE_REBUILD':
                return True
        return False


##############################################################################
# ##name  :      expand_disk_2_storage_pool
# ##parameter:   storage_pool_id:存储池id  disk_id:磁盘id
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 将磁盘添加到存储池中
##############################################################################
def expand_disk_2_storage_pool(storage_pool_id, disk_id):
    cmd = 'pscli --command=expand_storage_pool --storage_pool_id=%s --disk_ids=%s' % (storage_pool_id, disk_id)
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    return


##############################################################################
# ##name  :      wait_time
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 根据故障类型等待多长时间
##############################################################################
def wait_time(fault):
    time_lst = wait_times.get(fault)
    min_time = time_lst[0]
    max_time = time_lst[1]

    wait_time = random.randint(min_time, max_time)
    logging.info("wait %d s" % wait_time)
    time.sleep(wait_time)
    return


##############################################################################
# ##name  :      check_ping
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 检查ip是否可以ping通
##############################################################################
def check_ping(ip):
    cmd = 'ping -c 3 %s | grep "0 received" | wc -l' % ip
    rc, stdout = command(cmd)
    if '0' != stdout.strip():
        return False
    else:
        return True


##############################################################################
# ##name  :      get_zk_node_ips
# ##parameter:
# ##return:      zk_node_ip_lst: zk节点的管理ip列表
# ##             unzk_node_ip_lst: 非zk节点的管理ip列表
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 获取系统当前的zk节点和非zk节点的管理ip
##############################################################################
def get_zk_node_ips():
    cmd = "pscli --command=get_nodes"
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        zk_node_ip_lst = []
        unzk_node_ip_lst = []
        stdout_info = json_loads(stdout)
        nodes_info = stdout_info['result']['nodes']
        for node_info in nodes_info:
            if node_info['zk_id'] == 0:
                unzk_node_ip_lst.append(node_info['ctl_ips'][0]['ip_address'])
            else:
                zk_node_ip_lst.append(node_info['ctl_ips'][0]['ip_address'])
        return zk_node_ip_lst, unzk_node_ip_lst


##############################################################################
# ##name  :      get_fault_nodeips_by_zknum
# ##parameter:   zknum:集群总zk个数
# ##return:      disk_ip_lst: 可以做故障的节点的管理ip列表
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 获取系统当前可以做网络和节点故障的节点管理ip
##############################################################################
def get_fault_nodeips_by_zknum(zknum):
    # 获取当前系统的zk节点
    zk_nodeip_lst, unzk_node_ip_lst = get_zk_node_ips()

    now_zknum = len(zk_nodeip_lst)

    # 还可以故障的zk节点个数
    fault_zk_node_num = now_zknum - (zknum+1)/2

    if fault_zk_node_num < 0:
        logging.error("-z --zknum is not right or parastor current zknum is less than total zknum!!!")
        raise Exception("-z --zknum is not right or parastor current zknum is less than total zknum!!!")
    elif fault_zk_node_num == 0:
        if LOCALNODEIP in unzk_node_ip_lst:
            unzk_node_ip_lst.remove(LOCALNODEIP)
        return unzk_node_ip_lst
    else:
        if LOCALNODEIP in zk_nodeip_lst:
            zk_nodeip_lst.remove(LOCALNODEIP)
        disk_ip_lst = random.sample(zk_nodeip_lst, fault_zk_node_num)
        disk_ip_lst = disk_ip_lst + unzk_node_ip_lst
        return disk_ip_lst


##############################################################################
# ##name  :      startup
# ##parameter:
# ##return:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 启动系统
##############################################################################
def startup():
    cmd = 'pscli --command=startup'
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    return


##############################################################################
# ##name  :      check_ip
# ##parameter:   ip:***.***.***.***的格式的ip
# ##return:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 检查ip格式是否正确
##############################################################################
def check_ip(ip):
    pattern = re.compile(r'((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    match = pattern.match(ip)
    if match:
        return True
    else:
        return False


##############################################################################
# ##name  :      update_badjob_time
# ##parameter:
# ##return:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 修改坏对象上报时间
##############################################################################
def update_badjob_time():
    cmd = 'pscli --command=update_param --section=oApp --name=dataio_cmd_timeout_ms --current=120000'
    rc, stdout = run_command(cmd)
    if 0 != rc:
        logging.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    return


'''***********************************   参数解析   ***********************************'''


##############################################################################
# ##name  :      arg_analysis
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 参数解析
##############################################################################
def arg_analysis():
    global OPERATION
    global NUMBERS
    global FAULTDISKTYPE
    global FAULTDISKNUM
    global LOCALNODEFLAG
    global LOCALNODEIP
    global NODE_IP_LST
    global NODE_DATA_IP_LST
    global ZKNUM
    global MIXFAULT
    global MGR_DATA_IP_SAME
    global CORESTOP

    usage = "usage: %prog [options] arg1 arg2 arg3"
    version = "%prog 5.0"
    parser = OptionParser(usage=usage, version=version)
    parser.add_option("-o", "--operation",
                      action="append",
                      type="int",
                      dest="operation",
                      help="Required:True   Type:int                                     "
                           "fault operation                                              "
                           "0 : all                                                      "
                           "1 : down disk (no wait repair)                               "
                           "2 : down net  (no wait repair)                               "
                           "3 : down node (no wait repait)                               "
                           "4 : kill process                                             "
                           "5 : down disk (wait repair)                                  "
                           "6 : del disk  (wait transfer)                                "
                           "7 : down net  (wait repair)                                  "
                           "8 : down node (wait repait)                                  "
                           "9 : del node (wait transfer)                                "
                           "10: down part net                                            "
                      )

    parser.add_option("-z", "--zknum",
                      type="int",
                      dest="zknum",
                      help="Required:True   Type:int  Help:parastor zookeeper nums")

    parser.add_option("-n", "--numbers",
                      type="int",
                      dest="num",
                      default=10000,
                      help="Required:False   Type:int  Help:fault execution nums, default: %default, range is 1-10000")

    parser.add_option("-d", "--disk",
                      type="string",
                      dest="disktype",
                      metavar="TYPE",
                      default="data",
                      help="Required:False   Type:string  Help:fault disk type, e.g. data, meta, all. default: %default"
                           "this parameter work when disk fault")

    parser.add_option("-f", "--disknum",
                      type="int",
                      dest="faultdisknum",
                      default=1,
                      help="Required:False   Type:int  Help:fault disk nums, default: %default, range is 1-10")

    parser.add_option("-i", "--ip",
                      type="str",
                      dest="mgrip",
                      default=None,
                      help="Required:False   Type:str   Help:MGR node IP")

    parser.add_option("-m", "--mix",
                      action="store_true",
                      dest="mixflag",
                      help="Required:False   Type:bool  Help:mixed fault flag. If you want to do a mixed fault, "
                           "you need to configure this parameter")

    parser.add_option("-c", "--corestop",
                      action="store_true",
                      dest="core",
                      help="Required:False   Type:bool  Help:core stop. If you want to stop when there have cores, "
                           "you need to configure this parameter")

    options, args = parser.parse_args()
    # 检查-o参数
    if options.operation is None:
        parser.error("please input -o or --operation")
    operation_lst = list(set(options.operation))
    operation_lst.sort()
    if len(operation_lst) > 11:
        parser.error('the range of -o or --operation is 0-10')
    for tem in operation_lst:
        if tem not in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
            parser.error('the range of -o or --operation is 0-10')

    # 检查-z参数
    if options.zknum is None:
        parser.error("please input -z or --zknum")
    if options.zknum <= 0:
        parser.error("zknum must be more than 0")
    if options.zknum % 2 == 0:
        parser.error("zknum is odd")

    # 检查-n参数
    if options.num < 1 or options.num > 10000:
        parser.error("the range of -n or --num is 1-10000")

    # 检查-d参数
    if options.disktype not in ['data', 'meta', 'all']:
        parser.error('the -d or --disk just can be "data", "meta", "all"')

    # 检查-f参数
    if options.faultdisknum < 1 or options.faultdisknum > 10:
        parser.error("the range of -f or --disknum is 1-10")

    # 检查-i参数
    if options.mgrip is not None:
        # 检查ip的正确性
        if check_ip(options.mgrip) is False:
            parser.error("-i the ip format is incorrent!!!")
        mgr_ip = options.mgrip
        LOCALNODEFLAG = False
        NODE_IP_LST = get_nodes_ips_by_ip(mgr_ip)
        NODE_DATA_IP_LST = get_nodes_data_ip_by_ip(mgr_ip)

        # 如果本节点在集群内则报错
        def _check_localnode_in_ps(node_ip_lst):
            cmd = 'ip addr | grep "inet "'
            rc, stdout = command(cmd)
            if 0 != rc:
                raise Exception(
                    "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            lines = stdout.strip().split('\n')
            for line in lines:
                ip = line.split()[1].split('/')[0]
                if ip in node_ip_lst:
                    return True
            return False

        if _check_localnode_in_ps(NODE_IP_LST):
            parser.error("If the local node in the parastor, please don't enter -i or --ip")

        LOCALNODEIP = None

    else:
        # 检查本节点是否是集群节点
        cmd = 'ls /home/parastor/bin'
        rc, stdout = command(cmd)
        if rc != 0:
            parser.error('the local node not in parastor, please input -i or --ip')
        LOCALNODEFLAG = True
        LOCALNODEIP = get_local_node_ip()
        NODE_IP_LST = get_nodes_ip()
        NODE_DATA_IP_LST = get_nodes_data_ip_by_ip(NODE_IP_LST[0])

    # 检查-m参数
    if options.mixflag is True:
        # 5个节点以上才做混合故障
        if len(NODE_IP_LST) < 5:
            parser.error('mixed fault requires more than 5 nodes in ths system')
        # 混合故障需要做删节点和删磁盘的故障
        if (6 not in operation_lst) and (9 not in operation_lst):
            parser.error('mixed fault requires del disk or del node')
        MIXFAULT = True
    else:
        MIXFAULT = False

    # 检查-c参数
    if options.core is True:
        CORESTOP = True
    else:
        CORESTOP = False

    # 参数内容设置到全局变量中
    OPERATION = operation_lst
    NUMBERS = options.num
    FAULTDISKTYPE = options.disktype
    ZKNUM = options.zknum
    FAULTDISKNUM = options.faultdisknum

    # 如果管理网和数据网复用的情况，需要配置FREE_IP_DIR
    MGR_DATA_IP_SAME = False
    if set(NODE_IP_LST).issubset(set(NODE_DATA_IP_LST)):
        MGR_DATA_IP_SAME = True
        if sorted(NODE_IP_LST) != sorted(FREE_IP_DIR.keys()):
            parser.error('管理网和数据网复用的环境，需要手动填写FREE_IP_DIR，'
                         '字典的每一项的键是节点的管理ip，值是这个节点数据网没有用到的ip')
    return


##############################################################################
# ##name  :      get_fault
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 获取要做的故障
##############################################################################
def get_fault():
    all_fault_dir = {1: down_disk_no_wait,
                     2: down_net_no_wait,
                     3: down_node_no_wait,
                     4: kill_process,
                     5: down_disk_wait,
                     6: del_disk_wait,
                     7: down_net_wait,
                     8: down_node_wait,
                     9: move_node_wait,
                     10: down_part_net}

    all_fault_name_dir = {1: "down_disk_no_wait",
                          2: "down_net_no_wait",
                          3: "down_node_no_wait",
                          4: "kill_process",
                          5: "down_disk_wait",
                          6: "del_disk_wait",
                          7: "down_net_wait",
                          8: "down_node_wait",
                          9: "del_node_wait",
                          10: "down_part_net"}
    fault_lst = []
    fault_name_lst = []
    if 0 in OPERATION:
        fault_lst = all_fault_dir.values()
        fault_name_lst = all_fault_name_dir.values()
    else:
        for tag in OPERATION:
            fault_lst.append(all_fault_dir.get(tag))
            fault_name_lst.append(all_fault_name_dir.get(tag))

    string = "These faults will be done ", fault_name_lst
    logging.info(string)
    return fault_lst


##############################################################################
# ##name  :      run_fault
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.11.02
# ##Description: 进行故障操作
##############################################################################
def run_fault():
    global NUMBERS
    global NODE_IP_LST
    global NODE_DATA_IP_LST
    global FAULT_NODE_IP_LST

    logging.info(" ".join(sys.argv))
    logging.info("*********** the fault operation beginning ***********")
    # 检查环境是否有core
    check_core()

    # 检查环境是否有坏对象
    check_badobj(waitflag=False)
    # 检查环境是否有vset没有展平
    check_vset()
    # 检查环境中所有ds是否提供服务
    check_ds()
    # 检查元数据正确性
    # check_metadata()

    # 获取要做的故障类型
    fault_lst = get_fault()

    num = 0
    logging.info('*************************************************************************')

    # 混合故障处理
    fault_lst1 = []
    fault_lst2 = fault_lst[:]
    if MIXFAULT is True:
        if del_disk_wait in fault_lst:
            fault_lst1.append(del_disk_wait)
            fault_lst2.remove(del_disk_wait)
        if move_node_wait in fault_lst:
            fault_lst1.append(move_node_wait)
            fault_lst2.remove(move_node_wait)

    for i in range(NUMBERS):
        for func in fault_lst:
            # 每次故障前更新下可做节点故障的节点列表和集群节点列表
            # 根据输入的zk个数和当前环境zk节点个数，获取可以做故障的节点的ip列表
            fault_node_ip_lst = get_fault_nodeips_by_zknum(ZKNUM)
            FAULT_NODE_IP_LST = fault_node_ip_lst
            logging.info('down_net_wait,down_node_wait,move_node_wait fault node in %s' % FAULT_NODE_IP_LST)

            NODE_IP_LST = get_nodes_ip()
            logging.info('NODE_IP_LST is %s' % NODE_IP_LST)

            # 获取所有数据网ip
            NODE_DATA_IP_LST = get_nodes_data_ip()
            logging.info('NODE_DATA_IP_LST is %s' % NODE_DATA_IP_LST)

            if MIXFAULT is not True:
                func()
            else:
                interval_time = random.randint(0, 300)
                flag = random.randint(0, 1)
                if flag == 0:
                    func1 = random.choice(fault_lst1)
                    func2 = random.choice(fault_lst2)
                else:
                    func1 = random.choice(fault_lst2)
                    func2 = random.choice(fault_lst1)

                p1 = Process(target=func1)
                p2 = Process(target=func2)

                p1.start()
                time.sleep(interval_time)
                p2.start()

                p1.join()
                p2.join()

                if p1.exitcode != 0:
                    raise Exception("%s is failed!!!!!!" % func1)
                if p2.exitcode != 0:
                    raise Exception("%s is failed!!!!!!" % func2)

            # 检查环境是否有core
            check_core()
            # 检查环境是否有vset没有展平
            check_vset()
            # 检查环境中所有ds是否提供服务
            check_ds()
            # 检查元数据正确性
            # check_metadata()
            # 检查是否有坏对象
            check_badobj()
            num += 1
            logging.info('***************************** the %d fault ******************************' % num)


def main():
    # 参数解析
    arg_analysis()
    # 初始化日志文件
    log_init()
    # 执行故障
    run_fault()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.error("", exc_info=1)
        traceback.print_exc()
        exit(1)