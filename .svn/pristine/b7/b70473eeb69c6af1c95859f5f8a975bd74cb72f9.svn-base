#!/usr/bin/python
#-*-coding:utf-8 -*
"""
:Date: 2018-08-28
:Author: wuyq
:Description:
1、在节点A上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
3、在主机1上运行vdbench -f mix-R-Align.conf -jn；在主机2上运行vdbench -f mix-R.conf;
4、业务过程中，将两个节点各拔出一块元数据盘；
5、拔出报单状态对象的两块数据盘，将ZK主进程故障；
6、主机端执行vdbench -f mix-R-Align.conf -jro;校验数据一致性
7、将拔出的磁盘插回，数据修复完成系统恢复正常后，比较内部数据一致性。
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
#获取集群节点信息
deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
vip = login.login()
#修改vdbench配置文件的参数值
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
deploy_ls = deploy_ips[:]
fault_node_ip = reliable.get_master_zk(deploy_ls)
fault_node_id = node.get_node_id_by_ip(fault_node_ip)
deploy_ls.remove(fault_node_ip)
fault_node_ip1 = random.choice(deploy_ls)
fault_node_id1 = node.get_node_id_by_ip(fault_node_ip1)

share_disk1, data_disk1 = env_manage_repair_test.Reliable_osan.get_share_monopoly_disk_ids(fault_node_ip, fault_node_id)
share_disk2, data_disk2 = env_manage_repair_test.Reliable_osan.get_share_monopoly_disk_ids(fault_node_ip1, fault_node_id1)
disk_ids_DATA1 = []
disk_ids_DATA2 = []
disk_ids_SHARE1 = []
disk_ids_SHARE2 = []
for share_disk1 in share_disk1:
    disk_phy_id = env_manage_repair_test.Reliable_osan.get_physicalid_by_name(fault_node_ip, share_disk1)
    disk_ids_SHARE1.append(disk_phy_id)
for share_disk2 in share_disk2:
    disk_phy_id = env_manage_repair_test.Reliable_osan.get_physicalid_by_name(fault_node_ip1, share_disk2)
    disk_ids_SHARE2.append(disk_phy_id)
for data_disk1 in data_disk1:
    disk_phy_id = env_manage_repair_test.Reliable_osan.get_physicalid_by_name(fault_node_ip, data_disk1)
    disk_ids_DATA1.append(disk_phy_id)
for data_disk2 in data_disk2:
    disk_phy_id = env_manage_repair_test.Reliable_osan.get_physicalid_by_name(fault_node_ip1, data_disk2)
    disk_ids_DATA2.append(disk_phy_id)
disk_phy_id_share1 = random.choice(disk_ids_SHARE1)
disk_phy_id_share2 = random.choice(disk_ids_SHARE2)
disk_phy_id_data1 = random.choice(disk_ids_DATA1)
disk_phy_id_data2 = random.choice(disk_ids_DATA2)

disk_name1 = env_manage_repair_test.Reliable_osan.get_name_by_physicalid(fault_node_ip, disk_phy_id_share1)  # 磁盘名字
disk_name2 = env_manage_repair_test.Reliable_osan.get_name_by_physicalid(fault_node_ip1, disk_phy_id_share2)  # 磁盘名字
disk_name3 = env_manage_repair_test.Reliable_osan.get_name_by_physicalid(fault_node_ip, disk_phy_id_data1)  # 磁盘名字
disk_name4 = env_manage_repair_test.Reliable_osan.get_name_by_physicalid(fault_node_ip1, disk_phy_id_data2)  # 磁盘名字

disk_uuid1 = env_manage_repair_test.com_disk.get_disk_uuid_by_name(fault_node_id, disk_name1)  # 磁盘uuid
disk_uuid2 = env_manage_repair_test.com_disk.get_disk_uuid_by_name(fault_node_id1, disk_name2)  # 磁盘uuid
disk_uuid3 = env_manage_repair_test.com_disk.get_disk_uuid_by_name(fault_node_id, disk_name3)  # 磁盘uuid
disk_uuid4 = env_manage_repair_test.com_disk.get_disk_uuid_by_name(fault_node_id1, disk_name4)  # 磁盘uuid

disk_id1 = env_manage_repair_test.Reliable_osan.get_diskid_by_name(fault_node_ip, fault_node_id, disk_name1) #集群中的磁盘id
disk_id2 = env_manage_repair_test.Reliable_osan.get_diskid_by_name(fault_node_ip1, fault_node_id1, disk_name2) #集群中的磁盘id
disk_id3 = env_manage_repair_test.Reliable_osan.get_diskid_by_name(fault_node_ip, fault_node_id, disk_name3) #集群中的磁盘id
disk_id4 = env_manage_repair_test.Reliable_osan.get_diskid_by_name(fault_node_ip1, fault_node_id1, disk_name4) #集群中的磁盘id
stor_id_block = env_manage_repair_test.Lun_osan.get_storage__type_id(fault_node_ip)

def up_down():
    time.sleep(100)
    log.info("Step4:业务过程中将存储中的两块共享磁盘拔出,节点:%s,%s,磁盘:%s,%s" % (fault_node_ip,fault_node_ip1, disk_name1,disk_name2))
    env_manage_repair_test.Reliable_osan.remove_disk(fault_node_ip, disk_phy_id_share1, "SHARED")
    env_manage_repair_test.Reliable_osan.remove_disk(fault_node_ip1, disk_phy_id_share2, "SHARED")
    time.sleep(100)
    log.info("Step5:将两个阶段各拔出一块数据盘,节点:%s,%s,磁盘:%s,%s" % (fault_node_ip,fault_node_ip1, disk_name3,disk_name4))
    env_manage_repair_test.Reliable_osan.remove_disk(fault_node_ip, disk_phy_id_data1, "DATA")
    env_manage_repair_test.Reliable_osan.remove_disk(fault_node_ip1, disk_phy_id_data2, "DATA")
    log.info("Step5:数据修复过程中,将zk主进程故障,节点:%s" % (fault_node_ip))
    ReliableTest.run_kill_process(fault_node_ip, 'zk')
    time.sleep(100)
    while True:
        log.info("Step6:检查故障节点zk主进程状态,节点: %s." % (fault_node_ip))
        m_zk_ip = reliable.get_master_zk(deploy_ips)
        state = ReliableTest.check_process(m_zk_ip, 'zk')
        if state == 1:
            break
        time.sleep(20)

    log.info("Step7:将拔出的盘在超时内恢复,节点:%s" % (fault_node_ip))
    env_manage_repair_test.Reliable_osan.insert_disk(fault_node_ip, disk_phy_id_share1, "SHARED")
    env_manage_repair_test.Reliable_osan.insert_disk(fault_node_ip1, disk_phy_id_share2, "SHARED")
    env_manage_repair_test.Reliable_osan.insert_disk(fault_node_ip, disk_phy_id_data1, "DATA")
    env_manage_repair_test.Reliable_osan.insert_disk(fault_node_ip1, disk_phy_id_data2, "DATA")

    time.sleep(30)
    log.info("Step8:数据修复完成系统恢复正常后，比较内部数据一致性")
    reliable.compare_data()

def vdb_jn():
    log.info("Step3:在主机1上运行vdbench -f mix-R-Align.conf -jn.")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0],jn_jro="jn",time=1200)
    log.info("Step6:主机1上业务完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性.")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jro")

def vdb_run():
    log.info("Step3:在主机2上运行vdbench -f mix-R.conf.")
    osan.run_vdb(client_ips[1], mix_R, output=deploy_ips[0],time=1200)

def case():
    test_threads = []
    test_threads.append(threading.Thread(target=up_down))
    test_threads.append(threading.Thread(target=vdb_jn))
    test_threads.append(threading.Thread(target=vdb_run))
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