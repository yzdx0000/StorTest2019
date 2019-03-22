#!/usr/bin/python
#-*-coding:utf-8 -*

import os,sys
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
import breakdown
import re

conf_file = common2.CONF_FILE    #配置文件路径
clean_env = common2.CLEAN_ENV
file_name = os.path.basename(__file__)
file_name = file_name[:-3]      #获取本脚本名，去掉.py后缀
error.rel_check_before_run(file_name, jnl_rep=3, node_num=3)

deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
osan = common2.oSan()
osan.init_win_log(file_name)                    #初始化windows日志文件
node = common.Node()
disk = breakdown.disk()
vip = login.login()
#修改vdbench配置文件的参数值
seekpct1 = 40
seekpct2 = 70
rdpct1 = 25
rdpct2 = 45
offset = "2048"
xfersize1 = "(4k,80,16k,20)"
xfersize2 = "(4k,80,16k,20)"
lun1 = osan.ls_scsi_dev(client_ips[0])
lun2 = osan.ls_scsi_dev(client_ips[1])
mix_R_align = osan.gen_vdb_xml(lun=lun1, xfersize=xfersize1, seekpct=seekpct1,rdpct=rdpct1)
mix_R = osan.gen_vdb_xml(lun=lun2, xfersize=xfersize2, offset=offset, seekpct=seekpct2,rdpct=rdpct2)
mix_R_win = osan.gen_win_vdb_conf(xfersize="(4k,80,16k,20)",
                                  seekpct=0,
                                  rdpct=0)
fault_ip = None
vip_node_ip = osan.get_node_by_vip(vip=vip[0])
vip_node_id = node.get_node_id_by_ip(vip_node_ip)
jnl_gp_id = error.jnl_gp_id(vip=vip[0])
for gp_id in jnl_gp_id:
    if str(gp_id) == str(vip_node_id):
        continue
    else:
        fault_ip = error.jnl_gp_ip(gp_id)
        break
if fault_ip is None:
    log.error("Can not find the fault ip.")
    exit(1)


def up_down(pipeout):
    time.sleep(200)
    log.info("Begin down node:%s." %(fault_ip))
    node_info = error.down_node(fault_ip=fault_ip)
    os.write(pipeout,node_info)


def vdb_jn(pipein):
    log.info("Run vdbench with jn.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0],jn_jro="jn")
    while True:
        line = os.read(pipein,32)
        if len(line) != 0:
            for vid in line.strip().split(','):
                vid = re.sub('\\r','',vid)
                log.info("upnode : %s." %(vid.strip()))
                error.up_node(node_info=vid.strip())
            break
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")
    for ip in deploy_ips:
        common.check_ip(ip)
        error.check_host(ip)
    log.info("Check bad obj repairing.")
    common.check_badjobnr()   #等待所有坏对象修复完成
    disk.check_bad_obj()
    log.info("Run vdbench with jro after the file repaired.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")


def vdb_run():
    log.info("Run vdbench.")
    osan.run_vdb(client_ips[1], mix_R, output=deploy_ips[0])

def win_vdb_run():
    log.info("Step3:在windows主机上运行vdbench -f mix-R-win.conf.")
    osan.run_win_vdb(file_name, mix_R_win, jn_jro="jn", time=900)

def main():
    (pipein,pipeout) = os.pipe()
    test_threads = []
    test_threads.append(threading.Thread(target=up_down, args=(pipeout,)))
    test_threads.append(threading.Thread(target=vdb_jn, args=(pipein,)))
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
