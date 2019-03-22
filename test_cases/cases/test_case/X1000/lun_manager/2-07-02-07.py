# -*- coding:utf-8 _*-
"""
测试内容:thick 和thin lun写满存储池后删除thick lun后thin lun继续写入

步骤:
1、在访问区配置中，每个节点取1块磁盘创建副本模式存储池，创建存储池pool1，容量为50G；并创建和配置对于的访问分区和vip地址池；
2、创建10条逻辑卷，单卷大小为3G；
3、创建10条精简卷，单卷大小为20G；
4、为系统所有卷配置映射并映射到主机后，向每个逻辑卷卷写入3G数据，每个精简卷写入2G数据；
5、删除所有逻辑卷；
6、等空间释放后，向每个精简卷继续写入3G数据

检查项:
1、步骤2，10条逻辑卷创建成功；
2、步骤3，10条精简卷创建成功；
3、步骤4，数据写入成功，无报错；
4、步骤5，删除成功，系统可用剩余空间增加30G；
5、步骤6，数据写入成功，每个精简卷写入5G数据，存储池写满
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
client_ip2 = env_manage_lun_manage.client_ips[1]
esxi_ip = env_manage_lun_manage.Esxi_ips

"""读取存储池的容量"""
storage_pool_id = env_manage_lun_manage.osan.get_storage__type_id(s_ip=node_ip1, type="BLOCK")
az_id = env_manage_lun_manage.osan.get_access_zone_id(s_ip=node_ip1)[0]
storage_pool_size = env_manage_lun_manage.osan.get_option_single(s_ip=node_ip1, command='get_storage_pools', ids="ids",
                                                                 indexname="storage_pools", argv2="total_bytes",
                                                                 argv1=storage_pool_id) / int(
    cp("reserve", "replica_num"))
log.info("id为{}的存储池容量为{} byte".format(storage_pool_id, storage_pool_size))

thin_num = 10
thick_num = 10
thin_lun_size = 5368709120  # 5G
log.info("要创建的 thin lun 个数为{}".format(thin_num))
log.info("要创建的 thick lun 个数为{}".format(thick_num))
log.info("thin lun size 为{}".format(thin_lun_size))
thin_lun_total = int(cp("reserve", "thin_lun_reserve")) * thin_num
log.info("thin lun 总需要的预留空间为{} byte".format(thin_lun_total))
thick_lun_size = int((storage_pool_size - thin_lun_total) / thick_num / float(cp("reserve", "multiple")))
log.info("thick lun size为{} byte".format(thick_lun_size))


def iscsi_login1():
    global min_seq_w
    global min_seq_w2
    global min_seq_r
    login.login()

    # 修改vdbench配置文件的参数值
    seekpct = 0  # 随机
    rdpct1 = 0  # 读写比例(0是全写)
    rdpct2 = 100
    xfersize1 = cp("vdbench", "unmix_xfersize1")
    lun1 = env_manage_lun_manage.osan.ls_scsi_dev(client_ip1)
    lun2 = env_manage_lun_manage.osan.ls_scsi_dev(client_ip2)
    min_seq_w = env_manage_lun_manage.co2_osan.gen_vdb_xml(
        thread=cp("vdbench", "threads"),
        lun=lun1, xfersize=xfersize1, seekpct=seekpct, rdpct=rdpct1)
    min_seq_w2 = env_manage_lun_manage.co2_osan.gen_vdb_xml(
        thread=cp("vdbench", "threads"), lun=lun2, xfersize=xfersize1,
        seekpct=seekpct, rdpct=rdpct1)

    min_seq_r = env_manage_lun_manage.co2_osan.gen_vdb_xml(
        thread=cp("vdbench", "threads"),
        lun=lun1, xfersize=xfersize1, seekpct=seekpct, rdpct=rdpct2)


def iscsi_login2():
    global min_seq_w3
    global min_seq_r
    login.login()

    # 修改vdbench配置文件的参数值
    seekpct = 0  # 随机
    rdpct1 = 0  # 读写比例(0是全写)
    rdpct2 = 100
    xfersize1 = cp("vdbench", "unmix_xfersize1")
    lun2 = env_manage_lun_manage.osan.ls_scsi_dev(client_ip2)
    min_seq_w3 = env_manage_lun_manage.co2_osan.gen_vdb_xml(
        thread=cp("vdbench", "threads"),
        lun=lun2, xfersize=xfersize1, seekpct=seekpct, rdpct=rdpct1)


def create_thick_lun():
    for i in range(thick_num):
        lun_id = env_manage_lun_manage.osan.create_lun(s_ip=node_ip1, total_bytes=thick_lun_size, lun_type="THICK",
                                                       lun_name='lun_{}'.format(i), stor_pool_id=storage_pool_id,
                                                       acc_zone_id=az_id)


def create_thin_lun():
    for i in range(thick_num, thick_num + thin_num):
        lun_id = env_manage_lun_manage.osan.create_lun(s_ip=node_ip1, total_bytes=thin_lun_size, lun_type="THIN",
                                                       lun_name='lun_{}'.format(i), stor_pool_id=storage_pool_id,
                                                       acc_zone_id=az_id)


def map_lun():
    global hg_id1
    global hg_id2
    hg_id1 = env_manage_lun_manage.osan.create_host_group(s_ip=node_ip1, hg_name="hg_1")
    hg_id2 = env_manage_lun_manage.osan.create_host_group(s_ip=node_ip1, hg_name="hg_2")
    h_id1 = env_manage_lun_manage.osan.add_host(s_ip=node_ip1, h_name="h_1", hg_id=hg_id1)
    h_id2 = env_manage_lun_manage.osan.add_host(s_ip=node_ip1, h_name="h_2", hg_id=hg_id2)
    ini_id1 = env_manage_lun_manage.osan.add_initiator(s_ip=node_ip1, h_id=h_id1, iqn=cp('add_initiator', 'iqn'),
                                                       alias=cp('add_initiator', 'alias'))
    env_manage_lun_manage.osan.update_iscsid_conf(cli_ip=client_ip1, CHAPTYPE='None', s_ip=client_ip1)
    ini_id2 = env_manage_lun_manage.osan.add_initiator(s_ip=node_ip1, h_id=h_id2, iqn=cp('add_initiator', 'iqn1'),
                                                       alias=cp('add_initiator', 'alias1'))

    for i in env_manage_lun_manage.Reliable_osan.get_thick_lun(node_ip1):
        env_manage_lun_manage.osan.map_lun(s_ip=node_ip1, lun_ids=i, hg_id=hg_id1)

    for i in env_manage_lun_manage.Reliable_osan.get_thin_lun(node_ip1):
        env_manage_lun_manage.osan.map_lun(s_ip=node_ip1, lun_ids=i, hg_id=hg_id2)


def run_vdb1(arg=0):
    log.info("write some data to each thick lun")
    env_manage_lun_manage.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=min_seq_w, output=node_ip1, time=1200)


def run_vdb2(arg=1):
    log.info("write some data to each thin lun")
    env_manage_lun_manage.co2_osan.run_vdb(client_ip=client_ip2, vdb_xml=min_seq_w2, output=node_ip1, time=1200)


def case():
    log.info("在访问区配置中，每个节点取1块磁盘创建副本模式存储池，创建存储池pool1")
    log.info("创建10条逻辑卷，单卷大小为%s；创建10条精简卷，单卷大小为%s；为系统所有卷配置映射并映射到主机" % (thick_lun_size, thin_lun_size))
    create_thin_lun()
    create_thick_lun()
    map_lun()
    iscsi_login1()
    decorator_func.multi_threads(run_vdb1, run_vdb2)
    log.info("logout and clean all lun map")
    env_manage_lun_manage.clean_lun_map()
    log.info("delete each of thick lun")
    for lun_id1 in env_manage_lun_manage.Reliable_osan.get_thick_lun(node_ip1):
        env_manage_lun_manage.osan.delete_lun(s_ip=node_ip1, lun_id=lun_id1)
    env_manage_lun_manage.osan.reserve_wait(time_wait=120)
    log.info("create lun map to each of lun")
    for i in env_manage_lun_manage.Reliable_osan.get_thin_lun(node_ip1):
        env_manage_lun_manage.osan.map_lun(s_ip=node_ip1, lun_ids=i, hg_id=hg_id2)
    log.info("thin lun make login")
    iscsi_login2()
    log.info("again write some data to thin lun ")
    env_manage_lun_manage.co2_osan.run_vdb(client_ip=client_ip2, vdb_xml=min_seq_w3, output=node_ip1, time=1200)


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
