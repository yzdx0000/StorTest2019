#!/usr/bin/python
#-*-coding:utf-8 -*
"""
:Date: 2018-08-16
:Author: diws
:Description:
            1、在节点A上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
            2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
            3、每隔40秒，随机选择一个节点，随机选择一个进程，将其干掉；或者随机选择一个网络，将其断掉
            4、在主机1上运行vdbench -f mix-R-Align.conf -jn；在主机2上运行vdbench -f mix-R.conf;
            5、主机1上业务完成后，在主机1上执行vdbench -f mix-R-Align.conf -jro比较一致性；
:Changerlog:
        :By:diws
        :Date:2018-08-10
        :Changecontent:添加节点故障
        :By:diws
        :Date:2018-08-10
        :Changecontent:添加磁盘故障
        :By:diws
        :Date:2018-08-16
        :Changecontent:添加环境检查
注意：以上故障，未覆盖超时的情况，后期需要补充
"""
import os,sys
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

conf_file = common2.CONF_FILE    #配置文件路径
osan = common2.oSan()
disk = breakdown.disk()
node = common.Node()
# 初始化日志文件
file_name = os.path.basename(__file__)
file_name = file_name[:-3]      #获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)     #获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)       #初始化日志文件
#获取集群节点信息
deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
vip = login.login()
#修改vdbench配置文件的参数值
mix_R_Align = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[0])[:4],
                               xfersize="(1k,100)",
                               seekpct=0,
                               rdpct=0)
mix_R = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[1])[:4],
                         xfersize="(3k,100)",
                         offset=2048,
                         seekpct=0,
                         rdpct=0)
#故障类型
err_dict = {}
err_dict[0] = ['oMgcd', 'oRole', 'oSan','oStor']   #进程故障
err_dict[1] = ['data', 'io']               #网络故障
err_dict[2] = ['node']                     #节点故障
err_dict[3] = ['share','data']             #磁盘故障
#获取lun数据副本数和日志副本数
min_lun_rep = disk.get_min_lun_replica(s_ip=deploy_ips[0])
min_jnl_rep = disk.get_jnl_replica(s_ip=deploy_ips[0])
if min_jnl_rep < 2 or min_lun_rep < 2 :
    log.error("Sorry,I can not insert fault,because the jnl replica or the lun replica can't meet the condition.")
    os._exit(1)
