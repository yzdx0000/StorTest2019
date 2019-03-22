#!/usr/bin/python
#-*-coding:utf-8 -*
"""
:Date: 2018-08-16
:Author: diws
:Description:
            1、在节点A上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
            2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
            3、将节点B下电；
            4、在主机1上运行vdbench -f mix-S-align.conf -jn；在主机2上运行vdbench -f mix-S.conf;
            5、主机1上业务完成后，在主机1上执行vdbench -f mix-S-align.conf -jro比较一致性；
            6、节点B上电，数据修复中，在主机1上执行vdbench -f mix-S-align.conf -jro比较一致性；
            7、节点A数据修复完成，在主机1上执行vdbench -f mix-S-align.conf -jro比较一致性；
            8、比较存储内部数据一致性
:Changerlog:
"""
# testlink case: 1000-32331
import os
import sys
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
error.rel_check_before_run(file_name, jnl_rep=2, node_num=3, free_jnl_num=0, data_rep=2)

#获取集群节点信息
deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
vip = login.login()
#修改vdbench配置文件的参数值
mix_R_align = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[0]),
                               xfersize="(1k,100)",
                               seekpct=45,
                               rdpct=0)
mix_R = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[1]),
                         xfersize="(3k,100)",
                         offset=2048,
                         seekpct=0,
                         rdpct=0)
#检查日志节点副本数
disk_rep = disk.get_jnl_replica(s_ip=deploy_ips[0])
nodes = osan.get_nodes(s_ip=deploy_ips[0])
fault_node_ips = []
#获取日志节点ID和IP
if disk_rep == 1:
    log.error("Sorry,I can not going on,because there is only one or two jnl replica.")
    exit(1)
else:
    jnl_ids = osan.get_same_jnl_group(1)
    # 获取所有日志节点IP
    for id in jnl_ids:
        fault_node_ips.append(node.get_node_ip_by_id(id))
fault_node_ip = random.choice(fault_node_ips)
def up_down(pipeout):
    log.info("Step3:节点B下电 : %s." %(fault_node_ip))
    tmp = error.down_node(fault_ip=fault_node_ip)
    tmp = re.sub('\r', '', tmp)
    #节点B下电完成后，向匿名管道中写入节点b的ndoeinfo
    os.write(pipeout, tmp)
def vdb_jn(pipein):
    time.sleep(100)
    log.info("Step4:在主机1上运行vdbench -f mix-R-align.conf -jn.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0],jn_jro="jn")
    log.info("Step5:主机1上业务完成后，在主机1上执行vdbench -f mix-R-align.conf -jro比较一致性.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")
    #监控到匿名管道中写入数据后，给节点B上电，然后退出循环，执行jro
    while True:
        line = os.read(pipein,32)
        if len(line) != 0:
            for vid in line.strip().split(','):
                error.up_node(node_info=vid)
            break
    log.info("Step6:在数据修复过程中在主机1上执行vdbench -f S-align.conf -jro比较一致性.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")
    for ip in deploy_ips:
        common.check_ip(ip)
        error.check_host(ip)
    log.info("Step7:等待数据修复")
    for id in nodes:
        while 'HEALTHY' not in node.get_node_state(id):
            time.sleep(20)
            log.info("Step7:等待数据修复ing")
    log.info("Step7:数据修复完成后在主机1上执行vdbench -f S-align.conf -jro比较一致性.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")
    disk.multi_check_part_lun_uniform_by_ip()


def vdb_run():
    log.info("Step3:在主机2上运行vdbench -f mix-R.conf.")
    osan.run_vdb(client_ips[1], mix_R, output=deploy_ips[0],time=1200)
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
