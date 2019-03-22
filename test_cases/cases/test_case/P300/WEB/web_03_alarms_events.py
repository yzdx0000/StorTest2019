# -*-coding:utf-8 -*

import os
import time
from multiprocessing import Process

import utils_path
import log
import common
import get_config
import web_common
import make_fault
import prepare_clean


#######################################################
# 函数功能：界面自动化-----检测实时告警，检测事件
# 脚本作者：duyuli
# 日期：2018-11-28
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
SYSTEM_IP_0 = get_config.get_parastor_ip(0)
SYSTEM_IP_1 = get_config.get_parastor_ip(1)
SYSTEM_IP_2 = get_config.get_parastor_ip(2)
alarm_name1 = "网口链接异常"
alarm_name2 = "网口故障"

obj_node = common.Node()
node_id = obj_node.get_node_id_by_ip(SYSTEM_IP_2)
eth_list, data_ip_list, ip_mask_lst = obj_node.get_node_eth(node_id)
eth_fault = eth_list[1]


def down_part_eth(eth):
    time.sleep(5)
    make_fault.down_eth(SYSTEM_IP_2, eth)
    return


def up_part_eth(eth):
    make_fault.up_eth(SYSTEM_IP_2, eth, ip_mask_lst)
    return


def case():
    driver = web_common.init_web_driver()

    obj_alarm_event = web_common.Alarms_Events(driver)

    cluster_time_init = obj_alarm_event.get_cluster_time()

    # 检查告警
    p1 = Process(target=obj_alarm_event.check_alarms, args=(alarm_name1,))

    # 设置一故障
    p2 = Process(target=down_part_eth, args=(eth_fault,))

    p1.start()
    p2.start()

    p1.join()
    p2.join()
    up_part_eth(eth_fault)

    # 检查事件
    obj_alarm_event.check_events(alarm_name2, cluster_time_init)

    common.judge_rc(p1.exitcode, 0, "p1 exit failed", exit_flag=False)
    common.judge_rc(p2.exitcode, 0, "p2 exit failed", exit_flag=False)
    web_common.quit_web_driver(driver)


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)