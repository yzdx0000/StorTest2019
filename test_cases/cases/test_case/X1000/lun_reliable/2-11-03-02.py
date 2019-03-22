# -*-coding:utf-8 -*-
# !/usr/bin/python

'''
测试步骤：
1）创建逻辑卷创建完成后映射至主机将日志组一台非业务节点重启
2）检查逻辑卷状态
4）将逻辑卷重新映射至主机，对逻辑卷进行读写
检查项：
1）逻辑卷状态显示正常
2）可正常读写
'''

# testlink case: 1000-33660
import os
import time
import random
import commands
import utils_path
import log
import common
import ReliableTest
import prepare_x1000
import env_manage
import decorator_func

'''初始化'''
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log


def setup():
    '''获取业务节点IP和非业务节点IP'''
    global node_ip1
    global node_ip2
    global client_ip1
    node_ip1 = env_manage.get_inter_ids()[0]  # 业务节点IP
    node_ip2 = env_manage.get_inter_ids()[-1]  # 非业务节点IP
    client_ip1 = env_manage.client_ips[0]


def vdb_test():
    lun_name = env_manage.osan.ls_scsi_dev(client_ip=client_ip1)
    if len(lun_name) > 10:
        lun_name = lun_name[:10]
    vdb_file = env_manage.com2_osan.gen_vdb_xml(lun=lun_name, xfersize="4k", rdpct="50")
    log.info("vdbench 进行读写业务")
    env_manage.com2_osan.run_vdb(client_ip=client_ip1, vdb_xml=vdb_file, output=node_ip1, jn_jro="jn", time=600)
    env_manage.com2_osan.run_vdb(client_ip=client_ip1, vdb_xml=vdb_file, output=node_ip1, jn_jro="jro")


def vdb_result():
    log.info("保存vdb测试结果")
    env_manage.osan.save_vdb_log(c_ip=client_ip1, f_name="vdbtest")


def case():
    log.info("step:1.创建逻辑卷，创建lun map")
    env_manage.create_lun()
    env_manage.create_lun_map(ips=node_ip1)
    env_manage.create_iscsi_login()
    os_type = env_manage.get_os_type(node_ip2)
    info = env_manage.down_node(node_ip2, os_type, "init 6")
    log.info("step:2.节点%s 即将reboot，节点类型 %s，节点ID or IPMI IP：%s " % (node_ip2, info, os_type))
    log.info("step:3.主机运行vdbench，检查运行结果")
    vdb_test()
    vdb_result()
    log.info("step:4.检查节点及服务运行状态")
    env_manage.com_lh.get_os_status(node_ip2)
    env_manage.com_bd_disk.multi_check_part_lun_uniform_by_ip()  # 校验一致性


def main():
    env_manage.clean_test_env()
    setup()
    case()
    log.info("step:5.检查节点及服务运行状态")
    env_manage.osan.iscsi_logout_all(client_ip1)
    env_manage.clean_lun_map()
    env_manage.clean_lun()
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)
