#!/usr/bin/python
# -*- coding:utf-8 -*-
'''
Date:20180918
Author:diws
Description：
1、在节点A（los节点）中创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
2、使用2个主机与节点A建立iscsi连接，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
3、在主机1上运行vdbench -f mix-S-Align.conf -jn；在主机2上运行vdbench -f mix-S.conf;
4、在步骤3中的业务运行过程中，将节点B业务网断开；
5、等待上报故障后，将业务节点A业务网断开
5、主机1上业务完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性；
6、比较存储内部数据一致性。
'''
# testlink case: 1000-32737
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
import breakdown
import time
import commands
import random
import error

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
disk = breakdown.disk()
node = common.Node()
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
a_ip = osan.get_node_by_vip(vip=vip[0])
# 虚IP所在节点物理ID
a_id = node.get_node_id_by_ip(a_ip)
a_eths, a_extra = error.get_ioip_info(node_id=a_id)
# 主机 B 网络信息
for ip in vip:
    b_ip = osan.get_node_by_vip(vip=ip)
    if b_ip != a_ip:
        break
while b_ip == a_ip:
    b_ip = error.get_fault_ip()
b_id = node.get_node_id_by_ip(b_ip)
b_eths, b_extra = error.get_ioip_info(node_id=b_id)
log.info("Got machine A's info: fault ip is : %s,extra ip is %s,device name is :%s" % (a_ip, a_extra, a_eths))
log.info("Got machine B's info: fault ip is : %s,extra ip is %s,device name is :%s" % (b_ip, b_extra, b_eths))


def up_down():
    time.sleep(10)
    log.info("4、在步骤3中的业务运行过程中，将节点B业务网断开；")
    log.info("Begin down node:%s, eth %s through %s." % (b_ip, b_eths, b_extra))
    ReliableTest.run_down_net(b_extra[0], b_eths)
    time.sleep(120)
    log.info("5、等待上报故障后，将业务节点A业务网断开")
    log.info("Begin down node:%s, eth %s through %s." % (a_ip, a_eths, a_extra))
    ReliableTest.run_down_net(a_extra[0], a_eths)


def vdb_jn():
    log.info("3、在主机1上运行vdbench -f mix-S-Align.conf -jn；在主机2上运行vdbench -f mix-S.conf;")
    log.info("Run vdbench with jn on %s." % (client_ips[0]))
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jn")
    log.info("Begin up node:%s, eth %s through %s." % (a_ip, a_eths, a_extra))
    ReliableTest.run_up_net(a_extra[0], a_eths)
    log.info("Begin up node:%s, eth %s through %s." % (b_ip, b_eths, b_extra))
    ReliableTest.run_up_net(b_extra[0], b_eths)
    log.info("6、主机1上业务完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性；")
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")


    disk.multi_check_part_lun_uniform_by_ip()


def vdb_run():
    log.info("Run vdbench on %s." % (client_ips[1]))
    osan.run_vdb(client_ips[1], mix_R, output=deploy_ips[0])


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
    for c_ip in client_ips:
        osan.vdb_check(c_ip=c_ip, time=100, oper="iops", output=deploy_ips[0])


if __name__ == '__main__':
    main()