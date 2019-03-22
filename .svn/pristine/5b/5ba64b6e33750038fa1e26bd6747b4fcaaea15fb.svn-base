#!/usr/bin/python
#-*-coding:utf-8 -*

# testlink case: 1000-33052
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
import random
import breakdown

conf_file = common2.CONF_FILE    #配置文件路径
clean_env = common2.CLEAN_ENV
file_name = os.path.basename(__file__)
file_name = file_name[:-3]      #获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)     #获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)       #初始化日志文件

deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
osan = common2.oSan()
node = common.Node()
disk = breakdown.disk()

vip = login.login()
#修改vdbench配置文件的参数值
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
mix_R = osan.gen_vdb_xml(lun=lun2, xfersize=xfersize2, offset=offset, seekpct=seekpct2,rdpct=rdpct2)

# Get the node's ip to remove disk
fault_ip = error.get_fault_ip()
# Get the node's id by ip
node_id = node.get_node_id_by_ip(fault_ip)
# Get the node's disk names, disk type :data
disk_names = disk.get_rw_disk_by_node_id(s_ip=fault_ip,node_id=node_id,disk_type="data")
# Get the disks' phyid
disk_phyids = disk.get_disk_phyid_by_name(s_ip=fault_ip,disk_name=disk_names)

def up_down():
    time.sleep(20)
    for i in disk_phyids:
        log.info("Begin remove disk:%s %s." %(fault_ip,i))
        ReliableTest.remove_disk(fault_ip,i,"data")
        time.sleep(20)
    for i in disk_phyids:
        log.info("Begin add disk:%s %s." % (fault_ip, i))
        ReliableTest.insert_disk(fault_ip,i,"data")
        time.sleep(20)
def vdb_jn():
    log.info("Run vdbench with jn.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0],jn_jro="jn")
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")
    log.info("Check bad obj repairing.")
    common.check_badjobnr()   #等待所有坏对象修复完成
    disk.check_bad_obj()
    log.info("Run vdbench with jro after the file repaired.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")
    disk.multi_check_part_lun_uniform_by_ip()


def vdb_run():
    log.info("Run vdbench.")
    osan.run_vdb(client_ips[1], mix_R, output=deploy_ips[0],time=1200)
def main():
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
    for ip in vip:
        for cli in client_ips:
            pass
            #osan.iscsi_logout(cli,vip=ip)
if __name__ == '__main__':
    error.rel_check_before_run(file_name, jnl_rep=3, node_num=4, free_jnl_num=1, data_rep=3)
    main()
