#!usr/bin/env python
# -*- coding:utf-8 -*-
"""
:author: Liu he
:Description:
@file: 5-01-02-03.py
@time: 2018/11/01
测试项：
1、使用nwatch命令设置Lun的预读设置为禁止；
2、主机端下发单流小块顺序读(16k/1M)业务到完成
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

# testlink case: 1000-34074
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
client_ip1 = env_cache.client_ips[0]


def run_vdb1():
    lun_name = env_cache.osan.ls_scsi_dev(client_ip=client_ip1)
    vdb_file = env_cache.gen_vdb_xml(lun=lun_name[:1], xfersize="(16k,50,1M,50)", rdpct="100", thread=8, rhpct=0,
                                     seekpct=0)
    res = env_cache.run_vdb(vdb_file=vdb_file, c_ip=client_ip1, x_size="4k")
    return res


def run_vdb2():
    lun_name = env_cache.osan.ls_scsi_dev(client_ip=client_ip1)
    vdb_file = env_cache.gen_vdb_xml(lun=lun_name[1:2], xfersize="(16k,50,1M,50)", rdpct="100", thread=8, rhpct=0,
                                     seekpct=0)
    res = env_cache.run_vdb(vdb_file=vdb_file, c_ip=client_ip1, x_size="4k")
    return res


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
    env_cache.set_cache(id=lun_id1, mode=0)
    # env_cache.update_osan_params(0)
    log.info("step:6.主机端下发顺序读业务")
    result1 = run_vdb1()
    log.info("step:7.设置lun预读为自动")
    env_cache.set_cache(id=lun_id2, mode=1)
    # env_cache.update_osan_params(1)
    result2 = run_vdb2()
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
