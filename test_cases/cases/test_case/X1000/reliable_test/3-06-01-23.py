#!/usr/bin/python
# -*- coding:utf-8 -*-

# testlink case: 1000-32644
import os,sys
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

conf_file = common2.CONF_FILE
clean_env = common2.CLEAN_ENV
file_name = os.path.basename(__file__)
file_name = file_name[:-3]
log_file_path = log.get_log_path(file_name)
log.init(log_file_path, True)

deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
type_info = get_config.get_machine_type(conf_file)
if type_info == "vir":
    (esxi_ip, esxi_un, esxi_pw) = get_config.get_esxi(conf_file)
osan = common2.oSan()
disk = breakdown.disk()
node = common.Node()
vip = login.login()
svip = osan.get_svip(s_ip=deploy_ips[0])
#修改vdbench配置文件的参数值
seekpct1 = 45
seekpct2 = 58
rdpct1 = 30
rdpct2 = 45
offset = "2048"
xfersize1 = "(3k,100)"
xfersize2 = "(2k,100)"
lun1 = osan.ls_scsi_dev(client_ips[0])
lun2 = osan.ls_scsi_dev(client_ips[1])
mix_R_align = osan.gen_vdb_xml(lun=lun1, xfersize=xfersize1, seekpct=seekpct1, rdpct=rdpct1)
mix_R = osan.gen_vdb_xml(lun=lun2, xfersize=xfersize2, offset=offset, seekpct=seekpct2,rdpct=rdpct2)
#主机 A 网络信息
    #虚IP所在节点物理IP
vip_node_ip = osan.get_node_by_vip(vip=vip[0])
    #虚IP所在节点物理ID
vip_node_id = node.get_node_id_by_ip(vip_node_ip)
a_eths,a_extra = error.get_ioip_info(node_id=vip_node_id)
# 主机 B 网络信息
b_ip = error.get_fault_ip()
while b_ip == vip_node_ip:
    b_ip = error.get_fault_ip()
b_id = node.get_node_id_by_ip(b_ip)
b_eths,b_extra = error.get_ioip_info(node_id=b_id)
b_data,b_dex = error.get_dataip_info(node_id=b_id)
def up_down():
    time.sleep(200)
    log.info("Begin down node:%s." %(vip_node_ip))
    ReliableTest.run_down_net(a_extra[0],a_eths)
    time.sleep(30)
    log.info("Begin down node:%s." %(b_ip))
    ReliableTest.run_down_net(b_extra[0],b_eths)
    time.sleep(60)
    if b_data != b_eths:
        c_vip_node_ip = osan.get_node_by_vip(vip=vip[0])
        c_vip_node_id = node.get_node_id_by_ip(c_vip_node_ip)
        log.info("Begin down node:%s." %(c_vip_node_ip))
        c_eths,c_extra = error.get_ioip_info(node_id=c_vip_node_id)
        ReliableTest.run_down_net(c_extra[0],c_eths)
    time.sleep(600)
    log.info("Begin up node:%s." %(vip_node_ip))
    ReliableTest.run_up_net(a_extra[0],a_eths)
    log.info("Begin up node:%s." %(b_ip))
    ReliableTest.run_up_net(b_extra[0],b_eths)
    if b_data != b_eths:
        log.info("Begin up node:%s." %(c_vip_node_ip))
        ReliableTest.run_up_net(c_extra[0],c_eths)
def vdb_jn():
    log.info("Run vdbench with jn.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0],jn_jro="jn")
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")
    disk.multi_check_part_lun_uniform_by_ip()


def vdb_run():
    log.info("Run vdbench.")
    osan.run_vdb(client_ips[1], mix_R, output=deploy_ips[0])


def case():
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


def main():
    error.rel_check_before_run(file_name, jnl_rep=3, node_num=4, free_jnl_num=1, data_rep=3)
    case()


if __name__ == '__main__':
    main()