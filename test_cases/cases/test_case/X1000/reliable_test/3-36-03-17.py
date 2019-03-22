#!/usr/bin/python
# -*-coding:utf-8 -*
"""
:Author:Diws
:Date:20190219
:Description:
一日志组中JNL主进程故障和另一节点共享盘故障，另日志组一共享盘故障
"""
import os
import random
import utils_path
import common2
import common
import log
import get_config
import ReliableTest
import threading
import login
import time
import error
import breakdown

conf_file = common2.CONF_FILE
clean_env = common2.CLEAN_ENV
file_name = os.path.basename(__file__)
file_name = file_name[:-3]
error.rel_check_before_run(file_name, node_num=6, data_rep=3)

deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
osan = common2.oSan()
node = common.Node()
disk = breakdown.disk()
osrel = breakdown.Os_Reliable()
vip = login.login()

seekpct1 = 34
seekpct2 = 55
rdpct1 = 11
rdpct2 = 72
offset = "2048"
xfersize1 = "(3k,100)"
xfersize2 = "(2k,100)"
lun1 = osan.ls_scsi_dev(client_ips[0])
lun2 = osan.ls_scsi_dev(client_ips[1])
mix_R_align = osan.gen_vdb_xml(lun=lun1, xfersize=xfersize1, seekpct=seekpct1, rdpct=rdpct1)
mix_R = osan.gen_vdb_xml(lun=lun2, xfersize=xfersize2, offset=offset, seekpct=seekpct2, rdpct=rdpct2)
jnl_grps = disk.get_jnl_grp_id()
if len(jnl_grps) == 1:
    log.info("Attention!!! There is only one jnl groups in your cluster.")
nodes_1 = disk.get_jnl_id_by_grp_id(grp_id=jnl_grps[0])
loss = disk.get_lun_los_pair().values()
ips_1 = []
for node_1 in nodes_1:
    ips_1.append(disk.get_node_ip_by_id(n_id=node_1))
for los in loss:
    tmp = disk.get_nodeip_by_losid(losid=los)
    if tmp in ips_1:
        fault_ip_1 = tmp
        break
if len(jnl_grps) > 1:
    nodes_2 = disk.get_jnl_id_by_grp_id(grp_id=jnl_grps[1])
tag1 = threading.Event()
tag2 = threading.Event()


def up_down():
    time.sleep(30)
    ips_1.remove(fault_ip_1)
    fault_ip_12 = random.choice(ips_1)
    fault_node_12 = disk.get_node_id_by_ip(n_ip=fault_ip_12)
    share_disks = disk.get_rw_disk_by_node_id(s_ip=deploy_ips[0], node_id=fault_node_12, disk_type='share')
    share_disk_phy_ids = disk.get_disk_phyid_by_name(s_ip=fault_ip_12, disk_name=share_disks)
    log.info("Begin to kill oPara on %s." % (fault_ip_1,))
    ReliableTest.run_kill_process(fault_ip_1, 'oPara')
    log.info('Begin to remove share disk: %s  on %s.' % (share_disks, fault_ip_12))
    for did in share_disk_phy_ids:
        ReliableTest.remove_disk(fault_ip_1, did, 'SHARED')
    time.sleep(500)
    log.info('Begin to add share disk: %s on %s.' % (share_disks, fault_ip_12))
    for did in share_disk_phy_ids:
        ReliableTest.insert_disk(fault_ip_1, did, 'SHARED')
    tag1.set()


def up_down2():
    time.sleep(20)
    if len(jnl_grps) > 1:
        fault_node_2 = random.choice(nodes_2)
        fault_ip_2 = disk.get_node_ip_by_id(n_id=fault_node_2)
        share_disks = disk.get_rw_disk_by_node_id(s_ip=deploy_ips[0], node_id=fault_node_2, disk_type='share')[:1]
        share_disk_phy_ids = disk.get_disk_phyid_by_name(s_ip=fault_ip_2, disk_name=share_disks)
        log.info('Begin to remove share disk: %s on %s.' % (share_disks, fault_ip_2))
        for did in share_disk_phy_ids:
            ReliableTest.remove_disk(fault_ip_2, did, 'SHARED')
        time.sleep(500)
        log.info('Begin to add share disk: %s on %s.' % (share_disks, fault_ip_2))
        for did in share_disk_phy_ids:
            ReliableTest.insert_disk(fault_ip_2, did, 'SHARED')
    tag2.set()


def vdb_jn():
    log.info("Run vdbench with jn.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jn")
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")
    tag1.wait()
    tag2.wait()
    # 节点上电后，等待数据修复完成
    disk.check_bad_obj()
    log.info("Run vdbench with jro after the file repaired.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")
    disk.multi_check_part_lun_uniform_by_ip()


def vdb_run():
    log.info("Run vdbench.")
    osan.run_vdb(client_ips[1], mix_R, output=deploy_ips[0], time=1200)


def main():
    test_threads = []
    test_threads.append(threading.Thread(target=up_down))
    test_threads.append(threading.Thread(target=up_down2))
    test_threads.append(threading.Thread(target=vdb_jn))
    test_threads.append(threading.Thread(target=vdb_run))
    for test_thread in test_threads:
        test_thread.setDaemon(True)
        test_thread.start()
    for test_thread in test_threads:
        test_thread.join()


if __name__ == '__main__':
    main()
