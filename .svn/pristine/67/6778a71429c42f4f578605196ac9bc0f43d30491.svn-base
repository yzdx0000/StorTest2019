#!/usr/bin/python
#-*-coding:utf-8 -*
"""
:Date: 2019-01-02
:Author: wuyq
:Description:
1、创建N条LUN；
2、使用X个主机，分别映射每个节点上的LUN；
3、X个主机运行进行顺序读;
4、vdbench使用xfersize=1m,rdpct=100,seekpct=0,iorate=curve,curve=(5-100,5),warmup=60,elapsed=3600；
5、检查业务运行。"
:Changerlog:
"""
import os
import sys
import commands
import time
import ConfigParser
import utils_path
import common2
import common
import log
import get_config
import login
import breakdown

# 参数实例化
conf_file = common2.CONF_FILE
osan = common2.oSan()
reliable = breakdown.Os_Reliable()
disk = breakdown.disk()
node = common.Node()
conf = ConfigParser.ConfigParser()

# 初始化日志文件
file_name = os.path.basename(__file__)
file_name = file_name[:-3]
# error.rel_check_before_run(file_name, jnl_rep=1, node_num=1)
log_file_path = log.get_log_path(file_name)
log.init(log_file_path, True)

# 获取集群节点信息
deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
vip = login.login()
cur_dir = os.path.dirname(os.path.abspath(__file__))
vdb_conf = cur_dir + '/vdb.conf'

# 修改vdbench配置文件的参数值
log.info("Step1:Generate the vdbench stress test configuration file.")
conf.read(vdb_conf)
threads_conf = int(conf.get('stress_conf', 'threads'))
lun_nums_conf = int(conf.get('stress_conf', 'lun_nums'))
stress_io = osan.gen_stress_vdb(xfersize='(256k,40,513k,20,1024k,20,2047k,10,4096k,10)',
                                rdpct=100,
                                seekpct=0,
                                threads=threads_conf,
                                lun_nums=lun_nums_conf,
                                model='iorate=curve,curve=(5-100,5)')
output = 'stress_io'
cmd = ('cat %s' % stress_io)
result = commands.getoutput(cmd)
log.info('The vdbench stress IO model show:\n%s' % result)

def case():
    log.info("Step2:Run vdbench stress test in host 1.host IP:%s" % client_ips[0])
    osan.run_vdb(client_ips[0], stress_io, output=output, time=3600, whether_change_xml='N')
    time.sleep(10)
    log.info("Step3:View the vdbench execution results.host IP:%s" % client_ips[0])
    osan.view_vdb_result(client_ips[0], output=(output+'_nor'))
    time.sleep(10)
    log.info("Step4:Check the vdbench result whether disconnected 60 times.")
    osan.vdb_check(c_ip=client_ips[0], time=60, oper="iops", output=output)

if __name__ == '__main__':
    case()
