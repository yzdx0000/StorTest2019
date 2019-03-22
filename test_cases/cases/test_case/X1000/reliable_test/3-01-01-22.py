#!/usr/bin/python
# -*-coding:utf-8 -*
"""
:Date: 2018-10-30
:Author: diws
:Description:
1、在节点A上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
3、在主机1上运行vdbench -f OLTP.conf -jn；在主机2上运行vdbench -f mix-S.conf;
4、在步骤3中的业务运行过程中，将节点A和原日志组节点B同时掉电；
5、在主机1上执行vdbench -f OLTP.conf -jro比较一致性；
6、节点A和节点B超时后上电恢复；
7、检查数据修复和日志迁移
8、数据修复过程中，在主机1上执行vdbench -f OLTP.conf -jro比较数据一致性；
9、数据修复完成后，比较存储内部数据一致性。
:Changerlog:
"""
# testlink case: 1000-32306
import os, sys
import commands
import threading
import random
import time
import re
import utils_path
import common2
import common
import log
import get_config
import ReliableTest
import login
import error
import breakdown
import prepare_x1000

conf_file = common2.CONF_FILE
osan = common2.oSan()
disk = breakdown.disk()
node = common.Node()
# 初始化日志文件
file_name = os.path.basename(__file__)
file_name = file_name[:-3]
error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=4)

# 获取集群节点信息
deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
vip = login.login()
# 修改vdbench配置文件的参数值
lun1 = osan.ls_scsi_dev(client_ips[0])
if len(lun1) < 5:
    mix_S_align = osan.gen_vdb_xml(lun=lun1, xfersize="(3k,100)", seekpct=30, rdpct=0)
else:
    mix_S_align = osan.vdb_write(sd="default")
    for i in range(0, len(lun1)):
        j = i + 1
        if i == 0:
            mix_S_align = osan.vdb_write(sd="sd" + str(j), lun=lun1[i], wd="wd" + str(j), xfersize="8k", seekpct=100,
                                         rdpct=0, skew=20)
        elif i == 1:
            mix_S_align = osan.vdb_write(sd="sd" + str(j), lun=lun1[i], wd="wd" + str(j), xfersize="4k", seekpct=100,
                                         rdpct=0, skew=45)
        elif i == 2:
            mix_S_align = osan.vdb_write(sd="sd" + str(j), lun=lun1[i], wd="wd" + str(j), xfersize="8k", seekpct=0,
                                         rdpct=10, skew=15)
        elif i == 3:
            mix_S_align = osan.vdb_write(sd="sd" + str(j), lun=lun1[i], wd="wd" + str(j), xfersize="4k", seekpct=100,
                                         rdpct=0, skew=10)
        elif i == 4:
            mix_S_align = osan.vdb_write(sd="sd" + str(j), lun=lun1[i], wd="wd" + str(j), xfersize="4k", seekpct=0,
                                         rdpct=0, skew=10)
mix_S = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[1]),
                         xfersize="(3k,100)",
                         offset=2048,
                         seekpct=0,
                         rdpct=0)
jnl_ids = disk.get_jnl_node_id()
a_id = random.choice(jnl_ids)
jnl_ids.remove(a_id)
b_id = random.choice(jnl_ids)
a_ip = osan.get_node_by_vip(a_id)
b_ip = disk.get_node_ip_by_id(n_id=b_id)
log.info("Got node %s and %s." % (a_ip, b_ip))


def up_down(pipein):
    time.sleep(30)
    # 修改节点isolate参数，改为30s
    cmd = 'pscli --command=update_param --section=MGR --name=node_isolate_timeout --current=300000'
    rc, stdout = ReliableTest.run_pscli_cmd(cmd)
    if 0 != rc:
        log.error("Change node isolate time failed.")
        exit(1)
    log.info("4、在步骤3中的业务运行过程中，将节点A %s 和原日志组节点B %s 同时掉电；" % (a_ip, b_ip))
    log.info("Begin shutdown node %s and %s." % (a_ip, b_ip))
    m_a_info = error.down_node(fault_ip=a_ip)
    m_b_info = error.down_node(fault_ip=b_ip)
    while True:
        line = os.read(pipein, 32)
        if 'up' in line:
            break
    time.sleep(380)
    log.info("6、节点A和节点B超时后上电恢复；")
    log.info("Begin startup node %s and %s." % (a_ip, b_ip))
    error.up_node(node_info=m_a_info)
    error.up_node(node_info=m_b_info)


def vdb_jn(pipeout):
    log.info("3、在主机1上运行vdbench -f OLTP.conf -jn；在主机2上运行vdbench -f mix-S.conf;")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0], jn_jro="jn")
    log.info("5、在主机1上执行vdbench -f OLTP.conf -jro比较一致性；")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0], jn_jro="jro")
    # 通知故障注入线程，启动两个节点
    os.write(pipeout, "upnode")
    # 等待节点启动完成
    for ip in deploy_ips:
        common.check_ip(ip)
        error.check_host(ip)
    log.info("8、数据修复过程中，在主机1上执行vdbench -f OLTP.conf -jro比较数据一致性；")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0], jn_jro="jro")
    log.info("9、等待系统修复完成。")
    disk.check_bad_obj()
    log.info("9、数据修复完成后，比较存储内部数据一致性。")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0], jn_jro="jro")


    disk.multi_check_part_lun_uniform_by_ip()


def vdb_run():
    log.info("Step3:在主机2上运行vdbench -f mix-S.conf.")
    osan.run_vdb(client_ips[1], mix_S, output=deploy_ips[0], time=1200)


def main():
    test_threads = []
    (pipein, pipeout) = os.pipe()
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
    exit(-110)


if __name__ == '__main__':
    main()
