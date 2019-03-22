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
import commands


"""初始化日志和全局变量"""
conf_file = get_config.CONFIG_FILE  # 配置文件路径
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)  # 初始化日志文件

log.info("---------------全局初始化操作-----------------")
node_ip = env_manage_lun_manage.node_ip
client_ip = env_manage_lun_manage.client_ips[0]
node_ip1 = env_manage_lun_manage.node_ip1
node_ip2 = env_manage_lun_manage.deploy_ips[1]
client_ip1 = env_manage_lun_manage.client_ips[0]
client_ip2 = env_manage_lun_manage.client_ips[1]
esxi_ip = env_manage_lun_manage.Esxi_ips
osan = Lun_managerTest.oSan()
deploy_ips = get_config.get_env_ip_info(conf_file)  # 获取集群IP列表
client_ips = get_config.get_allclient_ip()  # 获取客户端IP

"""读取存储池的容量"""
storage_pool_id = env_manage_lun_manage.osan.get_storage__type_id(s_ip=node_ip1, type="BLOCK")
az_id = env_manage_lun_manage.osan.get_access_zone_id(s_ip=node_ip1)[0]
storage_pool_size = env_manage_lun_manage.osan.get_option_single(s_ip=node_ip1,
                                                                 command='get_storage_pools', ids="ids",
                                                                 indexname="storage_pools",
                                                                 argv2="total_bytes",
                                                                 argv1=storage_pool_id)


def case():
    # env_manage.osan.update_param(s_ip=node_ip, section='MGR', name='min_meta_replica', current='1')  # 降级模式
    """env_manage.osan.create_node_pool(s_ip=node_ip, node_ids=cp('create_node_pool', 'node_ids'),
                          replica_num=cp("create_node_pool", "replica_num"),
                          stripe_width=cp('create_node_pool', 'stripe_width'),
                          disk_parity_num=cp("create_node_pool", "disk_parity_num"),
                          node_parity_num=cp("create_node_pool", "node_parity_num"),
                          name="nodepool1")
    env_manage.osan.startup(s_ip=node_ip)
    env_manage.osan.create_storage_pool(s_ip=node_ip, node_pool_ids='1', name='pool1')
    env_manage.osan.update_param(s_ip=node_ip, section='MGR', name='mgcd_auto_mount_flag', current='0')  # 解除自动挂载
    env_manage.osan.create_access_zone(s_ip=node_ip, node_id='1,2,3', name='accesszone1')
    env_manage.osan.create_subnet(s_ip=node_ip, access_zone_id='1', name='subnet1', sv_ip=cp("create_subnet", "sv_ip"),
                       mask=cp("create_subnet", "mask"),
                       gate_way=cp("create_subnet", "gate_way"),
                       network_interface=cp("create_subnet", "network_interface"))
    env_manage.osan.add_vip_address_pool(s_ip=node_ip, subnet_id='1', domain_name=cp("add_vip_address_pool", "domain_name"),
                              vip=cp("add_vip_address_pool", "vip"))
    env_manage.osan.enable_san(s_ip=node_ip, access_zone_id=1)"""

    hg_id = env_manage_lun_manage.osan.create_host_group(s_ip=node_ip, hg_name='myhostgroup1')

    h_id = env_manage_lun_manage.osan.add_host(s_ip=node_ip, h_name='host1', hg_id=hg_id)
    iqn = env_manage_lun_manage.osan.write_iqn(cli_ip=client_ip, iqn='iqn.20207014.com.sugon')
    env_manage_lun_manage.osan.add_initiator(s_ip=node_ip, h_id=h_id, iqn=iqn,
                                             alias='alias2020714')
    env_manage_lun_manage.osan.update_iscsid_conf(cli_ip=client_ip, CHAPTYPE='None', s_ip=client_ip)
    global lun_id
    for i in range(0, 1):
        lun_id = env_manage_lun_manage.osan.create_lun(s_ip=node_ip, total_bytes='1073741824', lun_type="THICK",
                                                       lun_name='LUN{}'.format(i),
                                                       stor_pool_id=2, acc_zone_id=1)
        log.info(lun_id)

        decorator_func.judge_target(
            env_manage_lun_manage.osan.get_option_single(s_ip=node_ip, command="get_luns", indexname="luns"
                                                         , argv2="name", ids="ids", argv1=lun_id),
            'LUN{}'.format(i))
    lun_ids = env_manage_lun_manage.osan.get_lun(s_ip=node_ip)
    for lun_id in lun_ids:
        lun_map_id = env_manage_lun_manage.osan.map_lun(s_ip=node_ip, lun_ids=lun_id, hg_id=hg_id)
        decorator_func.judge_target(
            env_manage_lun_manage.osan.get_option_single(s_ip=node_ip, command='get_lun_maps', indexname='lun_maps',
                                                         argv2="lun_map_state",
                                                         ids="ids", argv1=lun_map_id),
            'LUNMAP_READY')
    login.login()
    lun1 = env_manage_lun_manage.osan.ls_scsi_dev(client_ip=client_ip1)[0]
    get_lun_total = env_manage_lun_manage.break_down.get_lun_size(client_ip1, lun1)
    env_manage_lun_manage.assert_ins.assertEqual(get_lun_total, 1073741824)


# @decorator_func.tasklet(int(env_manage.cp('timeout', 'second')), maxretry=int(env_manage.cp('timeout', 'maxretry')))
def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    env_manage_lun_manage.clean()
    case()  # 用例步骤
    decorator_func.pass_flag()


if __name__ == '__main__':
    main()