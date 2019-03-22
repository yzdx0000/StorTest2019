#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Date:20181022
Author:wangxiang
测试内容:大小块混合顺序读写中，业务节点业务网故障时，另一日志节点一块日志盘故障
1、部署3节点集群环境，配置访问分区为3个节点；
2、对齐大小块混合顺序读写业务为脚本mix-R-Align.conf，非对齐大小块混合顺序读写业务脚本为mix-R.conf

步骤:
1、在节点A上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
3、在主机1上运行vdbench -f mix-R-Align.conf -jn；在主机2上运行vdbench -f mix-R.conf;
4、在步骤3中的业务运行过程中，将A节点业务网故障，将节点B一块数据盘拔掉；
5、主机1上业务完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性；
6、数据修复完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性；
7、数据修复完成后，比较存储内部数据一致性

检查项:
1、步骤4，业务节点故障时，业务挂起，30秒内恢复，系统上报异常信息，节点A所有VIP正常迁移；
2、步骤5、数据比较一致
4、步骤6、数据比较一致
5、步骤7、内部数据比较一致
"""
# testlink case: 1000-33169
import os
import sys
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
import breakdown
import Lun_managerTest

conf_file = common2.CONF_FILE
clean_env = common2.CLEAN_ENV
file_name = os.path.basename(__file__)
file_name = file_name[:-3]
log_file_path = log.get_log_path(file_name)
log.init(log_file_path, True)
error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=1, node_num=4)

deploy_ips = get_config.get_env_ip_info(conf_file)

client_ips = get_config.get_allclient_ip()
type_info = get_config.get_machine_type(conf_file)
if type_info == "vir":
    (esxi_ip, esxi_un, esxi_pw) = get_config.get_esxi(conf_file)
osan = common2.oSan()
node = common.Node()
disk = breakdown.disk()
com_disk = common.Disk()
Reliable_osan = breakdown.Os_Reliable()
Lun_osan = Lun_managerTest.oSan()

vip = login.login()
svip = osan.get_svip(s_ip=deploy_ips[0])
# 修改vdbench配置文件的参数值
seekpct1 = 0
seekpct2 = 0
rdpct1 = 0
rdpct2 = 0
offset = "2048"
xfersize1 = "(3k,100)"
xfersize2 = "(2k,100)"
lun1 = osan.ls_scsi_dev(client_ips[0])
lun2 = osan.ls_scsi_dev(client_ips[1])
mix_R_align = osan.gen_vdb_xml(lun=lun1, xfersize=xfersize1, seekpct=seekpct1, rdpct=rdpct1)
mix_R = osan.gen_vdb_xml(lun=lun2, xfersize=xfersize2, offset=offset, seekpct=seekpct2, rdpct=rdpct2)
# 获取节点A虚IP所在节点物理IP
v_ip = random.choice(vip)
log.info("Got vip is %s." % (v_ip,))
a_ip = osan.get_node_by_vip(v_ip)
a_id = node.get_node_id_by_ip(a_ip)
a_eths, a_extra = error.get_dataip_info(node_id=a_id)
# 获取另一日志节点
use_jnl_ids = osan.get_same_jnl_group(1)
if a_id in use_jnl_ids:
    use_jnl_ids.remove(a_id)
b_id = random.choice(use_jnl_ids)
b_ip = node.get_node_ip_by_id(b_id)
node_id = node.get_node_id_by_ip(b_ip)
fault_vip = random.choice(vip)
fault_io_ip = osan.get_node_by_vip(fault_vip)
fault_io_id = node.get_node_id_by_ip(fault_io_ip)

data_eth_list = error.get_data_eth(fault_io_id)
io_eth_list = error.get_io_eth(fault_io_id)
data_eth_name = random.choice(data_eth_list)
io_eth_name = random.choice(io_eth_list)
log.info(
    "Got machine A's IP: %s, dev name is %s, extra IP is %s, and machine B's IP: %s." % (a_ip, a_eths, a_extra, b_ip))

"""获取指定节点数据盘和共享盘"""
share_disk, data_disk = Reliable_osan.get_share_monopoly_disk_ids(s_ip=b_ip, node_id=node_id)
disk_ids = []
for data_disk in data_disk:
    disk_phy_id = Reliable_osan.get_physicalid_by_name(b_ip, data_disk)
    disk_ids.append(disk_phy_id)
disk_phy_id = random.choice(disk_ids)  # 磁盘物理id
disk_name = Reliable_osan.get_name_by_physicalid(b_ip, disk_phy_id)  # 磁盘名字
disk_uuid = com_disk.get_disk_uuid_by_name(node_id=node_id, disk_name=disk_name)  # 磁盘uuid
disk_id = Reliable_osan.get_diskid_by_name(s_ip=b_ip, node_id=node_id,
                                           disk_name=disk_name)  # 集群中的磁盘id
stor_id_block = Lun_osan.get_storage__type_id(s_ip=b_ip)


def up_down(pipein):
    time.sleep(10)
    log.info("4、在步骤3中的业务运行过程中，将A节点数据网故障，将节点B一块数据盘拔掉再恢复")
    log.info("Begin down data net %s through %s ." % (a_eths, a_extra[0]))
    ReliableTest.run_down_net(a_extra[0], a_eths)
    log.info("On node %s remove disk." % b_ip)
    Reliable_osan.remove_disk(node_ip=b_ip, disk_id=disk_phy_id, disk_usage="DATA")
    time.sleep(30)

    Reliable_osan.insert_disk(b_ip, disk_id=disk_phy_id, disk_usage="DATA")
    # 监控到匿名管道中写入数据后，退出循环
    while True:
        line = os.read(pipein, 32)
        if 'up' in line:
            break
    log.info("Begin up data net %s through %s ." % (a_eths, a_extra[0]))
    ReliableTest.run_up_net(a_extra[0], a_eths)


def vdb_jn(pipeout):
    log.info("3、在主机1上运行vdbench -f mix-S-Align.conf -jn；在主机2上运行vdbench -f mix-S.conf;")
    log.info("Run vdbench with jn on %s." % (client_ips[0]))
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jn")
    log.info("5、业务执行完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性；")
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")
    os.write(pipeout, "upnet")
    disk.check_bad_obj()
    log.info("6、数据修复完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性；")
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")


    disk.multi_check_part_lun_uniform_by_ip()


def vdb_run():
    log.info("Run vdbench on %s." % (client_ips[1]))
    osan.run_vdb(client_ips[1], mix_R, output=deploy_ips[0])


def main():
    (pipein, pipeout) = os.pipe()
    test_threads = []
    test_threads.append(threading.Thread(target=up_down, args=(pipein,)))
    test_threads.append(threading.Thread(target=vdb_jn, args=(pipeout,)))
    test_threads.append(threading.Thread(target=vdb_run))
    for test_thread in test_threads:
        test_thread.setDaemon(True)
        test_thread.start()
    for test_thread in test_threads:
        test_thread.join()
    for c_ip in client_ips:
        osan.vdb_check(c_ip=c_ip, time=100, oper="iops", output=deploy_ips[0])

    osan.run_vdb(client_ip=client_ips[0], vdb_xml=mix_R_align, output=deploy_ips[0])


if __name__ == '__main__':
    main()