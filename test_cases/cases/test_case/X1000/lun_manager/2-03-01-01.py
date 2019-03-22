# -*- coding:utf-8 _*-
# Author:liuhe
# Date  :2018-10-24
"""
测试内容:逻辑卷写满前扩容

步骤:
1）在访问区配置中，每个节点取1块磁盘创建副本模式存储池，创建存储池pool1；
2）创建逻辑卷属性默认，选择pool1存储池，创建逻辑卷LUN1，设置容量为10GB；
3）将逻辑卷映射至主机
4）修改逻辑卷属性，将容量修改为100GB，提交，主机重新扫描逻辑卷容量有变化，并能写入100GB数据

检查项:
1）存储池创建成功
2）逻辑卷创建成功
3）修改成功，100GB数据写入成功
"""
import os, sys
import time
import utils_path
import Lun_managerTest
import env_manage_repair_test
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
osan = Lun_managerTest.oSan()
deploy_ips = get_config.get_env_ip_info(conf_file)  # 获取集群IP列表
client_ips = get_config.get_allclient_ip()  # 获取客户端IP

"""读取存储池的容量"""
storage_pool_id = env_manage_lun_manage.osan.get_storage__type_id(s_ip=node_ip1, type="BLOCK")
az_id = env_manage_lun_manage.osan.get_access_zone_id(s_ip=node_ip1)[0]

node_ip1 = env_manage_lun_manage.deploy_ips[0]

storage_pool_size = env_manage_lun_manage.osan.get_option_single(s_ip=node_ip1, command='get_storage_pools', ids="ids",
                                                                 indexname="storage_pools", argv2="total_bytes",
                                                                 argv1=storage_pool_id)


def get_iscsi_size_form_host():
    log.info("从主机端获取逻辑卷容量")
    lun1 = env_manage_lun_manage.osan.ls_scsi_dev(client_ip=client_ip1)[0]
    get_lun_total = env_manage_lun_manage.break_down.get_lun_size(client_ip1, lun1)
    log.info(get_lun_total)
    return get_lun_total


def case():
    global lun_size1
    global lun_id
    hg_id = env_manage_lun_manage.osan.create_host_group(s_ip=node_ip1, hg_name='myhostgroup1')
    h_id = env_manage_lun_manage.osan.add_host(s_ip=node_ip1, h_name='host1', hg_id=hg_id)
    ini_id = env_manage_lun_manage.osan.add_initiator(s_ip=node_ip1, h_id=h_id, iqn=cp("add_initiator", "iqn"),
                                                      alias=cp("add_initiator", "alias"))
    decorator_func.judge_target(
        env_manage_lun_manage.osan.get_option_single(s_ip=node_ip1, command="get_initiators", indexname="initiators",
                                                     argv2="auth_type", ids="ids", argv1=ini_id), "NONE")
    log.info("建逻辑卷属性默认，选择pool1存储池，创建逻辑卷LUN1")
    env_manage_lun_manage.osan.update_iscsid_conf(cli_ip=client_ip1, CHAPTYPE='None', s_ip=client_ip1)
    lun_id = env_manage_lun_manage.osan.create_lun(s_ip=node_ip1, total_bytes='1073741824', lun_type="THICK",
                                                   lun_name='LUN1', stor_pool_id=storage_pool_id, acc_zone_id=az_id)
    env_manage_lun_manage.osan.map_lun(s_ip=node_ip1, lun_ids=lun_id, hg_id=hg_id)

    login.login()
    lun_size1 = get_iscsi_size_form_host()

    log.info('修改逻辑卷属性，将容量修改为2GB')
    env_manage_lun_manage.osan.update_lun(s_ip=node_ip1, lun_id=lun_id, total_bytes="2147483648")
    log.info("重新挂载")
    osan.host_rescan(client_ip1)
    lun_size2 = get_iscsi_size_form_host()
    env_manage_lun_manage.assert_ins.assertEqual(lun_size2, 2147483648)



def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    env_manage_lun_manage.clean()
    case()  # 用例步骤


if __name__ == '__main__':
    main()