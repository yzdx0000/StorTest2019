# !/usr/bin/python
# -*-coding:utf-8 -*
"""
测试内容:删除含有lun的存储池

步骤:
1、配置节点池设置副本数为3
2、创建存储池，使用全部磁盘
3、创建访问区和对于的VIP地址池
4、创建一条LUN
5、删除存储池

检查项:
5、存储池删除失败
"""
# testlink case: 1000-34062
import os, sys
import commands
import random
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
    node_ids_list = osan.get_nodes(deploy_ips[0])
    node_ids = ",".join('%s' % id for id in node_ids_list)
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
    for i in range(2):
        log.info("will create storage :%s" % i)
        pool_id = ",".join('%s' % id for id in lists[i][0])
        cmd = (
                "ssh root@%s '/home/parastor/cli/pscli --command=create_storage_pool --name=stor%s --type=BLOCK --node_pool_ids=1 --disk_ids=%s '" % (
            deploy_ips[0], i, pool_id))
        log.info(cmd)
        commands.getstatusoutput(cmd)

    pool_id = ",".join('%s' % id for id in lists[2][0])
    cmd = (
            "ssh root@%s '/home/parastor/cli/pscli --command=create_storage_pool --name=stor1 --type=BLOCK --node_pool_ids=1 --disk_ids=%s '" % (
        deploy_ips[0], pool_id))
    log.info(cmd)
    res, final = commands.getstatusoutput(cmd)
    if res != 0:
        pass
    else:
        exit(1)


def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    env_manage_lun_manage.init_env(target="create_node_pool", reboot_node=1)
    case()  # 用例步骤
    decorator_func.pass_flag()
    env_manage_lun_manage.init_env(reboot_node=1) # 还原环境(还原到创建vip、enable_san)；用于lun管理用例的测试


if __name__ == '__main__':
    main()