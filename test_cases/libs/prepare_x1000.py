#!/usr/bin/python
# -*- encoding=utf8 -*-

'''

create time: 2018-06-06
author: baoruobing
function: 提供脚本运行前的准备工作和脚本运行完环境的清理工作

'''
import os
import sys
import time
import random
import breakdown
import common
import log
# import snap_common
# import event_common
import get_config

# import nas_common

# MOUNT_PAHT = get_config.get_one_mount_path()    # MOUNT_PAHT="/mnt/volume1"

"""minicase脚本运行路径"""
# MINICASE_PATH = os.path.join(MOUNT_PAHT, 'mini_case')    # MINICASE_PATH="/mnt/volume1/mini_case"

"""缺陷脚本运行路径"""
# DEFECT_PATH = get_config.get_one_defect_test_path()  # DEFECT_PATH="/mnt/volume1/defect_case"
'''客户端节点ip'''
# CLIENT_IP_1 = get_config.get_client_ip()
"""NAS执行命令点"""
# NODE_IP_1 = get_config.get_parastor_ip(0)
# NODE_IP_2 = get_config.get_parastor_ip(1)
# NODE_IP_3 = get_config.get_parastor_ip(2)
# NODE_IP_LIST = [NODE_IP_1, NODE_IP_2, NODE_IP_3]
# NAS_RANDOM_NODE_IP = NODE_IP_LIST[random.randint(0, len(NODE_IP_LIST) - 1)]


check_func_dic = {"badobj": {"func": common.check_badjobnr,
                             "okmsg": "The parastor has no badobj",
                             "errmsg": "badobj exist"},
                  "vset": {"func": common.check_vset,
                           "okmsg": "The parastor all vset is flatten",
                           "errmsg": "vset exist"},
                  "ds": {"func": common.check_ds,
                         "okmsg": "The parastor all ds service is OK",
                         "errmsg": "ds don't provide service"},
                  "jnl": {"func": common.check_jnl,
                          "okmsg": "The parastor all jnl is OK",
                          "errmsg": "jnl is not OK"}}


def check_func(type):
    """
    :author:      baoruobing
    :param type:  要检查的环境资源，必须是字典check_func_dic中的键
    :return: 
    :date  :      2018.06.06
    :description: 检查指定的环境资源项
    """

    log.info("\n******************** check %s begin! ********************" % type)
    func = check_func_dic[type]['func']
    okmsg = check_func_dic[type]['okmsg']
    errmsg = check_func_dic[type]['errmsg']

    """不断检查指定类型的环境资源是否正常"""
    start_time = time.time()
    while True:
        if func():
            break
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        time_str = "%s %dh:%dm:%ds" % (errmsg, h, m, s)
        log.info(time_str)
        time.sleep(20)
    log.info(okmsg)
    return


class Func():
    """
    :author:      baoruobing
    :date  :      2018.06.06
    :description: 执行添加的函数
    """

    def __init__(self):
        self.func_lst = []
        return

    def add_func(self, target, *args, **kwargs):
        func_dic = {}
        func_dic['target'] = target
        func_dic['args'] = tuple(args)
        func_dic['kwargs'] = dict(kwargs)
        self.func_lst.append(func_dic)
        return

    def run_func(self):
        if self.func_lst:
            for func_dic in self.func_lst:
                func_dic['target'](*func_dic['args'], **func_dic['kwargs'])
        return


