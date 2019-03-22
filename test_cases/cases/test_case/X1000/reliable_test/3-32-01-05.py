#!/usr/bin/python
# -*- coding:utf-8 -*-
'''
Date:20181022
Author:liuhe
Description：
1、在节点A上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
3、在主机1上运行vdbench -f mix-R-Align.conf -jn；在主机2上运行vdbench -f mix-R.conf;
4、在步骤3中的业务运行过程中，将A节点数据网故障，将节点BoPmgr进程异常；
5、主机1上业务完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性；
6、数据修复完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性；
7、业务节点超时后恢复，系统进行数据校验；
8、数据修复完成后，比较存储内部数据一致性
'''
# testlink case: 1000-33150
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
log_file_path = log.get_log_path(file_name)
log.init(log_file_path, True)
error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=1, node_num=4)

deploy_ips = get_config.get_env_ip_info(conf_file)  # 节点列表
client_ips = get_config.get_allclient_ip()  # 客户端列表
type_info = get_config.get_machine_type(conf_file)  # os 类型
if type_info == "vir":
    (esxi_ip, esxi_un, esxi_pw) = get_config.get_esxi(conf_file)
osan = common2.oSan()
node = common.Node()
disk = breakdown.disk()
os_break = breakdown.Os_Reliable()

vip = login.login()  # 返回已登录vip列表
svip = osan.get_svip(s_ip=deploy_ips[0])
# 修改vdbench配置文件的参数值
seekpct1 = 0
seekpct2 = 0
rdpct1 = 0
rdpct2 = 0
offset = "2048"
xfersize1 = "(3k,100)"
xfersize2 = "(2k,100)"
lun1 = osan.ls_scsi_dev(client_ips[0])
lun2 = osan.ls_scsi_dev(client_ips[1])
mix_R_align = osan.gen_vdb_xml(lun=lun1, xfersize=xfersize1, seekpct=seekpct1, rdpct=rdpct1)
mix_R = osan.gen_vdb_xml(lun=lun2, xfersize=xfersize2, offset=offset, seekpct=seekpct2, rdpct=rdpct2)
# 获取节点A虚IP所在节点物理IP
v_ip = random.choice(vip)
log.info("Got vip is %s." % (v_ip,))
a_ip = osan.get_node_by_vip(v_ip)  # vip所在节点管理ip
a_id = node.get_node_id_by_ip(a_ip)  # vip所在节点id
a_eths, a_extra = error.get_dataip_info(node_id=a_id)  # vip节点的数据网卡

# oRole主进程节点
master_role = os_break.get_master_oRole(deploy_ips[0])
# 如果主oROle进程和A节点重复那么断数据网oRole也会切换，
# 同一节点就使用断网实现进程和网络故障。如果不在统一节点上就分开执行
if a_ip == master_role:
    b_ip = a_ip
else:
    b_ip = master_role
log.info(
    "Got machine A's IP: %s, dev name is %s, extra IP is %s, and machine B's IP: %s." % (a_ip, a_eths, a_extra, b_ip))


def up_down(pipein):
    time.sleep(10)
    log.info("4、在步骤3中的业务运行过程中，将A节点数据网故障，将节点B oStor进程异常；")
    log.info("On node %s kill pmgr." % (b_ip,))
    os_break.kill_thread(b_ip, "oRole", "pmgr")  # 先杀进程，防止在一个节点上故障
    log.info("Begin down data net %s through %s ." % (a_eths, a_extra[0]))
    ReliableTest.run_down_net(a_extra[0], a_eths)
    # 监控到匿名管道中写入数据后，退出循环
    while True:
        line = os.read(pipein, 32)
        if 'up' in line:
            break
    log.info("Begin up data net %s through %s ." % (a_eths, a_extra[0]))
    ReliableTest.run_up_net(a_extra[0], a_eths)


def vdb_jn(pipeout):
    log.info("3、在主机1上运行vdbench -f mix-S-Align.conf -jn；在主机2上运行vdbench -f mix-S.conf;")
    log.info("Run vdbench with jn on %s." % (client_ips[0]))
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jn")
    log.info("5、业务执行完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性；")
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")
    os.write(pipeout, "upnet")
    disk.check_bad_obj()
    log.info("6、数据修复完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性；")
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")


    disk.multi_check_part_lun_uniform_by_ip()


def vdb_run():
    log.info("Run vdbench on %s." % (client_ips[1]))
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
