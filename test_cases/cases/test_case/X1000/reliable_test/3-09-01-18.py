#!/usr/bin/python
# -*- coding:utf-8 -*-
'''
Date:20180913
Author:diws
Description：
1、在节点A（los节点）中创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
2、使用2个主机与节点A建立iscsi连接，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
3、在主机1上运行vdbench -f mix-S-Align.conf -jn；在主机2上运行vdbench -f mix-S.conf;
4、在步骤3中的业务运行过程中，将节点A/B/C两个数据网口断开10秒后全部恢复；
5、主机1上业务完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性；
6、网络恢复后，数据开始重建，重建完成后在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性；
7、比较存储内部数据一致性。
'''
# testlink case: 1000-32733
import os
import sys
import utils_path
import common2
import common
import log
import get_config
import ReliableTest
import threading
import login
import time
import commands
import random
import error
import breakdown

conf_file = common2.CONF_FILE
clean_env = common2.CLEAN_ENV
file_name = os.path.basename(__file__)
file_name = file_name[:-3]
error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=1, node_num=5)

deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
type_info = get_config.get_machine_type(conf_file)
if type_info == "vir":
    (esxi_ip, esxi_un, esxi_pw) = get_config.get_esxi(conf_file)
osan = common2.oSan()
node = common.Node()
disk = breakdown.disk()
vip = login.login()
svip = osan.get_svip(s_ip=deploy_ips[0])
# 修改vdbench配置文件的参数值
seekpct1 = 45
seekpct2 = 58
rdpct1 = 30
rdpct2 = 45
offset = "2048"
xfersize1 = "(3k,100)"
xfersize2 = "(2k,100)"
lun1 = osan.ls_scsi_dev(client_ips[0])
lun2 = osan.ls_scsi_dev(client_ips[1])
mix_R_align = osan.gen_vdb_xml(lun=lun1, xfersize=xfersize1, seekpct=seekpct1, rdpct=rdpct1)
mix_R = osan.gen_vdb_xml(lun=lun2, xfersize=xfersize2, offset=offset, seekpct=seekpct2, rdpct=rdpct2)
# 获取节点A虚IP所在节点物理IP
nodes = osan.get_nodes(s_ip=deploy_ips[0])
use_jnl_ids = osan.get_same_jnl_group(1)
use_jnl_ids = use_jnl_ids[:3]
fault_info = {}
for jid in use_jnl_ids:
    jip = node.get_node_ip_by_id(jid)
    j_eths, j_extra = error.get_dataip_info(node_id=jid)
    fault_info[jip] = [j_eths, j_extra]
log.info("Got machine info: %s" % (fault_info, ))


def up_down(pipein):
    # 监控到匿名管道中写入数据后，退出循环，恢复环境
    while True:
        line = os.read(pipein, 32)
        if 'up' in line:
            break
    log.info("4、在步骤3中的业务运行过程中，将节点A/B/C两个数据网口断开10秒后全部恢复；")
    for f_key in fault_info.keys():
        log.info("Begin down node:%s, eth %s through %s." % (f_key, fault_info[f_key][0], fault_info[f_key][1]))
        ReliableTest.run_down_net(fault_info[f_key][1], fault_info[f_key][0])
    time.sleep(10)
    log.info("5、恢复环境；")
    for f_key in fault_info.keys():
        log.info("Begin up node:%s, eth %s through %s." % (f_key, fault_info[f_key][0], fault_info[f_key][1]))
        ReliableTest.run_up_net(fault_info[f_key][1], fault_info[f_key][0])


def vdb_jn(pipeout):
    log.info("3、在主机1上运行vdbench -f mix-S-Align.conf -jn；在主机2上运行vdbench -f mix-S.conf;")
    log.info("Run vdbench with jn on %s." % (client_ips[0]))
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jn")
    log.info("5、主机1上业务完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性；")
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")
    os.write(pipeout, "upnet")
    disk.check_bad_obj()
    log.info("6、数据修复到free节点，修复完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性")
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")


    disk.multi_check_part_lun_uniform_by_ip()


def vdb_run():
    log.info("3、Run vdbench on %s." % (client_ips[1]))
    osan.run_vdb(client_ips[1], mix_R, output=deploy_ips[0])


def main():
    (pipein, pipeout) = os.pipe()
    test_threads = []
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
