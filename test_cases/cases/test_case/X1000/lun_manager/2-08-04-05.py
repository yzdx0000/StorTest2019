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
Lun_osan = Lun_managerTest.oSan()
deploy_ips = get_config.get_env_ip_info(conf_file)  # 获取集群IP列表
client_ips = get_config.get_allclient_ip()  # 获取客户端IP


def case():
    node_ids_list = env_manage_lun_manage.osan.get_nodes(node_ip1)
    node_ids = ",".join('%s' % id for id in node_ids_list)
    node_pool_id = Lun_osan.create_node_pool(s_ip=node_ip1, node_ids=node_ids,
                                             replica_num=1,
                                             stripe_width=1,
                                             disk_parity_num=0,
                                             node_parity_num=0,
                                             name="nodepool1")
    storage_pool_id = Lun_osan.create_storage_pool(s_ip=node_ip1, node_pool_ids=node_pool_id, name='pool1')
    env_manage_lun_manage.osan.startup(node_ip1)
    az_id1 = Lun_osan.create_access_zone(s_ip=deploy_ips[0], node_id=node_ids_list[0], name='accesszonetest1')
    az_id2 = Lun_osan.create_access_zone(s_ip=deploy_ips[0], node_id=node_ids_list[1], name='accesszonetest2')
    az_id3 = Lun_osan.create_access_zone(s_ip=deploy_ips[0], node_id=node_ids_list[2], name='accesszonetest3')

    sub_id1 = Lun_osan.create_subnet(s_ip=node_ip1, access_zone_id=az_id1, name='subnet1',
                                     sv_ip=cp("create_subnet", "sv_ip"),
                                     mask=cp("create_subnet", "mask"),
                                     vv_ip=cp("create_subnet", "vv_ip"),
                                     gate_way=cp("create_subnet", "gate_way"),
                                     network_interface=cp("create_subnet", "network_interface"))
    svip = Lun_osan.get_option_single(s_ip=node_ip1,
                                      command='get_subnets', ids="ids",
                                      indexname="subnets",
                                      argv2="svip",
                                      argv1=sub_id1)
    sub_id2 = Lun_osan.create_subnet(s_ip=node_ip2, access_zone_id=az_id2, name='subnet2',
                                     sv_ip=cp("create_subnet", "sv_ip2"),
                                     mask=cp("create_subnet", "mask"),
                                     vv_ip=cp("create_subnet", "vv_ip2"),
                                     gate_way=cp("create_subnet", "gate_way"),
                                     network_interface=cp("create_subnet", "network_interface"))
    svip2 = Lun_osan.get_option_single(s_ip=node_ip1,
                                       command='get_subnets', ids="ids",
                                       indexname="subnets",
                                       argv2="svip",
                                       argv1=sub_id2)
    new_vip1 = Lun_osan.check_ping_ip(svip, 3)
    Lun_osan.add_vip_address_pool(s_ip=node_ip1, subnet_id=sub_id1,
                                  domain_name="{}1".format(cp("add_vip_address_pool", "domain_name")),
                                  vip=new_vip1)
    new_vip2 = Lun_osan.check_ping_ip(svip2, 3)
    Lun_osan.add_vip_address_pool(s_ip=node_ip1, subnet_id=sub_id2,
                                  domain_name="{}2".format(cp("add_vip_address_pool", "domain_name")),
                                  vip=new_vip2)
    env_manage_lun_manage.osan.enable_san(node_ip1, az_id1)
    env_manage_lun_manage.osan.enable_san(node_ip1, az_id2)
    hg_id1 = Lun_osan.create_host_group(s_ip=node_ip1, hg_name="hg_1")
    hg_id2 = Lun_osan.create_host_group(s_ip=node_ip1, hg_name="hg_2")
    h_id1 = Lun_osan.add_host(s_ip=node_ip1, h_name="h_1", hg_id=hg_id1)
    h_id2 = Lun_osan.add_host(s_ip=node_ip1, h_name="h_2", hg_id=hg_id2)
    ini_id1 = Lun_osan.add_initiator(s_ip=node_ip1, h_id=h_id1, iqn=cp('add_initiator', 'iqn'),
                                     alias=cp('add_initiator', 'alias'))
    Lun_osan.update_iscsid_conf(cli_ip=client_ip1, CHAPTYPE='None', s_ip=client_ip1)
    ini_id2 = Lun_osan.add_initiator(s_ip=node_ip1, h_id=h_id2, iqn=cp('add_initiator', 'iqn1'),
                                     alias=cp('add_initiator', 'alias1'))

    lun_id = Lun_osan.create_lun(s_ip=deploy_ips[0], lun_type="THIN",
                                 lun_name='LUN1',
                                 stor_pool_id=storage_pool_id, acc_zone_id=az_id1, stripe_width=1, disk_parity_num=0,
                                 node_parity_num=0, replica_num=1)
    log.info(lun_id)
    decorator_func.judge_target(
        Lun_osan.get_option_single(s_ip=deploy_ips[0], command="get_luns", indexname="luns"
                                   , argv2="name", ids="ids", argv1=lun_id),
        'LUN1')

    Lun_osan.map_lun(s_ip=node_ip1, lun_ids=lun_id, hg_id=hg_id1)
    login.login()
    msg = env_manage_lun_manage.osan.ls_scsi_dev(client_ip=client_ip1)
    env_manage_lun_manage.assert_ins.assertEqual(len(msg), 1, 'xstor device is  not found!')

    env_manage_lun_manage.iscsi_logout()
    env_manage_lun_manage.clean_lun_map()

    Lun_osan.map_lun(s_ip=node_ip1, lun_ids=lun_id, hg_id=hg_id2)
    login.login()
    msg = env_manage_lun_manage.osan.ls_scsi_dev(client_ip=client_ip2)
    env_manage_lun_manage.assert_ins.assertEqual(len(msg), 1, 'xstor device is  not found!')

    targets = env_manage_lun_manage.osan.gen_dict_mul(s_ip=node_ip1, command="get_targets", arg1="nodeId",
                                                      arg2="id",
                                                      arg3="targets", target=2)
    env_manage_lun_manage.clean_lun_map()
    env_manage_lun_manage.osan.lun_map_by_target(node_ip1, lun_ids=lun_id, target_id=targets[0], hp_id=hg_id2)


def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    # env_manage_lun_manage.rel_check_before_run(filename=file_name)  # 环境检测和准备
    env_manage_lun_manage.init_env(target="init", reboot_node=1)
    case()  # 用例步骤
    env_manage_lun_manage.init_env(reboot_node=1)  # 还原环境(还原到创建vip、enable_san)；用于lun管理用例的测试
    decorator_func.pass_flag()


if __name__ == '__main__':
    main()