def check_env_config(node_num=None, share_disk_num=None):
    """
    :author:               baoruobing
    :date  :               2018.07.24
    :description:          执行添加的函数
    :param node_num:       节点个数
    :param share_disk_num: 每个节点的共享盘个数
    :return:
    """
    obj_node = common.Node()
    obj_disk = common.Disk()
    if node_num:
        """检查节点个数"""
        env_node_num = obj_node.get_nodes_num()
        if node_num > env_node_num:
            log.info("the env node num is %s, case need node num is %s, case skip"
                     % (str(env_node_num), str(node_num)))
            os._exit(-1)

    if share_disk_num:
        """检查每个节点的共享盘的个数"""
        node_id_lst = obj_node.get_nodes_id()
        node_share_disk_num_lst = []
        for node_id in node_id_lst:
            share_disk_names, monopoly_disk_names = obj_disk.get_share_monopoly_disk_names(node_id)
            node_share_disk_num_lst.append(len(share_disk_names))
        min_share_disk_num = min(node_share_disk_num_lst)
        if share_disk_num > min_share_disk_num:
            log.info("the env share disk num is %s, case need share disk num is %s, case skip"
                     % (str(min_share_disk_num), str(share_disk_num)))
            os._exit(-1)
    return


def test_prepare(filename, **kwargs):
    """
    :author:         baoruobing
    :param filename: 脚本名字
    :param funcs:    要执行的函数
    :param **kwargs: 检查环境是否符合脚本要求的参数，check_env_config中的参数
    :return: 
    :date  :         2018.06.06
    :description:    每个脚本前要执行的准备操作，脚本跑case前调用
    """
    """初始化日志"""
    log_file_path = log.get_log_path(filename)
    log.init(log_file_path, True)

    log.info("\n****************************** prepare begin ******************************\n")

    """检查环境是否符合脚本条件"""
    check_env_config(**kwargs)

    """检查坏对象"""
    check_func("badobj")

    """检查vset是否展平"""
    check_func("vset")

    """检查ds是否提供服务"""
    check_func("ds")

    # """检查jnl是否正常"""
    # check_func("jnl")

    """检查磁盘状态是否正常"""
    rc = common.check_alldisks_health()
    common.judge_rc(rc, True, 'check all disks state')

    """检查服务状态是否正常"""
    # rc = common.check_service_state()
    # common.judge_rc(rc, True, 'check all services state')
    return


def x1000_test_prepare(filename=None, **kwargs):
    """
    :author:         wangxiang
    :param filename: 脚本名字
    :param funcs:    要执行的函数
    :param **kwargs: 检查环境是否符合脚本要求的参数，check_env_config中的参数
    :return:
    :date  :         2018.08.14
    :description:    每个脚本前要执行的准备操作，脚本跑case前调用
    """
    # """初始化日志"""
    if filename is not None:
        log_file_path = log.get_log_path(filename)
        log.init(log_file_path, True)

    log.info("****************************** prepare begin ******************************")

    """检查环境是否符合脚本条件"""
    check_env_config(**kwargs)

    """检查磁盘状态是否正常"""
    rc = common.check_alldisks_health()
    check_num = 1
    while rc is not True:
        log.info("Disk not OK.")
        rc = common.check_alldisks_health()
        time.sleep(60)
        check_num += 1
        if check_num == 6:
            break
    common.judge_rc(rc, True, 'check all disks state')

    log.info("Close the rcvr.")
    log.info("Separate the oJmgs master and oRole master.")
    breakdown.disk().seprate_ojmgs_orole()

    """检查服务状态是否正常"""
    rc = common.check_x1000_service_state()
    common.judge_rc(rc, True, 'check all services state')

    """检查坏对象"""
    check_func("badobj")

    """检查vset是否展平"""
    check_func("vset")

    """检查ds是否提供服务"""
    check_func("ds")

    """检查jnl是否正常"""
    check_func("jnl")

    return  #
