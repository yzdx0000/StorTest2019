#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
:author: Liu he
:Description:
@file: 5-01-02-04.py
@time: 2018/11/01
测试项：
1、使用nwatch命令设置Lun的预读设置为禁止；
2、主机端下发多流顺序读和随机读(16k)业务到完成
3、使用nwatch命令设置Lun的预读设置为自动
4、再次发起同步骤2中的主机业务
5、检查业务性能
预期：
1、步骤1，命令设置成功
2、步骤2，业务正常完成，记录性能
3、步骤3，命令设置成功
4、步骤4，业务正常发起
5、步骤5，业务性能相对步骤2中记录的性能值显著提高
"""

# testlink case: 1000-34075
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
# log.init(log_file_path, True)
'''定义节点IP'''
node_ip1 = env_cache.deploy_ips[0]
client_ip = env_cache.client_ips[0]


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
    # if None != rdpct:
    #     cmd = ("sed -i '2s/$/,rdpct=%s//g' %s" % (str(rdpct), vdb_xml))  # 修改读写占比
    #     log.info("Modify vdb_xml cmd %s" % (cmd))
    #     commands.getstatusoutput(cmd)
    if None != xfersize:
        cmd = ("sed -i -r 's/xfersizes.*?\)/xfersize=%s/g' %s" % (xfersize, vdb_xml))  # 修改xferrsize
        log.info("Modify vdb_xml cmd %s" % (cmd))
        commands.getstatusoutput(cmd)
    for dev_name in lun:
        sd_xml = ("sd=sd%d,lun=%s" % (sd_num, dev_name))
        cmd = ("sed -i '%da\%s' %s" % (sd_num, sd_xml, vdb_xml))  # 插入rd
        commands.getstatusoutput(cmd)
    for rd in seekpct:
        wd_xml = ("wd=wd%d,sd=sd%d,rhpct=%s,rdpct=%s" % (wd_num, sd_num, rhpct, rd))
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


def run_vdbench1():
    """
    :description: 16k 块大小，
    :return:
    """
    lun_name = env_cache.osan.ls_scsi_dev(client_ip)
    vdb_file = gen_vdb_xml(thread=8, lun=lun_name[:1], xfersize="16k", rdpct="100", seekpct=["100", "0"], interval=1,
                           rhpct=0)
    env_cache.com2_osan.run_vdb(client_ip=client_ip, vdb_xml=vdb_file, output="result_file", time=100)
    value = env_cache.get_vdbech_res(c_ip=client_ip, output="result_file")
    log.info("get performance %s" % (value))
    return value


def run_vdbench2():
    """
    :description: 16k 块大小，
    :return:
    """
    lun_name = env_cache.osan.ls_scsi_dev(client_ip)
    vdb_file = gen_vdb_xml(thread=8, lun=lun_name[1:2], xfersize="16k", rdpct="100", seekpct=["100", "0"], interval=1,
                           rhpct=0)
    env_cache.com2_osan.run_vdb(client_ip=client_ip, vdb_xml=vdb_file, output="result_file", time=100)
    value = env_cache.get_vdbech_res(c_ip=client_ip, output="result_file")
    log.info("get performance %s" % (value))
    return value


def case():
    log.info("step:1.创建逻辑卷,创建lun map")
    lun_id1 = env_manage.create_lun(name="lun1", size="99999999999", type="THIN")
    lun_id2 = env_manage.create_lun(name="lun2", size="99999999999", type="THIN")
    log.info("step:2.create lun map")
    env_manage.create_lun_map()
    log.info("step:3.主机iscsi映射")
    env_manage.create_iscsi_login()
    log.info("step:4.向所有lun 进行预埋数据")
    env_cache.pre_run_vdb()  # 进行预埋数据
    log.info("step:5.设置lun预读为禁止")
    # env_cache.update_osan_params(0)
    env_cache.set_cache(id=lun_id1, mode=0, size=0, s_ip=node_ip1, stype="dpc_lun_ra")
    log.info("step:6.主机端下发顺序读业务")
    result1 = run_vdbench1()
    log.info("step:7.设置lun预读为自动")
    # env_cache.update_osan_params(1)
    env_cache.set_cache(id=lun_id2, mode=1, size=0, s_ip=node_ip1, stype="dpc_lun_ra")
    result2 = run_vdbench2()
    log.info("step:8.对比两次测试结果")
    if float(result2["bw"]) - float(result1["bw"]) > 0:
        log.info("\noff read head:%s\nauto read head:%s" % (result1, result2))
        log.info("Turn off cache detected performance degradation")
        return
    else:
        log.info("\nauto read head:%s\noff read head:%s" % (result1, result2))
        log.error("Turn off cache detected performance not degradation!!!!")
        os._exit(1)


def main():
    env_cache.check_cache_env()
    case()
    env_cache.check_cache_env()
    log.info("The case finished!!!")


if __name__ == '__main__':
    main()