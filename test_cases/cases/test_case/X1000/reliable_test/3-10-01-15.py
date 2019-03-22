#!/usr/bin/python
# -*- coding:utf-8 -*-
'''
Date:20180925
Author:diws
Description：
1、在节点A上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
3、在主机1上运行vdbench -f OLTP.conf -jn；在主机2上运行vdbench -f mix-S.conf;
4、在步骤3中的业务运行过程中，将日志节点A业务网断开；
5、数据网断开后业务切换到B节点，将B节点断电；
6、业务执行完成后，在主机1上执行vdbench -f OLTP.conf -jro比较一致性；
7、节点A和节点B恢复后数据修复完成，比较存储内部数据一致性；
'''
# testlink case: 1000-32756
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
error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=1, node_num=4)

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
if len(lun1) < 5:
    mix_R_align = osan.gen_vdb_xml(lun=lun1, xfersize=xfersize1, seekpct=seekpct1, rdpct=rdpct1)
else:
    mix_R_align = osan.vdb_write(sd="default")
    for i in range(0, len(lun1)):
        j = i+1
        if i == 0:
            mix_R_align = osan.vdb_write(sd="sd"+str(j), lun=lun1[i], wd="wd"+str(j), xfersize="8k", seekpct=100, rdpct=0, skew=20)
        elif i == 1:
            mix_R_align = osan.vdb_write(sd="sd"+str(j), lun=lun1[i], wd="wd"+str(j), xfersize="4k",seekpct=100, rdpct=0, skew=45)
        elif i == 2:
            mix_R_align = osan.vdb_write(sd="sd"+str(j), lun=lun1[i], wd="wd"+str(j), xfersize="8k",seekpct=0, rdpct=10, skew=15)
        elif i == 3:
            mix_R_align = osan.vdb_write(sd="sd"+str(j), lun=lun1[i], wd="wd"+str(j), xfersize="4k",seekpct=100, rdpct=0, skew=10)
        elif i == 4:
            mix_R_align = osan.vdb_write(sd="sd"+str(j), lun=lun1[i], wd="wd"+str(j), xfersize="4k",seekpct=0, rdpct=0, skew=10)
mix_R = osan.gen_vdb_xml(lun=lun2, xfersize=xfersize2, offset=offset, seekpct=seekpct2, rdpct=rdpct2)
# 获取节点A虚IP所在节点物理IP
nodes = osan.get_nodes(s_ip=deploy_ips[0])
use_jnl_ids = osan.get_same_jnl_group(1)
# free_jnl_ids = error.get_free_jnl_id()
# no_use_jnl_ds = list(set(map(str, nodes)).difference(set(use_jnl_ids)))
# no_use_jnl_ds = list(set(no_use_jnl_ds).difference(set(free_jnl_ids)))
# if len(free_jnl_ids) == 0:
#     free_jnl_ids = nodes
r_vip = random.choice(vip)
a_ip = osan.get_node_by_vip(vip=r_vip)
a_id = node.get_node_id_by_ip(a_ip)
a_eths, a_extra = error.get_ioip_info(node_id=a_id)
log.info("Got machine A's info: fault ip is : %s,extra ip is %s,device name is :%s" % (a_ip, a_extra, a_eths))


def up_down(pipeout):
    time.sleep(30)
    log.info("4、在步骤3中的业务运行过程中，将日志节点A业务网断开；")
    log.info("Begin down node:%s, eth %s through %s." % (a_ip, a_eths, a_extra))
    ReliableTest.run_down_net(a_extra[0], a_eths)
    common.check_ip(r_vip)
    b_ip = osan.get_node_by_vip(vip=r_vip)
    log.info("Got machine B's info: fault ip is : %s." % (b_ip, ))
    log.info("5、数据网断开后业务切换到B节点，将B节点断电；")
    log.info("Begin shutdown node:%s." % (b_ip,))
    minfo = error.down_node(fault_ip=b_ip)
    time.sleep(30)
    log.info("Begin startup node:%s." % (b_ip, ))
    error.up_node(node_info=minfo)
    time.sleep(30)
    log.info("Begin up node:%s, eth %s through %s." % (a_ip, a_eths, a_extra))
    ReliableTest.run_up_net(a_extra[0], a_eths)
    os.write(pipeout, "upnode")


def vdb_jn(pipein):
    log.info("3、在主机1上运行vdbench -f mix-S-Align.conf -jn；在主机2上运行vdbench -f mix-S.conf;")
    log.info("Run vdbench with jn on %s." % (client_ips[0]))
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jn")
    log.info("6、主机1上业务完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性；")
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")
    # 监控到匿名管道中写入数据后，退出循环，恢复环境
    while True:
        line = os.read(pipein, 32)
        if 'up' in line:
            break
    disk.check_bad_obj()
    log.info("7、节点A和节点B恢复后数据修复完成，比较存储内部数据一致性；")
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")


    disk.multi_check_part_lun_uniform_by_ip()


def vdb_run():
    log.info("Run vdbench on %s." % (client_ips[1]))
    osan.run_vdb(client_ips[1], mix_R, output=deploy_ips[0])


def main():
    test_threads = []
    (pipein, pipeout) = os.pipe()
    test_threads.append(threading.Thread(target=up_down, args=(pipeout,)))
    test_threads.append(threading.Thread(target=vdb_jn, args=(pipein,)))
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
