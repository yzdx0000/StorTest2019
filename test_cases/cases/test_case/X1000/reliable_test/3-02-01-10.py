#!/usr/bin/python
# -*-coding:utf-8 -*
"""
:Date: 2018-08-06
:Author: diws
:Description:
            1、在节点A上创建12条LUN，其中LUN1-LUN6对应对齐大小块混合读写，LUN7-LUN12为非对齐大小块混合读写；
            2、使用2个主机，主机1映射LUN1-LUN6，主机2映射LUN7-LUN12；
            3、在主机1上运行vdbench -f mix-S-align.conf -jn；在主机2上运行vdbench -f mix-S.conf;
            4、将日志节点B下电；
            5、主机1上业务完成后，在主机1上执行vdbench mix-S-align.conf -jro比较一致性；
            6、节点B下电超时后上电，启动数据修复，数据修复中，在主机1上执行vdbench -f mix-S-align.conf -jro比较一致性；
            7、节点B数据修复完成，在主机1上执行vdbench -f mix-S-align.conf -jro比较一致性；
            8、比较存储内部数据一致性
:Changerlog:
"""
# testlink case: 1000-32479
import os, sys
import commands
import threading
import random
import time
import utils_path
import common2
import common
import log
import get_config
import ReliableTest
import login
import error
import breakdown

conf_file = common2.CONF_FILE  # 配置文件路径
osan = common2.oSan()
disk = breakdown.disk()
node = common.Node()
# 初始化日志文件
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
error.rel_check_before_run(file_name, jnl_rep=2, node_num=3, free_jnl_num=0, data_rep=2)

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
# 获取业务接入节点ID及其IP
interf_nodes_id = disk.get_interface_node(vips=vip)
# 随机选择一个业务接入节点ID并获取其IP
fault_node_id = random.choice(interf_nodes_id)
fault_node_ip = node.get_node_ip_by_id(fault_node_id)
log.info("Get fault ip:%s" % (fault_node_ip))


def up_down(pipeout):
    time.sleep(100)
    # 修改节点isolate参数，改为30s
    cmd = 'pscli --command=update_param --section=MGR --name=node_isolate_timeout --current=300000'
    rc, stdout = ReliableTest.run_pscli_cmd(cmd)
    if 0 != rc:
        log.error("Change node isolate time failed.")
        exit(1)
    log.info("Step4:将日志节点B下电 : %s." % (fault_node_ip))
    fault_node_info = error.down_node(fault_ip=fault_node_ip)
    os.write(pipeout, fault_node_info)
    time.sleep(360)
    cmd = 'pscli --command=update_param --section=MGR --name=node_isolate_timeout --current=3000000'
    rc, stdout = ReliableTest.run_pscli_cmd(cmd)
    if 0 != rc:
        log.error("Change node isolate time failed.")
        exit(1)


def vdb_jn(pipein):
    log.info("Step3:在主机1上运行vdbench -f mix-S-align.conf -jn.")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0], jn_jro="jn")
    log.info("Step5:主机1上业务完成后，在主机1上执行vdbench -f mix-S-align.conf -jro比较一致性.")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0], jn_jro="jro")
    while True:
        line = os.read(pipein, 16)
        if len(line) != 0:
            log.info("Step6:节点B上电 : %s." % (line))
            error.up_node(node_info=line.strip())
            break
        time.sleep(10)
    for ip in deploy_ips:
        common.check_ip(ip)
    log.info("Step6:主机1上业务完成后，在主机1上执行vdbench -f mix-R-align.conf -jro比较一致性.")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0], jn_jro="jro")
    log.info("Step7:节点B数据修复完成，在主机1上执行vdbench -f mix-R-align.conf -jro比较一致性；")
    osan.run_vdb(client_ips[0], mix_S_align, output=deploy_ips[0], jn_jro="jro")


    disk.multi_check_part_lun_uniform_by_ip()


def vdb_run():
    log.info("Step3:在主机2上运行vdbench -f mix-S.conf.")
    osan.run_vdb(client_ips[1], mix_S, output=deploy_ips[0], time=1200)


def case():
    (pipein, pipeout) = os.pipe()
    test_threads = []
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
    exit(-110)


def main():
    case()


if __name__ == '__main__':
    main()