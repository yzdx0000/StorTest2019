# -*- coding:utf-8 -*-
# 功能：获取集群的vip,initiator,target信息

import paramiko
import json
import log

MGR_node_ip = '10.2.40.252'

def get_vip():
    vip_list = []
    # 获取集群vip信息
    log.info('get vip info from system.interface node: %s' % MGR_node_ip)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=MGR_node_ip,port=22,username='root',password='111111')
    stdin,stdout,stderr = ssh.exec_command('pscli --command=get_vip_address_pools')
    result = stdout.read().decode()
    ssh.close()

    # 解析json，字符串处理，获取具体vip
    result_data = json.loads(result)
    vip_addr=result_data['result']['ip_address_pools'][0]['vip_addresses']
    vip_ls=vip_addr[0].split('.')
    if '-' in vip_ls[3]:
        vip_start = vip_ls[3].split('-')
        for vip in range(int(vip_start[0]), int(vip_start[1])+1):
            ip=vip_ls[0]+'.'+vip_ls[1]+'.'+vip_ls[2]+'.'+str(vip)
            vip_list.append(ip)
    else:
        vip_list.append(vip_addr[0])

    log.info('The system vips is %s' % (vip_list))
    return vip_list

def get_initiator():
    # 获取initiator
    log.info('get initiator info from system.interface node: %s' % MGR_node_ip)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=MGR_node_ip, port=22, username='root', password='111111')
    stdin,stdout,stderr = ssh.exec_command('pscli --command=get_initiators')
    result=stdout.read().decode()
    ssh.close()

    result_data = json.loads(result)
    initiator_result = result_data['result']['initiators']
    for initiator in initiator_result:
        if 'sugon' in initiator['alias']:
            log.info('The system initiators for windows host is %s.' % (initiator['name']))
            return initiator['name']
    log.error("Can't find initiator for windows host.Please check!")


def get_target():
    # 获取target
    log.info('get target info from system.interface node: %s' % MGR_node_ip)
    target_name_list = []
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=MGR_node_ip, port=22, username='root', password='111111')
    stdin, stdout, stderr = ssh.exec_command('pscli --command=get_targets')
    result=stdout.read().decode()
    ssh.close()

    result_data = json.loads(result)
    target_result = result_data['result']['targets']
    for target in target_result:
        target_name = target['name']
        target_name_list.append(target_name)
    log.info('The system target is %s' % target_name_list)
    return target_name_list

