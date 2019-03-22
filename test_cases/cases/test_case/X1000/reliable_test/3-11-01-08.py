#!/usr/bin/python
#-*-coding:utf-8 -*
"""
:Date: 2019-03-15
:Author: wuyq
:Description:
1、在节点A上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
3、在主机1上运行vdbench -f mix-S-Align.conf -jn；在主机2上运行vdbench -f mix-S.conf;
4、在步骤3中的业务运行过程中，将业务节点网配置成bond，将节点A业务网线拔出；
5、检查VIP接管节点，将接管节点关机
6、业务执行完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性；
7、节点A和节点B恢复后数据修复完成，比较存储内部数据一致性；
:Changerlog:
"""
import os
import threading
import random
import time
import utils_path
import breakdown
import common2
import common
import log
import get_config
import login
import error

# 参数实例化
conf_file = common2.CONF_FILE
osan = common2.oSan()
reliable = breakdown.Os_Reliable()
disk = breakdown.disk()
node = common.Node()
# 初始化日志文件
file_name = os.path.basename(__file__)
file_name = file_name[:-3]
error.rel_check_before_run(file_name, jnl_rep=3, node_num=4, data_rep=3)
# 获取集群节点信息
deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
vip = login.login()

# 修改vdbench配置文件的参数值
mix_R_Align = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[0]),
                               xfersize="(4k,80,16k,20)",
                               seekpct=0,
                               rdpct=0)
mix_R = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[1]),
                         xfersize="(4k,80,16k,20)",
                         offset=2048,
                         seekpct=0,
                         rdpct=0)

# 获取带有VIP的集群业务节点
io_node_ids = reliable.get_business_nodes()
test_node_id = random.choice(io_node_ids)
test_node_ip = node.get_node_ip_by_id(test_node_id)
io_eth_list = error.get_io_eth(test_node_id)
vip_dict = reliable.get_vips_with_node()
event1 = threading.Event()
event2 = threading.Event()

def up_down():
    time.sleep(100)
    log.info("Step2:在业务过程中,将节点 %s 的业务网卡配置为bond." % test_node_ip)
    reliable.bond_conf(test_node_ip, io_eth_list, 'bond0')
    time.sleep(100)
    log.info("Step3:在bond配置完成后,将业务节点 %s 的一个业务网卡断开." % test_node_ip)
    test_eth = random.choice(io_eth_list)
    reliable.network_test(test_node_ip, test_eth, 'down')
    time.sleep(100)
    vip_dict_fault = reliable.get_vips_with_node()
    vip_dict_fault.pop(test_node_ip)

    take_node = random.choice(vip_dict_fault.keys())
    break_flag = False
    for node_ip in vip_dict_fault.keys():
        if break_flag is True:
            break
        for ip in vip_dict[test_node_ip]:
            if ip in vip_dict_fault[node_ip]:
                take_node = node_ip
                break_flag = True
                break
    log.info("Step4:检查到VIP接管节点是 %s,并将其下电." % take_node)
    vm_info = error.down_node(take_node)
    time.sleep(100)
    log.info("Step5:将业务节点 %s 的业务网恢复." % test_node_ip)
    reliable.network_test(test_node_ip, test_eth, 'up')
    log.info("Step6:将VIP接管节点 %s 重新上电." % take_node)
    error.up_node(vm_info)
    log.info("Step7:检查VIP接管节点 %s 已恢复正常." % take_node)
    reliable.get_os_status_1(take_node)

    event1.wait()
    event2.wait()
    log.info("Step9:等待业务完成后,检查数据修复完成")
    disk.check_bad_obj()
    log.info("Step10:将bond配置取消,恢复业务节点 %s 至初始状态." % test_node_ip)
    reliable.bond_conf(test_node_ip, io_eth_list, 'bond0', switch=0)
    log.info("Step11:检查集群内部数据一致性.")
    disk.multi_check_part_lun_uniform_by_ip()

def vdb_jn():
    log.info("Step1:在主机1上运行vdbench -f mix-R-Align.conf -jn.")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jn", time=1200)
    log.info("Step7:主机1上业务完成后，在主机1上执行vdbench -f mix-R-Align.conf -jro比较一致性.")
    osan.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jro")
    event1.set()

def vdb_run():
    log.info("Step1:在主机2上运行vdbench -f mix-R.conf.")
    osan.run_vdb(client_ips[1], mix_R, output=deploy_ips[0], time=1200)
    event2.set()

def case():
    test_threads = []
    test_threads.append(threading.Thread(target=up_down))
    test_threads.append(threading.Thread(target=vdb_jn))
    test_threads.append(threading.Thread(target=vdb_run))
    for test_thread in test_threads:
        test_thread.start()
    for test_thread in test_threads:
        test_thread.join()
    for c_ip in client_ips:
        osan.vdb_check(c_ip=c_ip, time=100, oper="iops", output=deploy_ips[0])

if __name__ == '__main__':
    case()
