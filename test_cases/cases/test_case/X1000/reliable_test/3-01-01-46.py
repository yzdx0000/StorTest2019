#!/usr/bin/python
#-*-coding:utf-8 -*
"""
:Date: 2018-08-16
:Author: diws
:Description:
            1、在节点A上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
            2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
            3、在主机1上运行vdbench -f mix-S-align.conf -jn；在主机2上运行vdbench -f mix-S.conf;
            4、在步骤3中的业务运行过程中，将节点A下电，free日志节点E接管节点A的日志；
            5、节点E重启，节点B接管节点E并重建日志；
            6、节点E上电恢复后，日志从节点B迁移到节点E过程中时，节点C重启；
            7、节点C上电恢复，数据修复过程中在主机1上执行vdbench -f mix-S-align.conf -jro比较一致性；
            8、节点A上电恢复，数据修复完成后，比较存储内部数据一致性。
:Changerlog:
"""
# testlink case: 1000-32329
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

conf_file = common2.CONF_FILE    #配置文件路径
osan = common2.oSan()
disk = breakdown.disk()
node = common.Node()
# 初始化日志文件
file_name = os.path.basename(__file__)
file_name = file_name[:-3]      #获取本脚本名，去掉.py后缀
error.rel_check_before_run(file_name, jnl_rep=4, node_num=5, free_jnl_num=1, data_rep=4)

#获取集群节点信息
deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
vip = login.login()
#修改vdbench配置文件的参数值
mix_S_align = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[0]),
                               xfersize="(1k,100)",
                               seekpct=0,
                               rdpct=0)
mix_S = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[1]),
                         xfersize="(3k,100)",
                         offset=2048,
                         seekpct=0,
                         rdpct=0)
#检查日志节点副本数
disk_rep = disk.get_jnl_replica(s_ip=deploy_ips[0])
#获取所有节点
nodes = osan.get_nodes(s_ip=deploy_ips[0])
free_jnl_ips = []
use_jnl_ips = []
use_jnl_ids = osan.get_same_jnl_group(1)
for id in use_jnl_ids:
    use_jnl_ips.append(node.get_node_ip_by_id(id))
free_jnl_ids = error.get_free_jnl_id()
if len(free_jnl_ids) == 0:
    free_jnl_ids = use_jnl_ids
for id in free_jnl_ids:
    free_jnl_ips.append(node.get_node_ip_by_id(id))
fault_node_a_ip = random.choice(use_jnl_ips)
use_jnl_ips.remove(fault_node_a_ip)
if fault_node_a_ip in free_jnl_ips:
    free_jnl_ips.remove(fault_node_a_ip)
fault_node_b_ip = random.choice(use_jnl_ips)
use_jnl_ips.remove(fault_node_b_ip)
if fault_node_b_ip in free_jnl_ips:
    free_jnl_ips.remove(fault_node_b_ip)
fault_node_c_ip = random.choice(use_jnl_ips)
if fault_node_c_ip in free_jnl_ips:
    free_jnl_ips.remove(fault_node_c_ip)
fault_node_d_ip = random.choice(free_jnl_ips)
node_info = []
def up_down(pipeout):
    time.sleep(100)
    log.info("Step4:将节点A下电 : %s." %(fault_node_a_ip))
    #将节点A下电
    tmp_a = error.down_node(fault_ip=fault_node_a_ip)
    tmp_a = re.sub('\r','',tmp_a)
    #将free日志节点E重启
    log.info("Step5:将free日志节点E重启 : %s." % (fault_node_d_ip))
    tmp_d = error.down_node(fault_ip=fault_node_d_ip)
    tmp_d = re.sub('\r','',tmp_d)
    #将free日志节点E上电
    time.sleep(40)
    error.up_node(node_info=tmp_d)
    error.check_host(fault_node_d_ip)
    log.info("Step6:将节点C重启 : %s." % (fault_node_c_ip))
    tmp_c = error.down_node(fault_ip=fault_node_c_ip)
    tmp_c = re.sub('\r','',tmp_c)
    #将日志节点D上电
    time.sleep(40)
    error.up_node(node_info=tmp_c)
    error.check_host(fault_node_c_ip)
    #节点B重启完成后，向匿名管道中写入节点a的ndoeinfo
    os.write(pipeout, tmp_a)
def vdb_jn(pipein):
    log.info("Step3:在主机1上运行vdbench -f mix-S-align.conf -jn.")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0],jn_jro="jn")
    time.sleep(30)
    #监控到匿名管道中写入数据后，退出循环，执行jro
    while True:
        line = os.read(pipein,32)
        if len(line) != 0:
            for vid in line.strip().split(','):
                error.up_node(node_info=vid.strip())
            break
    log.info("Step7:数据修复中，在主机1上执行vdbench -f mix-S-align.conf -jro比较一致性.")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0], jn_jro="jro")
    log.info("Step8:节点B上电。")
    error.up_node(node_info=vid)
    log.info("Step8:等待系统修复。")
    for id in nodes:
        while 'HEALTHY' not in node.get_node_state(id):
            time.sleep(20)
            log.info("Step8:等待数据修复ing")
    disk.multi_check_part_lun_uniform_by_ip()


def vdb_run():
    log.info("Step3:在主机2上运行vdbench -f mix-S.conf.")
    osan.run_vdb(client_ips[1], mix_S, output=deploy_ips[0],time=1200)
def case():
    (pipein,pipeout) = os.pipe()
    test_threads = []
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
def main():
    case()
if __name__ == '__main__':
    main()
