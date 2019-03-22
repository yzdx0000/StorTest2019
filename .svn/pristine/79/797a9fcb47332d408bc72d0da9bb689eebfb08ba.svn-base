#!/usr/bin/python
# -*-coding:utf-8 -*
"""
:Author:Diws
:Date:20190119
:Description:
2副本节点池两节点业务网同时故障
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
error.rel_check_before_run(file_name, node_num=5, data_rep=2)

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
node_pool_info = disk.get_node_ids_in_node_pool()
nodes = random.choice(node_pool_info.values())
node_1 = random.choice(nodes)
nodes.remove(node_1)
node_2 = random.choice(nodes)
tag1 = threading.Event()
tag2 = threading.Event()
tag3 = threading.Event()
tag4 = threading.Event()


def up_down():
    time.sleep(20)
    fault_eths_1, extra_ip_1 = error.get_ioip_info(node_id=node_1)
    log.info("Begin to down io net:%s through %s." % (fault_eths_1, extra_ip_1[0]))
    ReliableTest.run_down_net(extra_ip_1[0], fault_eths_1)
    tag1.wait()
    log.info("Begin to up io net:%s through %s." % (fault_eths_1, extra_ip_1[0]))
    ReliableTest.run_up_net(extra_ip_1[0], fault_eths_1)
    tag3.set()


def up_down2():
    time.sleep(20)
    fault_eths_2, extra_ip_2 = error.get_ioip_info(node_id=node_2)
    log.info("Begin to down io net:%s through %s." % (fault_eths_2, extra_ip_2[0]))
    ReliableTest.run_down_net(extra_ip_2[0], fault_eths_2)
    tag2.wait()
    log.info("Begin to up io net:%s through %s." % (fault_eths_2, extra_ip_2[0]))
    ReliableTest.run_up_net(extra_ip_2[0], fault_eths_2)
    tag4.set()


def vdb_jn():
    log.info("Run vdbench with jn.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jn")
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")
    tag1.set()
    tag2.set()
    tag3.wait()
    tag4.wait()
    time.sleep(100)
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
