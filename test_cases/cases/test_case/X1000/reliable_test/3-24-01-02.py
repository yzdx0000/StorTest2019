#!/usr/bin/python
#-*-coding:utf-8 -*

# testlink case: 1000-33062
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
node = common.Node()
disk = breakdown.disk()

vip = login.login()
svip = osan.get_svip(s_ip=deploy_ips[0])
#修改vdbench配置文件的参数值
seekpct1 = 0
seekpct2 = 0
rdpct1 = 30
rdpct2 = 45
offset = "2048"
xfersize1 = "(3k,100)"
xfersize2 = "(2k,100)"
lun1 = osan.ls_scsi_dev(client_ips[0])
lun2 = osan.ls_scsi_dev(client_ips[1])
mix_S_align = osan.gen_vdb_xml(lun=lun1, xfersize=xfersize1, seekpct=seekpct1, rdpct=rdpct1)
mix_S = osan.gen_vdb_xml(lun=lun2, xfersize=xfersize2, offset=offset, seekpct=seekpct2,rdpct=rdpct2)

# Get the node's ip to remove disk
fault_ip = error.get_fault_ip()
# Get the node's id by ip
node_id = node.get_node_id_by_ip(fault_ip)
# Get the node's disk names, disk type :data
disk_names = disk.get_rw_disk_by_node_id(s_ip=fault_ip,node_id=node_id,disk_type="share")
disk_name = []
disk_name.append(random.choice(disk_names))
# Get the disks' phyid
disk_phyids = disk.get_disk_phyid_by_name(s_ip=fault_ip,disk_name=disk_name)
fault_disk = disk_phyids[0]
disk_id = disk.get_diskid_by_name(s_ip=fault_ip,node_id=node_id,disk_name=disk_name[0])
disk_uuid = disk.get_disk_uuid_by_name(s_ip=fault_ip,node_id=node_id,disk_name=disk_name[0])

def up_down(pipeout):
    time.sleep(10)
    cmd = "ssh %s 'pscli --command=update_param --section=MGR --name=disk_isolate2rebuild_timeout --current=300000'" %(fault_ip)
    rc, stdout = commands.getstatusoutput(cmd)
    if 0 != rc:
        log.error('update param failed!!!')
        exit(1)
    log.info("Begin remove disk:%s %s." %(fault_ip,fault_disk))
    ReliableTest.remove_disk(fault_ip,fault_disk,"share")
    time.sleep(390)
    cmd = "ssh %s 'pscli --command=update_param --section=MGR --name=disk_isolate2rebuild_timeout --current=3000000'" %(fault_ip)
    rc, stdout = commands.getstatusoutput(cmd)
    if 0 != rc:
        log.error('update param failed!!!')
        exit(1)

    log.info("Begin add disk:%s %s." % (fault_ip, fault_disk))
    ReliableTest.insert_disk(fault_ip,fault_disk,"share")
    while 'ZOMBIE' not in disk.check_disk_state(node_ip=fault_ip, disk_uuid=disk_uuid):
        time.sleep(10)
    disk.delete_disk(s_ip=fault_ip,disk_id=disk_id)
    disk.add_disk(s_ip=fault_ip,uuid=disk_uuid,usage="SHARED",node_id=node_id)
    os.write(pipeout, "adddisk")

def vdb_jn(pipein):
    log.info("Run vdbench with jn.")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0],jn_jro="jn")
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0], jn_jro="jro")
    while True:
        line = os.read(pipein, 32)
        if 'add' in line:
            break
    log.info("Run vdbench with jro after add disk.")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0], jn_jro="jro")
    disk.multi_check_part_lun_uniform_by_ip()


def vdb_run():
    log.info("Run vdbench.")
    osan.run_vdb(client_ips[1], mix_S, output=deploy_ips[0],time=1200)
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


if __name__ == '__main__':
    main()