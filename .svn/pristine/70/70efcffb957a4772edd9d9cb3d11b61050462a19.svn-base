#!/usr/bin/python
#-*-coding:utf-8 -*

import os,sys
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
import commands
import error

conf_file = common2.CONF_FILE    #配置文件路径
clean_env = common2.CLEAN_ENV
file_name = os.path.basename(__file__)
file_name = file_name[:-3]      #获取本脚本名，去掉.py后缀
error.rel_check_before_run(file_name)
osan.init_win_log(file_name)

deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
osan = common2.oSan()
vip = login.login()
#修改vdbench配置文件的参数值
mix_R_win = osan.gen_win_vdb_conf(xfersize="(4k,80,16k,20)",
                                  seekpct=0,
                                  rdpct=0)
#seekpct1 = 55
seekpct2 = 34
#rdpct1 = 11
rdpct2 = 0
offset = "2048"
xfersize1 = "(4k,80,16k,20)"
xfersize2 = "(4k,80,16k,20)"
lun1 = osan.ls_scsi_dev(client_ips[0])
lun2 = osan.ls_scsi_dev(client_ips[1])
mix_O = osan.vdb_write(sd="default")
for i in range(0,len(lun1)):
    j = i+1
    if i == 0:
        mix_O = osan.vdb_write(sd="sd"+str(j),lun=lun1[i],wd="wd"+str(j),xfersize="8k",seekpct=100,rdpct=10,skew=20)
    if i == 1:
        mix_O = osan.vdb_write(sd="sd"+str(j),lun=lun1[i],wd="wd"+str(j),xfersize="4k",seekpct=100,rdpct=10,skew=45)
    if i == 2:
        mix_O = osan.vdb_write(sd="sd"+str(j),lun=lun1[i],wd="wd"+str(j),xfersize="8k",seekpct=0,rdpct=10,skew=15)
    if i == 3:
        mix_O = osan.vdb_write(sd="sd"+str(j),lun=lun1[i],wd="wd"+str(j),xfersize="64k",seekpct=100,rdpct=0,skew=10)
    if i == 4:
        mix_O = osan.vdb_write(sd="sd"+str(j),lun=lun1[i],wd="wd"+str(j),xfersize="64k",seekpct=0,rdpct=0,skew=10)
mix_S = osan.gen_vdb_xml(lun=lun2, xfersize=xfersize2, offset=offset, seekpct=seekpct2,rdpct=rdpct2)
#主机 A 网络信息
    #虚IP所在节点物理IP
#vip_node_ip = osan.get_node_by_vip(vip=vip[0])
    #虚IP所在节点物理ID
#vip_node_id = node.get_node_id_by_ip(vip_node_ip)
#a_eths,a_extra = error.get_dataip_info(node_id=vip_node_id)
los_nodes_id = osan.get_los_id(s_ip=deploy_ips[0])
los_node_id = random.choice(los_nodes_id)
los_node_ip = node.get_node_ip_by_id(los_node_id)
jnl_gp_id = osan.get_same_jnl_group(los_node_id)
for gp_id in jnl_gp_id:
    if str(gp_id) == str(los_node_id):
        continue
    else:
        b_ip = error.jnl_gp_ip(gp_id)
        b_eths, b_extra = error.get_dataip_info(node_id=gp_id)
        break
if None == b_eths:
    b_ip = error.get_fault_ip()
    while b_ip == los_node_ip:
        b_ip = error.get_fault_ip()
    b_id = node.get_node_id_by_ip(b_ip)
    b_eths,b_extra = error.get_dataip_info(node_id=b_id)
def up_down():
    time.sleep(30)
    for i in range(0,10):
        log.info("Begin down node:%s." %(los_node_ip))
        ReliableTest.run_down_net(a_extra[0],b_eths)
        time.sleep(30)
        time.sleep(5)
        log.info("Begin up node:%s." %(los_node_ip))
        ReliableTest.run_up_net(a_extra[0],b_eths)
        time.sleep(5)
def vdb_jn():
    log.info("Run vdbench with jn.")
    osan.run_vdb(client_ips[0], mix_O, output=deploy_ips[0],jn_jro="jn")
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_O, output=deploy_ips[0], jn_jro="jro")
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_O, output=deploy_ips[0], jn_jro="jro")
    log.info("Check bad obj repairing.")
    common.check_badjobnr()   #等待所有坏对象修复完成
    log.info("Run vdbench with jro after the file repaired.")
    osan.run_vdb(client_ips[0], mix_O, output=deploy_ips[0], jn_jro="jro")
def vdb_run():
    log.info("Run vdbench.")
    osan.run_vdb(client_ips[1], mix_S, output=deploy_ips[0],time=2400)
def win_vdb_run():
    log.info("Step3:在windows主机上运行vdbench -f mix-R-win.conf.")
    osan.run_win_vdb(file_name, mix_R_win, jn_jro="jn", time=900)

def main():
    test_threads = []
    test_threads.append(threading.Thread(target=up_down))
    test_threads.append(threading.Thread(target=vdb_jn))
    test_threads.append(threading.Thread(target=vdb_run))
    test_threads.append(threading.Thread(target=win_vdb_run))
    for test_thread in test_threads:
        test_thread.start()
    for test_thread in test_threads:
        test_thread.join()
    for c_ip in client_ips:
        osan.vdb_check(c_ip=c_ip, time=100, oper="iops", output=deploy_ips[0])
    for ip in vip:
        for cli in client_ips:
            pass
            #osan.iscsi_logout(cli,vip=ip)
if __name__ == '__main__':
    main()
