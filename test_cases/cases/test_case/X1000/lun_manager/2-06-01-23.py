# !/usr/bin/python
# -*-coding:utf-8 -*
"""
测试内容:有业务时iSCSI服务停止

步骤:
1、配置节点池设置副本数为3
2、创建存储池，使用全部磁盘
3、创建一个访问区
4、启动该访问区iSCSI
5、配置业务子网和VIP，
6、创建LUN和映射，并在主机登录，并下发大小块顺序写
7、停止该访问区iSCSI
8、在主机端访问已映射的LUN
9、内部数据校验

检查项:
6、主机能正常访问LUN
7、访问区iSCSI服务停止成功，步骤6中业务中断，节点VIP的分配与iSCSI服务停止前一致
8、主机访问LUN失败
9、内部数据一致
"""
# testlink case: 1000-34167
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
import env_manage_repair_test
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

osan = Lun_managerTest.oSan()


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
    min_seq_w = env_manage_lun_manage.osan.gen_vdb_xml(thread=cp("vdbench", "threads"), lun=lun1,
                                                       xfersize=xfersize1, seekpct=seekpct, rdpct=rdpct1)
    min_seq_r = env_manage_lun_manage.osan.gen_vdb_xml(thread=cp("vdbench", "threads"), lun=lun1,
                                                       xfersize=xfersize1, seekpct=seekpct, rdpct=rdpct2)


def step1(arg=1):
    global node_ids_list
    global az_id
    storage_pool_id = env_manage_lun_manage.osan.get_storage__type_id(s_ip=node_ip1, type="BLOCK")
    node_ids_list = env_manage_lun_manage.osan.get_nodes(node_ip1)
    node_ids = ",".join('%s' % id for id in node_ids_list)
    az_id = osan.create_access_zone(s_ip=deploy_ips[0],
                                    node_id="{},{},{}".format(node_ids_list[0], node_ids_list[1], node_ids_list[2]),
                                    name='accesszonetest')

    osan.enable_san(s_ip=node_ip1, access_zone_id=az_id)

    sub_id1 = osan.create_subnet(s_ip=node_ip1, access_zone_id=az_id, name='subnet1',
                                 sv_ip=cp("create_subnet", "sv_ip"),
                                 mask=cp("create_subnet", "mask"),
                                 vv_ip=cp("create_subnet", "vv_ip"),
                                 gate_way=cp("create_subnet", "gate_way"),
                                 network_interface=cp("create_subnet", "network_interface"))
    osan.add_vip_address_pool(s_ip=node_ip1, subnet_id=sub_id1,
                              domain_name=cp("add_vip_address_pool", "domain_name"),
                              vip=cp("add_vip_address_pool", "vips"))



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

    env_manage_lun_manage.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=min_seq_w, jn_jro='jn', output=node_ip1,
                                           need_judge=1)


def disable_san_thread(arg=5):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    decorator_func.timer(45, 15)
    osan.disable_san(s_ip=node_ip1, access_zone_id=az_id)

    time.sleep(30)
    log.info("主机端重新扫描lun")
    env_manage_lun_manage.iscsi_logout()
    login.login()
    lun_length = len(env_manage_lun_manage.osan.ls_scsi_dev(client_ip1))
    env_manage_lun_manage.assert_ins.assertEqual(lun_length, 0)


def update_access_zone(arg=3):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    decorator_func.timer(int(cp("wait_time", "remove_disk")))
    env_manage_lun_manage.osan.update_access_zone(s_ip=node_ip1, node_ids=node_ids_list[3], access_zone_id=az_id)


def main():
    env_manage_lun_manage.revert_env()
    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    env_manage_lun_manage.clean(target="access_zone")
    step1()
    decorator_func.multi_threads(run_vdb, disable_san_thread)
    env_manage_repair_test.Reliable_osan.compare_data()

    env_manage_lun_manage.init_env(reboot_node=1)  # 还原环境(还原到创建vip、enable_san)；用于lun管理用例的测试
    decorator_func.pass_flag()


if __name__ == '__main__':
    main()