#!/usr/bin/python
#-*-coding:utf-8 -*

# testlink case: 1000-33049
import os,sys
import utils_path
import common2
import common
import log
import get_config
import ReliableTest
import threading
import login
import breakdown
import time
import commands
import random
import error

conf_file = common2.CONF_FILE    #配置文件路径
clean_env = common2.CLEAN_ENV
file_name = os.path.basename(__file__)
file_name = file_name[:-3]      #获取本脚本名，去掉.py后缀
error.rel_check_before_run(file_name)


deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
type_info = get_config.get_machine_type(conf_file)
if type_info == "vir":
    (esxi_ip, esxi_un, esxi_pw) = get_config.get_esxi(conf_file)

osan = common2.oSan()
node = common.Node()
disk = breakdown.disk()

vip = login.login()
svip = osan.get_svip(s_ip=deploy_ips[0])
#修改vdbench配置文件的参数值
seekpct1 = 45
seekpct2 = 78
rdpct1 = 30
rdpct2 = 45
offset = "2048"
xfersize1 = "(3k,100)"
xfersize2 = "(2k,100)"
lun1 = osan.ls_scsi_dev(client_ips[0])
lun2 = osan.ls_scsi_dev(client_ips[1])
mix_R_align = osan.gen_vdb_xml(lun=lun1, xfersize=xfersize1, seekpct=seekpct1, rdpct=rdpct1)
mix_R = osan.gen_vdb_xml(lun=lun2, xfersize=xfersize2, offset=offset, seekpct=seekpct2,rdpct=rdpct2)

# Get the node's ip to remove disk
fault_ip = error.get_fault_ip()
storage_id = osan.get_storage_id(s_ip=fault_ip)
if 1 in storage_id:
    storage_id.remove(1)
disk_pool_id = disk.get_disk_pool(s_ip=fault_ip,ids=storage_id[0])
disk_pool = disk.get_diskid_in_disk_pool(s_ip=fault_ip,s_id=storage_id[0])

disk_pool_id1 = random.choice(disk_pool_id)
disk_pool_id.remove(disk_pool_id1)
diskid1 = random.choice(disk_pool[disk_pool_id1])
disk_pool[disk_pool_id1].remove(diskid1)
diskid2 = random.choice(disk_pool[disk_pool_id1])
log.info("Storage pool id is: %s,disk pool id is :%s ,disk id is %s and %s."
        %(str(storage_id[0]),str(disk_pool_id1),str(diskid1),str(diskid2)))
# Get the node ip ,node id, disk name by diskid
c_ips1,n_id1,d_name1 = disk.get_nodeinfo_by_diskid(s_ip=fault_ip,disk_id=diskid1)
c_ips2,n_id2,d_name2 = disk.get_nodeinfo_by_diskid(s_ip=fault_ip,disk_id=diskid2)

#Get the disk pyhid by disk name and node ip
disk_phyids1 = disk.get_disk_phyid_by_name(s_ip=c_ips1[0],disk_name=d_name1)
disk_phyids2 = disk.get_disk_phyid_by_name(s_ip=c_ips2[0],disk_name=d_name2)

disk_uuid2 = disk.get_disk_uuid_by_name(s_ip=fault_ip,node_id=n_id2,disk_name=d_name2[0])
storage_pool_id = disk.get_storage_poolid_by_diskid(s_ip=fault_ip, node_id=n_id2, disk_id=diskid2)

def up_down():
    cmd = "ssh %s 'pscli --command=update_param --section=MGR --name=disk_isolate2rebuild_timeout --current=300000'" % (
        fault_ip)
    rc, stdout = commands.getstatusoutput(cmd)
    if 0 != rc:
        log.error('update param failed!!!')
        exit(1)
    time.sleep(320)
    log.info("Begin remove disk:%s %s." %(c_ips1[0],disk_phyids1[0]))
    ReliableTest.remove_disk(c_ips1[0],disk_phyids1[0],"data")
    log.info("Begin remove disk:%s %s." % (c_ips2[0], disk_phyids2[0]))
    ReliableTest.remove_disk(c_ips2[0], disk_phyids2[0], "data")
    time.sleep(50)
    log.info("Begin add disk:%s %s." % (c_ips1[0], disk_phyids1[0]))
    ReliableTest.insert_disk(c_ips1[0],disk_phyids1[0],"data")
    time.sleep(1000)
    log.info("Begin add disk:%s %s." % (c_ips2[0], disk_phyids2[0]))
    ReliableTest.insert_disk(c_ips2[0], disk_phyids2[0], "data")
    cmd = "ssh %s 'pscli --command=update_param --section=MGR --name=disk_isolate2rebuild_timeout --current=30000000'" % (
        fault_ip)
    rc, stdout = commands.getstatusoutput(cmd)
    if 0 != rc:
        log.error('update param failed!!!')
        exit(1)
    while 'ZOMBIE' not in disk.check_disk_state(node_ip=fault_ip, disk_uuid=disk_uuid2):
        time.sleep(10)
    disk.delete_disk(s_ip=fault_ip,disk_id=diskid2)
    time.sleep(20)
    disk.add_disk(s_ip=fault_ip,uuid=disk_uuid2,usage="DATA",node_id=n_id2)
    disk.expand_disk_2_storage_pool_by_uuid(s_ip=fault_ip,node_id=n_id2,uuid=disk_uuid2,storage_pool_id=storage_pool_id)

def vdb_jn():
    log.info("Run vdbench with jn.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0],jn_jro="jn")
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")
    disk.check_bad_obj()
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")
    disk.multi_check_part_lun_uniform_by_ip()


def vdb_run():
    log.info("Run vdbench.")
    osan.run_vdb(client_ips[1], mix_R, output=deploy_ips[0],time=1800)
def main():
    test_threads = []
    test_threads.append(threading.Thread(target=up_down))
    test_threads.append(threading.Thread(target=vdb_jn))
    test_threads.append(threading.Thread(target=vdb_run))
    for test_thread in test_threads:
        test_thread.setDaemon(True)
        test_thread.start()
    for test_thread in test_threads:
        test_thread.join()
    for c_ip in client_ips:
        osan.vdb_check(c_ip=c_ip, time=100, oper="iops", output=deploy_ips[0])
    for ip in vip:
        for cli in client_ips:
            pass
            #osan.iscsi_logout(cli,vip=ip)
if __name__ == '__main__':
    main()
