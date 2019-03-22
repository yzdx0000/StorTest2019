# !/usr/bin/python
# -*-coding:utf-8 -*
"""
测试内容:访问区业务子网和网卡数规格

步骤:
1）配置节点池设置副本数为3
2）创建存储池，使用全部磁盘
3）创建一个访问区
4）创建4个业务子网（配置4个网卡），并配置对应的VIP地址池

检查项:
4）业务子网创建成功，IP地址池创建成功
"""
# testlink case: 1000-34161
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
from repair_test import env_manage_repair_test
from expand import error
import ReliableTest

"""初始化日志和全局变量"""
conf_file = get_config.CONFIG_FILE  # 配置文件路径
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)  # 初始化日志文件

log.info("---------------全局初始化操作-----------------")
node_ip1 = env_manage_lun_manage.node_ip1
node_ip2 = env_manage_lun_manage.deploy_ips[1]
node_ip3 = env_manage_lun_manage.deploy_ips[2]
client_ip1 = env_manage_lun_manage.client_ips[0]
client_ip2 = env_manage_lun_manage.client_ips[1]
esxi_ip = env_manage_lun_manage.Esxi_ips

deploy_ips = get_config.get_env_ip_info(conf_file)  # 获取集群IP列表
client_ips = get_config.get_allclient_ip()  # 获取客户端IP
node_ids_list = env_manage_lun_manage.osan.get_nodes(node_ip1)
node_ids = ",".join('%s' % id for id in node_ids_list)
# 获取可扩容节点IP
expand_ips = get_config.get_expand_ip_info()

osan = Lun_managerTest.oSan()

log.info("获取机器类型，若为虚拟机则获取vm_id")
type_info = env_manage_repair_test.get_os_type(node_ip2)


vm_ids = None
if type_info != "phy":
    vm_ids = env_manage_repair_test.Reliable_osan.vm_id(esxi_ip=esxi_ip, u_name=cp("esxi", "esxi_user"),
                                                        pw=cp("esxi", "esxi_passwd"),
                                                        node_ip=node_ip2)
else:
    vm_ids = ReliableTest.get_ipmi_ip(node_ip2)


def generate_xml():
    """
    :Description:生成配置文件
    :return: 配置文件路径
    """
    if len(expand_ips) == 0:
        log.error("Sorry, I can't find any nodes to expand, please check /home/StorTest/conf/x1000_test_config.xml")
        os._exit(1)
    log.info("生成部署用的配置文件，带共享盘的那种.")
    xml_path = error.modify_deploy_xml(dst_ip=expand_ips[0])
    return xml_path


def iscsi_login():
    global min_seq_w
    global min_seq_r
    login.login()

    # 修改vdbench配置文件的参数值
    seekpct = 0  # 随机
    rdpct1 = 0  # 读写比例(0是全写)
    rdpct2 = 100
    xfersize1 = cp("vdbench", "unmix_xfersize1")
    lun1 = env_manage_lun_manage.osan.ls_scsi_dev(client_ip1)
    min_seq_w = env_manage_lun_manage.osan.gen_vdb_xml(maxdata="2G",
                                                       thread=cp("vdbench", "threads"), lun=lun1,
                                                       xfersize=xfersize1, seekpct=seekpct, rdpct=rdpct1)
    min_seq_r = env_manage_lun_manage.osan.gen_vdb_xml(maxdata="2G",
                                                       thread=cp("vdbench", "threads"), lun=lun1,
                                                       xfersize=xfersize1, seekpct=seekpct, rdpct=rdpct2)


def step1(arg=1):
    global az_id
    storage_pool_id = env_manage_lun_manage.osan.get_storage__type_id(s_ip=node_ip1, type="BLOCK")
    az_id = env_manage_lun_manage.osan.get_access_zone_id(s_ip=node_ip1)[0]
    hg_id = env_manage_lun_manage.osan.create_host_group(s_ip=node_ip1, hg_name='myhostgroup1')
    h_id = env_manage_lun_manage.osan.add_host(s_ip=node_ip1, h_name='host1', hg_id=hg_id)
    ini_id = env_manage_lun_manage.osan.add_initiator(s_ip=node_ip1, h_id=h_id, iqn=cp("add_initiator", "iqn"),
                                                      alias=cp("add_initiator", "alias"))

    env_manage_lun_manage.osan.update_iscsid_conf(cli_ip=client_ip1, CHAPTYPE='None', s_ip=client_ip1)
    for i in range(1):
        lun_id = env_manage_lun_manage.osan.create_lun(s_ip=node_ip1, lun_type="THIN",
                                                       lun_name='lun_{}'.format(i),
                                                       stor_pool_id=storage_pool_id, acc_zone_id=az_id)
        lun_map_id = env_manage_lun_manage.osan.map_lun(s_ip=node_ip1, lun_ids=lun_id, hg_id=hg_id)

    iscsi_login()


def run_vdb(arg=2):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))

    env_manage_lun_manage.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=min_seq_w, output=node_ip1)


def add_node(arg=3):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    decorator_func.timer(int(cp("wait_time", "remove_disk")))

    xml_file = generate_xml()
    new_node_id = env_manage_lun_manage.osan.add_nodes(node_ip1, xml_file)
    new_node_id = env_manage_repair_test.Reliable_osan.get_node_id_by_ip(expand_ips[0])

    node_ids_list2 = env_manage_lun_manage.osan.get_nodes(node_ip1)
    node_ids2 = ",".join('%s' % id for id in node_ids_list2)
    node_pool_id = \
        env_manage_lun_manage.osan.get_option(s_ip=node_ip1, command="get_node_pools", indexname="node_pools",
                                              argv="id")[-1]
    env_manage_lun_manage.osan.update_node_pool(node_ip1, node_ids2, node_pool_id=node_pool_id)
    osan.startup(node_ip1)
    meta_disks, data_disks = ReliableTest.get_share_monopoly_disk_ids(new_node_id)
    log.info("获取新添加的节点的共享盘 %s 和数据盘: %s." % (meta_disks, data_disks))
    log.info("将数据盘添加到存储池.")
    storage_pool_id = env_manage_lun_manage.osan.get_storage__type_id(s_ip=node_ip1, type="BLOCK")
    for s_ip in deploy_ips:
        if ReliableTest.check_ping(s_ip):
            for data_disk in data_disks:
                env_manage_lun_manage.osan.expand_storage_pool(s_ip=s_ip, storage_pool_id=storage_pool_id,
                                                               disk_ids=data_disk)
    log.info("将新添加的节点加到访问区.")
    for s_ip in deploy_ips:
        if ReliableTest.check_ping(s_ip):
            # 更新访问区
            env_manage_lun_manage.osan.update_access_zone(s_ip=node_ip1, access_zone_id=az_id, node_ids=node_ids2)


def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    env_manage_lun_manage.clean()
    step1()
    decorator_func.multi_threads(run_vdb, add_node)
    vm_id = env_manage_repair_test.down_node(node_ip2, type_info)
    time.sleep(60)
    env_manage_repair_test.up_node(node_info=vm_id, type_info=type_info)
    env_manage_repair_test.Reliable_osan.get_os_status(node_ip2)  # 检测重启后机器状态，是否已开机

    env_manage_lun_manage.init_env(reboot_node=1)  # 还原环境(还原到创建vip、enable_san)；用于lun管理用例的测试
    decorator_func.pass_flag()


if __name__ == '__main__':
    main()
