#!/usr/bin/python
#-*-coding:utf-8 -*
"""
:Date: 2018-11-21
:Author: wuyq
:Description:
1、创建VIP地址池，配置4倍节点个数的VIP，IP切换均衡策略使用连接数，自动均衡策略设置为自动
2、查看自动均衡策略设置
3、创建LUN和对应的映射，并在主机端登录并下发读写业务
4、故障节点A的数据网
5、5分钟后恢复
6、等待自动均衡完成后，查看均衡情况和业务情况

:Changerlog:
"""

import os
import sys
import commands
import threading
import random
import time
import utils_path
import common
import common2
import Lun_managerTest
import log
import get_config
import env_manage_lun_manage
from get_config import config_parser as cp
import error
import breakdown

# 重新部署系统
conf_file = common2.CONF_FILE   # 配置文件路径
osan = Lun_managerTest.oSan()
reliable = breakdown.Os_Reliable()
disk = breakdown.disk()
node = common.Node()
com2 = common2.oSan()

file_name = os.path.basename(__file__)
file_name = file_name[:-3]      # 获取本脚本名，去掉.py后缀
# error.rel_check_before_run(file_name, jnl_rep=3, node_num=3)
log_file_path = log.get_log_path(file_name)
log.init(log_file_path, True)
# 重新部署系统
env_manage_lun_manage.xstor_install()

# 获取集群节点信息
deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
sever_ips = deploy_ips[:]

mix_R_Align = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[0]),
                               xfersize="(4k,80,16k,20)",
                               seekpct=0,
                               rdpct=0)
mix_R = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[1]),
                         xfersize="(4k,80,16k,20)",
                         offset=2048,
                         seekpct=0,
                         rdpct=0)

def case():
    log.info("Step1:创建VIP地址池,配置4倍节点个数的VIP.VIP均衡策略:连接数,VIP均衡开关:关闭.")
    subnet_id = osan.get_subnet_id(deploy_ips[0])
    vip = cp('add_vip_address_pool', 'vips')
    osan.add_vip_address_pool(s_ip=deploy_ips[0], subnet_id=subnet_id[0], domain_name='sugon.com', vip=vip,
                              ip_failover_policy='IF_CONNECTION_COUNT', rebalance_policy='RB_AUTOMATIC')
    osan.enable_san(s_ip=deploy_ips[0], access_zone_id=1)

    time.sleep(30)
    log.info("Step2:查看自动均衡策略设置是否符合预期.")
    rebalance_policy, ip_failover_policy = osan.get_vip_policy(deploy_ips[0])
    if rebalance_policy == 'RB_AUTOMATIC' and ip_failover_policy == 'IF_CONNECTION_COUNT':
        log.info("自动均衡策略设置成功.")
    else:
        log.error("自动均衡策略设置失败.\n期望:均衡策略->连接数;均衡开关->关闭\n实际:均衡策略->%s;均衡开关->%s."
                  % (ip_failover_policy, rebalance_policy))
        os._exit(1)

    time.sleep(10)
    log.info("Step3:创建12条Lun,并平均映射给两个主机,下发读写业务")
    log.info("a.创建12条Lun")
    for count in range(12):
        lun_name = 'lun' + str(count + 1)
        osan.create_lun(s_ip=deploy_ips[0], lun_name=lun_name, stor_pool_id=2, acc_zone_id=1)
    log.info("b.创建两个主机组,然后分别添加一个主机")
    osan.create_host_group(deploy_ips[0], 'host_group1')
    osan.create_host_group(deploy_ips[0], 'host_group2')
    osan.add_host(deploy_ips[0], 'host1', 1)
    osan.add_host(deploy_ips[0], 'host2', 2)

    log.info("c.将ID为1-6的lun映射给host1,ID为7-12的Lun映射给host2")
    for count in range(6):
        osan.map_lun(deploy_ips[0], count+1, 1)
    for count in range(6):
        osan.map_lun(deploy_ips[0], count+7, 2)

    log.info("d.添加两个启动器,并修改主机启动器名称配置文件")
    iqn = cp('add_initiator', 'iqn')
    iqn1 = cp('add_initiator', 'iqn1')
    alias = cp('add_initiator', 'alias')
    alias1 = cp('add_initiator', 'alias1')
    osan.add_initiator(s_ip=deploy_ips[0], h_id=1, iqn=iqn, alias=alias)
    osan.add_initiator(s_ip=deploy_ips[0], h_id=1, iqn=iqn1, alias=alias1)
    osan.write_iqn(client_ips[0], iqn)
    osan.write_iqn(client_ips[1], iqn1)

    log.info("e.发现iscsi启动器,并且执行login操作")
    vips = osan.get_vips_by_pool(deploy_ips[0], 1)
    for vip in vips:
        for client in client_ips:
            target = osan.discover_scsi(client, vip)
            osan.iscsi_login(client, target)
    time.sleep(10)

def up_down():
    time.sleep(100)
    log.info("Step4:故障一个带业务节点的所有数据网卡,5min后恢复")
    fault_ip = random.choice(sever_ips)
    fault_id = breakdown.disk().get_node_id_by_ip(n_ip=fault_ip)
    data_eth_list = error.get_data_eth(fault_id)
    log.info("将故障节点的所有数据网故障,节点:%s" % fault_ip)
    threads = []
    for eth in data_eth_list:
        threads.append(threading.Thread(target=reliable.network_test, args=(fault_ip, eth, 'down')))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    log.info("5min后将该节点的数据网恢复")
    time.sleep(300)
    for eth in data_eth_list:
        reliable.network_test(fault_ip, eth, 'up')

    time.sleep(100)
    log.info("Step5:等待自动均衡完成后,查看此时各均衡情况")
    vips = [len(osan.get_vips_by_node(x, 1)) for x in deploy_ips]
    if set(vips) == 1 and vips[0] == 4:
        log.info("VIP自动均衡成功!每个节点VIP数量为4")
    else:
        log.error("异常!VIP自动均衡失败,数量分布情况:%s" % ','.join(map(str, vips)))
        os._exit(1)

def vdb_jn():
    mix_R_Align = com2.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[0]),
                                   xfersize="(4k,80,16k,20)",
                                   seekpct=0,
                                   rdpct=0)
    log.info("Step4:在主机1上运行vdbench -f mix-R-Align.conf -jn.")
    com2.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jn", time=900)
    log.info("Step5:主机1上业务完成后，在主机1上执行vdbench -f mix-R-Align.conf -jro比较一致性.")
    com2.run_vdb(client_ips[0], mix_R_Align, output=deploy_ips[0], jn_jro="jro")

def vdb_run():
    mix_R = com2.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[1]),
                             xfersize="(4k,80,16k,20)",
                             offset=2048,
                             seekpct=0,
                             rdpct=0)
    log.info("Step4:在主机2上运行vdbench -f mix-R.conf.")
    com2.run_vdb(client_ips[1], mix_R, output=deploy_ips[0], time=1000)

def main():
    case()
    test_threads = []
    test_threads.append(threading.Thread(target=up_down))
    test_threads.append(threading.Thread(target=vdb_jn))
    test_threads.append(threading.Thread(target=vdb_run))
    for test_thread in test_threads:
        test_thread.start()
    for test_thread in test_threads:
        test_thread.join()
    for c_ip in client_ips:
        com2.vdb_check(c_ip=c_ip, time=100, oper="iops", output=deploy_ips[0])

if __name__ == '__main__':
    main()