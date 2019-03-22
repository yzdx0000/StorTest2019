#!/usr/bin/python
#-*-coding:utf-8 -*
"""
:Date: 2018-08-13
:Author: diws
:Description:
            1、在节点A上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
            2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
            3、在主机1上运行vdbench -f OLTP.conf -jn；在主机2上运行vdbench -f mix-R.conf;
            4、在步骤3中的业务运行过程中，将节点A同组的日志节点B业务网单网口故障（节点B无业务）；
            5、节点A重启，
            6、在主机1上执行vdbench -f OLTP.conf -jro比较一致性；
            7、节点A上电后进行数据修复中，在主机1上执行vdbench -f OLTP.conf -jro比较一致性；
            8、节点A数据修复完成，在主机1上执行vdbench -f OLTP.conf -jro比较一致性；
            9、比较存储内部数据一致性。
:Changerlog:
"""
# testlink case: 1000-32303
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
error.rel_check_before_run(file_name, jnl_rep=3, node_num=4, free_jnl_num=1, data_rep=3)

#获取集群节点信息
deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
vip = login.login()
#修改vdbench配置文件的参数值
mix_O = osan.vdb_write(sd="default")
lun1 = osan.ls_scsi_dev(client_ips[0])
for i in range(0,len(lun1)):
    j = i+1
    if i == 0:
        mix_O = osan.vdb_write(sd="sd"+str(j),lun=lun1[i],wd="wd"+str(j),xfersize="8k",seekpct=100,rdpct=10,skew=20)
    if i == 1:
        mix_O = osan.vdb_write(sd="sd"+str(j),lun=lun1[i],wd="wd"+str(j),xfersize="4k",seekpct=100,rdpct=10,skew=45)
    if i == 2:
        mix_O = osan.vdb_write(sd="sd"+str(j),lun=lun1[i],wd="wd"+str(j),xfersize="8k",seekpct=0,rdpct=10,skew=15)
    if i == 3:
        mix_O = osan.vdb_write(sd="sd"+str(j),lun=lun1[i],wd="wd"+str(j),xfersize="4k",seekpct=100,rdpct=0,skew=10)
    if i == 4:
        mix_O = osan.vdb_write(sd="sd"+str(j),lun=lun1[i],wd="wd"+str(j),xfersize="4k",seekpct=0,rdpct=0,skew=10)
mix_R = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[1]),
                         xfersize="(3k,100)",
                         offset=2048,
                         seekpct=0,
                         rdpct=0)
#检查日志节点副本数
disk_rep = disk.get_jnl_replica(s_ip=deploy_ips[0])
nodes = osan.get_nodes(s_ip=deploy_ips[0])
#获取日志节点ID和IP
if disk_rep < 3:
    log.error("Sorry,I can not going on,because there is only one or two jnl replica.")
    exit(1)
else:
    jnl_ids = disk.get_jnl_node_id()
    # 随机选择一个日志节点ID并获取其IP
    fault_node_id = random.choice(jnl_ids)
    fault_node_ip = node.get_node_ip_by_id(fault_node_id)
#获取非业务接入节点ID和IP
"""获取所有业务接入节点ID"""
interface_node_id = disk.get_interface_node(vips=vip)
no_interface_node_id = list(set(nodes).difference(set(interface_node_id)))
"""获取非业务接入节点ID"""
if len(no_interface_node_id) == 0:
    no_interface_node_id = nodes
if fault_node_id in no_interface_node_id:
    no_interface_node_id.remove(fault_node_id)
no_interface_node_id = random.choice(no_interface_node_id)
err_eth, extra_ip = error.get_dataip_info(no_interface_node_id)
err_eth = err_eth[:1]
def up_down():
    time.sleep(100)
    fault_node_info = []
    """断业务网先"""
    log.info("Step4:在步骤3中的业务运行过程中，将节点A同组的日志节点B业务网故障 : %s--%s." %(extra_ip,err_eth))
    ReliableTest.run_down_net(extra_ip[0], err_eth)
    time.sleep(30)
    """把节点给下电吧......"""
    log.info("Step5:节点A重启 : %s." %(fault_node_ip))
    tmp = error.down_node(fault_ip=fault_node_ip)
    time.sleep(10)
    log.info("Step5:节点A上电 : %s." % (tmp))
    error.up_node(node_info=tmp)
def vdb_jn():
    log.info("Step3:在主机1上运行vdbench -f OLTP.conf -jn.")
    osan.run_vdb(client_ips[0], mix_O, output=deploy_ips[0],jn_jro="jn")
    log.info("Step6:主机1上业务完成后，在主机1上执行vdbench -f OLTP.conf -jro比较一致性.")
    osan.run_vdb(client_ips[0], mix_O, output=deploy_ips[0], jn_jro="jro")
    """少年，莫急，这就恢复网络了"""
    log.info("Step7:节点B恢复网络.")
    ReliableTest.run_up_net(extra_ip[0],err_eth)
    for ip in deploy_ips:
        common.check_ip(ip)
        error.check_host(ip)
    log.info("Step7:在数据修复过程中在主机1上执行vdbench -f S-align.conf -jro比较一致性.")
    osan.run_vdb(client_ips[0], mix_O, output=deploy_ips[0], jn_jro="jro")
    for ip in deploy_ips:
        common.check_ip(ip)
        error.check_host(ip)
    log.info("Step8:等待节点B数据修复")
    for id in nodes:
        while 'HEALTHY' not in node.get_node_state(id):
            time.sleep(20)
            log.info("Step8:等待数据修复ing")
    log.info("Step8:数据修复完成后在主机1上执行vdbench -f S-align.conf -jro比较一致性.")
    osan.run_vdb(client_ips[0], mix_O, output=deploy_ips[0], jn_jro="jro")
    disk.multi_check_part_lun_uniform_by_ip()


def vdb_run():
    log.info("Step3:在主机2上运行vdbench -f mix-R.conf.")
    osan.run_vdb(client_ips[1], mix_R, output=deploy_ips[0],time=1200)
def case():
    test_threads = []
    test_threads.append(threading.Thread(target=up_down))
    test_threads.append(threading.Thread(target=vdb_jn))
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