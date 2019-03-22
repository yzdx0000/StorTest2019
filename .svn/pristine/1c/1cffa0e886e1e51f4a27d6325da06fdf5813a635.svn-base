#!/usr/bin/python
#-*-coding:utf-8 -*
"""
:Date: 2018-08-13
:Author: diws
:Usage:
        1、在节点A上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
        2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
        3、在主机1上运行vdbench -f mix-R-align.conf -jn；在主机2上运行vdbench -f mix-S.conf;
        4、在步骤3中的业务运行过程中，将节点A掉电；
        5、在主机1上执行vdbench -f mix-R-align.conf -jro比较一致性
        6、节点A下点超时后上电；
        7、节点A上数据修复过程中，在主机1上执行vdbench -f mix-S-align.conf -jro比较一致性；
        8、节点A上数据修复完成后，再次在主机1上执行vdbench -f mix-S-align.conf -jro比较一致性。
        9、比较存储内部数据一致性。
:Changelog:
"""
# testlink case: 1000-32287
import os
import sys
import re
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

conf_file = common2.CONF_FILE    #配置文件路径
clean_env = common2.CLEAN_ENV
file_name = os.path.basename(__file__)
file_name = file_name[:-3]      #获取本脚本名，去掉.py后缀
error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=1, node_num=4)

deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
osan = common2.oSan()
disk = breakdown.disk()
vip = login.login()
#修改vdbench配置文件的参数值
seekpct1 = 70
seekpct2 = 0
rdpct1 = 50
rdpct2 = 20
offset = "2048"
xfersize1 = "(3k,100)"
xfersize2 = "(2k,100)"
lun1 = osan.ls_scsi_dev(client_ips[0])
lun2 = osan.ls_scsi_dev(client_ips[1])
mix_R_align = osan.gen_vdb_xml(lun=lun1, xfersize=xfersize1, seekpct=seekpct1,rdpct=rdpct1)
mix_S = osan.gen_vdb_xml(lun=lun2, xfersize=xfersize2, offset=offset, seekpct=seekpct2,rdpct=rdpct2)
fault_ip = osan.get_node_by_vip(vip=vip[0])
log.info("Get fault ip:%s" %(fault_ip))
def up_down(pipeout):
    time.sleep(100)
    log.info("Begin down node:%s." %(fault_ip))
    node_info = error.down_node(fault_ip=fault_ip)
    os.write(pipeout, node_info)
def vdb_jn(pipein):
    log.info("Run vdbench with jn.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0],jn_jro="jn")
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")
    log.info("Begin up node:%s." %(fault_ip))
    while True:
        line = os.read(pipein,32)
        if len(line) != 0:
            for vid in line.strip().split(','):
                vid = re.sub('\\r','',vid)
                log.info("Begin up node:%s." % (fault_ip))
                error.up_node(node_info=vid.strip())
            break
    log.info("Run vdbench with jro.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")
    for ip in deploy_ips:
        common.check_ip(ip)
        error.check_host(ip)
    log.info("Check bad obj repairing.")
    common.check_badjobnr()   #等待所有坏对象修复完成
    disk.check_bad_obj()
    log.info("Run vdbench with jro after the file repaired.")
    osan.run_vdb(client_ips[0], mix_R_align, output=deploy_ips[0], jn_jro="jro")
    # cmd = 'pscli --command=update_param --section=MGR --name=node_isolate_timeout --current=864000000'
    # osan.run_cmd(cmd,fault_node_ip=fault_ip)
    disk.multi_check_part_lun_uniform_by_ip()


def vdb_run():
    log.info("Run vdbench.")
    osan.run_vdb(client_ips[1], mix_S, output=deploy_ips[0])
def main():
    test_threads = []
    (pipein,pipeout) = os.pipe()
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
    for ip in vip:
        for cli in client_ips:
            pass
            #osan.iscsi_logout(cli,vip=ip)
if __name__ == '__main__':
    main()