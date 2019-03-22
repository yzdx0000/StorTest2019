# -*- coding:utf-8 _*-
# Author:wangxiang
# Date  :2018-8-13
"""
测试内容:逻辑卷Qos在线修改读带宽

步骤:
1）在访问区配置中，每个节点取1块磁盘创建副本模式存储池，创建存储池pool1；
2）选择创建逻辑卷，选择存储池pool1，逻辑卷名称为LUN；
3）将逻辑卷映射至主机，并进行读业务；
4）检查主机业务带宽，待稳定后设置QoS带宽值为实际的50%；
5）提交申请后，立即查看主机实际读带宽，带宽值约为实际值的50%（忽略性能波动）。
6）再次修改读带宽值为实际值的75%

检查项:
1）存储池成功创建
2）逻辑卷成功创建
3）业务带宽稳定
4）QoS设置可立即生效
"""
import os
import sys
import utils_path
import common2
import common
import Lun_managerTest
import log
import error
import login
import error
import get_config
import threading
import time
import commands
import random
import breakdown
import ReliableTest

import env_manage_lun_manage
import decorator_func
from get_config import config_parser as cp

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

"""读取存储池的容量"""
storage_pool_id = env_manage_lun_manage.osan.get_storage__type_id(s_ip=node_ip1, type="BLOCK")
az_id = env_manage_lun_manage.osan.get_access_zone_id(s_ip=node_ip1)[0]
storage_pool_size = env_manage_lun_manage.osan.get_option_single(s_ip=node_ip1,
                                                                 command='get_storage_pools', ids="ids",
                                                                 indexname="storage_pools",
                                                                 argv2="total_bytes",
                                                                 argv1=storage_pool_id)


def iscsi_login():
    global min_seq_w
    global min_seq_r
    global lun_id

    hg_id = env_manage_lun_manage.osan.create_host_group(s_ip=node_ip1, hg_name='myhostgroup1')
    h_id = env_manage_lun_manage.osan.add_host(s_ip=node_ip1, h_name='host1', hg_id=hg_id)
    ini_id = env_manage_lun_manage.osan.add_initiator(s_ip=node_ip1, h_id=h_id, iqn=cp("add_initiator", "iqn"),
                                                      alias=cp("add_initiator", "alias"))
    decorator_func.judge_target(
        env_manage_lun_manage.osan.get_option_single(s_ip=node_ip1, command="get_initiators", indexname="initiators"
                                                     , argv2="auth_type", ids="ids", argv1=ini_id),
        "NONE")
    env_manage_lun_manage.osan.update_iscsid_conf(cli_ip=client_ip1, CHAPTYPE='None', s_ip=client_ip1)
    lun_id = env_manage_lun_manage.osan.create_lun(s_ip=node_ip1, lun_type="THICK",
                                                   lun_name='LUN1',
                                                   stor_pool_id=storage_pool_id, acc_zone_id=az_id)
    lun_map_id = env_manage_lun_manage.osan.map_lun(s_ip=node_ip1, lun_ids=lun_id, hg_id=hg_id)

    login.login()

    # 修改vdbench配置文件的参数值
    seekpct = cp("vdbench", "seekpct")  # 随机
    rdpct1 = 0  # 读写比例(0是全写)
    rdpct2 = 100
    xfersize1 = cp("vdbench", "unmix_xfersize1")
    lun1 = env_manage_lun_manage.osan.ls_scsi_dev(client_ip=client_ip1)
    min_seq_w = env_manage_lun_manage.co2_osan.gen_vdb_xml(lun=lun1, xfersize=xfersize1, seekpct=seekpct, rdpct=rdpct1)
    min_seq_r = env_manage_lun_manage.co2_osan.gen_vdb_xml(lun=lun1, xfersize=xfersize1, seekpct=seekpct, rdpct=rdpct2)


def run_vdb(arg=1):
    log.info('Run task %s (%s)...' % (arg, os.getpid()))
    env_manage_lun_manage.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=min_seq_r, output=node_ip1)


def get_avg_bandwidth(arg=1):
    log.info('Run task %s (%s)...' % (arg, os.getpid()))
    avg_bandwidth = env_manage_lun_manage.osan.Qos_count(c_ip=client_ip1, s_ip=node_ip1)
    avg_iops, avg_bandwidth = env_manage_lun_manage.osan.Qos_count(c_ip=client_ip1, s_ip=node_ip1, qos_arg="all")

    log.info("step2:检查主机业务带宽，待稳定后设置QoS带宽值为实际的50%，设置IOPS值为实际的50%； ...")

    osan.update_lun(s_ip=node_ip1, lun_id=lun_id, max_throughput=int(avg_bandwidth * 0.5), max_iops=int(avg_iops * 0.5))

    log.info("提交申请后，立即查看主机实际读带宽，带宽值和IOPS约为实际值的50%（忽略性能波动）")
    avg_iops2, avg_bandwidth2 = env_manage_lun_manage.osan.Qos_count(c_ip=client_ip1, s_ip=node_ip1, qos_arg="all")
    env_manage_lun_manage.assert_ins.assert_less_than(avg_bandwidth, avg_bandwidth2, avg_bandwidth, percentage=0.5,
                                                      suc_msg="qos修改生效")
    env_manage_lun_manage.assert_ins.assert_less_than(avg_iops, avg_iops2, avg_iops, percentage=0.5, suc_msg="qos修改生效")

    log.info("再次修改带宽和IOPS值为实际值的75%")
    osan.update_lun(s_ip=node_ip1, lun_id=lun_id, max_throughput=int(avg_bandwidth * 0.75),
                    max_iops=int(avg_iops * 0.75))

    avg_iops3, avg_bandwidth3 = env_manage_lun_manage.osan.Qos_count(c_ip=client_ip1, s_ip=node_ip1, qos_arg="all")
    env_manage_lun_manage.assert_ins.assert_less_than(avg_bandwidth, avg_bandwidth3, avg_bandwidth, percentage=0.75,
                                                      suc_msg="qos修改生效")
    env_manage_lun_manage.assert_ins.assert_less_than(avg_iops, avg_iops3, avg_iops, percentage=0.75, suc_msg="qos修改生效")


def case():
    log.info("step1:生成vdbench配置文件，将逻辑卷映射至主机，并进行读业务...")

    iscsi_login()

    decorator_func.multi_threads(run_vdb, get_avg_bandwidth)


def main():
    env_manage_lun_manage.revert_env()

    # error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)

    env_manage_lun_manage.clean()  # 环境清理

    case()  # 用例步骤

    decorator_func.pass_flag()


if __name__ == '__main__':
    common.case_main(main)  # 主函数执行入口
