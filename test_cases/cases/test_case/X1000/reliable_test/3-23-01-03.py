#!/usr/bin/python
#-*-coding:utf-8 -*

# testlink case: 1000-33044
import os,sys
import utils_path
import common2
import common
import log
import get_config
import ReliableTest
import threading
import login
import time
import commands
import error
import random
import breakdown

conf_file = common2.CONF_FILE    #配置文件路径
clean_env = common2.CLEAN_ENV
file_name = os.path.basename(__file__)
file_name = file_name[:-3]      #获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)     #获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)       #初始化日志文件

deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
osan = common2.oSan()
node = common.Node()
disk = breakdown.disk()

vip = login.login()
#修改vdbench配置文件的参数值
#seekpct1 = 55
seekpct2 = 0
#rdpct1 = 11
rdpct2 = 72
offset = "2048"
xfersize1 = "(3k,100)"
xfersize2 = "(2k,100)"
lun1 = osan.ls_scsi_dev(client_ips[0])
lun2 = osan.ls_scsi_dev(client_ips[1])
mix_O = osan.vdb_write(sd="default")
for i in range(0,len(lun1)):
    j = i+1
    if i == 0:
        mix_O = osan.vdb_write(sd="sd"+str(j),lun=lun1[i],wd="wd"+str(j),xfersize="8k",seekpct=100,rdpct=0,skew=20)
    if i == 1:
        mix_O = osan.vdb_write(sd="sd"+str(j),lun=lun1[i],wd="wd"+str(j),xfersize="4k",seekpct=100,rdpct=0,skew=45)
    if i == 2:
        mix_O = osan.vdb_write(sd="sd"+str(j),lun=lun1[i],wd="wd"+str(j),xfersize="8k",seekpct=0,rdpct=0,skew=15)
    if i == 3:
        mix_O = osan.vdb_write(sd="sd"+str(j),lun=lun1[i],wd="wd"+str(j),xfersize="4k",seekpct=100,rdpct=0,skew=10)
    if i == 4:
        mix_O = osan.vdb_write(sd="sd"+str(j),lun=lun1[i],wd="wd"+str(j),xfersize="4k",seekpct=0,rdpct=0,skew=10)
mix_S = osan.gen_vdb_xml(lun=lun2, xfersize=xfersize2, offset=offset, seekpct=seekpct2,rdpct=rdpct2)

# Get the node's ip to remove disk
fault_ip = error.get_fault_ip()
# Get the node's id by ip
node_id = node.get_node_id_by_ip(fault_ip)
# Get the node's disk names, disk type :data
disk_names = disk.get_rw_disk_by_node_id(s_ip=fault_ip,node_id=node_id,disk_type="data")
disk_name = []
disk_name.append(random.choice(disk_names))
# Get the disks' phyid
disk_phyids = disk.get_disk_phyid_by_name(s_ip=fault_ip,disk_name=disk_name)
#fault_disk = random.choice(disk_phyids)
disk_id = disk.get_diskid_by_name(s_ip=fault_ip,node_id=node_id,disk_name=disk_name[0])
disk_uuid = disk.get_disk_uuid_by_name(s_ip=fault_ip,node_id=node_id,disk_name=disk_name[0])
storage_pool_id = disk.get_storage_poolid_by_diskid(s_ip=fault_ip, node_id=node_id, disk_id=disk_id)
event1 = threading.Event()


def up_down():
    time.sleep(20)
    cmd = "ssh %s 'pscli --command=update_param --section=MGR --name=disk_isolate2rebuild_timeout --current=300000'" %(fault_ip)
    rc, stdout = commands.getstatusoutput(cmd)
    if 0 != rc:
        log.error('update param failed!!!')
        exit(1)
    log.info("Begin remove disk:%s %s." %(fault_ip,disk_phyids[0]))
    ReliableTest.remove_disk(fault_ip,disk_phyids[0],"data")
    time.sleep(320)
    log.info("Begin add disk:%s %s." % (fault_ip, disk_phyids[0]))
    ReliableTest.insert_disk(fault_ip,disk_phyids[0],"data")
    cmd = "ssh %s 'pscli --command=update_param --section=MGR --name=disk_isolate2rebuild_timeout --current=3000000'" % (
        fault_ip)
    rc, stdout = commands.getstatusoutput(cmd)
    if 0 != rc:
        log.error('update param failed!!!')
        exit(1)
    while 'ZOMBIE' not in disk.check_disk_state(node_ip=fault_ip, disk_uuid=disk_uuid):
        time.sleep(10)
    event1.set()
    disk.delete_disk(s_ip=fault_ip,disk_id=disk_id)
    time.sleep(20)
    disk.add_disk(s_ip=fault_ip,uuid=disk_uuid,usage="DATA",node_id=node_id)
    disk.expand_disk_2_storage_pool_by_uuid(s_ip=fault_ip,node_id=node_id,uuid=disk_uuid,storage_pool_id=storage_pool_id)

def vdb_jn():
    log.info("Run vdbench with jn.")
    osan.run_vdb(client_ips[0], mix_O, output=deploy_ips[0],jn_jro="jn")
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_O, output=deploy_ips[0], jn_jro="jro")
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_O, output=deploy_ips[0], jn_jro="jro")
    log.info("Check bad obj repairing.")
    event1.wait()
    common.check_badjobnr()   #等待所有坏对象修复完成
    disk.check_bad_obj()
    log.info("Run vdbench with jro after the file repaired.")
    osan.run_vdb(client_ips[0], mix_O, output=deploy_ips[0], jn_jro="jro")
    disk.multi_check_part_lun_uniform_by_ip()


def vdb_run():
    log.info("Run vdbench.")
    osan.run_vdb(client_ips[1], mix_S, output=deploy_ips[0],time=1200)
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
    error.rel_check_before_run(file_name, jnl_rep=3, node_num=4, free_jnl_num=1, data_rep=3)
    main()