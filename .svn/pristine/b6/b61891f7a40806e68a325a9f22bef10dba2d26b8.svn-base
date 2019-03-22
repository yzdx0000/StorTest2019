#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
:author: Liu he
:Description:
@file: 5-01-03-01.py
@time: 2018/11/01
测试项：
1、使用nwatch命令设置Lun的预读设置为自动；
2、主机端下发多流顺序读，部分命中的业务
3、业务过程中业务节点掉电
4、节点恢复正常后，数据修复完成，比较数据一致性
5、比较副本一致性
预期：
1、步骤1，命令设置成功
2、步骤2，业务正常完成，记录性能
3、步骤3，命令设置成功
4、步骤4，业务正常发起
5、步骤5，业务性能相对步骤2中记录的性能值显著提高
"""

# testlink case: 1000-34081
import os
import time
import json
import threading
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
node_ip1 = env_manage.get_inter_ids()[0]  # 业务节点IP
client_ip = env_cache.client_ips[0]

os_types = []
infos = []


def run_vdbench():
    lun_name = env_cache.osan.ls_scsi_dev(client_ip)
    vdb_file = env_cache.gen_vdb_xml(lun=lun_name, xfersize="4k", rdpct=100, thread=8, seekpct=0, rhpct=20)
    env_cache.com2_osan.run_vdb(client_ip=client_ip, vdb_xml=vdb_file, output="result_file", time=100)
    # env_cache.com2_osan.run_vdb(client_ip=client_ip, vdb_xml=vdb_file, output="result_file", time=60)
    value = env_cache.get_vdbech_res(c_ip=client_ip, output="result_file")
    log.info("get performance %s" % (value))
    return value


def down_node():
    time.sleep(30)
    log.info("the node will down")
    os_type = env_manage.get_os_type(node_ip1)
    info = env_manage.down_node(node_ip1, os_type, "init 0")
    os_types.append(os_type)
    infos.append(info)
    log.info("down node finished")


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
    log.info("step:6.主机端下发顺序多流读业务,运行中业务节点关机")
    threads = []
    threads.append(threading.Thread(target=run_vdbench))
    threads.append(threading.Thread(target=down_node))
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    log.info("step：7、业务节点开机。")
    env_manage.up_node(infos[0], os_types[0])
    env_cache.com_bk_os.get_os_status(node_ip1)
    env_cache.com_bd_disk.check_bad_obj()


def main():
    env_cache.check_cache_env()
    case()
    env_cache.check_cache_env()
    log.info("The case finished!!!")


if __name__ == '__main__':
    main()
