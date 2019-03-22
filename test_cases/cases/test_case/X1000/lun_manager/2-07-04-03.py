# -*- coding:utf-8 _*-
"""
测试内容:并发写入thin lun数据触发空间预留确认时，oPmgr反复进程故障
1、部署3节点集群环境，配置日志3副本，配置访问分区为3个节点；
2、对齐 大小块混合顺序读写业务为脚本mix-S-Align.conf

步骤:
1、 创建12条精简卷；
2、使用1个主机所有卷；
3、在主机上运行vdbench -f mix-S-Align.conf -jn；
4、在步骤3中的业务运行过程中，将卷所属oSan节点的oSan进程以间隔1分钟反复被杀10次；
5、业务执行完成后，在主机1上执行vdbench -f mix-S-Align.conf -jro比较一致性；
6、比较存储内部数据一致性；

检查项:
1、步骤4，故障过程中业务正常；
2、步骤5，数据比较一致；
3、步骤6，内部数据比较一致。
"""

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
fault_ip = env_manage_lun_manage.Reliable_osan.get_master_oRole(node_ip2)  # 获取oPmgr主进程节点ip

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
thick_lun_size = int(storage_pool_size * 0.8 / 10 / float(cp("reserve", "multiple")))
log.info("thick lun size为{} byte".format(thick_lun_size))
reserve = "{}M".format(
    int(cp("reserve", "thin_lun_reserve_M")) * int(cp("reserve", "thin_lun_warn")) / 100 + 1)  # 触发空间预留的量
log.info("thin lun预留空间的80%为{}".format(reserve))


def iscsi_login():
    global mix_R_Align
    global mix_R
    login.login()

    # 修改vdbench配置文件的参数值
    seekpct = 0  # 随机
    rdpct1 = 0  # 读写比例(0是全写)
    rdpct2 = 50
    xfersize1 = cp("vdbench", "mix_xfersize1")
    lun1 = env_manage_repair_test.Lun_osan.ls_scsi_dev(client_ip1)
    lun2 = env_manage_repair_test.Lun_osan.ls_scsi_dev(client_ip2)
    mix_R_Align = env_manage_repair_test.co2_osan.gen_vdb_xml(max_range=reserve,
                                                              maxdata="3G",
                                                              thread=cp("vdbench", "threads"), lun=lun1,
                                                              xfersize=xfersize1, seekpct=seekpct,
                                                              rdpct=rdpct2)
    mix_R = env_manage_repair_test.Lun_osan.gen_vdb_xml(max_range=reserve,
                                                        maxdata="3G",
                                                        thread=cp("vdbench", "threads"), lun=lun1, xfersize=xfersize1,
                                                        seekpct=seekpct,
                                                        rdpct=rdpct2, offset=int(cp("vdbench", "offset")))


def create_thick_lun():
    for i in range(10):
        lun_id = env_manage_lun_manage.osan.create_lun(s_ip=node_ip1, total_bytes=thick_lun_size, lun_type="THICK",
                                                       lun_name='lun_{}'.format(i),
                                                       stor_pool_id=storage_pool_id, acc_zone_id=az_id)


def create_thin_lun():
    for i in range(12):
        lun_id = env_manage_lun_manage.osan.create_lun(s_ip=node_ip1, total_bytes=10737418240, lun_type="THIN",
                                                       lun_name='lun_{}'.format(i),
                                                       stor_pool_id=storage_pool_id, acc_zone_id=az_id)


def process_error(arg=1):
    decorator_func.timer(10)
    for i in range(10):
        time.sleep(60)
        ReliableTest.run_kill_process(node_ip=fault_ip, process="oRole")


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


def run_vdb1(arg=0):
    log.info('Run task %s (%s)...' % (sys._getframe().f_code.co_name, os.getpid()))
    env_manage_repair_test.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=mix_R_Align, jn_jro='jn', output=node_ip1,
                                            whether_change_xml="N")


def case():
    log.info("在访问区配置中，每个节点取1块磁盘创建副本模式存储池，创建存储池pool1 50G；并创建和配置对于的访问分区和vip地址池；")
    log.info("创建12条精简卷")
    create_thin_lun()
    map_lun()
    iscsi_login()
    log.info("在步骤3中的业务运行过程中，将卷所属oSan节点的oSan进程以间隔1分钟反复被杀10次")
    decorator_func.multi_threads(run_vdb1, process_error)
    env_manage_lun_manage.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=mix_R_Align, jn_jro='jro', output=node_ip1,
                                           whether_change_xml="N")
    env_manage_repair_test.Reliable_osan.compare_data()


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
