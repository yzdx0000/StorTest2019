#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
:author: Liu he
:Description:
@file: 5-01-02-06.py
@time: 2018/11/05
测试项：
1、使用nwatch命令设置Lun的预读设置为自动；
2、主机端下发同一地址区间的大块（1M）顺序写和小块（16K）顺序读
3、数据一致性比较
预期：
1、步骤1，命令设置成功
2、步骤2，业务正常完成
3、步骤3，数据一致
"""

# testlink case: 1000-34077
import os
import time
import json
import datetime
import utils_path
import Lun_managerTest
import common
import common2
import commands
import breakdown
import log
import env_cache
import get_config
import env_manage
import prepare_x1000

'''初始化'''
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
env_manage.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)

'''定义节点IP'''
node_ip1 = env_cache.deploy_ips[0]
client_ip1 = env_cache.client_ips[0]


def gen_vdb_xml(thread=8, offset=None, align=None, lun=None, xfersize=None, rdpct=None, seekpct=None, interval=1,
                rhpct=0):
    '''
    date    :   2018-05-17
    Description :   生成vdbench配置文件
    param   :  vdbench标准配置参数
    return  :   vdbench xml file path
    '''
    t1 = datetime.datetime.now()
    template_file = get_config.get_tools_path() + "/osan/template"  # 获取配置文件模板路径
    vdb_xml = get_config.get_tools_path() + "/osan/vdb_xml." + str(t1.microsecond)  # vdbench测试所用的文件
    sd_num = 1  # 初始化sd数量
    wd_num = 1
    threads = []
    # vdb_path = get_config.get_vdbench_path()        #获取vdbench路径
    if True == os.path.exists(vdb_xml):
        cmd = ("rm -rf %s" % (vdb_xml))
        commands.getstatusoutput(cmd)
    cmd = ("cp %s %s" % (template_file, vdb_xml))
    commands.getstatusoutput(cmd)
    if None == lun or len(lun) == 0:
        log.error("Found no scsi devices.")
        exit(1)
    if None != offset:
        cmd = ("sed -i '1s/$/,offset=%s/g' %s" % (str(offset), vdb_xml))  # 修改前偏移量
        log.info("Modify vdb_xml cmd %s" % (cmd))
        commands.getstatusoutput(cmd)
    if None != align:
        cmd = ("sed -i '1s/$/,align=%s/g' %s" % (str(align), vdb_xml))  # 修改后偏移量
        log.info("Modify vdb_xml cmd %s" % (cmd))
        commands.getstatusoutput(cmd)
    if None != rdpct:
        cmd = ("sed -i '2s/$/,rdpct=%s/g' %s" % (str(rdpct), vdb_xml))  # 修改读写占比
        log.info("Modify vdb_xml cmd %s" % (cmd))
        commands.getstatusoutput(cmd)
    if None != seekpct:
        cmd = ("sed -i '2s/$/,seekpct=%s/g' %s" % (str(seekpct), vdb_xml))  # 修改读写占比
        log.info("Modify vdb_xml cmd %s" % (cmd))
        commands.getstatusoutput(cmd)
        if None != xfersize:
            cmd = ("sed -i -r 's/,xfersizes.*?\)//g' %s" % (vdb_xml))  # 修改xferrsize
            log.info("Modify vdb_xml cmd %s" % (cmd))
        commands.getstatusoutput(cmd)
    for dev_name in lun:
        sd_xml = ("sd=sd%d,lun=%s" % (sd_num, dev_name))
        cmd = ("sed -i '%da\%s' %s" % (sd_num, sd_xml, vdb_xml))  # 插入rd
        commands.getstatusoutput(cmd)
    for xf in xfersize:
        wd_xml = ("wd=wd%d,sd=sd%d,rdpct=%s,xfersize=%s" % (wd_num, sd_num, xf[0], xf[1]))
        cmd = ("sed -i '$i\%s' %s" % (wd_xml, vdb_xml))  # 插入wd
        commands.getstatusoutput(cmd)
        wd_num = wd_num + 1
    cmd = ("sed -i -r 's/iorate=[0-9]+/iorate=max/g' %s" % (vdb_xml))  # 修改iorate为max
    commands.getstatusoutput(cmd)
    cmd = ("sed -i -r 's/thread.*?/threads=%s/g' %s" % (thread, vdb_xml))  # 修改每个wd的进程数
    commands.getstatusoutput(cmd)
    cmd = ("sed -i -r 's/interval.*?/interval=%s/g' %s" % (interval, vdb_xml))  # 修改每个wd的interval
    commands.getstatusoutput(cmd)
    log.info(vdb_xml)
    return vdb_xml


def case():
    log.info("step:1.创建逻辑卷,创建lun map")
    lun_id = env_manage.create_lun(size="99999999999", type="THIN")
    log.info("step:2.create lun map")
    env_manage.create_lun_map()
    log.info("step:3.主机iscsi映射")
    env_manage.create_iscsi_login()
    log.info("step:4.向所有lun 进行预埋数据")
    env_cache.pre_run_vdb()  # 进行预埋数据
    log.info("step:5.设置lun预读为自动")
    # env_cache.update_osan_params(1)
    env_cache.set_cache(id=lun_id, mode=1, size=0, s_ip=node_ip1, stype="dpc_lun_ra")
    log.info("step:6.主机端下发顺序读业务")
    lun_name = env_cache.osan.ls_scsi_dev(client_ip1)
    vdb_file = gen_vdb_xml(thread=8, lun=lun_name[:1], xfersize=(["0", "1M"], ["100", "16k"]), seekpct=0, interval=1,
                           rhpct=0)
    env_cache.com2_osan.run_vdb(client_ip=client_ip1, vdb_xml=vdb_file, output="result_file", time=100)
    # env_cache.com2_osan.run_vdb(client_ip=client_ip1, vdb_xml=vdb_file, output="result_file", time=300)
    value = env_cache.get_vdbech_res(c_ip=client_ip1, output="result_file")
    log.info("get performance %s" % (value))


def main():
    env_cache.check_cache_env()
    case()
    env_cache.check_cache_env()
    log.info("The case finished!!!")


if __name__ == '__main__':
    main()
