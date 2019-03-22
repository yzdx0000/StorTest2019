# -*-coding:utf-8 -*
import os
import time

import utils_path
import common
import snap_common
import log
import shell
import get_config
import prepare_clean
import random
import nas_common
import json
"""
author@liangxy
date 2018-07-30
@summary：
     缺陷自动化：使用pscli --command=get_params --name命令查找参数--name不起作用
@steps:
    1、使用get_params将所有name字段保存到列表all_name_lst（标准输出到列表）
    2、随机从列表中得到--name参数的测试值test_name
    3、使用get_params加上--name参数得到的name字段保存到列表rst_name_lst（标准输出到列表）
    4、遍历结果列表，如果有name字段有同测试值不同的，返回失败，跳出

@changelog：
     date 2018-0731   使用已有的库函数替代自己构建的函数
"""
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
MAX_WAIT_TIME = 600


def get_name_lst(case_ip, cmd_all):
    """
    author：LiangXiaoyu
    function:获取结果字典中的“name”字段字典
    :param case_ip:访问区所在节点ip；
    :param flag:开启（True）或关闭（False）nas
    :return:“name”字段的列表
    @changelog：
    """
    all_name_lst = []
    rc_all, stdout_all = common.run_command(case_ip, cmd_all)
    if 0 != rc_all:
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s \n" %
            (cmd_all, stdout_all))
    else:
        log.info("stdout:%s" % stdout_all)
        log.info("%s finished" % cmd_all)
    msg_json_all = common.json_loads(stdout_all)
    for parameters in msg_json_all['result']['parameters']:
        all_name = [parameters['section'], parameters['name']]
        all_name_lst.append(all_name)
    #  pscli --command=get_params | grep "\"name\":" | wc -l 1013
    log.info("totla in cmd result:%d, len of list:%d" %
             (msg_json_all['result']['total'], len(all_name_lst)))
    return all_name_lst


def random_choose_node(ob_node):
    """
        name  :      delete_disk_random_beta
        parameter:   common库中的node类
        author:      LiangXiaoyu
        date  :      2018.07.13
        Description: 返回一个随机得到的node_id和IP
        @changelog：
    """
    nodeid_list = ob_node.get_nodes_id()
    '''随机选一个节点'''
    fault_node_id = random.choice(nodeid_list)
    return fault_node_id


def case():
    log.info("case begin")
    rc, stdout = common.get_params(name='disk_isolate2rebuild_timeout')
    common.judge_rc_unequal(rc, 0, 'get params succeed!!!')
    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
