#!/usr/bin/python
# -*-coding:utf-8 -*
"""
:Author:Diws
:Date:20190219
:Description:
两日志组中一日志组一个节点数据网故障，另一访问区一节点业务网闪断，另一节点故障
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
fault_node_1 = random.choice(disk.get_jnl_id_by_grp_id(grp_id=jnl_grps[0]))
# fault_ip_1 = disk.get_node_ip_by_id(n_id=fault_node_1)
down_eths_1, extra_ip_1 = error.get_dataip_info(node_id=fault_node_1)
if len(jnl_grps) > 1:
    fault_node_2 = random.choice(disk.get_jnl_id_by_grp_id(grp_id=jnl_grps[1]))
    down_eths_2, extra_ip_2 = error.get_dataip_info(node_id=fault_node_2)
tag1 = threading.Event()
tag2 = threading.Event()
tag3 = threading.Event()


def up_down():
    time.sleep(30)
    log.info("Begin to down node: %s through:%s." % (down_eths_1, extra_ip_1[0]))
    ReliableTest.run_down_net(extra_ip_1[0], down_eths_1)
    tag1.wait()
    log.info("Begin to up node: %s through: %s." % (down_eths_1, extra_ip_1[0]))
    ReliableTest.run_up_net(extra_ip_1[0], down_eths_1)


def up_down2():
    time.sleep(20)
    if len(jnl_grps) > 1:
        log.info("Begin to down node: %s through:%s." % (down_eths_2[:1], extra_ip_2[0]))
        ReliableTest.run_down_net(extra_ip_2[0], down_eths_2[:1])
        time.sleep(60)
        tag2.wait()
        log.info("Begin to shutdown node: %s." % (extra_ip_2[0]))
        m_info = error.down_node(fault_ip=extra_ip_2[0])
        error.up_node(node_info=m_info)
    tag3.set()


def vdb_jn():
    log.info("Run vdbench with jn.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jn")
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")
    tag1.set()
    tag2.set()
    tag3.wait()
    time.sleep(300)
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
