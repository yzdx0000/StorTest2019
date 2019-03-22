# -*- coding:utf-8 _*-
"""
测试内容:删除已写入大量数据的lun后完全释放空间

步骤:
1、在访问区配置中，每个节点取1块磁盘创建副本模式存储池，创建存储池pool1，容量为50G；并创建和配置对于的访问分区和vip地址池；
2、创建10条逻辑卷，单卷大小为2G；
3、创建10条精简卷，单卷大小为5G；
4、为系统所有卷配置映射并映射到主机后，向每个卷写入2G数据；
5、删除5条逻辑卷和5条精简卷；
6、创建2条逻辑卷，单卷大小为5G；
7、为步骤6新增逻辑卷配置卷映射并映射到主机，向每个卷写入5G数据

检查项:
1、步骤2，10条逻辑卷创建成功；
2、步骤3，10条精简卷创建成功；
3、步骤4，数据写入成功，无报错；
4、步骤5，删除成功，系统可用剩余空间增加20G；
5、步骤6，2条逻辑卷创建成功；
6、步骤7，数据写入成功，无报错
"""

import os, sys
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
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)  # 初始化日志文件

log.info("---------------全局初始化操作-----------------")
node_ip1 = env_manage_lun_manage.deploy_ips[0]
node_ip2 = env_manage_lun_manage.deploy_ips[1]
client_ip1 = env_manage_lun_manage.client_ips[0]
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
thick_lun_size = int(storage_pool_size * 0.4 / 10 / float(cp("reserve", "multiple")))
log.info("thick lun size为{} byte".format(thick_lun_size))
thin_lun_size = int(storage_pool_size / 10)
log.info("thin lun size为{} byte".format(thin_lun_size))


def iscsi_login1():
    global min_seq_w
    global min_seq_r
    login.login()

    # 修改vdbench配置文件的参数值
    seekpct = 0  # 随机
    rdpct1 = 0  # 读写比例(0是全写)
    rdpct2 = 100
    xfersize1 = cp("vdbench", "unmix_xfersize1")
    lun1 = env_manage_lun_manage.osan.ls_scsi_dev(client_ip1)
    min_seq_w = env_manage_lun_manage.co2_osan.gen_vdb_xml(
        thread=cp("vdbench", "threads"), lun=lun1,
        xfersize=xfersize1, seekpct=seekpct, rdpct=rdpct1)

    min_seq_r = env_manage_lun_manage.osan.gen_vdb_xml(maxdata=thick_lun_size,
                                                       thread=cp("vdbench", "threads"), lun=lun1,
                                                       xfersize=xfersize1, seekpct=seekpct, rdpct=rdpct2)


def iscsi_login2():
    global min_seq_w2
    login.login()

    # 修改vdbench配置文件的参数值
    seekpct = 0  # 随机
    rdpct1 = 0  # 读写比例(0是全写)
    rdpct2 = 100
    xfersize1 = cp("vdbench", "unmix_xfersize1")
    lun2 = env_manage_lun_manage.osan.ls_scsi_dev(client_ip1)

    min_seq_w2 = env_manage_lun_manage.osan.gen_vdb_xml(maxdata=thin_lun_size,
                                                        thread=cp("vdbench", "threads"), lun=lun2,
                                                        xfersize=xfersize1, seekpct=seekpct, rdpct=rdpct1)


def create_thick_lun():
    for i in range(10):
        lun_id = env_manage_lun_manage.osan.create_lun(s_ip=node_ip1, total_bytes=thick_lun_size, lun_type="THICK",
                                                       lun_name='lun_{}'.format(i),
                                                       stor_pool_id=storage_pool_id, acc_zone_id=az_id)


def create_thin_lun():
    for i in range(10, 10 + 10):
        lun_id = env_manage_lun_manage.osan.create_lun(s_ip=node_ip1, total_bytes=thin_lun_size, lun_type="THIN",
                                                       lun_name='lun_{}'.format(i),
                                                       stor_pool_id=storage_pool_id, acc_zone_id=az_id)


def map_lun():
    global hg_id1
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
    for i in lun:
        env_manage_lun_manage.osan.map_lun(s_ip=node_ip1, lun_ids=i, hg_id=hg_id1)


def case():
    log.info("在访问区配置中，每个节点取1块磁盘创建副本模式存储池，创建存储池pool1，容量为50G；并创建和配置对于的访问分区和vip地址池;创建200条精简卷")
    log.info("创建10条逻辑卷，单卷大小为5G；删除2条逻辑卷，等删除逻辑卷的空间释放完成后，创建40条精简卷")
    create_thin_lun()
    create_thick_lun()
    map_lun()
    iscsi_login1()
    env_manage_lun_manage.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=min_seq_w, output=node_ip1,
                                           whether_change_xml="N")
    env_manage_lun_manage.clean_lun_map()
    for lun_id1 in random.sample(env_manage_lun_manage.Reliable_osan.get_thin_lun(node_ip1), 5):
        env_manage_lun_manage.osan.delete_lun(s_ip=node_ip1, lun_id=lun_id1)

    for lun_id2 in random.sample(env_manage_lun_manage.Reliable_osan.get_thick_lun(node_ip1), 5):
        env_manage_lun_manage.osan.delete_lun(s_ip=node_ip1, lun_id=lun_id2)

    new_lun = []

    for i in range(10 + 10, 10 + 10 + 2):
        new_lun.append(env_manage_lun_manage.osan.create_lun(s_ip=node_ip1, total_bytes=thin_lun_size, lun_type="THICK",
                                                             lun_name='lun_{}'.format(i),
                                                             stor_pool_id=storage_pool_id, acc_zone_id=az_id))
    for i in new_lun:
        env_manage_lun_manage.osan.map_lun(s_ip=node_ip1, lun_ids=i, hg_id=hg_id1)

    iscsi_login2()
    env_manage_lun_manage.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=min_seq_w2, output=node_ip1,
                                           whether_change_xml="N")


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
