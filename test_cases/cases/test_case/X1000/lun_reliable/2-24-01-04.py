# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-9
'''
测试内容:数据网异常情况下创建逻辑卷
测试步骤：
1）创建访问区，配置访问区
2）创建逻辑卷
3）创建过程中将日志组非业务节点数据网闪断5次
检查项：
1）访问区配置成功
2）逻辑卷创建成功

'''

# testlink case: 1000-33833
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
    node_ip2 = env_manage.get_inter_ids()[-1]  # 非业务节点IP
    client_ip1 = env_manage.client_ips[0]


def network_test():
    rc = env_manage.com_lh.get_cmd_status(node_ip1, cmd_name="create_lun")
    if rc == 0:
        data_net = env_manage.com_lh.get_eth_name(s_ip=node_ip2)[1]
        env_manage.com_lh.net_flash_test(node_ip2, data_net)
        return
    elif rc == 1:
        log.error("Not find CMD ,timeout will exit")
        os._exit(1)


def create_luns():
    for i in range(5):
        lun_name = "LUN" + str(i)
        env_manage.create_lun(node_ip1, lun_name)


def case():
    log.info("step:1.在创建逻辑卷过程中网卡闪断。")
    threads = []
    t1 = threading.Thread(target=create_luns)
    threads.append(t1)
    t2 = threading.Thread(target=network_test)
    threads.append(t2)
    for i in threads:
        i.start()
    for i in threads:
        i.join()


def main():
    env_manage.clean_test_env()
    setup()
    case()
    log.info("step:2.检查清理测试环境。")
    env_manage.clean_lun()
    env_manage.clean_test_env()
    log.info("The case finished!!!")


if __name__ == "__main__":
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)