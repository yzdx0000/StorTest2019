#!/usr/bin/python
# -*-coding:utf-8 -*
"""
:Date: 2018-10-17
:Author: diws
:Description:
1、在节点A上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
3、在主机1上运行vdbench -f mix-R-Align.conf -jn；在主机2上运行vdbench -f mix-R.conf;
4、日志节点B下电，日志被接管时oRole主节点数据网闪断10秒；
5、业务执行完成后，在主机1上执行vdbench -f mix-R-Align.conf -jro比较一致性；
6、节点C数据网恢复；
7、节点B上电恢复后数据修复完成，比较存储内部数据一致性；
:Changerlog:
"""
# testlink case: 1000-32563
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
error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=4)

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
# 获取losid-nodeid-jnlstate对应关系
los_nid_state = disk.get_jnl_state()
log.info("Before inject error,the loss' state are{los_id:[node_id, los_state]}:%s" % (los_nid_state,))
# 获取所有los id
losids = los_nid_state.keys()
# 随机选择一个los
losid = random.choice(losids)
log.info("Select los is %d." % (losid,))
b_id = los_nid_state[losid][0]
b_ip = node.get_node_ip_by_id(b_id)


def up_down(pipein):
    c_id = error.get_orole_master_id()
    time.sleep(30)
    log.info("4、日志节点B %s下电" % (b_ip,))
    log.info("Begin shutdown node %s." % (b_ip,))
    m_b_info = error.down_node(fault_ip=b_ip)
    if str(c_id) == str(b_id):
        time.sleep(40)
        c_id = error.get_orole_master_id()
    c_ip = disk.get_node_ip_by_id(n_id=c_id)
    c_eths, c_extra = error.get_dataip_info(node_id=c_id)
    log.info("The major oRole's IP is %s." % (c_ip,))
    log.info("4、日志节点B下电，日志被接管时oRole主节点%s数据网闪断10秒；" % (c_ip,))
    log.info("Begin down data net %s through %s." % (c_eths, c_extra))
    ReliableTest.run_down_net(c_extra[0], c_eths)
    time.sleep(10)
    log.info("Begin up data net %s through %s." % (c_eths, c_extra))
    ReliableTest.run_up_net(c_extra[0], c_eths)
    while True:
        line = os.read(pipein, 32)
        if 'up' in line:
            break
    log.info("Begin startup node %s." % (b_ip,))
    error.up_node(node_info=m_b_info)
    error.check_host(b_ip)


def vdb_jn(pipeout):
    log.info("Step3:在主机1上运行vdbench -f mix-S-align.conf -jn.")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0], jn_jro="jn")
    log.info("5、业务执行完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性；")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0], jn_jro="jro")
    log.info("7、等待系统修复。")
    os.write(pipeout, "upnode")
    # 等待节点启动完成
    for ip in deploy_ips:
        common.check_ip(ip)
        error.check_host(ip)
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


if __name__ == '__main__':
    main()
