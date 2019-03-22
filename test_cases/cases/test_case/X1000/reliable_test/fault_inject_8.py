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
:Changelog:
        :By:diws
        :Date:2018-08-10
        :Change content:添加节点故障
        :By:diws
        :Date:2018-08-10
        :Change content:添加磁盘故障
        :By:diws
        :Date:2018-08-16
        :Change content:添加环境检查
        :By:diws
        :Date:2018-08-17
        :Changecontent:
                    1. 修正了在zk盘独立挂载的情况下，误拔zk挂载盘的问题
                    2. 修正了prepare函数中，判断磁盘状态进入死循环的问题
                    3. 增加了oSan坏对象的检查：disk.check_bad_obj
                    4. 增加了逻辑盘坏对象的检查：common.check_badjobnr()
        :By:diws
        :Date:2019-01-03
        ;Change content:
                    1. 添加了参数支持：-n 故障节点数；-t 运行次数
                    2. 添加了多线程、多节点支持，目前不支持三节点故障两节点的操作，在下一版本解决。
        :By: diws
        :Date:2019-01-03
        :Change content:
                    1. 对三节点环境进行判断，支持三节点集群，在两个节点注入故障
        :By: diws
        :Date:2019-01-10
        :Change content:
                    1. 每种故障类型，新增故障次数，随机值。
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
import prepare_x1000

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
# 进程故障，这个可以自行编辑
err_dict[0] = ['oRole', 'oSan', 'oStor']
# 网络、节点、磁盘故障，不建议修改
err_dict[1] = ['data', 'io']
err_dict[2] = ['node']
err_dict[3] = ['share', 'data']


def get_args():
    parser = optparse.OptionParser('Usage:%prog -n <faullt node num> -t <run times>')
    parser.add_option('-n',
                      dest='node_nums',
                      type='int',
                      default=2,
                      help='specify the node nums which you want to inject error.')
    parser.add_option('-t',
                      dest='run_times',
                      type='int',
                      default=10,
                      help='specify the times to run for your test.')
    options, args = parser.parse_args()
    node_nums = options.node_nums
    run_times = options.run_times
    return node_nums, run_times

def check_core():
    for ip in deploy_ips:
        cmd1 = ("ssh root@%s 'ls /core* 2> /dev/null'" % (ip, ))
        cmd2 = ("ssh root@%s 'ls /home/parastor/log/core* 2> /dev/null'" % (ip, ))
        rc1, stdout1 = commands.getstatusoutput(cmd1)
        rc2, stdout2 = commands.getstatusoutput(cmd2)
        if rc1 == 0 or rc2 == 0:
            print "Found core on:%s." % (ip,)
            os._exit(1)
def up_down(fault_ip, run_times, fault_node_num):
    """
    :param fault_ip: 故障节点IP
    :param run_times: 故障次数
    :param fault_node_num: 故障节点编号，用来处理三节点环境故障两个节点的情况
    :return: None
    """
    # 获取所有节点ID
    nodes = osan.get_nodes()
    # 统计集群中节点个数
    node_nums = len(nodes)
    # 如果是三节点环境，同时故障节点数为2，则第二个节点只注入进程故障；其他情况则所有故障节点使用所有故障类型
    if node_nums == 3 and fault_node_num == 2:
        fault_num = 0
    else:
        fault_num = 2
    # 获取故障节点id
    fault_id = disk.get_node_id_by_ip(n_ip=fault_ip)
    time.sleep(60)
    for i in range(run_times):
        check_core()
        err_type = random.randint(0, fault_num)
        # 进程故障分支
        if err_type == 0:
            fault_pro = random.choice(err_dict[0])
            fault_times = random.randint(1, 20)
            log.info("Step3: 故障次数：%d" % (fault_times,))
            for i in range(fault_times):
                log.info("将节点 %s 干掉: %s." % (fault_ip, fault_pro))
                cmd = ("ssh %s 'killall -9 %s'" % (fault_ip, fault_pro))
                commands.getstatusoutput(cmd)
                fault_time = random.randint(180, 300)
                time.sleep(fault_time)
        # 网络故障分支
        elif err_type == 1:
            # 随机选择断数据网还是业务网
            eth_type = random.choice(err_dict[1])
            if eth_type == 'data':
                err_eth, extra_ip = error.get_dataip_info(fault_id)
            else:
                err_eth, extra_ip = error.get_ioip_info(fault_id)
            # 网络故障次数
            err_times = random.randint(1, 10)
            log.info("Step3:选择断网次数：%d" % (err_times,))
            for j in range(err_times):
                # 随机选择，是全部断还是断一部分
                eth_err_type = random.randint(0, 2)
                # 如果随到的值是0，则断一部分；其他情况则全部断。两者比例：1:2，及全部断网的概率是断部分网络的两倍
                if eth_err_type == 0:
                    err_eth = random.choice(err_eth).split()
                log.info("选择网络：%s--%s，额外IP：%s" % (eth_type, err_eth, extra_ip))
                ReliableTest.run_down_net(extra_ip[0], err_eth)
                time_down = random.randint(35, 130)
                log.info("选择断网间隔：%d" % (time_down,))
                time.sleep(time_down)
                ReliableTest.run_up_net(extra_ip[0], err_eth)
                time_down = random.randint(35, 127)
                log.info("等待：%d秒后，注入下一次网络故障" % (time_down,))
                time.sleep(time_down)
        # 节点故障分支
        elif err_type == 2:
            fault_type = random.choice(err_dict[2])
            if fault_type == 'node':
                fault_times = random.randint(1, 10)
                log.info("Step3: 故障次数：%d" % (fault_times,))
                for i in range(fault_times):
                    log.info("将%s下电." % (fault_ip,))
                    fault_node_info = error.down_node(fault_ip)
                    time_down = random.randint(100, 300)
                    log.info("将节点 %s 宕机: %d秒." % (fault_ip, time_down))
                    time.sleep(time_down)
                    log.info("将%s上电." % (fault_ip,))
                    error.up_node(fault_node_info)
                    common.check_ip(fault_ip)
                    fault_time = random.randint(300, 500)
                    time.sleep(fault_time)
        # 磁盘故障分支
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
            fault_times = random.randint(1, 15)
            log.info("Step3: 故障次数：%d" % (fault_times,))
            for i in range(fault_times):
                for ip in remove_disk.keys():
                    node_remove_disk_time = random.randint(0, 20)
                    log.info("%d秒后，%s 开始拔盘" % (node_remove_disk_time, ip))
                    time.sleep(node_remove_disk_time)
                    for disk_id in remove_disk[ip]:
                        disk_remove_time = random.randint(0, 20)
                        log.info("当前节点，%d秒后，拔下一块盘" % (disk_remove_time,))
                        time.sleep(disk_remove_time)
                        ReliableTest.remove_disk(ip, disk_id, fault_type)
                for ip in remove_disk.keys():
                    for disk_id in remove_disk[ip]:
                        log.info("节点：%s,开始添加磁盘：%s" % (ip, disk_id))
                        ReliableTest.insert_disk(ip, disk_id, fault_type)
                        time.sleep(1)
        # 等待一段时间再注入下一次故障，是为了让故障节点重新提供服务，然后再注入下一次的故障
        wait_time = random.randint(150, 260)
        time.sleep(wait_time)


