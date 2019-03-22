# !/usr/bin/python
# -*-coding:utf-8 -*
"""
测试内容:逻辑卷添加到访问区

步骤:
1）配置访问区，配置节点池，存储池，创建主机组、添加主机，配置启动器
2）配置轮映射，将指定逻辑卷添加到指定访问区

检查项:
1）节点池，存储池，主机组，主机创建成功
2）逻辑卷可添加到指定访问区
"""
import os, sys
import time
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

Lun_osan = Lun_managerTest.oSan()

"""读取存储池的容量"""
storage_pool_id = env_manage_lun_manage.osan.get_storage__type_id(s_ip=node_ip1, type="BLOCK")
az_id = env_manage_lun_manage.osan.get_access_zone_id(s_ip=node_ip1)[0]
storage_pool_size = env_manage_lun_manage.osan.get_option_single(s_ip=node_ip1,
                                                                 command='get_storage_pools', ids="ids",
                                                                 indexname="storage_pools",
                                                                 argv2="total_bytes",
                                                                 argv1=storage_pool_id)


def iscsi_login():
    global min_seq_w1

    # 修改vdbench配置文件的参数值
    seekpct = 0  # 随机
    rdpct1 = 0  # 读写比例(0是全写)
    rdpct2 = 100
    xfersize1 = cp("vdbench", "unmix_xfersize1")
    lun1 = env_manage_lun_manage.osan.ls_scsi_dev(client_ip1)
    min_seq_w1 = env_manage_lun_manage.osan.gen_vdb_xml(maxdata='2G',
                                                        thread=cp("vdbench", "threads"), lun=lun1,
                                                        xfersize=xfersize1, seekpct=seekpct, rdpct=rdpct1)


def case():
    hg_id1 = Lun_osan.create_host_group(s_ip=node_ip1, hg_name="hg_1")
    h_id1 = Lun_osan.add_host(s_ip=node_ip1, h_name="h_1", hg_id=hg_id1)
    ini_id1 = Lun_osan.add_initiator(s_ip=node_ip1, h_id=h_id1, iqn=cp('add_initiator', 'iqn'),
                                     alias=cp('add_initiator', 'alias'))
    Lun_osan.update_iscsid_conf(cli_ip=client_ip1, CHAPTYPE='None', s_ip=client_ip1)
    for i in range(5):
        lun_id = Lun_osan.create_lun(s_ip=deploy_ips[0], lun_type="THIN",
                                     lun_name='LUN{}'.format(i),
                                     stor_pool_id=storage_pool_id, acc_zone_id=az_id, stripe_width=3)

    lun_ids = Lun_osan.get_lun(s_ip=node_ip1)

    for lun_id in lun_ids:
        Lun_osan.map_lun(s_ip=node_ip1, lun_ids=lun_id, hg_id=hg_id1)
    login.login()
    msg = env_manage_lun_manage.osan.ls_scsi_dev(client_ip=client_ip1)
    env_manage_lun_manage.assert_ins.assertEqual(len(msg), 5, 'xstor device is  not found!')
    iscsi_login()
    env_manage_lun_manage.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=min_seq_w1, output=node_ip1)


def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    # env_manage_lun_manage.rel_check_before_run(filename=file_name)  # 环境检测和准备
    env_manage_lun_manage.clean()
    case()  # 用例步骤
    decorator_func.pass_flag()


if __name__ == '__main__':
    main()
