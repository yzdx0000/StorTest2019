#!/usr/bin/python
# -*-coding:utf-8 -*
"""
:Author:Diws
:Date:20190120
:Description:
两访问区中每访问区两个节点一块共享盘故障和两块数据盘故障
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
access_zones = osrel.get_access_zones(node_ip=deploy_ips[0])[:2]
if len(access_zones) == 1:
    log.info("Attention!!! There is only one access zone in your cluster.")
tag1 = threading.Event()
tag2 = threading.Event()
tag3 = threading.Event()
tag4 = threading.Event()
nodes_1 = osrel.get_access_zone_node(az_id=access_zones[0])
fault_node_1 = random.choice(nodes_1)
nodes_1.remove(fault_node_1)
fault_node_2 = random.choice(nodes_1)
if len(access_zones) > 1:
    nodes_2 = osrel.get_access_zone_node(az_id=access_zones[1])
    fault_node_3 = random.choice(nodes_2)
    nodes_2.remove(fault_node_3)
    fault_node_4 = random.choice(nodes_2)


def up_down():
    time.sleep(20)
    fault_ip_1 = disk.get_node_ip_by_id(n_id=fault_node_1)
    share_disks = disk.get_rw_disk_by_node_id(s_ip=deploy_ips[0], node_id=fault_node_1, disk_type='share')
    share_disk_phy_ids = disk.get_disk_phyid_by_name(s_ip=fault_ip_1, disk_name=share_disks[:1])
    data_disks = disk.get_rw_disk_by_node_id(s_ip=deploy_ips[0], node_id=fault_node_1, disk_type='data')
    data_disk_phy_ids = disk.get_disk_phyid_by_name(s_ip=fault_ip_1, disk_name=data_disks[:2])
    for did in share_disk_phy_ids:
        log.info("Begin to remove disk:%s on %s, type: share." % (did, fault_ip_1))
        ReliableTest.remove_disk(fault_ip_1, did, 'SHARED')
    for did in data_disk_phy_ids:
        log.info("Begin to remove disk:%s on %s, type: data." % (did, fault_ip_1))
        ReliableTest.remove_disk(fault_ip_1, did, 'DATA')
    time.sleep(200)
    for did in share_disk_phy_ids:
        log.info("Begin to add disk:%s on %s, type: share." % (did, fault_ip_1))
        ReliableTest.insert_disk(fault_ip_1, did, 'SHARED')
    for did in data_disk_phy_ids:
        log.info("Begin to add disk:%s on %s, type: data." % (did, fault_ip_1))
        ReliableTest.insert_disk(fault_ip_1, did, 'DATA')
    tag1.set()


def up_down2():
    time.sleep(20)
    fault_ip_2 = disk.get_node_ip_by_id(n_id=fault_node_2)
    share_disks = disk.get_rw_disk_by_node_id(s_ip=deploy_ips[0], node_id=fault_node_2, disk_type='share')
    share_disk_phy_ids = disk.get_disk_phyid_by_name(s_ip=fault_ip_2, disk_name=share_disks[:1])
    data_disks = disk.get_rw_disk_by_node_id(s_ip=deploy_ips[0], node_id=fault_node_2, disk_type='data')
    data_disk_phy_ids = disk.get_disk_phyid_by_name(s_ip=fault_ip_2, disk_name=data_disks[:2])
    for did in share_disk_phy_ids:
        log.info("Begin to remove disk:%s on %s, type: share." % (did, fault_ip_2))
        ReliableTest.remove_disk(fault_ip_2, did, 'SHARED')
    for did in data_disk_phy_ids:
        log.info("Begin to remove disk:%s on %s, type: data." % (did, fault_ip_2))
        ReliableTest.remove_disk(fault_ip_2, did, 'DATA')
    time.sleep(200)
    for did in share_disk_phy_ids:
        log.info("Begin to add disk:%s on %s, type: share." % (did, fault_ip_2))
        ReliableTest.insert_disk(fault_ip_2, did, 'SHARED')
    for did in data_disk_phy_ids:
        log.info("Begin to add disk:%s on %s, type: data." % (did, fault_ip_2))
        ReliableTest.insert_disk(fault_ip_2, did, 'DATA')
    tag2.set()


def up_down3():
    time.sleep(70)
    if len(access_zones) > 1:
        fault_ip_3 = disk.get_node_ip_by_id(n_id=fault_node_3)
        share_disks = disk.get_rw_disk_by_node_id(s_ip=deploy_ips[0], node_id=fault_node_3, disk_type='share')
        share_disk_phy_ids = disk.get_disk_phyid_by_name(s_ip=fault_ip_3, disk_name=share_disks[:1])
        data_disks = disk.get_rw_disk_by_node_id(s_ip=deploy_ips[0], node_id=fault_node_3, disk_type='data')
        data_disk_phy_ids = disk.get_disk_phyid_by_name(s_ip=fault_ip_3, disk_name=data_disks[:2])
        for did in share_disk_phy_ids:
            log.info("Begin to remove disk:%s on %s, type: share." % (did, fault_ip_3))
            ReliableTest.remove_disk(fault_ip_3, did, 'SHARED')
        for did in data_disk_phy_ids:
            log.info("Begin to remove disk:%s on %s, type: data." % (did, fault_ip_3))
            ReliableTest.remove_disk(fault_ip_3, did, 'DATA')
        time.sleep(200)
        for did in share_disk_phy_ids:
            log.info("Begin to add disk:%s on %s, type: share." % (did, fault_ip_3))
            ReliableTest.insert_disk(fault_ip_3, did, 'SHARED')
        for did in data_disk_phy_ids:
            log.info("Begin to add disk:%s on %s, type: data." % (did, fault_ip_3))
            ReliableTest.insert_disk(fault_ip_3, did, 'DATA')
    tag3.set()


def up_down4():
    time.sleep(70)
    if len(access_zones) > 1:
        fault_ip_4 = disk.get_node_ip_by_id(n_id=fault_node_4)
        share_disks = disk.get_rw_disk_by_node_id(s_ip=deploy_ips[0], node_id=fault_node_4, disk_type='share')
        share_disk_phy_ids = disk.get_disk_phyid_by_name(s_ip=fault_ip_4, disk_name=share_disks[:1])
        data_disks = disk.get_rw_disk_by_node_id(s_ip=deploy_ips[0], node_id=fault_node_4, disk_type='data')
        data_disk_phy_ids = disk.get_disk_phyid_by_name(s_ip=fault_ip_4, disk_name=data_disks[:2])
        for did in share_disk_phy_ids:
            log.info("Begin to remove disk:%s on %s, type: share." % (did, fault_ip_4))
            ReliableTest.remove_disk(fault_ip_4, did, 'SHARED')
        for did in data_disk_phy_ids:
            log.info("Begin to remove disk:%s on %s, type: data." % (did, fault_ip_4))
            ReliableTest.remove_disk(fault_ip_4, did, 'DATA')
        time.sleep(200)
        for did in share_disk_phy_ids:
            log.info("Begin to add disk:%s on %s, type: share." % (did, fault_ip_4))
            ReliableTest.insert_disk(fault_ip_4, did, 'SHARED')
        for did in data_disk_phy_ids:
            log.info("Begin to add disk:%s on %s, type: data." % (did, fault_ip_4))
            ReliableTest.insert_disk(fault_ip_4, did, 'DATA')
    tag4.set()


def vdb_jn():
    log.info("Run vdbench with jn.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jn")
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")
    tag1.wait()
    tag2.wait()
    tag3.wait()
    tag4.wait()
    time.sleep(400)
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
    test_threads.append(threading.Thread(target=up_down3))
    test_threads.append(threading.Thread(target=up_down4))
    test_threads.append(threading.Thread(target=vdb_jn))
    test_threads.append(threading.Thread(target=vdb_run))
    for test_thread in test_threads:
        test_thread.setDaemon(True)
        test_thread.start()
    for test_thread in test_threads:
        test_thread.join()


if __name__ == '__main__':
    main()
