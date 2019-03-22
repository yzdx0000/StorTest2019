#!/usr/bin/python
# -*-coding:utf-8 -*
"""
:Date: 2018-10-22
:Author: diws
:Description:
1、在节点A上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
3、在主机1上运行vdbench -f mix-R-Align.conf -jn；在主机2上运行vdbench -f mix-R.conf;
4、在步骤3中的业务运行过程中，将日志节点A断开一个业务网；
5、业务切到另一个业务网口上，再断开另一个业务网口。
6、前端业务挂住后，将主oPmgr进程kill掉
7、业务执行完成后，在主机1上执行vdbench -f mix-R-Align.conf -jro比较一致性；
8、节点A和节点B恢复后数据修复完成，比较存储内部数据一致性；
:Changerlog:
"""
# testlink case: 1000-32906
import os,sys
import commands
import threading
import random
import time
import re
import copy
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
error.rel_check_before_run(file_name, jnl_rep=2, free_jnl_num=0, node_num=3, data_rep=2)

# 获取集群节点信息
deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
vip = login.login()
# 修改vdbench配置文件的参数值
mix_S_align = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[0]),
                               xfersize="(1k,100)",
                               seekpct=0,
                               rdpct=0)
mix_S = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[1]),
                         xfersize="(3k,100)",
                         offset=2048,
                         seekpct=0,
                         rdpct=0)
fault_vip = random.choice(vip)
common.check_ip(fault_vip)
a_ip = osan.get_node_by_vip(fault_vip)
a_id = disk.get_node_id_by_ip(n_ip=a_ip)
a_eths, aextras = error.get_ioip_info(node_id=a_id)
tmp_eths = copy.deepcopy(a_eths)


def up_down(pipein):
    orole_id = error.get_orole_master_id()
    orole_ip = disk.get_node_ip_by_id(n_id=orole_id)
    time.sleep(30)
    a_eth = []
    tmp_eth = random.choice(a_eths)
    a_eth.append(tmp_eth)
    a_eths.remove(tmp_eth)
    log.info("4、在步骤3中的业务运行过程中，将日志节点A %s断开一个业务网%s；；" % (a_ip, a_eth))
    log.info("Begin down node %s io net %s through %s." % (a_ip, tmp_eth, aextras))
    ReliableTest.run_down_net(aextras[0], a_eth)
    log.info("Check vip: %s." % (fault_vip,))
    common.check_ip(fault_vip)
    if len(a_eths) != 0:
        log.info("5、业务切到另一个业务网口上，再断开另一个业务网口 %s。" % (a_eths,))
        log.info("Begin down node %s io net %s through %s." % (a_ip, a_eths, aextras))
        ReliableTest.run_down_net(aextras[0], a_eths)
    log.info("6、前端业务挂住后，将%s 主oPmgr进程kill掉；" % (orole_ip,))
    ReliableTest.run_kill_process(orole_ip, 'oRole')
    while True:
        line = os.read(pipein, 32)
        if 'up' in line:
            break
    log.info("Begin up node %s io net %s." % (a_ip, tmp_eths))
    ReliableTest.run_up_net(aextras[0], tmp_eths)


def vdb_jn(pipeout):
    log.info("Step3:在主机1上运行vdbench -f mix-S-align.conf -jn.")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0], jn_jro="jn")
    log.info("6、业务执行完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性；")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0], jn_jro="jro")
    # 通知故障注入线程，启动两个节点
    os.write(pipeout, "upnode")
    # 等待节点启动完成
    for ip in deploy_ips:
        common.check_ip(ip)
        error.check_host(ip)
    log.info("7、等待系统修复。")
    disk.check_bad_obj()
    log.info("7、修复完成后，校验内部数据一致性；")
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


if __name__ == '__main__':
    main()