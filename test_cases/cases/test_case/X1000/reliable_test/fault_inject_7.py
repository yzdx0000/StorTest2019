#!/usr/bin/python
# -*-coding:utf-8 -*
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
        :By:diws
        :Date:2018-08-17
        :Changecontent:
                    1. 修正了在zk盘独立挂载的情况下，误拔zk挂载盘的问题
                    2. 修正了prepare函数中，判断磁盘状态进入死循环的问题
                    3. 增加了oSan坏对象的检查：disk.check_bad_obj
                    4. 增加了逻辑盘坏对象的检查：common.check_badjobnr()
        :By:diws
        :Date:2019-01-04
        ;Changecontent:
                    1. 添加了参数支持：-n 故障节点数；-t 运行次数
                    2. 添加了多线程、多节点支持，目前不支持三节点故障两节点的操作，在下一版本解决。
注意：以上故障，未覆盖超时的情况，后期需要补充
"""
import os, sys
import commands
import threading
import random
import time
import optparse
import utils_path
import common2
import common
import log
import get_config
import ReliableTest
import login
import error
import breakdown

conf_file = common2.CONF_FILE  # 配置文件路径
osan = common2.oSan()
disk = breakdown.disk()
node = common.Node()
# 初始化日志文件
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)  # 初始化日志文件
# 获取集群节点信息
deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()


# 故障类型
err_dict = {}
err_dict[0] = ['oMgcd', 'oRole', 'oSan', 'oStor']
err_dict[1] = ['data', 'io']
err_dict[2] = ['node']
err_dict[3] = ['share', 'data']
# 获取lun数据副本数和日志副本数
# min_lun_rep = disk.get_min_lun_replica(s_ip=deploy_ips[0])
# min_jnl_rep = disk.get_jnl_replica(s_ip=deploy_ips[0])
# if min_jnl_rep < 2 or min_lun_rep < 2:
#     log.error("Sorry,I can not insert fault,because the jnl replica or the lun replica can't meet the condition.")
#     os._exit(1)


def get_args():
    parser = optparse.OptionParser('Usage:%prog -n <faullt node num> -t <run times>')
    parser.add_option('-n',
                      dest='node_nums',
                      type='int',
                      default=1,
                      help='specify the node nums which you want to inject error.')
    parser.add_option('-t',
                      dest='run_times',
                      type='int',
                      default=100,
                      help='specify the run times for your test.')
    options, args = parser.parse_args()
    node_nums = options.node_nums
    run_times = options.run_times
    return node_nums, run_times


def up_down(fault_ip, run_times):
    time.sleep(60)
    fault_id = disk.get_node_id_by_ip(n_ip=fault_ip)
    for i in range(run_times):
        err_type = random.randint(0, 4)
        if err_type == 0:
            fault_pro = random.choice(err_dict[0])
            log.info("将节点 %s 干掉: %s." % (fault_ip, fault_pro))
            cmd = ("ssh %s 'killall -9 %s'" % (fault_ip, fault_pro))
            commands.getstatusoutput(cmd)
        elif err_type == 1:
            eth_type = random.choice(err_dict[1])
            if eth_type == 'data':
                err_eth, extra_ip = error.get_dataip_info(fault_id)
            else:
                err_eth, extra_ip = error.get_ioip_info(fault_id)
            err_times = random.randint(1, 10)
            log.info("Step3:选择断网次数：%d" % (err_times,))
            eth_err_type = random.randint(0, 2)
            if eth_err_type == 0:
                err_eth = random.choice(err_eth).split()
            log.info("选择网络：%s--%s，额外IP：%s" % (eth_type, err_eth, extra_ip))
            for j in range(err_times):
                ReliableTest.run_down_net(extra_ip[0], err_eth)
                time_down = random.randint(35, 130)
                log.info("选择断网间隔：%d" % (time_down,))
                time.sleep(time_down)
                ReliableTest.run_up_net(extra_ip[0], err_eth)
                time_down = random.randint(35, 127)
                log.info("等待：%d秒后，注入下一次网络故障" % (time_down,))
                time.sleep(time_down)
        # 注意注意
        elif err_type == 2:
            fault_type = random.choice(err_dict[2])
            if fault_type == 'node':
                log.info("将%s下电." % (fault_ip,))
                fault_node_info = error.down_node(fault_ip)
                time_down = random.randint(0, 150)
                # log.info("将节点 %s 宕机: %d秒." %(fault_ip,time_down))
                time.sleep(time_down)
                log.info("将%s上电." % (fault_ip,))
                error.up_node(fault_node_info)
                common.check_ip(fault_ip)
        elif err_type == 3:
            fault_type = random.choice(err_dict[3])
            fault_disk = {}
            if fault_type == 'data':
                disk_names = disk.get_rw_disk_by_node_id(s_ip=fault_ip, node_id=fault_id, disk_type='data')
                fault_disk_phyid = disk.get_disk_phyid_by_name(s_ip=fault_ip, disk_name=disk_names)
                fault_disk[fault_ip] = fault_disk_phyid
            elif fault_type == 'share':
                disk_names = disk.get_rw_disk_by_node_id(s_ip=fault_ip, node_id=fault_id, disk_type='share')
                fault_disk_phyid = disk.get_disk_phyid_by_name(s_ip=fault_ip, disk_name=disk_names)
                fault_disk[fault_ip] = fault_disk_phyid
            remove_disk = {}
            for ip in fault_disk.keys():
                remove_disk_nums = random.randint(1, len(fault_disk[ip]))
                remove_disk[ip] = random.sample(fault_disk[ip], remove_disk_nums)
            log.info("磁盘类型：%s,删除磁盘：%s." % (fault_type, remove_disk))
            for ip in remove_disk.keys():
                node_remove_disk_time = random.randint(0, 20)
                log.info("%d秒后，%s 开始拔盘" % (node_remove_disk_time, ip))
                time.sleep(node_remove_disk_time)
                for disk_id in remove_disk[ip]:
                    disk_remove_time = random.randint(0, 20)
                    log.info("当前节点，%d秒后，拔下一块盘" % (disk_remove_time))
                    time.sleep(disk_remove_time)
                    ReliableTest.remove_disk(ip, disk_id, fault_type)
            for ip in remove_disk.keys():
                for disk_id in remove_disk[ip]:
                    log.info("节点：%s,开始添加磁盘：%s" % (ip, disk_id))
                    ReliableTest.insert_disk(ip, disk_id, fault_type)
                    time.sleep(1)
        time.sleep(300)


def vdb_jn(run_times):
    # 修改vdbench配置文件的参数值
    mix_R_Align = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[0])[:4],
                                   xfersize="(13k,100)",
                                   seekpct=0,
                                   rdpct=0)
    run_times = run_times/6
    if run_times == 0:
        run_times = 1
    for i in range(run_times):
        log.info("Step4:在主机1上运行vdbench -f mix-R-Align.conf -jn.")
        osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jn")
        log.info("Step5:主机1上业务完成后，在主机1上执行vdbench -f mix-R-Align.conf -jro比较一致性.")
        osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jro")
        log.info("Step6:主机1上业务完成后，在主机1上执行vdbench -f mix-R-Align.conf -jro比较一致性.")
        osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jro")


def vdb_run(run_times):
    mix_R = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[1])[:4],
                             xfersize="(3k,100)",
                             offset=2048,
                             seekpct=0,
                             rdpct=0)
    run_times = run_times/2
    if run_times == 0:
        run_times = 1
    for i in range(run_times):
        log.info("Step4:在主机2上运行vdbench -f mix-R.conf.")
        osan.run_vdb(client_ips[1], mix_R, output=deploy_ips[0], time=2400)


def case(node_nums, run_times):
    test_threads = []
    for i in range(node_nums):
        fault_ip = random.choice(deploy_ips)
        deploy_ips.remove(fault_ip)
        test_threads.append(threading.Thread(target=up_down, args=(fault_ip, run_times)))
    test_threads.append(threading.Thread(target=vdb_jn, args=(run_times,)))
    test_threads.append(threading.Thread(target=vdb_run, args=(run_times,)))
    for test_thread in test_threads:
        test_thread.setDaemon(True)
        test_thread.start()
    for test_thread in test_threads:
        test_thread.join()


def main():
    node_nums, run_times = get_args()
    login.login()
    case(node_nums, run_times)


if __name__ == '__main__':
    main()
