#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Date:20181220
Author:Diws
:Description:
将集群空间写至90%
"""
import threading
import utils_path
import common2
import get_config
import error
import log
import login

osan = common2.oSan()
# 初始化全局变量
conf_file = common2.CONF_FILE
# 获取集群节点管理IP
deploy_ips = get_config.get_env_ip_info(conf_file)
# 获取客户端节点管理IP
client_ips = get_config.get_allclient_ip()
# login
vip = login.login()
# 生成vdb配置文件
cluster_cap = int(error.get_cluster_cap()*0.45)


def vdb_jn():
    """
    :Description:执行带校验的vdb
    :return:
    """
    mix_1 = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[0]),
                             xfersize="(8k,100)",
                             seekpct=0,
                             rdpct=0,
                             max_range=None,
                             maxdata=cluster_cap)
    log.info("2、在主机1上运行vdbench -f mix-S-Align.conf -jn.")
    osan.run_vdb(client_ips[0], mix_1, output=deploy_ips[0], time=1600)


def vdb_run():
    """
    :Description:执行不带校验的vdb
    :return:
    """
    mix_2 = osan.gen_vdb_xml(lun=osan.ls_scsi_dev(client_ips[1]),
                             xfersize="(8k,100)",
                             offset=0,
                             seekpct=0,
                             rdpct=0,
                             max_range=None,
                             maxdata=cluster_cap)
    log.info("2、在主机2上运行vdbench -f mix-S.conf.")
    osan.run_vdb(client_ips[1], mix_2, output=deploy_ips[0], time=1600)


def preare_vdb():
    test_threads = []
    test_threads.append(threading.Thread(target=vdb_jn))
    test_threads.append(threading.Thread(target=vdb_run))
    for test_thread in test_threads:
        test_thread.setDaemon(True)
        test_thread.start()
    for test_thread in test_threads:
        test_thread.join()


if __name__ == '__main__':
    preare_vdb()