# -*- coding:utf-8 _*-
"""
@author: wangxiang
@file: 2-01-03-11.py
@time: 2018/07/11
"""
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

node_ids_list = env_manage_lun_manage.osan.get_nodes(node_ip1)
node_ids = ",".join('%s' % id for id in node_ids_list)

osan = Lun_managerTest.oSan()


def case():
    storage_pool_id = env_manage_lun_manage.osan.get_storage__type_id(s_ip=node_ip1, type="BLOCK")
    az_id = env_manage_lun_manage.osan.get_access_zone_id(s_ip=node_ip1)[0]
    hg_id = osan.create_host_group(s_ip=deploy_ips[0], hg_name='myhostgroup1')
    h_id = osan.add_host(s_ip=deploy_ips[0], h_name='host1', hg_id=hg_id)
    osan.add_initiator(s_ip=deploy_ips[0], h_id=h_id, iqn=cp("add_initiator", "iqn"),
                       alias=cp("add_initiator", "alias"))
    lun_id = osan.create_lun(s_ip=deploy_ips[0], lun_type="THIN",
                             lun_name='LUN1',
                             stor_pool_id=storage_pool_id, acc_zone_id=az_id)

    lun_map_id = osan.map_lun(s_ip=deploy_ips[0], lun_ids=lun_id, hg_id=hg_id)
    decorator_func.judge_target(
        osan.get_option_single(s_ip=deploy_ips[0], command='get_lun_maps', indexname='lun_maps',
                               argv2="lun_map_state",
                               ids="ids", argv1=lun_map_id),
        'LUNMAP_READY')
    msg = osan.delete_access_zone(s_ip=node_ip1, azid=az_id, need_judge=1)
    env_manage_lun_manage.assert_ins.assertNotequal(msg, '', 'judge failed')


def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    env_manage_lun_manage.clean()
    case()  # 用例步骤
    env_manage_lun_manage.init_env(reboot_node=1)  # 还原环境(还原到创建vip、enable_san)；用于lun管理用例的测试
    decorator_func.pass_flag()


if __name__ == '__main__':
    main()