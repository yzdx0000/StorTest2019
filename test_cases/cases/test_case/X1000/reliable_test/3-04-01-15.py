#!/usr/bin/python
# -*-coding:utf-8 -*
"""
:Date: 2018-10-11
:Author: diws
:Description:
1、在节点A上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
3、在主机1上运行vdbench -f mix-S-Align.conf -jn；在主机2上运行vdbench -f mix-S.conf;
4、在步骤3中的业务运行过程中，将节点A下电，日志节点C接管节点A的日志；
5、节点A上电恢复后，日志迁移到节点A过程中时，oRole主被kill；
6、数据修复过程中在主机1上执行vdbench -f mix-R-Align.conf -jro比较一致性；
7、数据修复完成后，比较存储内部数据一致性。
:Changerlog:
"""
# testlink case: 1000-32553
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
                               xfersize="(4k,100)",
                               seekpct=0,
                               rdpct=0)
mix_S = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[1]),
                         xfersize="(3k,100)",
                         offset=2048,
                         seekpct=0,
                         rdpct=0)
# 获取losid-nodeid-jnlstate对应关系
los_nid_state = disk.get_jnl_state()
log.info("Before inject error,the loss' state are{los_id:[node_id, los_state]}:%s" % (los_nid_state,))
# 获取所有los id
losids = los_nid_state.keys()
# 随机选择一个los
losid = random.choice(losids)
log.info("Select los is %d." % (losid,))
a_id = los_nid_state[losid][0]
a_ip = node.get_node_ip_by_id(a_id)


def up_down():
    time.sleep(30)
    log.info("4、在步骤3中的业务运行过程中，将节点A %s下电，日志节点C接管节点A的日志；" % (a_ip,))
    log.info("Begin shutdown node %s." % (a_ip,))
    m_a_info = error.down_node(fault_ip=a_ip)
    # 获取新的losid-nodeid-jnlstate对应关系
    time.sleep(30)
    los_nid_state_new = disk.get_jnl_state()
    log.info("After inject error,the loss' state are{los_id:[node_id, los_state]}:%s" % (los_nid_state_new,))
    # 获取主oRole节点ID和IP
    c_id = error.get_orole_master_id(s_ip=deploy_ips[0])
    c_ip = disk.get_node_ip_by_id(removed_ip=a_ip, n_id=c_id)
    log.info("The major oRole's IP is %s." % (c_ip,))
    log.info("Begin startup node %s." % (a_ip,))
    error.up_node(node_info=m_a_info)
    error.check_host(a_ip)
    log.info("5、节点A上电恢复后，日志迁移到节点A过程中时，%s节点oRole主被kill；" % (c_ip,))
    ReliableTest.run_kill_process(c_ip, 'oRole')


def vdb_jn():
    log.info("Step3:在主机1上运行vdbench -f mix-S-align.conf -jn.")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0], jn_jro="jn")
    log.info("5、业务执行完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性；")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0], jn_jro="jro")
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
    test_threads.append(threading.Thread(target=up_down))
    test_threads.append(threading.Thread(target=vdb_jn))
    test_threads.append(threading.Thread(target=vdb_run))
    for test_thread in test_threads:
        test_thread.setDaemon(True)
        test_thread.start()
    for test_thread in test_threads:
        test_thread.join()


if __name__ == '__main__':
    main()