# def test_clean(fault=False):
#     """
#     :author:         baoruobing
#     :return:
#     :date  :         2018.06.06
#     :description:    每个脚本运行完执行的清理操作，脚本跑case后调用
#     """
#     if fault:
#         log.info("wait 30s")
#         time.sleep(30)
#
#         """检查坏对象"""
#         check_func("badobj")
#
#         """检查vset是否展平"""
#         check_func("vset")
#
#         """检查ds是否提供服务"""
#         check_func("ds")
#
#         """检查jnl是否正常"""
#         check_func("jnl")
#
#         """检查磁盘状态是否正常"""
#         rc = common.check_alldisks_health()
#         common.judge_rc(rc, True, 'check all disks state')
#
#         """检查服务状态是否正常"""
#         rc = common.check_service_state()
#         common.judge_rc(rc, True, 'check all services state')
#     return
#
#
# def snap_test_prepare(filename, **kwargs):
#     """
#     :author:         baoruobing
#     :param filename: 脚本名字
#     :return:
#     :date  :         2018.06.07
#     :description:    每个snap脚本前要执行的准备操作，脚本跑case前调用
#     """
#     """公共准备函数"""
#     test_prepare(filename, **kwargs)
#
#     snap_true_path = os.path.join(snap_common.SNAP_PATH, filename)             # /mnt/liyao/snap/snap_13_0_1_1
#     snap_common.cleaning_environment(filename, snap_true_path)
#     snap_common.create_snap_path(snap_true_path)
#     log.info("\n****************************** snap prepare finish ******************************\n")
#     return
#
#
# def snap_test_clean(filename, fault=False):
#     """
#     :author:         baoruobing
#     :param filename: 脚本名字
#     :return:
#     :date  :         2018.06.07
#     :description:    每个snap脚本运行完执行的清理操作，脚本跑case后调用
#     """
#     log.info("\n****************************** snap clean begin ******************************\n")
#     """公共检查环境函数"""
#     test_clean(fault)
#
#     snap_true_path = os.path.join(snap_common.SNAP_PATH, filename)  # /mnt/liyao/snap/snap_13_0_1_1
#     snap_common.cleaning_environment(filename, snap_true_path, False)
#
#     """等待快照完全删除"""
#     snap_common.wait_snap_del_by_name(filename)
#
#     """等待策略完全删除"""
#     snap_common.wait_snapstrategy_del_by_name(filename)
#     log.info("\n****************************** snap clean finish ******************************\n")
#     return
#
# '''
# '''
# def event_test_prepare(filename, **kwargs):
#     '''
#     :author:         liyao
#     :param filename: 脚本名字
#     :return:
#     :date  :         2018.08.11
#     :description:    每个告警/事件脚本前要执行的准备操作，脚本跑case前调用
#     '''
#     """公共准备函数"""
#     test_prepare(filename, **kwargs)
#
#     event_true_path = os.path.join(event_common.EVENT_TEST_PATH, filename)  # /mnt/volume1/event/events_5_3_1_1
#     event_common.cleaning_environment(event_true_path)
#     event_common.create_event_path(event_true_path)
#     log.info("\n****************************** event prepare finish ******************************\n")
#     return
#
#
# def event_test_clean(filename, fault=False):
#     """
#     author: liyao
#     date: 2018.8.11
#     description: 执行完事件/告警后，清理环境
#     :param filename: 脚本名称
#     :param fault:
#     :return:
#     """
#     log.info("\n****************************** event clean begin ******************************\n")
#     """公共检查环境函数"""
#     test_clean(fault)
#
#     event_true_path = os.path.join(event_common.EVENT_TEST_PATH, filename)  # /mnt/volume1/event/events_5_3_1_1
#     event_common.cleaning_environment(event_true_path)
#     log.info("\n****************************** snap clean finish ******************************\n")
#     return
#
#
# def defect_test_prepare(filename, **kwargs):
#     """
#     :author:         baoruobing
#     :param filename: 脚本名字
#     :return:
#     :date  :         2018.06.07
#     :description:    每个缺陷脚本前要执行的准备操作，脚本跑case前调用
#     """
#     """公共准备函数"""
#     test_prepare(filename, **kwargs)
#
#     defect_true_path = os.path.join(DEFECT_PATH, filename)             # /mnt/volume1/defect_case/P300-1
#     """删除本脚本运行目录"""
#     common.rm_exe(CLIENT_IP_1, defect_true_path)
#
#     """创建缺陷总路径"""
#     common.mkdir_path(CLIENT_IP_1, DEFECT_PATH)
#     """创建本脚本运行目录"""
#     common.mkdir_path(CLIENT_IP_1, defect_true_path)
#     log.info("\n****************************** defect prepare finish ******************************\n")
#     return
#
#
# def defect_test_clean(filename, fault=False):
#     """
#     :author:         baoruobing
#     :param filename: 脚本名字
#     :return:
#     :date  :         2018.06.07
#     :description:    每个缺陷脚本运行完执行的清理操作，脚本跑case后调用
#     """
#     log.info("\n****************************** defect clean begin ******************************\n")
#     """公共检查环境函数"""
#     test_clean(fault)
#
#     defect_true_path = os.path.join(DEFECT_PATH, filename)  # /mnt/volume1/defect_case/P300-1
#     """删除本脚本运行目录"""
#     common.rm_exe(CLIENT_IP_1, defect_true_path)
#     log.info("\n****************************** defect clean finish ******************************\n")
#     return
#
#
# def minicase_test_prepare(filename, **kwargs):
#     """
#     :author:         baoruobing
#     :param filename: 脚本名字
#     :return:
#     :date  :         2018.06.07
#     :description:    每个最小用例脚本前要执行的准备操作，脚本跑case前调用
#     """
#     """公共准备函数"""
#     test_prepare(filename, **kwargs)
#
#     minicase_true_path = os.path.join(MINICASE_PATH, filename)             # /mnt/volume1/mini_case/P300-1
#     """删除本脚本运行目录"""
#     common.rm_exe(CLIENT_IP_1, minicase_true_path)
#
#     """创建缺陷总路径"""
#     common.mkdir_path(CLIENT_IP_1, MINICASE_PATH)
#     """创建本脚本运行目录"""
#     common.mkdir_path(CLIENT_IP_1, minicase_true_path)
#     log.info("\n****************************** minicase prepare finish ******************************\n")
#     return
#
#
# def minicase_test_clean(filename, fault=False):
#     """
#     :author:         baoruobing
#     :param filename: 脚本名字
#     :return:
#     :date  :         2018.06.07
#     :description:    每个最小用例脚本运行完执行的清理操作，脚本跑case后调用
#     """
#     log.info("\n****************************** minicase clean begin ******************************\n")
#     """公共检查环境函数"""
#     test_clean(fault)
#
#     minicase_true_path = os.path.join(MINICASE_PATH, filename)  # /mnt/volume1/mini_case/P300-1
#     """删除本脚本运行目录"""
#     common.rm_exe(CLIENT_IP_1, minicase_true_path)
#     log.info("\n****************************** minicase clean finish ******************************\n")
#     return
#
#
# def nas_test_prepare(filename, **kwargs):
#     """
#     :author:         zhangchengyu
#     :param filename: 脚本名字
#     :return:
#     :date  :         2018.08.13
#     :description:    每个NAS用例脚本前要执行的准备操作，脚本跑case前调用
#     """
#     log.info("\n****************************** nas prepare begin ******************************\n")
#     """公共准备函数"""
#     test_prepare(filename, **kwargs)
#     """删除所有NAS的配置文件"""
#     nas_common.delete_all_nas_config()
#     """删除所有的NAS目录"""
#     common.rm_exe(NAS_RANDOM_NODE_IP, nas_common.NAS_PATH)
#     nas_common.mkdir_nas_path()
#     log.info("\n****************************** nas prepare finish ******************************\n")
#     return
#
#
# def nas_test_clean(fault=False):
#     """
#     :author:         zhangchengyu
#     :param filename: 脚本名字
#     :return:
#     :date  :         2018.08.13
#     :description:    NAS环境清理，建议跑NAS脚本前、后都做一次环境的清理
#     """
#     log.info("\n****************************** nas clean begin ******************************\n")
#     """公共检查环境函数"""
#     test_clean(fault)
#     """删除所有NAS的配置文件"""
#     nas_common.delete_all_nas_config()
#     """删除所有的NAS目录"""
#     common.rm_exe(NAS_RANDOM_NODE_IP, nas_common.NAS_PATH)
#     log.info("\n****************************** nas clean finish ******************************\n")
#     return
# '''
