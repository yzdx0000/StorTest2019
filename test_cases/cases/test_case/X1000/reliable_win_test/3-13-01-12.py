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
import random
import error

conf_file = common2.CONF_FILE    #配置文件路径
clean_env = common2.CLEAN_ENV
file_name = os.path.basename(__file__)
file_name = file_name[:-3]      #获取本脚本名，去掉.py后缀
error.rel_check_before_run(file_name)



deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
type_info = get_config.get_machine_type(conf_file)
if type_info == "vir":
    (esxi_ip, esxi_un, esxi_pw) = get_config.get_esxi(conf_file)
osan = common2.oSan()
osan.init_win_log(file_name)                    #初始化windows日志文件/g
node = common.Node()
vip = login.login()
svip = osan.get_svip(s_ip=deploy_ips[0])
#修改vdbench配置文件的参数值
mix_R_win = osan.gen_win_vdb_conf(xfersize="(4k,80,16k,20)",
                                  seekpct=0,
                                  rdpct=0)
seekpct1 = 0
seekpct2 = 0
rdpct1 = 30
rdpct2 = 45
offset = "2048"
xfersize1 = "(4k,80,16k,20)"
xfersize2 = "(4k,80,16k,20)"
lun1 = osan.ls_scsi_dev(client_ips[0])
lun2 = osan.ls_scsi_dev(client_ips[1])
mix_S_align = osan.gen_vdb_xml(lun=lun1, xfersize=xfersize1, seekpct=seekpct1, rdpct=rdpct1)
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
a_eths,a_extra = error.get_dataip_info(node_id=los_node_id)
def up_down():
#    fault_ip = error.get_fault_ip()
#     cmd = 'pscli --command=update_param --section=MGR --name=node_isolate_timeout --current=400000'
#     osan.run_cmd(cmd,fault_node_ip=vip_node_ip)
#     log.info(cmd)
    time.sleep(30)
    log.info("Begin down node:%s." %(los_node_ip))
    ReliableTest.run_down_net(a_extra[0],a_eths)
    time.sleep(30)
def vdb_jn():
    log.info("Run vdbench with jn.")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0],jn_jro="jn")
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0], jn_jro="jro")
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0], jn_jro="jro")
    log.info("Begin up node:%s." %(los_node_ip))
    ReliableTest.run_up_net(a_extra[0],a_eths)
    # cmd = 'pscli --command=update_param --section=MGR --name=node_isolate_timeout --current=864000000'
    # osan.run_cmd(cmd,fault_node_ip=los_node_ip)
    # log.info(cmd)
def vdb_run():
    log.info("Run vdbench.")
    osan.run_vdb(client_ips[1], mix_S, output=deploy_ips[0],time=1800)
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
