#!/usr/bin/python
# -*- encoding=utf8 -*-
'''
Author : Di Weisong
Date  :2018-07-25
'''
import os
import json
import shell
import time
import subprocess
import commands
import log
import get_config
import sys
import re
import common2
import random
import ReliableTest
reload(sys)
sys.setdefaultencoding('utf-8')

class disk():
    '''
    get_rw_disk_by_node_id
    get_disk_phyid_by_name
    get_diskid_by_name
    get_disk_uuid_by_name
    delete_disk
    add_disk
    get_disk_pool
    get_diskid_in_disk_pool
    get_nodeinfo_by_diskid
    get_storage_poolid_by_diskid
    get_disk_id_by_uuid
    expand_disk_2_storage_pool
    get_lun_size
    '''
    def get_rw_disk_by_node_id(self,s_ip=None,node_id=None,disk_type=None):
        '''
        :Usage : get disks which are reading or writing by nodeid
        :param s_ip: server ip
        :param node_id: node id to check
        :disk_type : data or shared
        :return: list,list of disk names
        '''
        disks = []
        cmd = ("ssh %s 'pscli --command=get_disks --node_ids=%s'" %(s_ip,str(node_id)))
        (res, output) = commands.getstatusoutput(cmd)
        while 'ioStat' not in output:
            (res, output) = commands.getstatusoutput(cmd)
            time.sleep(1)
        if res != 0:
            log.error("Get disk name failed.")
            exit(1)
        else:
            result = json.loads(output)
            disk_list = result['result']['disks']
            for disk in disk_list:
                if disk_type == "share" or disk_type == "SHARE":
                    if disk["usage"] == "SHARED":
                        iops = str(disk["ioStat"]["tps"])
                        if iops != "0":
                            disks.append(disk["devname"])

                else:
                    if disk["usage"] == "DATA":
                        iops = str(disk["ioStat"]["tps"])
                        if iops != "0":
                            disks.append(disk["devname"])
            return disks
    def get_disk_phyid_by_name(self,s_ip=None,disk_name=None):
        '''
        :Usage : get disk physic id by disk name
        :param s_ip: node ip to get the disk
        :param disk_name:disk name ,ex:/dev/sdb
        :return: list,disks' phy id ex:0 0 1 0
        '''
        uuids = []
        for disk in disk_name:
            cmd = ("ssh %s 'lsscsi |grep %s'" %(s_ip, disk))
            (res, output) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error("Get disk uuid failed.")
                exit(1)
            else:
                uuids.append(re.sub(':',' ',re.sub('\[|\]','',output.split()[0])))
        return uuids
    def get_diskid_by_name(self,s_ip=None,node_id=None,disk_name=None):
        '''
        :Usage : get disk name by node id and disk name
        :param s_ip: server ip
        :param node_id: node id on which to check the disk
        :param disk_name: ex:/dev/sdb
        :return:int, disk id
        '''
        cmd = ("ssh %s 'pscli --command=get_disks --node_ids=%s'" % (s_ip, str(node_id)))
        (res, output) = commands.getstatusoutput(cmd)
        if res != 0:
            log.error("Get disk id failed.")
            exit(1)
        else:
            result = json.loads(output)
            disk_list = result['result']['disks']
            for disk in disk_list:
                if disk["devname"] == disk_name:
                    return disk["id"]
    def get_disk_uuid_by_name(self,s_ip=None,node_id=None,disk_name=None):
        '''
        :Usage : get disk uuid by its name and node id
        :param s_ip: server ip
        :param node_id: node where the disk locate
        :param disk_name: ex: /dev/sdb
        :return: str,disk's uuid
        '''
        cmd = ("ssh %s 'pscli --command=get_disks --node_ids=%s'" % (s_ip, str(node_id)))
        rc, stdout = commands.getstatusoutput(cmd)
        if 0 != rc:
            log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            exit(1)
        else:
            result = json.loads(stdout)
            disk_list = result['result']['disks']
            for disk in disk_list:
                if disk['devname'] == disk_name:
                    return disk['uuid']
    def delete_disk(self,s_ip=None,disk_id=None):
        '''
        :Usage : delete disk by pscli command
        :param s_ip: node ip to delete the disk
        :param disk_id: disk id
        :return: None
        '''
        cmd = ("ssh %s 'pscli --command=remove_disks --disk_ids=%s'" % (s_ip,str(disk_id)))
        rc, stdout = commands.getstatusoutput(cmd)
        if 0 != rc:
            log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            exit(1)
        return
    def add_disk(self,s_ip=None,uuid=None,usage=None):
        '''
        :Usage : add disk on one node through pscli command
        :param s_ip: node ip to add disk
        :param uuid: disk's uuid
        :param usage: data or share
        :return: None
        '''
        cmd = ("ssh %s 'pscli --command=add_disks --node_ids=%s --disk_uuids=%s --usage=%s'" %(s_ip,str(node_id), uuid, usage))
        rc, stdout = commands.getstatusoutput(cmd)
        if 0 != rc:
            log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            exit(1)
        else:
            log.info("Add disk success.")
    def get_disk_pool(self,s_ip=None,ids=None):
        '''
        :Usage : get disk pool by storage id
        :param s_ip:server ip
        :return: list,disk pool id
        '''
        disk_pool_id = []
        cmd = ("ssh %s \"pscli --command=get_storage_pool_stat --ids=%s| awk '{print \$4}'\"" % (s_ip,str(ids)))
        rc, stdout = commands.getstatusoutput(cmd)
        if 0 != rc:
            log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            exit(1)
        else:
            for line in stdout.strip().split("\n"):
                if line == "disk_pool_id" or line == '':
                    continue
                else:
                    disk_pool_id.append(line)
            return disk_pool_id
    def get_diskid_in_disk_pool(self,s_ip=None,s_id=None):
        '''
        :Usage : get disk id by storage id
        :param s_ip:server ip
        :param d_pool_id: storage id
        :return:list ,disk id in the same disk pool
        '''
        disk_pool_id = {}
        disk_id = []
        cmd = ("ssh %s \"pscli --command=get_storage_pool_stat --ids=%s| "
               "awk '(diskid=NF-1)(poolid=NF-2)"
               "{if (poolid>0)print \$poolid,\$diskid;"
               "else if (diskid>0 && poolid<=0)print \$diskid}'\""
               % (s_ip,str(s_id)))
        rc, stdout = commands.getstatusoutput(cmd)
        if 0 != rc:
            log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
            exit(1)
        else:
            for id in stdout.split("\n"):
                if id == 'disk_pool_id disk_id':
                    continue
                else:
                    ids = id.split()
                    if len(ids) == 2:
                        disk_id = []
                        id_key = ids[0]
                        disk_id.append(ids[1])
                        disk_pool_id[id_key] = disk_id
                    else:
                        disk_id.append(id)
                        disk_pool_id[id_key] = disk_id
            return disk_pool_id
    def get_nodeinfo_by_diskid(self,s_ip=None,disk_id=None):
        '''
        :Usage : get node ctr ip ,node id ,disk name by disk id
        :param s_ip: server ip
        :param disk_id: disk id
        :return: list,int,list
        '''
        osan = common2.oSan()
        node_ids = osan.get_nodes(s_ip=s_ip)
        for node_id in node_ids:
            cmd = ("ssh %s 'pscli --command=get_disks --node_ids=%s'" % (s_ip, str(node_id)))
            (res, output) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error("Get disk id failed.")
                exit(1)
            else:
                result = json.loads(output)
                disk_list = result['result']['disks']
                for disk in disk_list:
                    if str(disk["id"]) == str(disk_id):
                        d_name = []
                        ctl_ips = ReliableTest.get_ctl_ips(node_ip=s_ip, node_id=node_id)
                        print ctl_ips
                        ips = osan.analysis_vip(ctl_ips)
                        name = disk["devname"]
                        d_name.append(name)
                        return ips,node_id,d_name

    def get_storage_poolid_by_diskid(self,s_ip=None,node_id=None,disk_id=None):
        '''
        :Usage : get strage pool id by disk id
        :param s_ip: server ip
        :param node_id:
        :param disk_id:
        :return:int
        '''
        cmd = ("ssh %s 'pscli --command=get_disks --node_ids=%s'" %(s_ip,str(node_id)))
        (res, output) = commands.getstatusoutput(cmd)
        if res != 0:
            log.error("Get disk info failed.")
            exit(1)
        else:
            msg = json_loads(stdout)
            disks_info = msg["result"]["disks"]
            for disk in disks_info:
                if disk['id'] == disk_id:
                    return disk['storagePoolId']
            log.info("there is not a disk's id is %s!!!" %(str(disk_id)))
            return None
    def get_disk_id_by_uuid(self,s_ip=None,node_id=None,disk_uuid=None):
        '''
        :Usage : get disk id by its uuid
        :param s_ip:
        :param node_idd:
        :param disk_uuid:
        :return: int
        '''
        cmd = ("ssh %s 'pscli --command=get_disks --node_ids=%s'" %(s_ip,str(node_id)))
        (res, output) = commands.getstatusoutput(cmd)
        if res != 0:
            log.error("Get disk info failed.")
            exit(1)
        else:
            result = json_loads(stdout)
            disk_list = result['result']['disks']
            for disk in disk_list:
                if disk['uuid'] == disk_uuid:
                    return disk['id']
        return None
    def expand_disk_2_storage_pool(self,s_ip=None,stor_id=None,disk_id=None):
        '''
        :Usage : add disk to storage pool
        :param s_ip:
        :param stor_id:
        :param disk_id:
        :return:None
        '''
        cmd = ("ssh %s 'pscli --command=expand_storage_pool --storage_pool_id=%s --disk_ids=%s'" %(s_ip,str(stor_id),str(disk_id)))
        (res, output) = commands.getstatusoutput(cmd)
        if res != 0:
            log.error("Add disk: %s to storage pool: %s failed." %(str(disk_id),str(stor_id)))
            exit(1)
    def expand_disk_2_storage_pool_by_uuid(self,s_ip=None,node_id=None,uuid=None):
        '''
        :Usage : add disk to storage pool by its uuid
        :param s_ip:
        :param node_id:
        :param uuid:
        :return:
        '''
        disk_id = get_disk_id_by_uuid(s_ip=s_ip,node_id=node_id,disk_uuid=uuid)
        storage_pool_id = get_storage_poolid_by_diskid(s_ip=s_ip, node_id=node_id, disk_id=disk_id)
        expand_disk_2_storage_pool(s_ip=s_ip, stor_id=storage_pool_id, disk_id=disk_id)
    def get_lun_size(self,c_ip=None,lun=None):
        '''
        :Usage : get lun's size
        :param c_ip:
        :param lun:
        :return: int,unit:GB
        '''
        cmd = ("ssh %s \"fdisk -l %s 2> /dev/null | grep '%s' | awk -F ',| ' '{print \$3}'\"" % (c_ip,lun,lun))
        (res, output) = commands.getstatusoutput(cmd)
        if res != 0:
            log.error("Get %s size failed." %(lun))
            exit(1)
        else:
            return output
    def parted_lun(self,c_ip=None,lun=None,min_size=None,max_size=None):
        '''
        :Usage : make a part for the disk by parted tool
        :param c_ip: host ip
        :param lun: lun to make part
        :param min_size: range
        :param max_size: range
        :return: part name
        '''
        # range_1 : min:0G,max:4G
        # range_2 : min:4G,max:16384G(16T)
        # range_3 : min:16384G,max:65536G(64T)
        # range_4 : min:65536G,max:262144G(256T)

        #Judge if the lun is exist
        cmd = ("ssh %s 'ls %s1'" % (c_ip,lun))
        (res, output) = commands.getstatusoutput(cmd)
        if res != 0:
            lun_size = self.get_lun_size(c_ip=c_ip,lun=lun)
            lun_size = int(lun_size.split('.')[0])
            if min_size == None or max_size ==None:
                if lun_size <= 4:
                    return lun
                elif lun_size <= 16384 and lun_size >4:
                    range_num = random.randint(0,1)
                    if range_num == 0:
                        min_size = random.randint(0,4)
                        max_size = min_size+2
                    else:
                        min_size = random.randint(0,lun_size-2)
                        max_size = min_size+2
                elif lun_size > 16384 and lun_size <= 65536:
                    range_num = random.randint(0,2)
                    if range_num == 0:
                        min_size = random.randint(0, 4)
                        max_size = min_size + 2
                    elif range_num == 1:
                        min_size = random.randint(4,16384)
                        max_size = min_size+2
                    else:
                        min_size = random.randint(16384,lun_size-2)
                        max_size = min_size+2
                else:
                    range_num = random.randint(0,3)
                    if range_num == 0:
                        min_size = random.randint(0, 4)
                        max_size = min_size + 2
                    elif range_num == 1:
                        min_size = random.randint(4, 16384)
                        max_size = min_size + 2
                    elif range_num == 2:
                        min_size = random.randint(16384,65536)
                        max_size = min_size + 2
                    else:
                        min_size = random.randint(65536,lun_size-2)
                        max_size = min_size+2

            cmd = ("ssh %s 'parted -s %s mklabel gpt mkpart primary %sM %sM'" %(c_ip,lun,str(min_size),str(max_size)))
            (res, output) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error("Parted %s and mkpart %s to %s on %s failed." %(lun,str(min_size),str(max_size),c_ip))
                exit(1)
            else:
                return lun+'1'
        else:
            return lun+'1'
    def del_lun_part(self,c_ip=None,lun=None):
        '''
        :Usage : delete the lun partion
        :param c_ip: host ip
        :param lun: lun name
        :return: None
        '''
        cmd = ("ssh %s 'parted -s %s rm 1'" % (c_ip, lun))
        (res, output) = commands.getstatusoutput(cmd)
        if res != 0:
            log.error("Rm partion %s on %s failed." % (lun, c_ip))
        else:
            return