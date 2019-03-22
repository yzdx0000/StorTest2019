# -*- coding:utf-8 _*-
"""
测试内容:thick lun持续写入时删除thin lun

步骤:
1、在访问区配置中，每个节点取1块磁盘创建副本模式存储池，创建存储池pool1 50G ；并创建和配置对于的访问分区和vip地址池；
2、创建10条逻辑卷，单卷大小为2G；
3、创建10条精简卷，单卷大小为50G
4、配置卷映射，10条逻辑卷每条写入2G数据，逻辑卷每条写入1G数据
5、逻辑卷写入过程中，精简卷前端业务已完成，卸载主机映射的5条精简卷和删除对应的卷映射后，删除其中5条精简卷

检查项:
1、步骤2，逻辑卷创建成功；
2、步骤3，精简卷创建成功；
3、步骤5，查看精简卷写入1G大小，主机卸载卷成功，删除卷映射成功，删除精简卷成功；精简卷删除后对应的存储池可用空间增加5G
"""

import os, sys
import time
import random
import utils_path
import Lun_managerTest
import common
import ReliableTest
import log
import error
import get_config
import login
import error
import decorator_func
from get_config import config_parser as cp
import env_manage_lun_manage
import env_manage_repair_test

"""初始化日志和全局变量"""
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

"""读取存储池的容量"""
storage_pool_id = env_manage_lun_manage.osan.get_storage__type_id(s_ip=node_ip1, type="BLOCK")
az_id = env_manage_lun_manage.osan.get_access_zone_id(s_ip=node_ip1)[0]
storage_pool_size = env_manage_lun_manage.osan.get_option_single(s_ip=node_ip1,
                                                                 command='get_storage_pools', ids="ids",
                                                                 indexname="storage_pools",
                                                                 argv2="total_bytes",
                                                                 argv1=storage_pool_id) / int(
    cp("reserve", "replica_num"))
log.info("id为{}的存储池容量为{} byte".format(storage_pool_id, storage_pool_size))
thick_lun_size = 300 * 1024 ** 2
thin_lun_maxdata = int(storage_pool_size / 50)
lun_num = 10


def iscsi_login():
    global min_seq_w1
    global min_seq_w2
    login.login()

    # 修改vdbench配置文件的参数值
    seekpct = 0  # 随机
    rdpct1 = 0  # 读写比例(0是全写)
    rdpct2 = 100
    xfersize1 = cp("vdbench", "unmix_xfersize1")
    lun1 = env_manage_lun_manage.osan.ls_scsi_dev(client_ip1)
    lun2 = env_manage_lun_manage.osan.ls_scsi_dev(client_ip2)
    min_seq_w1 = env_manage_lun_manage.co2_osan.gen_vdb_xml(max_range="100M",
                                                            thread=cp("vdbench", "threads"), lun=lun1,
                                                            xfersize=xfersize1, seekpct=seekpct, rdpct=rdpct1)
    min_seq_w2 = env_manage_lun_manage.co2_osan.gen_vdb_xml(max_range="200M",
                                                            thread=cp("vdbench", "threads"), lun=lun2,
                                                            xfersize=xfersize1, seekpct=seekpct, rdpct=rdpct1)
    min_seq_r = env_manage_lun_manage.osan.gen_vdb_xml(maxdata=thin_lun_maxdata,
                                                       thread=cp("vdbench", "threads"), lun=lun2,
                                                       xfersize=xfersize1, seekpct=seekpct, rdpct=rdpct2)


def create_lun_thick(arg=1):
    for i1 in range(10):
        lun_id = env_manage_lun_manage.osan.create_lun(s_ip=node_ip1, lun_type="THICK", total_bytes=thick_lun_size,
                                                       lun_name='LUN{}'.format(i1),
                                                       stor_pool_id=storage_pool_id, acc_zone_id=az_id)


def create_lun_thin(arg=1):
    for i1 in range(10, 10 + lun_num):
        lun_id = env_manage_lun_manage.osan.create_lun(s_ip=node_ip1, total_bytes=storage_pool_size, lun_type="THIN",
                                                       lun_name='LUN{}'.format(i1),
                                                       stor_pool_id=storage_pool_id, acc_zone_id=az_id)


