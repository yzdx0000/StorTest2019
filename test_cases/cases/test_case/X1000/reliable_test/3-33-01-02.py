#!/usr/bin/python
# -*-coding:utf-8 -*
'''
Date:20181022
Author:liuhe
Description：
1、在节点A上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
3、在主机1上运行vdbench -f mix-R-OLTP.conf -jn；在主机2上运行vdbench -f mix-R.conf;
4、在步骤3中的业务运行过程中，将A节点故障，将节点B一块数据盘拔掉；
5、主机1上业务完成后，在主机1上执行vdbench -f mix-S-OLTP.conf -jro比较一致性；
6、数据修复完成后，在主机1上执行vdbench -f mix-S-OLTP.conf -jro比较一致性；
7、数据盘超时后恢复，系统进行数据校验；
'''

# testlink case: 1000-33156
import os, sys
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

conf_file = common2.CONF_FILE  # 配置文件路径
clean_env = common2.CLEAN_ENV
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
error.rel_check_before_run(file_name)
deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
osan = common2.oSan()
node = common.Node()
disk = breakdown.disk()
vip = login.login()
# 修改vdbench配置文件的参数值
mix_O = osan.vdb_write(sd="default")
lun1 = osan.ls_scsi_dev(client_ips[0])
if len(lun1) < 6:
    mix_O = osan.gen_vdb_xml(lun=lun1, xfersize="(3k,100)", offset=2048, seekpct=0, rdpct=0)
else:
    for i in range(0, len(lun1)):
        j = i + 1
        if i == 0:
            mix_O = osan.vdb_write(sd="sd" + str(j), lun=lun1[i], wd="wd" + str(j), xfersize="8k", seekpct=100,
                                   rdpct=10, skew=20)
        if i == 1:
            mix_O = osan.vdb_write(sd="sd" + str(j), lun=lun1[i], wd="wd" + str(j), xfersize="4k", seekpct=100,
                                   rdpct=10, skew=45)
        if i == 2:
            mix_O = osan.vdb_write(sd="sd" + str(j), lun=lun1[i], wd="wd" + str(j), xfersize="8k", seekpct=0, rdpct=10,
                                   skew=15)
        if i == 3:
            mix_O = osan.vdb_write(sd="sd" + str(j), lun=lun1[i], wd="wd" + str(j), xfersize="4k", seekpct=100,
                                   rdpct=0, skew=10)
        if i == 4:
            mix_O = osan.vdb_write(sd="sd" + str(j), lun=lun1[i], wd="wd" + str(j), xfersize="4k", seekpct=0, rdpct=0,
                                   skew=10)
mix_R = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[1]), xfersize="(3k,100)", offset=2048, seekpct=0, rdpct=0)

#确定A节点和B节点IP
v_ip = random.choice(vip)
log.info("Got vip is %s." % (v_ip,))
a_ip = osan.get_node_by_vip(v_ip)
a_id = node.get_node_id_by_ip(a_ip)
# 获取另一日志节点
use_jnl_ids = osan.get_same_jnl_group(1)
if a_id in use_jnl_ids:
    use_jnl_ids.remove(a_id)
b_id = random.choice(use_jnl_ids)
b_ip = node.get_node_ip_by_id(b_id)
log.info("Got machine A's IP: %s, and machine B's IP: %s." % (a_ip, b_ip))

#选出一个数据盘和数据盘的uuid再确定所在pool
disk_names = disk.get_rw_disk_by_node_id(s_ip=b_ip, node_id=b_id, disk_type="data")
disk_name = []
disk_name.append(random.choice(disk_names))
disk_phyids = disk.get_disk_phyid_by_name(s_ip=b_ip, disk_name=disk_name)
disk_id = disk.get_diskid_by_name(s_ip=b_ip, node_id=b_id, disk_name=disk_name[0])
disk_uuid = disk.get_disk_uuid_by_name(s_ip=b_ip, node_id=b_id, disk_name=disk_name[0])
storage_pool_id = disk.get_storage_poolid_by_diskid(s_ip=b_ip, node_id=b_id, disk_id=disk_id)


def up_down(pipein):
    time.sleep(10)
    cmd = "ssh %s 'pscli --command=update_param --section=MGR --name=disk_isolate2rebuild_timeout --current=30000'" % (
        a_ip)
    rc, stdout = commands.getstatusoutput(cmd)
    if 0 != rc:
        log.error('update param failed!!!')
        exit(1)
    time.sleep(40)
    log.info("4、在步骤3中的业务运行过程中，将A节点关机，拔掉B节点一个数据盘；")
    log.info("Begin shutdown node:%s." % (a_ip,))
    m_info = error.down_node(fault_ip=a_ip)
    log.info("On node %s remove disk" % (b_ip,))
    ReliableTest.remove_disk(b_ip, disk_id, "data")
    # 监控到匿名管道中写入数据后，退出循环
    while True:
        line = os.read(pipein, 32)
        if 'up' in line:
            break
    log.info("Begin startup node %s through %s." % (a_ip, m_info))
    error.up_node(node_info=m_info)
    time.sleep(300)
    disk.delete_disk(b_ip, disk_id)
    ReliableTest.insert_disk(b_ip, disk_id, "data")
    disk.add_disk(s_ip=b_ip, uuid=disk_uuid, usage="DATA", node_id=b_id)
    disk.expand_disk_2_storage_pool_by_uuid(s_ip=b_ip, node_id=b_id, uuid=disk_uuid, storage_pool_id=storage_pool_id)


def vdb_jn(pipeout):
    log.info("Step4:在主机1上运行vdbench -f OLTP.conf -jn.")
    osan.run_vdb(client_ips[0], mix_O, output=deploy_ips[0], jn_jro="jn")
    log.info("Step5:主机1上业务完成后，在主机1上执行vdbench -f OLTP.conf -jro比较一致性.")
    osan.run_vdb(client_ips[0], mix_O, output=deploy_ips[0], jn_jro="jro")
    os.write(pipeout, "upnode")
    disk.check_bad_obj()
    log.info("Step7:节点B数据修复完成，在主机1上执行vdbench -f OLTP.conf -jro比较一致性；")
    osan.run_vdb(client_ips[0], mix_O, output=deploy_ips[0], jn_jro="jro")


    disk.multi_check_part_lun_uniform_by_ip()


def vdb_run():
    log.info("Step4:在主机2上运行vdbench -f mix-R.conf.")
    osan.run_vdb(client_ips[1], mix_R, output=deploy_ips[0], time=1200)


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


if __name__ == '__main__':
    main()
