# -*- coding=utf-8 -*-
# indows端自动完成login initiator-target
# 完成磁盘自动联机、初始化功能
# 获取映射到主机的x1000卷ID号

import os
import subprocess
import get_info
import log

def iSCSI_login():
    vip_list = get_info.get_vip()
    initiator_name = get_info.get_initiator()
    target_list = get_info.get_target()
    log.info('Start iSCSI login operation!')
    # 启动iscsi服务程序
    log.info('Start iSCSI service program.')
    cmd = 'net start msiscsi'
    (rc, stdout) = subprocess.getstatusoutput(cmd)
    if 0 != rc:
        log.error('iSCSI service start failed!!!info:%s' % stdout)
    else:
        log.info('iSCSI service start successful!!!')

    # 修改本机的iqn

    log.info('Start update initiator operation!')
    cmd = ('iscsicli NodeName %s' % initiator_name)
    (rc, stdout) = subprocess.getstatusoutput(cmd)
    if 0 != rc:
        log.error('update initiator failed!!!info:%s' % stdout)
    else:
        log.info('update initiator successful!!!')


    # 登录目标
    log.info('Start add target portal operation!')
    for vip in vip_list:
        cmd_addIP = ('iscsicli QAddTargetPortal %s' % vip)
        (rc, stdout) = subprocess.getstatusoutput(cmd_addIP)
        if 0 != rc:
            log.error('add target portal failed!!!\nvip:%s.info:%s' % (vip, stdout))
        else:
            log.info('add target portal successful!!!')

    # 登陆到IP-SAN
    log.info('Start target login operation!')
    for tgt_iqn in target_list:
        cmd_login = ('iscsicli QloginTarget %s' % tgt_iqn)
        (rc, stdout) = subprocess.getstatusoutput(cmd_login)
        if 0 != rc:
            log.error('target login failed!!!\ntagert:%s.info:%s' % (tgt_iqn, stdout))
        else:
            log.info('target login successful!!!')

def ISCSI_logout():
    log.info('iSCSI logout all target.')
    cmd = 'iscsicli SessionList'
    cmd_logout = 'iscsicli LogoutTarget '
    session_list = []
    result = os.popen(cmd).read()
    result_list = result.split('\n')
    for line in result_list:
        if 'Session Id' in line:
            session = line.split(':')
            session_id = session[1].strip()
            session_list.append(session_id)
    for eve_session in session_list:
        cmd = cmd_logout + eve_session
        (rc, stdout) = subprocess.getstatusoutput(cmd)
        if rc != 0:
            log.error('logout failed!!!info:%s' % stdout)
        else:
            log.info('iSCSI logout successful!')


def disk_operation():
    note='disk_conf.txt'
    cmd_disk='diskpart /s '+note
    (rc, stdout) = subprocess.getstatusoutput(cmd_disk)
    if rc != 0:
        log.error('init disk failed!!!info:%s' % stdout)
    else:
        log.info('init disk successful!')


def conf_X1000_disk():
    disk_idlist = []  # 磁盘ID列表
    # 获取映射到主机端的磁盘id号
    cmd = 'powershell disk'
    disklist = os.popen(cmd).read()
    with open('disk_conf.txt','w+') as filew:
        filew.write(disklist)
    with open('disk_conf.txt','r') as filer:
        for line in filer:
            if line.find('SUGON Xstor1000') != -1:
                linelist=line.split(' ')
                diskid=linelist[0]
                disk_idlist.append(diskid)

    # 将所有映射到主机端的磁盘获取并且联机
    for x1000_dsid in disk_idlist:
        log.info('Initialize the disk %s' % (x1000_dsid))
        cmdlist1 = 'select disk '+x1000_dsid+'\n'+'attributes disk clear readonly\nconvert MBR\n'+\
                'select disk '+x1000_dsid+'\n'+'online disk\n'+'rescan'
        with open('disk_conf.txt','w+') as filew:
            filew.write(cmdlist1)
        disk_operation()
        cmdlist2 = 'select disk '+x1000_dsid+'\n'+'online disk\n'+'rescan'
        with open('disk_conf.txt','w+') as filew:
            filew.write(cmdlist2)
        log.info('start online disk operation.')
        disk_operation()
    return disk_idlist

