#!/usr/bin/python
# -*-coding:utf-8 -*
"""
:Date: 2018-10-23
:Author: diws
:Description:
1、在节点A上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
3、在主机1上运行vdbench -f OLTP.conf -jn；在主机2上运行vdbench -f mix-S.conf;
4、将非日志节点D下电；
5、主机1上业务完成后，在主机1上执行vdbench OLTP.conf -jro比较一致性；
6、节点D下电超时后上电，启动数据修复，数据修复中，在主机1上执行vdbench -f OLTP.conf -jro比较一致性；
7、节点D数据修复完成，在主机1上执行vdbench -f OLTP.conf -jro比较一致性；
8、比较存储内部数据一致性.
:Changerlog:
"""
# testlink case: 1000-32484
import os,sys
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
        j = i+1
        if i == 0:
            mix_S_align = osan.vdb_write(sd="sd"+str(j), lun=lun1[i], wd="wd"+str(j), xfersize="8k", seekpct=100,
                                         rdpct=0, skew=20)
        elif i == 1:
            mix_S_align = osan.vdb_write(sd="sd"+str(j), lun=lun1[i], wd="wd"+str(j), xfersize="4k", seekpct=100,
                                         rdpct=0, skew=45)
        elif i == 2:
            mix_S_align = osan.vdb_write(sd="sd"+str(j), lun=lun1[i], wd="wd"+str(j), xfersize="8k", seekpct=0,
                                         rdpct=10, skew=15)
        elif i == 3:
            mix_S_align = osan.vdb_write(sd="sd"+str(j), lun=lun1[i], wd="wd"+str(j), xfersize="4k", seekpct=100,
                                         rdpct=0, skew=10)
        elif i == 4:
            mix_S_align = osan.vdb_write(sd="sd"+str(j), lun=lun1[i], wd="wd"+str(j), xfersize="4k", seekpct=0,
                                         rdpct=0, skew=10)
mix_S = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[1]),
                         xfersize="(3k,100)",
                         offset=2048,
                         seekpct=100,
                         rdpct=0)
# 获取losid-nodeid-jnlstate对应关系
los_nid_state = disk.get_jnl_state()
log.info("Before inject error,the loss' state are{los_id:[node_id, los_state]}:%s" % (los_nid_state,))
# 获取所有los id
losids = los_nid_state.keys()
# 随机选择一个los
losid = random.choice(losids)
log.info("Select los is %d." % (losid,))
a_id = los_nid_state[losid][0]
non_jnl_ids = error.get_non_free_node_id()
if len(non_jnl_ids) != 0:
    a_id = random.choice(non_jnl_ids)
    log.info("非日志节点ID为：%d" % (int(a_id)))
a_ip = node.get_node_ip_by_id(a_id)


def up_down(pipein):
    time.sleep(30)
    # 修改节点isolate参数，改为30s
    cmd = 'pscli --command=update_param --section=MGR --name=node_isolate_timeout --current=300000'
    rc, stdout = ReliableTest.run_pscli_cmd(cmd)
    if 0 != rc:
        log.error("Change node isolate time failed.")
        exit(1)
    log.info("4、将非日志节点D %s 下电；" % (a_ip,))
    log.info("Begin shutdown node %s." % (a_ip,))
    m_a_info = error.down_node(fault_ip=a_ip)
    time.sleep(390)
    while True:
        line = os.read(pipein, 32)
        if 'up' in line:
            break
    log.info("6、节点D上电恢复；")
    log.info("Begin startup node %s." % (a_ip,))
    error.up_node(node_info=m_a_info)
    cmd = 'pscli --command=update_param --section=MGR --name=node_isolate_timeout --current=3000000'
    rc, stdout = ReliableTest.run_pscli_cmd(cmd)
    if 0 != rc:
        log.error("Change node isolate time failed.")
        exit(1)


def vdb_jn(pipeout):
    log.info("4、:在主机1上运行vdbench -f mix-S-align.conf -jn.")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0], jn_jro="jn")
    log.info("5、主机1上业务完成后，在主机1上执行vdbench mix-S-Align.conf -jro比较一致性；")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0], jn_jro="jro")
    log.info("6、节点B下电超时后上电，启动数据修复，数据修复中，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性；")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0], jn_jro="jro")
    # 通知故障注入线程，启动两个节点
    os.write(pipeout, "upnode")
    # 等待节点启动完成
    for ip in deploy_ips:
        common.check_ip(ip)
        error.check_host(ip)
    log.info("6、等待系统修复。")
    disk.check_bad_obj()
    log.info("7、节点B数据修复完成，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性；")
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