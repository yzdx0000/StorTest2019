#!/usr/bin/python
# -*-coding:utf-8 -*
"""
:Author:Diws
:Date:20190120
:Description:
两访问分区一访问分区一个节点业务网闪断，一节点oSan进程反复故障，另一访问一节点故障
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
nodes_1 = osrel.get_access_zone_node(az_id=access_zones[0])
fault_node_1 = random.choice(nodes_1)
fault_eths_1, extra_1 = error.get_ioip_info(node_id=fault_node_1)
nodes_1.remove(fault_node_1)
fault_node_2 = random.choice(nodes_1)
fault_ip_2 = disk.get_node_ip_by_id(n_id=fault_node_2)
if len(access_zones) > 1:
    nodes_2 = osrel.get_access_zone_node(az_id=access_zones[1])
    fault_node_3 = random.choice(nodes_2)
    fault_ip_3 = disk.get_node_ip_by_id(n_id=fault_node_3)


def up_down():
    time.sleep(20)
    log.info("Begin to down io net: %s through: %s." % (fault_eths_1, extra_1[0]))
    ReliableTest.run_down_net(extra_1[0], fault_eths_1)
    time.sleep(60)
    log.info("Begin to up io net: %s through: %s." % (fault_eths_1, extra_1[0]))
    ReliableTest.run_up_net(extra_1[0], fault_eths_1)
    time.sleep(120)
    tag1.set()


def up_down2():
    time.sleep(20)
    for i in range(10):
        log.info("Begin to kill oSan on: %s." % (fault_ip_2,))
        ReliableTest.run_kill_process(fault_ip_2, 'oSan')
        time.sleep(60)
    tag2.set()


def up_down3():
    time.sleep(70)
    if len(access_zones) > 1:
        log.info("Begin to shutdown node: %s." % (fault_ip_3,))
        m_info = error.down_node(fault_ip=fault_ip_3)
        time.sleep(360)
        log.info("Begin to startup node: %s." % (fault_ip_3,))
        error.up_node(node_info=m_info)
        time.sleep(420)
    tag3.set()


def vdb_jn():
    log.info("Run vdbench with jn.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jn")
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")
    tag1.wait()
    tag2.wait()
    tag3.wait()
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
    test_threads.append(threading.Thread(target=vdb_jn))
    test_threads.append(threading.Thread(target=vdb_run))
    for test_thread in test_threads:
        test_thread.setDaemon(True)
        test_thread.start()
    for test_thread in test_threads:
        test_thread.join()


if __name__ == '__main__':
    main()
