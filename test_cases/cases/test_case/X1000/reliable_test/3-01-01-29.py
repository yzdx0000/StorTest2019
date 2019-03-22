#!/usr/bin/python
#-*-coding:utf-8 -*
"""
:Date: 2018-08-14
:Author: diws
:Description:
1、在节点A上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
3、在主机1上运行vdbench -f OLTP.conf -jn；在主机2上运行vdbench -f mix-S.conf;
4、在步骤3中的业务运行过程中，将节点A和节点B掉电；
5、五分钟后节点A和节点B上电恢复等数据修复完成后比较数据一致性；
6、重复步骤4，步骤5动作4次；
7、数据修复完成后，比较存储内部数据一致性。
:Changerlog:
"""
# testlink case: 1000-32312
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
error.rel_check_before_run(file_name, jnl_rep=3, node_num=5, free_jnl_num=0, data_rep=3)

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
fault_node_ip = []
if disk_rep == 1:
    log.error("Sorry,I can not going on,because there is only one jnl replica.")
    exit(1)
else:
    jnl_ids = disk.get_jnl_node_id()
    for i in range(disk_rep-1):
        # 随机选择一个日志节点ID并获取其IP
        fault_node_id = random.choice(jnl_ids)
        jnl_ids.remove(fault_node_id)
        fault_node_ip.append(node.get_node_ip_by_id(fault_node_id))
log.info("Get fault ip:%s" % (fault_node_ip))
def up_down(pipeout):
    time.sleep(100)
    fault_node_info = []
    for ip in fault_node_ip:
        log.info("Step4:在步骤3中的业务运行过程中，将节点掉电 : %s." %(ip))
        tmp = error.down_node(fault_ip=ip)
        tmp = re.sub('\r', '', tmp)
        fault_node_info.append(tmp.strip())
    fault_node_info = re.sub('\[|\]|\'|\r', '', str(fault_node_info))
    os.write(pipeout,fault_node_info)
def vdb_jn(pipein):
    log.info("Step3:在主机1上运行vdbench -f OLTP.conf -jn.")
    osan.run_vdb(client_ips[0], mix_O, output=deploy_ips[0],jn_jro="jn")
    #jn阶段完成后，将两个故障节点上电
    while True:
        line = os.read(pipein,32)
        if len(line) != 0:
            for vid in line.strip().split(','):
                vid = re.sub('\\r','',vid)
                log.info("Step5:节点上电 : %s." %(vid.strip()))
                error.up_node(node_info=vid.strip())
                time.sleep(10)
            break
        time.sleep(10)
    #检查所有节点是否能正常登陆
    for ip in deploy_ips:
        common.check_ip(ip)
        error.check_host(ip)
    #检查所有节点是否已修复完成
    for id in nodes:
        log.info("Step5:等待数据修复")
        while 'HEALTHY' not in node.get_node_state(id):
            time.sleep(20)
            log.info("Step5:等待数据修复ing")
    log.info("Step5:数据修复完成后在主机1上执行vdbench -f S-align.conf -jro比较一致性.")
    osan.run_vdb(client_ips[0], mix_O, output=deploy_ips[0], jn_jro="jro")
    #循环四次
    for i in range(2):
        fault_node_info = []
        #将节点宕机
        for ip in fault_node_ip:
            log.info("Step4:在步骤3中的业务运行过程中，将节点掉电 : %s." % (ip))
            tmp = error.down_node(fault_ip=ip)
            tmp = re.sub('\r', '', tmp)
            fault_node_info.append(tmp.strip())
        time.sleep(300)
        #将节点上电
        for vid in fault_node_info:
            log.info("Step4:节点上电 : %s." % (vid.strip()))
            error.up_node(node_info=vid.strip())
        # 检查所有节点是否能正常登陆
        for ip in deploy_ips:
            common.check_ip(ip)
            error.check_host(ip)
        # 检查所有节点是否已修复完成
        for id in nodes:
            log.info("Step5:等待数据修复")
            while 'HEALTHY' not in node.get_node_state(id):
                time.sleep(20)
                log.info("Step5:等待数据修复ing")
        log.info("Step5:数据修复完成后在主机1上执行vdbench -f S-align.conf -jro比较一致性.")
        osan.run_vdb(client_ips[0], mix_O, output=deploy_ips[0], jn_jro="jro")
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
