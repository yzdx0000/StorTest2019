#!/usr/bin/python
# -*-coding:utf-8 -*
"""
:Author:Diws
:Date:20190128
:Description:
两访问区中两个节点一块共享盘故障和两块数据盘故障
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


def up_down(pipe_write):
    node_flag = 0
    fault_disk = {}
    for az in access_zones:
        nodes = osrel.get_access_zone_node(az_id=az)
        fault_node = random.choice(nodes)
        nodes.remove(fault_node)
        if node_flag == 0:
            fault_ip_1 = disk.get_node_ip_by_id(n_id=fault_node)
            data_disks = disk.get_rw_disk_by_node_id(s_ip=deploy_ips[0], node_id=fault_node, disk_type='data')
            meta_disks = disk.get_rw_disk_by_node_id(s_ip=deploy_ips[0], node_id=fault_node, disk_type='share')
            fault_disks_1 = data_disks[:2] + meta_disks[:1]
            fault_disks_id_1 = disk.get_disk_phyid_by_name(s_ip=fault_ip_1, disk_name=fault_disks_1)
            fault_disk[fault_ip_1] = fault_disks_id_1
            node_flag += 1
        elif node_flag == 1:
            fault_ip_2 = disk.get_node_ip_by_id(n_id=fault_node)
            data_disks = disk.get_rw_disk_by_node_id(s_ip=deploy_ips[0], node_id=fault_node, disk_type='data')
            meta_disks = disk.get_rw_disk_by_node_id(s_ip=deploy_ips[0], node_id=fault_node, disk_type='share')
            fault_disks_2 = data_disks[:2] + meta_disks[:1]
            fault_disks_id_2 = disk.get_disk_phyid_by_name(s_ip=fault_ip_2, disk_name=fault_disks_2)
            fault_disk[fault_ip_2] = fault_disks_id_2
            break
    for dip in fault_disk.keys():
        for fdisk in fault_disk[dip]:
            log.info("Begin remove disk:%s %s." % (dip, fdisk))
            ReliableTest.remove_disk(dip, fdisk, "data")
    time.sleep(320)
    for dip in fault_disk.keys():
        for fdisk in fault_disk[dip]:
            log.info("Begin add disk:%s %s." % (dip, fdisk))
            ReliableTest.insert_disk(dip, fdisk, "data")
    os.write(pipe_write, "success")


def vdb_jn(pipe_read):
    log.info("Run vdbench with jn.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jn")
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")
    while True:
        disk_info = os.read(pipe_read, 30)
        if len(disk_info) != 0:
            log.info(disk_info)
            log.info("Add disk finished.")
            break
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
    pipe_read, pipe_write = os.pipe()
    test_threads.append(threading.Thread(target=up_down, args=(pipe_write,)))
    test_threads.append(threading.Thread(target=vdb_jn, args=(pipe_read,)))
    test_threads.append(threading.Thread(target=vdb_run))
    for test_thread in test_threads:
        test_thread.setDaemon(True)
        test_thread.start()
    for test_thread in test_threads:
        test_thread.join()


if __name__ == '__main__':
    main()
