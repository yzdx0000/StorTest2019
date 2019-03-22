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
# testlink case: 1000-34056
import os, sys, commands
import time
import utils_path
import Lun_managerTest
import common
import log
import error
import get_config
import login
from expand import error
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


def case(reboot=0):
    decorator_func.timer(15)
    if reboot:
        for ip in deploy_ips:
            cmd = ("ssh root@%s 'reboot'" % (ip))
            log.info(cmd)
            res, output = commands.getstatusoutput(cmd)
    for ip in deploy_ips:
        env_manage_lun_manage.Reliable_osan.get_os_status_1(ip)
    osan.uninstall_Xstor(node_ip1)
    tgt_res = 0
    for ip in deploy_ips:
        cmd = ("ssh root@%s 'lsmod |grep -w tgt'" % (ip,))
        res, output = commands.getstatusoutput(cmd)
        if res == 0:
            log.error("Sorry, I detect that there is tgt module on %s" % (ip,))
            tgt_res = 1
        if tgt_res == 1:
            log.error("Begin to restart these nodes.")
            cmd = ("ssh root@%s 'reboot'" % (ip))
            log.info(cmd)
            res, output = commands.getstatusoutput(cmd)
            env_manage_lun_manage.Reliable_osan.get_os_status_1(ip)
            osan.uninstall_Xstor(node_ip1)
    osan.install_Xstor(node_ip1, "/home/deploy/deploy_config_1.xml")
    osan.startup(node_ip1)

    xm1_file2 = error.modify_deploy_xml(dst_ip=node_ip2, ssd='false')

    new_node_id = env_manage_lun_manage.osan.add_nodes(node_ip1, xm1_file2)

    node_ids_list = env_manage_lun_manage.osan.get_nodes(deploy_ips[0])
    node_ids = ",".join('%s' % id for id in node_ids_list)
    node_pool_id1 = osan.create_node_pool(s_ip=node_ip1, node_ids=node_ids_list[0],
                                          replica_num=1,
                                          stripe_width=1,
                                          disk_parity_num=0,
                                          node_parity_num=0,
                                          name="nodepool1")

    node_pool_id2 = osan.create_node_pool(s_ip=node_ip1, node_ids=node_ids_list[1],
                                          replica_num=1,
                                          stripe_width=1,
                                          disk_parity_num=0,
                                          node_parity_num=0,
                                          name="nodepool2")

    osan.delete_node_pools(s_ip=node_ip2, node_pool_id=2)


def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    case()  # 用例步骤
    decorator_func.pass_flag()
    env_manage_lun_manage.init_env(reboot_node=1)  # 还原环境(还原到创建vip、enable_san)；用于lun管理用例的测试


if __name__ == '__main__':
    main()
