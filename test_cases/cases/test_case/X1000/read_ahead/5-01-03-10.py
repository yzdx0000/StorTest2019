#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
:author: Liu he
:Description:
@file: 5-01-03-10.py
@time: 2018/11/05
测试项：
1、使用nwatch命令设置Lun的预读设置为自动；
2、主机端下发打洞写和顺序读的业务
3、业务过程中oSan进程故障
4、节点恢复正常后，数据修复完成，比较数据一致性
5、比较副本一致性
预期：
1、步骤1，命令设置成功
2、步骤2，业务正常完成
3、步骤3，数据一致
"""

# testlink case: 1000-34090
import os
import time
import json
import random
import threading
import datetime
import utils_path
import Lun_managerTest
import common
import common2
import commands
import breakdown
import ReliableTest
import log
import env_cache
import get_config
import env_manage
import prepare_x1000

'''初始化'''
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
# env_manage.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
log.init(log_file_path, True)

'''定义节点IP'''
node_ip1 = env_cache.deploy_ips[0]
client_ip = env_cache.client_ips[0]

os_types = []
infos = []


def run_vdbench():
    lun_name = env_cache.osan.ls_scsi_dev(client_ip)
    vdb_file = env_cache.analysis_xml_file(lun_name)
    log.info("vdbench 进行读业务:xfersize=512k")
    env_cache.run_vdb_hole(client_ip=client_ip, vdb_xml=vdb_file, output="result_file", time=100)
    log.info("will get vdbench result")
    value = env_cache.get_vdbech_res(c_ip=client_ip, output="result_file")
    log.info("get performance %s" % (value))


def pro_test():
    node_ip = random.random(env_manage.deploy_ips)
    time.sleep(30)
    log.info("will kill oSan process")
    ReliableTest.run_kill_process(node_ip=node_ip, process="oSan")


def case():
    log.info("step:1.创建逻辑卷,创建lun map")
    lun_id = env_manage.create_lun(size="99999999999", type="THIN")
    env_manage.create_lun_map()
    log.info("step:2.主机iscsi映射")
    env_manage.create_iscsi_login()
    log.info("step:3.向所有lun 进行预埋数据")
    env_cache.pre_run_vdb()  # 进行预埋数据
    log.info("step:4.设置lun预读为自动")
    # env_cache.update_osan_params(1)
    env_cache.set_cache(id=lun_id, mode=1, size=0, s_ip=node_ip1, stype="dpc_lun_ra")
    log.info("step:5.主机端下发同一地址区间的打洞写和顺序读")
    threads = []
    threads.append(threading.Thread(target=run_vdbench))
    threads.append(threading.Thread(target=pro_test))
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    log.info("step：6、检查坏对象。")
    env_cache.com_bd_disk.check_bad_obj()


def main():
    env_cache.check_cache_env()
    case()
    env_cache.check_cache_env()
    log.info("The case finished!!!")


if __name__ == '__main__':
    main()