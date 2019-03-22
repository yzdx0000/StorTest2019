# !/usr/bin/python
# -*-coding:utf-8 -*
"""
测试内容:访问区节点异常后添加新节点

步骤:
1、配置节点池含5节点，设置副本数为3
2、创建存储池，使用全部磁盘
3、创建一个访问区，包含3个节点
4、给访问区添加1个IP地址池，至少包含3个IP
5、启动iSCSI，创建一条LUN和对应的映射
6、主机下发业务中，业务节点掉电
7、添加节点池一个节点到访问区

检查项:
7、节点添加成功，日志迁移到新加入节点，日志服务正常
"""
# testlink case: 1000-34165
import os, sys
import time
import random
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
import env_manage_repair_test
import ReliableTest
import error

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
    global vip_pool_id
    storage_pool_id = env_manage_lun_manage.osan.get_storage__type_id(s_ip=node_ip1, type="BLOCK")
    az_id = osan.create_access_zone(s_ip=deploy_ips[0],
                                    node_id="{},{},{}".format(node_ids_list[0], node_ids_list[1], node_ids_list[2]),
                                    name='accesszonetest')
    sub_id1 = osan.create_subnet(s_ip=node_ip1, access_zone_id=az_id, name='subnet1',
                                 sv_ip=cp("create_subnet", "sv_ip"),
                                 mask=cp("create_subnet", "mask"),
                                 vv_ip=cp("create_subnet", "vv_ip"),
                                 gate_way=cp("create_subnet", "gate_way"),
                                 network_interface=cp("create_subnet", "network_interface"))
    vip_pool_id = osan.add_vip_address_pool(s_ip=node_ip1, subnet_id=sub_id1,
                                            domain_name=cp("add_vip_address_pool", "domain_name"),
                                            vip=cp("add_vip_address_pool", "vips"))
    osan.enable_san(s_ip=node_ip1, access_zone_id=az_id)
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

    env_manage_lun_manage.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=min_seq_w, jn_jro='jn', output=node_ip1)


def update_access_zone(arg=3):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    decorator_func.timer(int(cp("wait_time", "remove_disk")) + 20)
    env_manage_lun_manage.osan.update_access_zone(s_ip=node_ip1,
                                                  node_ids="{},{},{},{}".format(node_ids_list[0], node_ids_list[3],
                                                                                node_ids_list[1], node_ids_list[2]),
                                                  access_zone_id=az_id)

    # 获取losid-nodeid-jnlstate对应关系
    los_nid_state = env_manage_lun_manage.com_disk.get_jnl_state()
    log.info("Before inject error,the loss' state are{los_id:[node_id, los_state]}:%s" % (los_nid_state,))
    # 获取所有los id
    losids = los_nid_state.keys()
    # 随机选择一个los
    losid = random.choice(losids)
    log.info("Select los is %d." % (losid,))
    b_id = los_nid_state[losid][0]
    b_ip = env_manage_lun_manage.com_node.get_node_ip_by_id(b_id)


def os_error(arg=3):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    decorator_func.timer(int(cp("wait_time", "remove_disk")))
    env_manage_repair_test.down_node(node_ip=node_ip2, type_info=type_info, vm_id=vm_ids)
    time.sleep(240)
    env_manage_repair_test.up_node(node_info=vm_ids, type_info=type_info)
    env_manage_lun_manage.Reliable_osan.get_os_status_1(node_ip2)  # 检测重启后机器状态，是否已开机


def main():
    env_manage_lun_manage.revert_env()
    error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=5)
    env_manage_lun_manage.init_env(target="create_storage_pool", reboot_node=1)
    step1()
    decorator_func.multi_threads(run_vdb, os_error, update_access_zone)
    error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=5)

    env_manage_lun_manage.init_env(reboot_node=1)  # 还原环境(还原到创建vip、enable_san)；用于lun管理用例的测试
    decorator_func.pass_flag()


if __name__ == '__main__':
    main()
