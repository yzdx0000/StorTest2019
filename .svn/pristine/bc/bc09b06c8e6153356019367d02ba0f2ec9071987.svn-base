#-*-coding:utf-8 -*
#!/usr/bin/python

'''
单节点数据盘故障
'''

import os
import time

import utils_path
from utils import common
from utils import log
from utils import shell
from utils import get_config

SYSTEM_NODES_ID = ['10.20.0.72', '10.20.0.73', '10.20.0.99']
CLIENT_IP = '10.20.0.99'
VDBENCH_PATH = '/home/vdbench504/'
INIT_SCRIPT = '/root/datacheck/00.init.sh'
DATACHECK_SCRIPT = '/root/datacheck/01.datacheck.sh'
VDBENCH_LOG_PATH = '/root/datacheck/output/test1/logfile.html'

#开始进行数据读写
def datacheck():
    cmd = ("%s %s %s" %(DATACHECK_SCRIPT, VDBENCH_PATH, CLIENT_IP))
    log.info(cmd)
    rc, stdout, stderr = shell.ssh(CLIENT_IP, cmd)
    if 0 != rc:
        log.error("Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))

#获取逻辑节点

#拔出硬盘
def remove_disk():
    share_diskpool_ids, monopoly_diskpool_ids = common.get_diskpool_ids()
    share_disk_names, monopoly_disk_names = common.get_share_monopoly_disk_names('1', share_diskpool_ids, monopoly_diskpool_ids)
    disk_id = common.get_physicalid_by_name('10.20.0.72', monopoly_disk_names[0])
    cmd = ("echo scsi remove-single-device %s > /proc/scsi/scsi" %disk_id)
    log.info(cmd)
    rc, stdout, stderr = shell.ssh('10.20.0.72', cmd)
    if 0 != rc:
        log.error("Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))

def work_1():
    #进程1运行vdbench脚本
    cmd = ("%s %s %s" %(DATACHECK_SCRIPT, VDBENCH_PATH, CLIENT_IP))
    log.info(cmd)
    rc, stdout, stderr = shell.ssh(CLIENT_IP, cmd)
    if 0 != rc:
        log.error("Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))

def work_2():
    #做故障
    time.sleep(20)
    count1 = 0
    count2 = 0
    steps = 0
    while True:
        steps += 1
        if steps > 200:
            log.info("time out")
            break

        dat_file = open(VDBENCH_LOG_PATH, 'r')
        lines = dat_file.readlines()
        count2 = len(lines)
        if count1 == count2:
            log.info("The script finished")
            break
        if count2 > 20:
            num = 20
        else:
            num = count2
        file_msg = []
        for i in range(1, num+1):
            n = -i
            last_line = lines[n].strip()
            file_msg.append(last_line)
        dat_file.close()

        for mem in file_msg:
            if "RD=rd1" in mem:
                log.info("The rd1 begin")
                break






def case():
    #首先运行创建脚本
    cmd = ("%s %s %s" %(INIT_SCRIPT, VDBENCH_PATH, CLIENT_IP))
    log.info(cmd)
    rc, stdout, stderr = shell.ssh(CLIENT_IP, cmd)
    if 0 != rc:
        log.error("Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))

