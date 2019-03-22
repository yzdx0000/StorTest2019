# -*- coding:utf-8 _*-
"""
测试内容:并发创建thinl lun和thick lun，oSan进程故障

步骤:
1、在访问区配置中，每个节点取1块磁盘创建副本模式存储池，创建存储池；并创建和配置对于的访问分区和vip地址池；
2、并发创建20条逻辑卷和20条精简卷时，oSan进程以间隔1分钟反复被杀10次

检查项:
1、步骤2，oSan被拉起前，创建挂住，恢复后创建正常，直到所有卷创建完成
"""

import os
import threading
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

"""初始化日志和全局变量"""
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)  # 初始化日志文件

log.info("---------------全局初始化操作-----------------")
node_ip1 = env_manage_lun_manage.node_ip1
node_ip2 = env_manage_lun_manage.deploy_ips[1]
client_ip1 = env_manage_lun_manage.client_ips[0]
esxi_ip = env_manage_lun_manage.Esxi_ips

"""读取存储池的容量"""
storage_pool_id = env_manage_lun_manage.osan.get_storage__type_id(s_ip=node_ip1, type="BLOCK")
az_id = env_manage_lun_manage.osan.get_access_zone_id(s_ip=node_ip1)[0]
storage_pool_size = int(env_manage_lun_manage.osan.get_option_single(s_ip=node_ip1,
                                                                 command='get_storage_pools', ids="ids",
                                                                 indexname="storage_pools",
                                                                 argv2="total_bytes",
                                                                 argv1=storage_pool_id) / int(
    cp("reserve", "replica_num")) / float(cp("reserve", "multiple")))
log.info("id为{}的存储池容量为{} byte".format(storage_pool_id, storage_pool_size))
lun_num = 20  # thin  lun个数
thin_lun_total = int(cp("reserve", "thin_lun_reserve")) * lun_num
thick_lun_size = int((storage_pool_size - thin_lun_total) / 20)
log.info("thick lun size为{} byte".format(thick_lun_size))


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
    min_seq_w1 = env_manage_lun_manage.osan.gen_vdb_xml(maxdata=int(thick_lun_size * 10),
                                                        thread=cp("vdbench", "threads"), lun=lun1,
                                                        xfersize=xfersize1, seekpct=seekpct, rdpct=rdpct1)
    min_seq_w2 = env_manage_lun_manage.osan.gen_vdb_xml(maxdata=int(storage_pool_size * 10),
                                                        thread=cp("vdbench", "threads"), lun=lun1,
                                                        xfersize=xfersize1, seekpct=seekpct, rdpct=rdpct1)
    min_seq_r = env_manage_lun_manage.osan.gen_vdb_xml(maxdata=int(thick_lun_size * 0.2),
                                                       thread=cp("vdbench", "threads"), lun=lun1,
                                                       xfersize=xfersize1, seekpct=seekpct, rdpct=rdpct2)


def create_lun_thick(arg1):
    env_manage_lun_manage.osan.create_lun(s_ip=node_ip1, total_bytes=thick_lun_size, lun_type="THICK",
                                          lun_name='LUN{}'.format(arg1),
                                          stor_pool_id=storage_pool_id, acc_zone_id=az_id)


def create_lun_thin(arg2):
    env_manage_lun_manage.osan.create_lun(s_ip=node_ip1, total_bytes=storage_pool_size, lun_type="THIN",
                                          lun_name='LUN{}'.format(arg2),
                                          stor_pool_id=storage_pool_id, acc_zone_id=az_id)


def process_error(arg=1):
    decorator_func.timer(10)
    for i in range(10):
        ReliableTest.run_kill_process(node_ip=node_ip1, process="oSan")
        time.sleep(60)


def map_lun():
    hg_id = env_manage_lun_manage.osan.create_host_group(s_ip=node_ip1, hg_name='myhostgroup1')
    h_id = env_manage_lun_manage.osan.add_host(s_ip=node_ip1, h_name='host1', hg_id=hg_id)
    ini_id = env_manage_lun_manage.osan.add_initiator(s_ip=node_ip1, h_id=h_id, iqn=cp("add_initiator", "iqn"),
                                                      alias=cp("add_initiator", "alias"))
    decorator_func.judge_target(
        env_manage_lun_manage.osan.get_option_single(s_ip=node_ip1, command="get_initiators", indexname="initiators"
                                                     , argv2="auth_type", ids="ids", argv1=ini_id),
        "NONE")

    env_manage_lun_manage.osan.update_iscsid_conf(cli_ip=client_ip1, CHAPTYPE='None', s_ip=client_ip1)
    lun = env_manage_lun_manage.osan.get_lun(s_ip=node_ip1)
    for i in lun:
        env_manage_lun_manage.osan.map_lun(s_ip=node_ip1, lun_ids=i, hg_id=hg_id)


def case():
    log.info("在访问区配置中，每个节点取1块磁盘创建副本模式存储池，创建存储池pool1 50G；并创建和配置对于的访问分区和vip地址池；")
    log.info("并发创建20条逻辑卷和20条精简卷时，oSan进程以间隔1分钟反复被杀10次")
    lun_num1 = env_manage_lun_manage.osan.get_lun(s_ip=node_ip1)  # 执行前查询lun数量
    threads = []
    for i in range(lun_num):
        threads.append(threading.Thread(target=create_lun_thin, args=(i,)))
    for j in range(lun_num, lun_num + 20):
        threads.append(threading.Thread(target=create_lun_thick, args=(j,)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    process_error()
    lun_total = len(lun_num1) + 20 + lun_num  # 执行完成后lun的总数
    while True:
        lun_num2 = env_manage_lun_manage.osan.get_lun(s_ip=node_ip1)  # 执行开始后查询lun数量
        log.info("Wait execute finish ...")
        time.sleep(20)
        if len(lun_num2) == lun_total:
            break


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
