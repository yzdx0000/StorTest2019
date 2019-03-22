#!/usr/bin/python
# -*-coding:utf-8 -*

# testlink case: 1000-33054
import os, sys
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

conf_file = common2.CONF_FILE  # 配置文件路径
clean_env = common2.CLEAN_ENV
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)  # 初始化日志文件

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
# 修改vdbench配置文件的参数值
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
mix_R = osan.gen_vdb_xml(lun=lun2, xfersize=xfersize2, offset=offset, seekpct=seekpct2, rdpct=rdpct2)

# Get the node's ip to remove disk
fault_ip = error.get_fault_ip()
stor_pool_ids = disk.get_storage_pool_id()
# 移除共享池
stor_pool_ids.remove(1)
# 磁盘信息：disk_id:storage_pool_id
disk_info = {}
for stor_pool_id in stor_pool_ids:
    disks = disk.get_diskid_in_disk_pool(s_ip=deploy_ips[0], s_id=stor_pool_id)
    disk_id = random.choice(disks[str(stor_pool_id)])
    disk_info[disk_id] = stor_pool_id
    disks[str(stor_pool_id)].remove(disk_id)
    disk_id = random.choice(disks[str(stor_pool_id)])
    disk_info[disk_id] = stor_pool_id
diskids = disk_info.keys()
a_disk_ids = diskids[:len(diskids)/2+1]
b_disk_ids = diskids[len(diskids)/2+1:]


def up_down():
    adisk_phyid = {}
    for d_id in a_disk_ids:
        c_ips, n_id, d_name = disk.get_nodeinfo_by_diskid(s_ip=fault_ip, disk_id=d_id)
        adisk_phyid[c_ips[0]] = disk.get_disk_phyid_by_name(s_ip=c_ips[0], disk_name=d_name)
    if len(b_disk_ids) != 0:
        bdisk_phyid = {}
        for d_id in b_disk_ids:
            c_ips, n_id, d_name = disk.get_nodeinfo_by_diskid(s_ip=fault_ip, disk_id=d_id)
            bdisk_phyid[c_ips[0]] = disk.get_disk_phyid_by_name(s_ip=c_ips[0], disk_name=d_name)
    cmd = "ssh %s 'pscli --command=update_param --section=MGR --name=disk_isolate2rebuild_timeout --current=300000'" % (
        fault_ip)
    rc, stdout = commands.getstatusoutput(cmd)
    if 0 != rc:
        log.error('update param failed!!!')
        exit(1)
    time.sleep(300)
    for d_id in disk_ids:
        # Get the node ip ,node id, disk name by diskid
        c_ips, n_id, d_name = disk.get_nodeinfo_by_diskid(s_ip=fault_ip, disk_id=d_id)
        # Get the disk pyhid by disk name and node ip
        disk_phyids = disk.get_disk_phyid_by_name(s_ip=c_ips[0], disk_name=d_name)
        log.info("Begin remove disk:%s %s." % (c_ips[0], disk_phyids[0]))
        ReliableTest.remove_disk(c_ips[0], disk_phyids[0], "data")
    time.sleep(15)
    for d_id in adisk_phyid.keys():
        disk_phyids = adisk_phyid[d_id]
        log.info("Begin add disk:%s %s." % (d_id, disk_phyids[0]))
        ReliableTest.insert_disk(d_id, disk_phyids[0], "data")
    time.sleep(90)
    if len(b_disk_ids) != 0:
        for d_id in bdisk_phyid.keys():
            disk_phyids = bdisk_phyid[d_id]
            log.info("Begin add disk:%s %s." % (c_ips[0], disk_phyids[0]))
            ReliableTest.insert_disk(c_ips[0], disk_phyids[0], "data")
        time.sleep(10)
        for d_id in b_disk_ids:
            # Get the node ip ,node id, disk name by diskid
            c_ips, n_id, d_name = disk.get_nodeinfo_by_diskid(s_ip=fault_ip, disk_id=d_id)
            # Get the disk pyhid by disk name and node ip
            disk_uuid = disk.get_disk_uuid_by_name(s_ip=fault_ip, node_id=n_id, disk_name=d_name[0])
            disk.delete_disk(s_ip=fault_ip, disk_id=d_id)
            disk.add_disk(s_ip=fault_ip, uuid=disk_uuid, usage="DATA", node_id=n_id)
            disk.expand_disk_2_storage_pool_by_uuid(s_ip=fault_ip, node_id=n_id, uuid=disk_uuid, storage_pool_id=2)

    cmd = "ssh %s 'pscli --command=update_param --section=MGR --name=disk_isolate2rebuild_timeout --current=30000000'" % (
        fault_ip)
    rc, stdout = commands.getstatusoutput(cmd)
    if 0 != rc:
        log.error('update param failed!!!')
        exit(1)


def vdb_jn():
    log.info("Run vdbench with jn.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jn")
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")
    disk.check_bad_obj()
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")
    disk.multi_check_part_lun_uniform_by_ip()


def vdb_run():
    log.info("Run vdbench.")
    osan.run_vdb(client_ips[1], mix_R, output=deploy_ips[0], time=1800)


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
            # osan.iscsi_logout(cli,vip=ip)


if __name__ == '__main__':
    error.rel_check_before_run(file_name, jnl_rep=3, node_num=4, free_jnl_num=1, data_rep=3)
    main()
