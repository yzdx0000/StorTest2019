# !/usr/bin/python
# -*-coding:utf-8 -*
"""
测试内容:修改SVIP和名称

步骤:
1、创建节点池
2、创建存储池，使用全部磁盘
3、创建访问区
4、创建SVIP，填写zone id，svip name，IP地址，掩码，网关，网卡名称，提交后可成功创建
5、修改该业务子网的SVIP和名称

检查项:
1、节点池创建成功
2、存储池创建成功
3、访问区创建成功
4、成功创建SVIP
5、成功修改SVIP和子网名称
"""
# testlink case: 1000-34173
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

osan = Lun_managerTest.oSan()


def case():
    storage_pool_id = env_manage_lun_manage.osan.get_storage__type_id(s_ip=node_ip1, type="BLOCK")
    az_id = env_manage_lun_manage.osan.get_access_zone_id(s_ip=node_ip1)[0]
    sub_id1 = osan.create_subnet(s_ip=node_ip1, access_zone_id=az_id, name='subnet1',
                                 sv_ip=cp("create_subnet", "sv_ip"),
                                 mask=cp("create_subnet", "mask"),
                                 vv_ip=cp("create_subnet", "vv_ip"),
                                 gate_way=cp("create_subnet", "gate_way"),
                                 network_interface=cp("create_subnet", "network_interface"))
    svip = osan.get_option_single(s_ip=node_ip1,
                                  command='get_subnets', ids="ids",
                                  indexname="subnets",
                                  argv2="svip",
                                  argv1=sub_id1)
    new_ip=osan.check_ping_ip(svip,1)
    osan.update_subnet(s_ip=node_ip1,svip=new_ip,subnet_id=sub_id1,subnet_name="update_subnet1")

    new_vip = osan.check_ping_ip(new_ip, 6)
    vip_id = osan.add_vip_address_pool(s_ip=node_ip1, subnet_id=sub_id1,
                                       domain_name=cp("add_vip_address_pool", "domain_name"),
                                       vip=new_vip)
    hg_id = osan.create_host_group(s_ip=deploy_ips[0], hg_name='myhostgroup1')
    h_id = osan.add_host(s_ip=deploy_ips[0], h_name='host1', hg_id=hg_id)
    osan.add_initiator(s_ip=deploy_ips[0], h_id=h_id, iqn=cp("add_initiator", "iqn"),
                       alias=cp("add_initiator", "alias"))
    lun_id = osan.create_lun(s_ip=deploy_ips[0], total_bytes='1024000', lun_type="THIN",
                                 lun_name='LUN1',
                                 stor_pool_id=storage_pool_id, acc_zone_id=az_id)
    lun_ids = osan.get_lun(s_ip=deploy_ips[0])
    for lun_id in lun_ids:
        lun_map_id = osan.map_lun(s_ip=deploy_ips[0], lun_ids=lun_id, hg_id=hg_id)
        decorator_func.judge_target(
            osan.get_option_single(s_ip=deploy_ips[0], command='get_lun_maps', indexname='lun_maps',
                                   argv2="lun_map_state",
                                   ids="ids", argv1=lun_map_id),
            'LUNMAP_READY')
    env_manage_lun_manage.create_iscsi_login(subnet_id=sub_id1)
    msg=osan.ls_scsi_dev(client_ip1)
    env_manage_lun_manage.assert_ins.assertEqual(len(msg), 1, 'xstor device is  not found!')




def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    env_manage_lun_manage.clean(target="subnet")
    # env_manage_lun_manage.init_env(target="create_node_pool",reboot_node=1)
    case()  # 用例步骤
    decorator_func.pass_flag()
    env_manage_lun_manage.init_env(reboot_node=1) # 还原环境(还原到创建vip、enable_san)；用于lun管理用例的测试


if __name__ == '__main__':
    main()