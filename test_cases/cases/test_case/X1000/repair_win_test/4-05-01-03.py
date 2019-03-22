#!/usr/bin/python
#-*-coding:utf-8 -*
"""
:Date: 2018-08-28
:Author: wuyq
:Description:
1、在节点A上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
3、在主机1上运行vdbench -f mix-R-Align.conf -jn；在主机2上运行vdbench -f mix-R.conf;
4、业务过程中，将一个节点数据盘拔出；
5、拔出后，将oSan所在节点掉电；
6、主机端执行vdbench -f mix-R-Align.conf -jro;校验数据一致性
7、将故障的数据盘插回，节点恢复正常，数据修复完成系统恢复正常后，比较内部数据一致性。
:Changerlog:
"""
import os
import sys
import commands
import threading
import random
import time
import utils_path
import common2
import common
import log
import get_config
import ReliableTest
import login
import error
import breakdown
import env_manage_repair_test

conf_file = common2.CONF_FILE    #配置文件路径
osan = common2.oSan()
reliable = breakdown.Os_Reliable()
disk = breakdown.disk()
node = common.Node()

file_name = os.path.basename(__file__)
file_name = file_name[:-3]                      #获取本脚本名，去掉.py后缀
error.rel_check_before_run(file_name, jnl_rep=3, node_num=3)
osan.init_win_log(file_name)                    #初始化windows日志文件
#获取集群节点信息
deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
vip = login.login()
#修改vdbench配置文件的参数值
mix_R_win = osan.gen_win_vdb_conf(xfersize="(4k,80,16k,20)",
                                  seekpct=0,
                                  rdpct=0)
mix_R_Align = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[0]),
                               xfersize="(4k,80,16k,20)",
                               seekpct=0,
                               rdpct=0)
mix_R = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[1]),
                         xfersize="(4k,80,16k,20)",
                         offset=2048,
                         seekpct=0,
                         rdpct=0)

# 随机选择一个节点的数据盘
fault_node_ip = random.choice(deploy_ips)
fault_node_id = node.get_node_id_by_ip(fault_node_ip)

share_disk, data_disk = env_manage_repair_test.Reliable_osan.get_share_monopoly_disk_ids(fault_node_ip, fault_node_id)
disk_ids = []
for data_disk in data_disk:
    disk_phy_id = env_manage_repair_test.Reliable_osan.get_physicalid_by_name(fault_node_ip, data_disk)
    disk_ids.append(disk_phy_id)
disk_phy_id = random.choice(disk_ids)  # 磁盘物理id
disk_name = env_manage_repair_test.Reliable_osan.get_name_by_physicalid(fault_node_ip, disk_phy_id)  # 磁盘名字
disk_uuid = env_manage_repair_test.com_disk.get_disk_uuid_by_name(fault_node_id, disk_name)          # 磁盘uuid
disk_id = env_manage_repair_test.Reliable_osan.get_diskid_by_name(fault_node_ip, fault_node_id, disk_name) # 集群中的磁盘id
stor_id_block = env_manage_repair_test.Lun_osan.get_storage__type_id(fault_node_ip)

def up_down():
    time.sleep(100)
    log.info("Step4:业务过程中将存储中的一块数据磁盘拔出,节点:%s,磁盘:%s" % (fault_node_ip, disk_name))
    env_manage_repair_test.Reliable_osan.remove_disk(fault_node_ip, disk_phy_id, "DATA")
    time.sleep(100)
    log.info("Step5:数据修复过程中,将oSan所在节点掉电,节点:%s" % (fault_node_ip))
    vm_id = error.down_node(fault_node_ip)
    while True:
        time.sleep(30)
        log.info("等待oSan节点重新启动,节点:%s" % fault_node_ip)
        error.up_node(vm_id)
        rc = reliable.get_os_status(fault_node_ip)  # 检测重启后机器状态，是否已开机
        if 0 == rc:
            log.info("故障oSan节点启动成功,节点:%s" % fault_node_ip)
            break

    time.sleep(100)
    log.info("Step6:将拔出的盘在超时内恢复,节点:%s,磁盘:%s" % (fault_node_ip, disk_name))
    env_manage_repair_test.Reliable_osan.insert_disk(fault_node_ip, disk_phy_id, "DATA")

    time.sleep(30)
    log.info("Step7:数据修复完成系统恢复正常后，比较内部数据一致性")
    reliable.compare_data()

def vdb_jn():
    log.info("Step3:在主机1上运行vdbench -f mix-R-Align.conf -jn.")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0],jn_jro="jn",time=900)
    log.info("Step6:主机1上业务完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性.")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jro")

def vdb_run():
    log.info("Step3:在主机2上运行vdbench -f mix-R.conf.")
    osan.run_vdb(client_ips[1], mix_R, output=deploy_ips[0],time=1000)

def win_vdb_run():
    log.info("Step3:在windows主机上运行vdbench -f mix-R-win.conf.")
    osan.run_win_vdb(file_name, mix_R_win, jn_jro="jn", time=900)

def case():
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
def main():
    case()
if __name__ == '__main__':
    main()