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
import breakdown
import time
import commands
import random
import error
'''
Date : 2018-08-02
Author  : diws
Description :
            1、创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
            2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
            3、在主机1上运行vdbench -f mix-R-align.conf -jn；在主机2上运行vdbench -f mix-R.conf;
            4、在步骤3中的业务运行过程中，将一节点有读写一块日志盘故障；
            5、5分钟后，该节点另一块日志盘故障；
            6、主机1上业务完成后，在主机1上执行vdbench -f mix-R-align.conf -jro比较一致性；
            7、数据修复完成后，比较存储内部数据一致性。
'''

conf_file = common2.CONF_FILE    #配置文件路径
clean_env = common2.CLEAN_ENV
file_name = os.path.basename(__file__)
file_name = file_name[:-3]      #获取本脚本名，去掉.py后缀
error.rel_check_before_run(file_name)


deploy_ips = get_config.get_env_ip_info(conf_file)    #集群节点IP
client_ips = get_config.get_allclient_ip()    # 主机端节点IP
#机器类型，暂未使用
type_info = get_config.get_machine_type(conf_file)
if type_info == "vir":
    (esxi_ip, esxi_un, esxi_pw) = get_config.get_esxi(conf_file)

osan = common2.oSan()
node = common.Node()
disk = breakdown.disk()

vip = login.login()     #虚IP
svip = osan.get_svip(s_ip=deploy_ips[0])   #svip
#修改vdbench配置文件的参数值
seekpct1 = 45
seekpct2 = 99
rdpct1 = 30
rdpct2 = 45
offset = "2048"
xfersize1 = "(3k,100)"
xfersize2 = "(2k,100)"
lun1 = osan.ls_scsi_dev(client_ips[0])
lun2 = osan.ls_scsi_dev(client_ips[1])
mix_R_align = osan.gen_vdb_xml(lun=lun1, xfersize=xfersize1, seekpct=seekpct1, rdpct=rdpct1)
mix_R = osan.gen_vdb_xml(lun=lun2, xfersize=xfersize2, offset=offset, seekpct=seekpct2,rdpct=rdpct2)
# 随机选择节点
fault_ip = error.get_fault_ip()
# Get shared disks' replica
#disk_rep = disk.get_jnl_replica(s_ip=fault_ip)
nodeids = osan.get_nodes(fault_ip)
#根据节点ID获取日志盘盘符和所在节点IP
disk_ids = []
disk_uuids = []
fault_disk = {}
jnl_num = 1
for node_id in nodeids:
    disk_names = disk.get_rw_disk_by_node_id(s_ip=fault_ip,node_id=node_id,disk_type="share")
    if None == disk_names[0]:
        continue
    else:
        jnl_num += 1
        node_ip = node.get_node_ip_by_id(node_id)
        disk_phyids = disk.get_disk_phyid_by_name(s_ip=node_ip,disk_name=disk_names)
        fault_disk[node_ip] = disk_phyids
        for diskname in disk_names:
            disk_ids.append(disk.get_diskid_by_name(s_ip=node_ip,node_id=node_id,disk_name=diskname))
            disk_uuids.append(disk.get_disk_uuid_by_name(s_ip=node_ip,node_id=node_id,disk_name=diskname))
        if jnl_num == 2:
            break
#插拔盘操作
def up_down(pipeout):
    time.sleep(200)
    for ip in fault_disk.keys():
        log.info("Begin remove disk:%s %s." %(ip,fault_disk[ip]))
        # 每隔5分钟拔一块日志盘
        for rm_disk in fault_disk[ip]:
            ReliableTest.remove_disk(ip,rm_disk,"share")
            time.sleep(300)
    for ip in fault_disk.keys():
        log.info("Begin add disk:%s %s." % (ip, fault_disk[ip]))
        #插回磁盘
        for rm_disk in fault_disk[ip]:
            ReliableTest.insert_disk(ip,rm_disk,"share")
    os.write(pipeout, "adddisk")

def vdb_jn(pipein):
    log.info("Run vdbench with jn.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0],jn_jro="jn")
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")
    while True:
        line = os.read(pipein, 32)
        if 'add' in line:
            break
    log.info("Run vdbench with jro after add disk.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")
    disk.multi_check_part_lun_uniform_by_ip()


def vdb_run():
    log.info("Run vdbench.")
    osan.run_vdb(client_ips[1], mix_R, output=deploy_ips[0],time=1200)
def main():
    test_threads = []
    (pipein, pipeout) = os.pipe()
    test_threads.append(threading.Thread(target=up_down, args=(pipeout,)))
    test_threads.append(threading.Thread(target=vdb_jn, args=(pipein,)))
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
    main()
