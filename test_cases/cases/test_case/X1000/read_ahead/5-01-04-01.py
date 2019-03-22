#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
:author: Liu he
:Description:
@file: 5-01-04-01.py
@time: 2018/11/01
测试项：
1、使用nwatch命令设置Lun的预读设置为禁止；
2、主机端下压力并发小块(32k)写和顺序读的业务
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
# testlink case: 1000-34091
import os
import time
import json
import utils_path
import Lun_managerTest
import common
import common2
import commands
import breakdown
import log
import env_cache
import env_manage
import prepare_x1000

'''初始化'''
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
env_manage.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)

'''定义节点IP'''
node_ip1 = env_cache.deploy_ips[0]
client_ip = env_cache.client_ips[0]


def run_vdbench1():
    lun_name = env_cache.osan.ls_scsi_dev(client_ip)
    vdb_file = env_cache.gen_vdb_xml(lun=lun_name[:1], xfersize="32k", seekpct=0, rdpct=100, thread=8)
    log.info("vdbench 进行读业务:xfersize=32k")
    env_cache.com2_osan.run_vdb(client_ip=client_ip, vdb_xml=vdb_file, output="result_file", time=100)
    value = env_cache.get_vdbech_res(c_ip=client_ip, output="result_file")
    log.info("get performance %s" % (value))
    return value


def run_vdbench2():
    lun_name = env_cache.osan.ls_scsi_dev(client_ip)
    vdb_file = env_cache.gen_vdb_xml(lun=lun_name[1:2], xfersize="32k", seekpct=0, rdpct=100, thread=8)
    log.info("vdbench 进行读业务:xfersize=32k")
    env_cache.com2_osan.run_vdb(client_ip=client_ip, vdb_xml=vdb_file, output="result_file", time=100)
    value = env_cache.get_vdbech_res(c_ip=client_ip, output="result_file")
    log.info("get performance %s" % (value))
    return value


def case():
    log.info("step:1.创建逻辑卷,创建lun map")
    lun_id1 = env_manage.create_lun(size="99999999999", name="LUN1", type="THIN")
    lun_id2 = env_manage.create_lun(size="99999999999", name="LUN2", type="THIN")
    env_manage.create_lun_map()
    log.info("step:2.主机iscsi映射")
    env_manage.create_iscsi_login()
    log.info("step:3.向所有lun 进行预埋数据")
    env_cache.pre_run_vdb()  # 进行预埋数据
    log.info("step:4.设置lun预读为禁止")
    # env_cache.update_osan_params(0)
    env_cache.set_cache(id=lun_id1, mode=0, size=0, s_ip=node_ip1, stype="dpc_lun_ra")
    log.info("step:5.主机端下发顺序读业务")
    run_vdbench1()
    log.info("step:6.设置lun预读为自动")
    # env_cache.update_osan_params(1)
    env_cache.set_cache(id=lun_id2, mode=1, size=0, s_ip=node_ip1, stype="dpc_lun_ra")
    run_vdbench2()


def main():
    env_cache.check_cache_env()
    case()
    env_cache.check_cache_env()
    log.info("The case finished!!!")


if __name__ == '__main__':
    main()
