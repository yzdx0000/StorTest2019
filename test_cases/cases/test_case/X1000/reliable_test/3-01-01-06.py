#!/usr/bin/python
#-*-coding:utf-8 -*
"""
:Date: 2018-08-13
:Author: diws
:Description:
            1、在节点A上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
            2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
            3、在主机1上运行vdbench -f mix-S-align.conf -jn；在主机2上运行vdbench -f mix-S.conf;
            4、在步骤3中的业务运行过程中，将节点A同组的日志节点B重启；
            5、节点B上电，数据修复中，在主机1上执行vdbench -f mix-s-align.conf -jro比较一致性；
            6、节点B数据修复完成，在主机1上执行vdbench -f mix-s-align.conf -jro比较一致性；
            7、比较存储内部数据一致性。
:Changelog:
"""
# testlink case: 1000-32290
import os,sys
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
import error
import breakdown
import re

# 配置文件路径
conf_file = common2.CONF_FILE
clean_env = common2.CLEAN_ENV
file_name = os.path.basename(__file__)
# 获取本脚本名，去掉.py后缀
file_name = file_name[:-3]
error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=1, node_num=4)

deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
osan = common2.oSan()
node = common.Node()
disk = breakdown.disk()
vip = login.login()
#修改vdbench配置文件的参数值
seekpct1 = 0
seekpct2 = 0
rdpct1 = 40 
rdpct2 = 70
offset = "2048"
xfersize1 = "(3k,100)"
xfersize2 = "(2k,100)"
lun1 = osan.ls_scsi_dev(client_ips[0])
lun2 = osan.ls_scsi_dev(client_ips[1])
mix_S_align = osan.gen_vdb_xml(lun=lun1, xfersize=xfersize1, seekpct=seekpct1, rdpct=rdpct1)
mix_S = osan.gen_vdb_xml(lun=lun2, xfersize=xfersize2, offset=offset, seekpct=seekpct2, rdpct=rdpct2)
vip_node_ip = osan.get_node_by_vip(vip=vip[0])
vip_node_id = node.get_node_id_by_ip(vip_node_ip)
jnl_gp_id = error.jnl_gp_id(vip=vip[0])
fault_ip = None
for gp_id in jnl_gp_id:
    if str(gp_id) == str(vip_node_id):
        continue
    else:
        fault_ip = error.jnl_gp_ip(gp_id)
        break
if fault_ip is None:
    log.error("Can not find the fault ip.")
    exit(1)
def up_down():
    time.sleep(300)
    log.info("Begin down node:%s." %(fault_ip))
    node_info = error.down_node(fault_ip=fault_ip)
    log.info("Begin up node:%s." %(fault_ip))
    error.up_node(node_info=node_info)
def vdb_jn():
    log.info("Run vdbench with jn.")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0],jn_jro="jn")
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0], jn_jro="jro")
    for ip in deploy_ips:
        common.check_ip(ip)
        error.check_host(ip)
    log.info("Check bad obj repairing.")
    # 等待所有坏对象修复完成
    common.check_badjobnr()
    disk.check_bad_obj()
    log.info("Run vdbench with jro after the file repaired.")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0], jn_jro="jro")
    disk.multi_check_part_lun_uniform_by_ip()


def vdb_run():
    log.info("Run vdbench.")
    osan.run_vdb(client_ips[1], mix_S, output=deploy_ips[0])
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
    for ip in vip:
        for cli in client_ips:
            pass
            #osan.iscsi_logout(cli,vip=ip)
if __name__ == '__main__':
    main()