def vdb_jn(run_times):
    # 修改vdbench配置文件的参数值
    mix_R_Align = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[0])[:4],
                                   xfersize="(13k,100)",
                                   seekpct=0,
                                   rdpct=0)
    run_times = run_times / 6
    if run_times == 0:
        run_times = 1
    for i in range(run_times):
        log.info("Step4:在主机1上运行vdbench -f mix-R-Align.conf -jn.")
        osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jn")
        osan.vdb_check(c_ip=client_ips[0], time=100, oper="iops", output=deploy_ips[0])
        log.info("Step5:主机1上业务完成后，在主机1上执行vdbench -f mix-R-Align.conf -jro比较一致性.")
        osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jro")
        osan.vdb_check(c_ip=client_ips[0], time=100, oper="iops", output=deploy_ips[0])
        log.info("Step6:主机1上业务完成后，在主机1上执行vdbench -f mix-R-Align.conf -jro比较一致性.")
        osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jro")
        osan.vdb_check(c_ip=client_ips[0], time=100, oper="iops", output=deploy_ips[0])


def vdb_run(run_times):
    # 不带校验的vdbench测试
    mix_R = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[1])[:4],
                             xfersize="(3k,100)",
                             offset=2048,
                             seekpct=0,
                             rdpct=0)
    run_times = run_times / 2
    if run_times == 0:
        run_times = 1
    for i in range(run_times):
        log.info("Step4:在主机2上运行vdbench -f mix-R.conf.")
        osan.run_vdb(client_ips[1], mix_R, output=deploy_ips[0], time=2400)
        osan.vdb_check(c_ip=client_ips[1], time=100, oper="iops", output=deploy_ips[0])


def case(node_nums, run_times):
    for i in range(run_times):
        deploy_ips = get_config.get_env_ip_info(conf_file)
        disk.check_bad_obj()
        disk.check_lnode_state()
        time.sleep(120)
        prepare_x1000.x1000_test_prepare()
        test_threads = []
        for i in range(node_nums):
            fault_ip = random.choice(deploy_ips)
            deploy_ips.remove(fault_ip)
            test_threads.append(threading.Thread(target=up_down, args=(fault_ip, 1, i + 1)))
        test_threads.append(threading.Thread(target=vdb_jn, args=(1,)))
        test_threads.append(threading.Thread(target=vdb_run, args=(1,)))
        for test_thread in test_threads:
            test_thread.setDaemon(True)
            test_thread.start()
        for test_thread in test_threads:
            test_thread.join()


def main():
    # 获取参数
    node_nums, run_times = get_args()
    # 获取lun数据副本数和日志副本数
    min_lun_rep = disk.get_min_lun_replica(s_ip=deploy_ips[0])
    min_jnl_rep = disk.get_jnl_replica(s_ip=deploy_ips[0])
    # 如果lun副本数小于等于故障节点数，则将故障节点数重置为lun副本数减1
    if min_jnl_rep <= node_nums or min_lun_rep <= node_nums:
        node_nums = min_lun_rep - 1
    # 挂载lun
    login.login()
    # 开始测试
    case(node_nums, run_times)


if __name__ == '__main__':
    main()