def up_down():
    time.sleep(100)
    for i in range(400):
        error.prepare()
        disk.check_bad_obj()

        fault_ip = error.get_fault_ip()
        #common.check_ip(fault_ip)
        fault_id = node.get_node_id_by_ip(fault_ip)
        err_type = random.randint(3,3)
        if err_type == 0:
            log.info("主oRole：%d" %(int(error.get_orole_master_id(s_ip=fault_ip))))
            fault_pro = random.choice(err_dict[0])
            if fault_pro == 'oRole':
                while int(fault_id) == int(error.get_orole_master_id(s_ip=fault_ip)):
                    fault_ip = error.get_fault_ip()
                    fault_id = node.get_node_id_by_ip(fault_ip)
            log.info("将节点 %s 干掉: %s." %(fault_ip,fault_pro))
            cmd = ("ssh %s 'killall -9 %s'" %(fault_ip,fault_pro))
            res,output = commands.getstatusoutput(cmd)
        elif err_type == 1:
            eth_type = random.choice(err_dict[1])
            if eth_type == 'data':
                err_eth, extra_ip = error.get_dataip_info(fault_id)
            else:
                err_eth, extra_ip = error.get_ioip_info(fault_id)
            err_times = random.randint(1,10)
            log.info("Step3:选择断网次数：%d" % (err_times))
            eth_err_type = random.randint(0,2)
            if eth_err_type == 0:
                err_eth = random.choice(err_eth).split()
            log.info("选择网络：%s--%s，额外IP：%s" % (eth_type,err_eth, extra_ip))
            for i in range(err_times):
                ReliableTest.run_down_net(extra_ip[0],err_eth)
                time_down = random.randint(1,30)
                log.info("选择断网间隔：%d" % (time_down))
                time.sleep(time_down)
                ReliableTest.run_up_net(extra_ip[0],err_eth)
                time_down = random.randint(1,30)
                log.info("等待：%d秒后，注入下一次网络故障" % (time_down))
                time.sleep(time_down)
        #屏蔽掉节点故障
        #注意注意
        elif err_type == 2:
            fault_type = random.choice(err_dict[2])
            if fault_type == 'node':
                log.info("将%s下电." %(fault_ip))
                fault_node_info = error.down_node(fault_ip)
                time_down = random.randint(0,150)
                #log.info("将节点 %s 宕机: %d秒." %(fault_ip,time_down))
                time.sleep(time_down)
                log.info("将%s上电." % (fault_ip))
                error.up_node(fault_node_info)
                common.check_ip(fault_ip)
        elif err_type == 3:
            fault_type = random.choice(err_dict[3])
            fault_disk = {}
            if fault_type == 'data':
                #随机选择min_lun_rep-1个节点，获取所有数据盘
                for i in range(min_lun_rep-1):
                    fault_ip = error.get_fault_ip()
                    fault_id = node.get_node_id_by_ip(fault_ip)
                    disk_names = disk.get_rw_disk_by_node_id(s_ip=fault_ip,node_id=fault_id,disk_type='data')
                    fault_disk_phyid = disk.get_disk_phyid_by_name(s_ip=fault_ip,disk_name=disk_names)
                    fault_disk[fault_ip] = fault_disk_phyid
            elif fault_type == 'share':
                #随机选择min_jnl_rep-1个节点，获取所有共享盘
                for i in range(min_jnl_rep-1):
                    fault_ip = error.get_fault_ip()
                    fault_id = node.get_node_id_by_ip(fault_ip)
                    disk_names = disk.get_rw_disk_by_node_id(s_ip=fault_ip,node_id=fault_id,disk_type='share')
                    fault_disk_phyid = disk.get_disk_phyid_by_name(s_ip=fault_ip,disk_name=disk_names)
                    fault_disk[fault_ip] = fault_disk_phyid
            remove_disk = {}
            #获取到的min_jnl_rep-1/min_lun_rep-1个节点所有盘中，随机选择一批，将其移除
            for ip in fault_disk.keys():
                remove_disk_nums = random.randint(1, len(fault_disk[ip]))
                remove_disk[ip] = random.sample(fault_disk[ip], remove_disk_nums)
            log.info("磁盘类型：%s,删除磁盘：%s." %(fault_type,remove_disk))
            for ip in remove_disk.keys():
                node_remove_disk_time = random.randint(0, 20)
                log.info("%d秒后，%s 开始拔盘" % (node_remove_disk_time, ip))
                time.sleep(node_remove_disk_time)
                for disk_id in remove_disk[ip]:
                    disk_remove_time = random.randint(0, 20)
                    log.info("当前节点，%d秒后，拔下一块盘" % (disk_remove_time))
                    time.sleep(disk_remove_time)
                    ReliableTest.remove_disk(ip,disk_id,fault_type)
            for ip in remove_disk.keys():
                for disk_id in remove_disk[ip]:
                    log.info("节点：%s,开始添加磁盘：%s" % (ip, disk_id))
                    ReliableTest.insert_disk(ip,disk_id,fault_type)
                    time.sleep(1)
        time.sleep(60)
def vdb_jn():
    log.info("Step4:在主机1上运行vdbench -f mix-R-Align.conf -jn.")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0],jn_jro="jn")
    log.info("Step5:主机1上业务完成后，在主机1上执行vdbench -f mix-R-Align.conf -jro比较一致性.")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jro")
    log.info("Step6:主机1上业务完成后，在主机1上执行vdbench -f mix-R-Align.conf -jro比较一致性.")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jro")
    log.info("Step7:主机1上业务完成后，在主机1上执行vdbench -f mix-R-Align.conf -jro比较一致性.")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jro")
def vdb_run():
    log.info("Step4:在主机2上运行vdbench -f mix-R.conf.")
    osan.run_vdb(client_ips[1], mix_R, output=deploy_ips[0],time=2400)
    log.info("Step5:在主机2上运行vdbench -f mix-R.conf.")
    osan.run_vdb(client_ips[1], mix_R, output=deploy_ips[0],time=2400)
    log.info("Step6:在主机2上运行vdbench -f mix-R.conf.")
    osan.run_vdb(client_ips[1], mix_R, output=deploy_ips[0],time=2400)
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
            osan.iscsi_logout(cli,vip=ip)
def main():
    case()
if __name__ == '__main__':
    common.case_main(main)
