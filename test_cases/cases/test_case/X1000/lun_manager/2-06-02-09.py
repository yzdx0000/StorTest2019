# -*- coding:utf-8 _*-
"""
@author: wangxiang
@file: 2-06-02-11.py
@time: 2018/07/06
"""
"""
测试内容:批量创建精简卷

步骤:
1）在访问区配置中，每个节点取1块磁盘创建副本模式存储池，共创建三个存储池pool1，pool2，pool3；
2）选择批量创建精简卷，选择存储池pool1，逻辑卷名称为LUN，设置个数为100；
3）提交后开始批量创建。

检查项:
1）存储池创建成功
4）逻辑卷创建成功，逻辑卷列表中可查看到该逻辑卷
"""
# testlink case: 1000-34058
import os, sys
import time
import commands
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
    node_ids_list = env_manage_lun_manage.osan.get_nodes(deploy_ips[0])
    node_ids = ",".join('%s' % id for id in node_ids_list)
    node_pool_id1 = osan.create_node_pool(s_ip=node_ip1, node_ids=node_ids_list[0],
                                          replica_num=1,
                                          stripe_width=3,
                                          disk_parity_num=0,
                                          node_parity_num=0,
                                          name="nodepool1")

    node_pool_id2 = osan.create_node_pool(s_ip=node_ip1, node_ids=node_ids_list[1],
                                          replica_num=1,
                                          stripe_width=3,
                                          disk_parity_num=0,
                                          node_parity_num=0,
                                          name="nodepool2")

    node_pool_id3 = osan.create_node_pool(s_ip=node_ip1, node_ids=node_ids_list[2],
                                          replica_num=1,
                                          stripe_width=3,
                                          disk_parity_num=0,
                                          node_parity_num=0,
                                          name="nodepool3")

    data_unuse_disks = []
    for i in node_ids_list:
        j = env_manage_lun_manage.break_down.get_assign_data_disk_id(s_ip=deploy_ips[0], node_id=i)
        data_unuse_disks.append(j)
    lists = [[] for a in range(3)]
    for m in range(3):
        new_list = []
        for list in data_unuse_disks:
            new_list.append(list[m])
        lists[m].append(new_list)

    log.info("集群中的所有未使用数据盘:{}".format(lists))
    for j in range(1, len(node_ids_list) + 1):
        i = 0
        log.info("will create storage :%s" % i)
        pool_id = ",".join('%s' % id for id in lists[i][0])
        cmd = (
                "ssh root@%s '/home/parastor/cli/pscli --command=create_storage_pool --name=stor%s --type=BLOCK --node_pool_ids=%s --disk_ids=%s '" % (
            deploy_ips[0], i, j, pool_id))
        log.info(cmd)
        commands.getstatusoutput(cmd)
        i += 1

    node_pool_ids = osan.get_option(s_ip=node_ip1, command="get_node_pools", indexname="node_pools", argv="id")
    log.info(node_pool_ids)
    if len(node_pool_ids) >= 2:
        node_pool_ids.remove(1)  # 列表删除共享节点池
        log.info(node_pool_ids)
        msg = env_manage_lun_manage.osan.delete_node_pools(s_ip=node_ip1, node_pool_id=node_pool_ids[0], needjudge=1)
        env_manage_lun_manage.assert_ins.assertNotequal(msg, '', 'judge failed')


def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    env_manage_lun_manage.init_env(target="init", reboot_node=1)
    case()  # 用例步骤
    decorator_func.pass_flag()
    env_manage_lun_manage.init_env(reboot_node=1) # 还原环境(还原到创建vip、enable_san)；用于lun管理用例的测试


if __name__ == '__main__':
    main()