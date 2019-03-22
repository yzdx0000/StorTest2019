#!/usr/bin/python
#-*-coding:utf-8 -*

import os,sys
import utils_path
import common2
import log
import get_config
import ReliableTest
import threading
import login
import time
import commands

conf_file = common2.CONF_FILE    #配置文件路径
clean_env = common2.CLEAN_ENV
file_name = os.path.basename(__file__)
file_name = file_name[:-3]      #获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)     #获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)       #初始化日志文件

deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()

osan = common2.oSan()
vip = login.login()
#修改vdbench配置文件的参数值
seekpct = 0
offset = "2048"
xfersize1 = "(4k,20,8k,20,128k,15,256k,15,1m,15,4m,15)"
xfersize2 = "(3k,20,9k,20,121k,15,250k,15,1025k,15,4097k,15)"
lun1 = osan.ls_scsi_dev(client_ips[0])
lun2 = osan.ls_scsi_dev(client_ips[1])
mix_S_Align = osan.gen_vdb_xml(lun=lun1, xfersize=xfersize1, seekpct=seekpct)
mix_S = osan.gen_vdb_xml(lun=lun2, xfersize=xfersize2, offset=offset, seekpct=seekpct)
def up_down():
    log.info("Shutdown node:%s" % (deploy_ips[0]))
    time.sleep(10)
    log.info("Startup node:%s" % (deploy_ips[0]))
    #vm_id = ReliableTest.run_down_vir_node(esxi_ip="10.22.129.2",u_name="root",pw="parastor123;",node_ip="10.22.129.3")
    #print vm_id 
    #ReliableTest.run_up_vir_node(esxi_ip="10.22.129.2",u_name="root",pw="parastor123;",vm_id=19)
def vdb_jn():
    log.info("Run vdbench with jn.")
    log.info("Run vdbench with jro.")
    vdb_xml = osan.auto_gen_vdb_jn_xml(lun=lun1, thread=5,output=deploy_ips[0])
    cmd = ("cat %s" % (vdb_xml))
    res, output = commands.getstatusoutput(cmd)
    osan.run_vdb(client_ips[0], vdb_xml, jn_jro="yes",output=deploy_ips[0])
#    osan.run_vdb(client_ips[0], mix_S_Align, output=deploy_ips[0],jn_jro="jn")
#    osan.run_vdb(client_ips[0], mix_S_Align, output=deploy_ips[0], jn_jro="jro")
def vdb_run():
    log.info("Run vdbench.")
    vdb_xml = osan.auto_gen_vdb_xml(lun=lun2, thread=5)
    cmd = ("cat %s" % (vdb_xml))
    res, output = commands.getstatusoutput(cmd)
    osan.run_vdb(client_ips[1], vdb_xml,output=deploy_ips[0])
#    osan.run_vdb(client_ips[1], mix_S, output=deploy_ips[0])
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
    osan.vdb_check(c_ip=c_ip, time=60, oper="iops", output=deploy_ips[0])
for ip in vip:
    for cli in client_ips:
        osan.iscsi_logout(cli,vip=ip)
