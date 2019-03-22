# -*-coding:utf-8 -*-
# !/usr/bin/python

'''
测试步骤：
1）创建节点池，创建存储池，配置访问区，开启SAN协议，
2）制造 主oPmgr进程反复故障，在故障期间创建LUN
检查项：
1）访问区配置成功
2）逻辑卷成功创建


'''

# testlink case: 1000-33729
import os
import time
import threading
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
    node_ip2 = env_manage.get_inter_ids()[1]  # 业务节点IP
    client_ip1 = env_manage.client_ips[0]


def run_kill_thread():
    log.info("step:2.1查杀oPmgr线程")
    rc = env_manage.com_lh.get_cmd_status(node_ip1, cmd_name="map_luns_to_host_group")
    if rc == 0:
        for i in range(3):
            orole_master_ip = env_manage.com_lh.get_master_oRole(s_ip=node_ip1)
            log.info("node %s will kill pmgr thread process" % (orole_master_ip))
            env_manage.com_lh.kill_thread(s_ip=orole_master_ip, p_name="oRole", t_name="pmgr")
            time.sleep(20)
        return
    elif rc == 1:
        log.error("Not find CMD ,timeout will exit")
        os._exit(1)



def case():
    log.info("step:1.创建逻辑卷")
    env_manage.create_luns()
    log.info("step:2.创建lun map过程中kill oJmgs 进程")
    threads = []
    t1 = threading.Thread(target=run_kill_thread)
    threads.append(t1)
    t2 = threading.Thread(target=env_manage.create_lun_map, args=(node_ip1,))
    threads.append(t2)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    log.info("step:3.ISCSI登录，检查lun 数量")
    env_manage.create_iscsi_login()
    lun_name = env_manage.osan.ls_scsi_dev(client_ip=client_ip1)
    lun_ids = env_manage.osan.get_lun()
    if len(lun_name) == len(lun_ids):
        log.info("host get lun numbers right")
    else:
        log.error("check xstor disk is not equal 10 ,find disk is %s" % (len(lun_name)))
        exit(1)


def main():
    env_manage.clean_test_env()
    setup()
    case()
    log.info("step:4.检查清理测试环境")
    env_manage.osan.iscsi_logout_all(client_ip1)
    env_manage.clean_lun_map()
    env_manage.clean_lun()
    env_manage.com_lh.get_os_status(node_ip1)
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)
