#!/usr/bin/python
# -*-coding:utf-8 -*
"""
:Author:Diws
:Date:20190128
:Description:
两访问分区一访问分区一个节点业务网闪断，一节点ostor进程反复故障，另一访问一节点数据网故障
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
    for az in access_zones:
        nodes = osrel.get_access_zone_node(az_id=az)
        fault_node = random.choice(nodes)
        nodes.remove(fault_node)
        if node_flag == 0:
            fault_eth1, fault_ip1 = error.get_dataip_info(node_id=fault_node)
            node_flag += 1
        elif node_flag == 1:
            fault_eth2, fault_ip2 = error.get_ioip_info(node_id=fault_node)
            down_node = random.choice(nodes)
            down_ip = disk.get_node_ip_by_id(n_id=down_node)
            break
    log.info("Begin shutdown data net: %s on node: %s." % (fault_eth1, fault_ip1[0]))
    ReliableTest.run_down_net(fault_ip1[0], fault_eth1)
    log.info("Begin shutdown io net: %s on node: %s." % (fault_eth2, fault_ip2[0]))
    ReliableTest.run_down_net(fault_ip2[0], fault_eth2)
    log.info("Begin to kill oStor on node: %s." % (down_ip,))
    for i in range(10):
        ReliableTest.run_kill_process(down_ip, 'oStor')
        time.sleep(10)
    time.sleep(30)
    log.info("Begin up io net: %s on node: %s." % (fault_eth2, fault_ip2[0]))
    ReliableTest.run_up_net(fault_ip2[0], fault_eth2)
    time.sleep(60)
    log.info("Begin up data net: %s on node: %s." % (fault_eth1, fault_ip1[0]))
    ReliableTest.run_up_net(fault_ip1[0], fault_eth1)
    time.sleep(30)
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
