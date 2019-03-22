#!/usr/bin/python
# -*- encoding=utf8 -*-

import os
import sys
import commands
import time
import threading
from optparse import OptionParser

sys.path.append('/home/StorTest/test_cases/libs')

import daemon_pro
import get_config
import collect_log
import common2


conf_file = common2.CONF_FILE
deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
#获取集群内节点的IPMI IP 或者 vmid
m_info = daemon_pro.get_machine_info()
##############################################################################
# ##name  :      check_path_exist
# ##parameter:   path:文件路径
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 检查文件路径是否存在
##############################################################################
def run_tests():
    # 检查所有节点IP是否能连通，不通的就强制重启
    daemon_pro.restart_node(m_info)
    # 重启后检查所有节点网络
    for ip in deploy_ips:
        cmd = ("ssh %s 'hostname'" % (ip))
        rc, stdout = commands.getstatusoutput(cmd)
        while rc != 0:
            time.sleep(10)
            rc, stdout = commands.getstatusoutput(cmd)
    log_path = sys.argv[1]
    #下刷otrc信息
    for ip in deploy_ips:
        cmd = ("ssh root@%s '/home/parastor/tools/otrc -c'" % (ip))
        commands.getstatusoutput(cmd)
    #收集服务节点日志
    collect_log.collect_parastors(s_ip=deploy_ips, dst=log_path)
    #收集主机端日志
    collect_log.collect_clis(s_ip=client_ips, dst=log_path)
    #收集测试脚本日志
    collect_log.collect_script(dst=log_path)

if __name__ == '__main__':
    run_tests()
    print "The collect is finished!!!!!!!!!!!!!!!!!!"
