# !/usr/bin/python
# -*-coding:utf-8 -*
"""
测试内容:批量删除后再创建卷

步骤:
1）在访问区中配置100个逻辑卷和精简卷映射至主机端
2）在访问区中解除全部映射关系
4）批量删除逻辑卷和精简卷
5）重新创建100个逻辑卷和精简卷

检查项:
1）映射完成
2）解除映射全部完成
4）批量删除逻辑卷完成
5）100个卷重新创建成功
"""
import os, sys
import time
import random
import utils_path
import Lun_managerTest
import common
import log
import error
import get_config
import login
import error
import decorator_func
from get_config import config_parser as cp
import env_manage_lun_manage
from multiprocessing import Pool

"""初始化日志和全局变量"""
conf_file = get_config.CONFIG_FILE  # 配置文件路径
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)  # 初始化日志文件

log.info("---------------全局初始化操作-----------------")
node_ip1 = env_manage_lun_manage.node_ip1
node_ip2 = env_manage_lun_manage.deploy_ips[1]
client_ip1 = env_manage_lun_manage.client_ips[0]
client_ip2 = env_manage_lun_manage.client_ips[1]
esxi_ip = env_manage_lun_manage.Esxi_ips

deploy_ips = get_config.get_env_ip_info(conf_file)  # 获取集群IP列表
client_ips = get_config.get_allclient_ip()  # 获取客户端IP

osan = Lun_managerTest.oSan()

"""读取存储池的容量"""
storage_pool_id = env_manage_lun_manage.osan.get_storage__type_id(s_ip=node_ip1, type="BLOCK")
az_id = env_manage_lun_manage.osan.get_access_zone_id(s_ip=node_ip1)[0]
storage_pool_size = env_manage_lun_manage.osan.get_option_single(s_ip=node_ip1,
                                                                 command='get_storage_pools', ids="ids",
                                                                 indexname="storage_pools",
                                                                 argv2="total_bytes",
                                                                 argv1=storage_pool_id)

iqn_list = ['iqn.1994-05189.com.sugon', 'iqn.1994-05190.com.sugon', 'iqn.1994-05191.com.sugon',
            'iqn.1994-05192.com.sugon', 'iqn.1994-05193.com.sugon', 'iqn.1994-05194.com.sugon',
            'iqn.1994-05195.com.sugon', 'iqn.1994-05196.com.sugon', 'iqn.1994-05197.com.sugon',
            'iqn.1994-05198.com.sugon', ]


def case(arg=1):
    hg_id1 = osan.create_host_group(s_ip=node_ip1, hg_name="hg_1")
    hg_id2 = osan.create_host_group(s_ip=node_ip1, hg_name="hg_2")
    h_id1 = osan.add_host(s_ip=node_ip1, h_name="h_1", hg_id=hg_id1)
    h_id2 = osan.add_host(s_ip=node_ip1, h_name="h_2", hg_id=hg_id2)
    ini_id1 = osan.add_initiator(s_ip=node_ip1, h_id=h_id1, iqn=cp('add_initiator', 'iqn'),
                                 alias=cp('add_initiator', 'alias'))
    osan.update_iscsid_conf(cli_ip=client_ip1, CHAPTYPE='None', s_ip=client_ip1)
    ini_id2 = osan.add_initiator(s_ip=node_ip1, h_id=h_id2, iqn=cp('add_initiator', 'iqn1'),
                                 alias=cp('add_initiator', 'alias1'))
    for i in range(24):
        lun_id = osan.create_lun(s_ip=deploy_ips[0], lun_type="THIN",
                                 lun_name='LUN{}'.format(i),
                                 stor_pool_id=storage_pool_id, acc_zone_id=az_id, stripe_width=3)
        log.info(lun_id)
        decorator_func.judge_target(
            osan.get_option_single(s_ip=deploy_ips[0], command="get_luns", indexname="luns"
                                   , argv2="name", ids="ids", argv1=lun_id),
            'LUN{}'.format(i))

    lun = osan.get_lun(s_ip=node_ip1)
    for i in lun:
        if i % 2 == 0:
            osan.map_lun(s_ip=node_ip1, lun_ids=i, hg_id=hg_id1)
        else:
            osan.map_lun(s_ip=node_ip1, lun_ids=i, hg_id=hg_id2)

    login.login()
    msg1 = env_manage_lun_manage.osan.ls_scsi_dev(client_ip1)
    msg2 = env_manage_lun_manage.osan.ls_scsi_dev(client_ip2)
    env_manage_lun_manage.assert_ins.assertEqual(12, len(msg1))
    env_manage_lun_manage.assert_ins.assertEqual(12, len(msg2))


def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    env_manage_lun_manage.clean()
    case()
    decorator_func.pass_flag()


if __name__ == '__main__':
    main()
