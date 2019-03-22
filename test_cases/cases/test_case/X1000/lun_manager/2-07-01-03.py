# -*- coding:utf-8 _*-
"""
测试内容:多thin lun写满存储池

步骤:
1、在访问区配置中，每个节点取1块磁盘创建副本模式存储池，创建存储池pool1，容量为50G；并创建和配置对于的访问分区和vip地址池；
2、创建10条精简卷，容量都为30G，并配置卷映射；
3、10条卷并发写，每条卷写入6G大小数据。

检查项:
1、步骤2，卷创建成功；
2、步骤3，存储池空间写满，卷前段io可能报错，卷最多写入4G大小数据
"""

import os
import sys
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
node_ip1 = env_manage_lun_manage.node_ip1
node_ip2 = env_manage_lun_manage.deploy_ips[1]
client_ip1 = env_manage_lun_manage.client_ips[0]
esxi_ip = env_manage_lun_manage.Esxi_ips

FLAG = True  # True为使用THICK lun占一部分及空间再写;Flase为不创建THICK lun占空间
thin_lun_total = 5368709120  # 要写的thin lun大小设置为5G

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

if FLAG:
    thin_lun_size = int(thin_lun_total / 10)
    thick_lun_size = int((storage_pool_size - thin_lun_total) / float(cp("reserve", "multiple")))
    log.info("创建一条{}大小的thick lun，用来占用空间".format(thick_lun_size))


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
        min_seq_w = env_manage_lun_manage.osan.gen_vdb_xml(maxdata=thin_lun_total,
                                                           thread=cp("vdbench", "threads"), lun=lun1,
                                                           xfersize=xfersize1, seekpct=seekpct, rdpct=rdpct1)
        min_seq_r = env_manage_lun_manage.osan.gen_vdb_xml(maxdata=thin_lun_total,
                                                           thread=cp("vdbench", "threads"), lun=lun1,
                                                           xfersize=xfersize1, seekpct=seekpct, rdpct=rdpct2)


    def create_thick_lun():
        env_manage_lun_manage.osan.create_lun(s_ip=node_ip1, total_bytes=thick_lun_size, lun_type="THICK",
                                              lun_name='LUN_thick',
                                              stor_pool_id=storage_pool_id, acc_zone_id=az_id)


    def create_lun():
        hg_id = env_manage_lun_manage.osan.create_host_group(s_ip=node_ip1, hg_name='myhostgroup1')
        h_id = env_manage_lun_manage.osan.add_host(s_ip=node_ip1, h_name='host1', hg_id=hg_id)
        ini_id = env_manage_lun_manage.osan.add_initiator(s_ip=node_ip1, h_id=h_id, iqn=cp("add_initiator", "iqn"),
                                                          alias=cp("add_initiator", "alias"))
        decorator_func.judge_target(
            env_manage_lun_manage.osan.get_option_single(s_ip=node_ip1, command="get_initiators", indexname="initiators"
                                                         , argv2="auth_type", ids="ids", argv1=ini_id),
            "NONE")

        env_manage_lun_manage.osan.update_iscsid_conf(cli_ip=client_ip1, CHAPTYPE='None', s_ip=client_ip1)
        for i in range(10):
            lun_id = env_manage_lun_manage.osan.create_lun(s_ip=node_ip1, total_bytes=thin_lun_size, lun_type="THIN",
                                                           lun_name='lun_{}'.format(i),
                                                           stor_pool_id=storage_pool_id, acc_zone_id=az_id)
            lun_map_id = env_manage_lun_manage.osan.map_lun(s_ip=node_ip1, lun_ids=lun_id, hg_id=hg_id)


    def case():
        log.info("创建一条{}的THICK lun,占着空间".format(thick_lun_size))
        create_thick_lun()
        create_lun()
        iscsi_login()
        log.info("{}卷并发写，每条卷写入{}大小数据".format(10, thin_lun_size))
        env_manage_lun_manage.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=min_seq_w, output=node_ip1)


    def main():
        env_manage_lun_manage.revert_env()

        error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)
        env_manage_lun_manage.osan.xstor_pre_config(node_ip1, 0, 1)

        env_manage_lun_manage.clean()

        case()  # 用例步骤
        env_manage_lun_manage.osan.xstor_pre_config(node_ip1, 1, 0)
        decorator_func.pass_flag()


    if __name__ == '__main__':
        common.case_main(main)  # 主函数执行入口

else:
    avg_lun_size = int(storage_pool_size * 0.6)
    log.info("lun size为{}".format(avg_lun_size))


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
        min_seq_w = env_manage_lun_manage.osan.gen_vdb_xml(maxdata=int(avg_lun_size * 0.2),
                                                           thread=cp("vdbench", "threads"), lun=lun1,
                                                           xfersize=xfersize1, seekpct=seekpct, rdpct=rdpct1)
        min_seq_r = env_manage_lun_manage.osan.gen_vdb_xml(maxdata=int(avg_lun_size * 0.2),
                                                           thread=cp("vdbench", "threads"), lun=lun1,
                                                           xfersize=xfersize1, seekpct=seekpct, rdpct=rdpct2)


    def create_lun_1():
        hg_id = env_manage_lun_manage.osan.create_host_group(s_ip=node_ip1, hg_name='myhostgroup1')
        h_id = env_manage_lun_manage.osan.add_host(s_ip=node_ip1, h_name='host1', hg_id=hg_id)
        ini_id = env_manage_lun_manage.osan.add_initiator(s_ip=node_ip1, h_id=h_id, iqn=cp("add_initiator", "iqn"),
                                                          alias=cp("add_initiator", "alias"))
        decorator_func.judge_target(
            env_manage_lun_manage.osan.get_option_single(s_ip=node_ip1, command="get_initiators", indexname="initiators"
                                                         , argv2="auth_type", ids="ids", argv1=ini_id),
            "NONE")

        env_manage_lun_manage.osan.update_iscsid_conf(cli_ip=client_ip1, CHAPTYPE='None', s_ip=client_ip1)
        for i in range(10):
            lun_id = env_manage_lun_manage.osan.create_lun(s_ip=node_ip1, total_bytes=avg_lun_size, lun_type="THIN",
                                                           lun_name='lun_{}'.format(i),
                                                           stor_pool_id=storage_pool_id, acc_zone_id=az_id)
            lun_map_id = env_manage_lun_manage.osan.map_lun(s_ip=node_ip1, lun_ids=lun_id, hg_id=hg_id)


    def case():
        log.info("在访问区配置中，每个节点取1块磁盘创建副本模式存储池，创建存储池pool1，容量为50G；并创建和配置对于的访问分区和vip地址池")
        log.info("创建10条精简卷，容量都为30G，并配置卷映射")
        create_lun_1()
        iscsi_login()
        log.info("10条卷并发写，每条卷写入6G大小数据")
        env_manage_lun_manage.co2_osan.run_vdb(client_ip=client_ip1, vdb_xml=min_seq_w, jn_jro='jn', output=node_ip1)


    def main():
        env_manage_lun_manage.revert_env()

        error.rel_check_before_run(file_name, jnl_rep=3, free_jnl_num=0, node_num=3)

        env_manage_lun_manage.clean()

        case()  # 用例步骤

        env_manage_lun_manage.clean()


    if __name__ == '__main__':
        common.case_main(main)  # 主函数执行入口
