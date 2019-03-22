#!/usr/bin/python
#-*-coding:utf-8 -*
"""
:Date: 2019-02-26
:Author: wuyq
:Description:
1、创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
3、在主机1上运行vdbench -f mix-R-Align.conf -jn；在主机2上运行vdbench -f mix-R.conf;
4、一个节点的一块数据盘变为慢盘，延迟在1000ms以上（通过）；使用FIO工具（FIO
2.1.10） 对其进行1024k随机读操作， 使其IO响应时延超过1000ms。
FIO 命 令 参 考 如 下 ： fio -name=test -filename=/dev/sdb -
ioengine=libaio -direct=1 -bs=1024k -iodepth=128 -
rw=randread -runtime=604800 -time_based
5. 查看步骤2中存储节点上的iostat信息， 确认FIO操作的磁盘时延
(await)已经大于1000ms
6、观察vdbench性能和系统集群情况。"
:Changerlog:
"""
import os
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
import prepare_clean
import breakdown

conf_file = common2.CONF_FILE
osan = common2.oSan()
reliable = breakdown.Os_Reliable()
disk = breakdown.disk()
node = common.Node()

# 初始化日志文件
file_name = os.path.basename(__file__)
file_name = file_name[:-3]
prepare_clean.rel_check_before_run(file_name, jnl_rep=2, node_num=3, data_rep=2)

# 获取集群节点信息
deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
vip = login.login()

# 修改vdbench配置文件的参数值
mix_R_Align = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[0]),
                               xfersize="(4k,80,16k,20)",
                               seekpct=0,
                               rdpct=0)
mix_R = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[1]),
                         xfersize="(4k,80,16k,20)",
                         offset=2048,
                         seekpct=0,
                         rdpct=0)

event1 = threading.Event()
event2 = threading.Event()
fault_node_ip = random.choice(deploy_ips)
share_disks, data_disks = disk.get_disk_symbol(fault_node_ip)
fault_data_disk = random.choice(data_disks)

def up_down():
    time.sleep(100)
    log.info("Step4:业务过程中将节点 %s 的数据磁盘 %s 加压变成慢盘" % (fault_node_ip, fault_data_disk))
    cmd = ("ssh %s 'ls /home/fio*/fio'" % fault_node_ip)
    rc = os.system(cmd)
    if rc == 0:
        log.info("检查到该节点 %s 已安装fio工具" % fault_node_ip)
    else:
        log.info("检查到该节点 %s 未安装fio工具,请安装." % fault_node_ip)

    cmd = ("ssh %s '/home/fio*/fio -name=test -filename=%s -ioengine=libaio -direct=1 "
           "-bs=1024k -iodepth=128 -rw=randread -runtime=1000 -time_based' &" % (fault_node_ip, fault_data_disk))
    log.info(cmd)
    os.system(cmd)
    time.sleep(60)
    log.info("Step5:确认节点 %s 的数据磁盘 %s 时延已经增大" % (fault_node_ip, fault_data_disk))
    avg_await = disk.get_disk_await(fault_node_ip, fault_data_disk)
    log.info("节点 %s 的数据磁盘 %s 在近30s的延迟为 %s ms" % (fault_node_ip, fault_data_disk, avg_await))

    event1.wait()
    event2.wait()

    log.info("Step7:检查集群是否出现坏对象及修复任务")
    disk.check_bad_obj()


def vdb_jn():
    log.info("Step3:在主机1上运行vdbench -f mix-R-Align.conf -jn.")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jn", time=1200)
    log.info("Step5:主机1上业务完成后，在主机1上执行vdbench -f mix-R-Align.conf -jro比较一致性.")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jro")
    event1.set()

    log.info("Step7:检查集群内部数据一致性.")
    disk.multi_check_part_lun_uniform_by_ip()

def vdb_run():
    log.info("Step3:在主机2上运行vdbench -f mix-R.conf.")
    osan.run_vdb(client_ips[1], mix_R, output=deploy_ips[0], time=1200)
    event2.set()

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

if __name__ == '__main__':
    case()