def process_error(arg=1):
    decorator_func.timer(10)
    fault_ip = env_manage_lun_manage.Reliable_osan.get_master_oRole(node_ip2)  # 获取oPmgr主进程节点ip
    for i in range(10):
        time.sleep(60)
        ReliableTest.run_kill_process(node_ip=fault_ip, process="oRole")


def network_error(arg=1):
    decorator_func.timer(10)
    fault_ip = env_manage_lun_manage.Reliable_osan.get_master_oRole(node_ip2)  # 获取oPmgr主进程节点ip
    env_manage_lun_manage.Reliable_osan.net_flash_test(fault_ip, cp("create_subnet", "network_interface"))


def map_lun():
    hg_id1 = env_manage_lun_manage.osan.create_host_group(s_ip=node_ip1, hg_name="hg_1")
    hg_id2 = env_manage_lun_manage.osan.create_host_group(s_ip=node_ip1, hg_name="hg_2")
    h_id1 = env_manage_lun_manage.osan.add_host(s_ip=node_ip1, h_name="h_1", hg_id=hg_id1)
    h_id2 = env_manage_lun_manage.osan.add_host(s_ip=node_ip1, h_name="h_2", hg_id=hg_id2)
    ini_id1 = env_manage_lun_manage.osan.add_initiator(s_ip=node_ip1, h_id=h_id1, iqn=cp('add_initiator', 'iqn'),
                                                       alias=cp('add_initiator', 'alias'))
    env_manage_lun_manage.osan.update_iscsid_conf(cli_ip=client_ip1, CHAPTYPE='None', s_ip=client_ip1)
    ini_id2 = env_manage_lun_manage.osan.add_initiator(s_ip=node_ip1, h_id=h_id2, iqn=cp('add_initiator', 'iqn1'),
                                                       alias=cp('add_initiator', 'alias1'))

    lun = env_manage_lun_manage.osan.get_lun(s_ip=node_ip1)
    for i in env_manage_lun_manage.Reliable_osan.get_thick_lun(node_ip1):
        env_manage_lun_manage.osan.map_lun(s_ip=node_ip1, lun_ids=i, hg_id=hg_id1)

    for i in env_manage_lun_manage.Reliable_osan.get_thin_lun(node_ip1):
        env_manage_lun_manage.osan.map_lun(s_ip=node_ip1, lun_ids=i, hg_id=hg_id2)


def run_vdb1(arg=0):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=min_seq_w1, output=node_ip1,
                                            whether_change_xml="N")
    delete_thick_lun()


def run_vdb2(arg=0):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip2, vdb_xml=min_seq_w2, output=node_ip1,
                                            whether_change_xml="N")


def delete_thick_lun(arg=2):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    for lun_id1 in random.sample(env_manage_lun_manage.Reliable_osan.get_thick_lun(node_ip1), 5):
        map_id = env_manage_repair_test.Lun_osan.gen_dict1(s_ip=node_ip1, command="get_lun_maps", arg1="lun_id",
                                                           arg2="id",
                                                           arg3="lun_maps", target=lun_id1)  # 根据lun id获取对应lun_map id
        env_manage_lun_manage.osan.delete_lun_map(s_ip=node_ip1, map_id=map_id)
        env_manage_lun_manage.osan.delete_lun(s_ip=node_ip1, lun_id=lun_id1)


def case():
    log.info("在访问区配置中，每个节点取1块磁盘创建副本模式存储池，创建存储池pool1 50G；并创建和配置对于的访问分区和vip地址池；")
    log.info("创建10条逻辑卷，单卷大小为2G，创建10条精简卷，单卷大小为50G")
    create_lun_thin()
    create_lun_thick()
    log.info("配置卷映射，10条逻辑卷每条写入2G数据，逻辑卷每条写入1G数据")
    map_lun()
    iscsi_login()
    log.info("逻辑卷写入过程中，精简卷前端业务已完成，卸载主机映射的5条精简卷和删除对应的卷映射后，删除其中5条精简卷")
    decorator_func.multi_threads(run_vdb1, run_vdb2)


def main():
    env_manage_lun_manage.revert_env()

    error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
    env_manage_lun_manage.osan.xstor_pre_config(node_ip1, 0, 1)

    env_manage_lun_manage.clean()

    case()  # 用例步骤

    env_manage_lun_manage.clean()
    env_manage_lun_manage.osan.xstor_pre_config(node_ip1, 1, 0)
    decorator_func.pass_flag()


if __name__ == '__main__':
    common.case_main(main)  # 主函数执行入口