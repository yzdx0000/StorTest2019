#!/usr/bin/python
# -*-coding:utf-8 -*
"""
:Author:Diws
:Date:20190109
:Description:
同一存储池同一Vset 两块数据盘故障后，一块盘超时内恢复
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
error.rel_check_before_run(file_name, node_num=3, data_rep=3)

deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
osan = common2.oSan()
node = common.Node()
disk = breakdown.disk()
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


def up_down(pipe_write):
    stor_pool_ids = disk.get_storage_pool_id()
    # 移除共享池
    stor_pool_ids.remove(1)
    # 选择两个存储池
    stor_pool_ids = stor_pool_ids[:2]
    # 磁盘信息：disk_id:storage_pool_id
    disk_info = {}
    # 超时磁盘id，每个存储池选择一个磁盘
    timeout_disk = []
    # 超时内磁盘id
    timein_disk = []
    for stor_pool_id in stor_pool_ids:
        disks = disk.get_diskid_in_disk_pool(s_ip=deploy_ips[0], s_id=stor_pool_id)
        disk_id = random.choice(disks)
        disk_info[disk_id] = stor_pool_id
        timein_disk.append(disk_id)
        disks.remove(disk_id)
        disk_id = random.choice(disks)
        disk_info[disk_id] = stor_pool_id
        timeout_disk.append(disk_id)
    # 所有故障磁盘id
    disk_ids = disk_info.keys()
    disk_phyid_info = {}
    for d_id in disk_ids:
        c_ips, n_id, d_name = disk.get_nodeinfo_by_diskid(s_ip=deploy_ips[0], disk_id=d_id)
        disk_phyid = disk.get_disk_phyid_by_name(s_ip=c_ips[0], disk_name=d_name)
        disk_phyid_info[d_id] = [c_ips[0], disk_phyid, n_id]
    time.sleep(20)
    for i in disk_phyid_info.keys():
        log.info("Begin remove disk:%s %s." % (disk_phyid_info[i][0], disk_phyid_info[i][1]))
        ReliableTest.remove_disk(disk_phyid_info[i][0], disk_phyid_info[i][1], "data")
    cmd = "pscli --command=update_param --section=MGR --name=disk_isolate2rebuild_timeout --current=300000"
    osan.run_pscli_cmd(pscli_cmd=cmd)
    log.info(cmd)
    time.sleep(100)
    for diskid in disk_phyid_info.keys():
        if diskid in timein_disk:
            log.info("Begin add disk:%s %s." % (disk_phyid_info[diskid][0], disk_phyid_info[diskid][1]))
            ReliableTest.insert_disk(disk_phyid_info[diskid][0], disk_phyid_info[diskid][1], "data")
    time.sleep(300)
    for diskid in disk_phyid_info.keys():
        if diskid in timeout_disk:
            log.info("Begin add disk:%s %s." % (disk_phyid_info[diskid][0], disk_phyid_info[diskid][1]))
            ReliableTest.insert_disk(disk_phyid_info[diskid][0], disk_phyid_info[diskid][1], "data")
            disk_uuid = disk.get_disk_uuid_by_diskid(disk_id=diskid)
            disk.delete_disk(s_ip=deploy_ips[0], disk_id=diskid)
            time.sleep(30)
            # 添加磁盘到集群
            disk.add_disk(s_ip=deploy_ips[0], uuid=disk_uuid, usage='DATA', node_id=disk_phyid_info[diskid][2])
            # 添加磁盘到原存储池
            disk.expand_disk_2_storage_pool_by_uuid(s_ip=deploy_ips[0], node_id=disk_phyid_info[diskid][2],
                                                    uuid=disk_uuid, storage_pool_id=disk_info[diskid])
    time.sleep(20)
    cmd = "pscli --command=update_param --section=MGR --name=disk_isolate2rebuild_timeout --current=1440000"
    osan.run_pscli_cmd(pscli_cmd=cmd)
    log.info(cmd)
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
    # 磁盘插回后，等待数据修复完成
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
