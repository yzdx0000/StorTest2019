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
import common
import breakdown
import log
import snap_common
import event_common
import get_config
import nas_common
# import s3_common
import quota_common
import rep_common

MOUNT_PAHT = get_config.get_one_mount_path()    # MOUNT_PAHT="/mnt/volume1"

"""minicase脚本运行路径"""
MINICASE_PATH = os.path.join(MOUNT_PAHT, 'mini_case')    # MINICASE_PATH="/mnt/volume1/mini_case"
"""s3脚本运行路径"""
S3_PATH = os.path.join(MOUNT_PAHT, 's3_case')    # MINICASE_PATH="/mnt/volume1/mini_case"
"""quota脚本运行路径"""
QUOTA_PATH = os.path.join(MOUNT_PAHT, 'quota_test_dir')    # MINICASE_PATH="/mnt/volume1/quota_test_dir"
"""缺陷脚本运行路径"""
DEFECT_PATH = get_config.get_one_defect_test_path()  # DEFECT_PATH="/mnt/volume1/defect_case"
"""性能脚本运行路径"""
PROPERTY_PATH = os.path.join(MOUNT_PAHT, 'property_test_dir')    # MINICASE_PATH="/mnt/volume1/property_test_dir"

'''客户端节点ip'''
CLIENT_IP_1 = get_config.get_client_ip()
"""NAS执行命令点"""
NODE_IP_1 = get_config.get_parastor_ip(0)
NODE_IP_2 = get_config.get_parastor_ip(1)
NODE_IP_3 = get_config.get_parastor_ip(2)
NODE_IP_LIST = [NODE_IP_1, NODE_IP_2, NODE_IP_3]
NAS_RANDOM_NODE_IP = NODE_IP_LIST[random.randint(0, len(NODE_IP_LIST) - 1)]


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


def check_share_disk_fault():
    """
    :author:      baoruobing
    :date  :      2018.07.24
    :description: 检查是否可以做元数据盘故障
    :return:
    """
    obj_node = common.Node()
    obj_disk = common.Disk()
    obj_volume = common.Volume()
    """获取所有节点id"""
    node_id_lst = obj_node.get_nodes_id()
    """获取所有共享盘"""
    all_share_disk_lst = []
    for node_id in node_id_lst:
        share_disk_names, data_disk_names = obj_disk.get_share_monopoly_disk_names(node_id)
        all_share_disk_lst += share_disk_names
    share_disk_num = len(all_share_disk_lst)

    """获取所有卷的最大副本数"""
    rc, layout_lst = obj_volume.get_all_volume_layout()
    if rc != 0:
        return False
    replica_num = 0
    for layout in layout_lst:
        if layout['disk_parity_num'] != 0:
            replica_num_tmp = layout['disk_parity_num'] + 1
        else:
            replica_num_tmp = layout['replica_num']
        replica_num = replica_num_tmp > replica_num and replica_num_tmp or replica_num

    if share_disk_num > replica_num:
        return True
    else:
        return False


def check_env_config(node_num=None, check_share_disk_num=False):
    """
    :author:                     baoruobing
    :date  :                     2018.07.24
    :description:                执行添加的函数
    :param node_num:             节点个数
    :param check_share_disk_num: 检查共享盘个数是否大于副本数
    :return:
    """
    obj_node = common.Node()
    obj_disk = common.Disk()
    if node_num:
        """检查节点个数"""
        env_node_num = obj_node.get_nodes_num()
        if node_num > env_node_num:
            log.warn("the env node num is %s, case need node num is %s, case skip"
                     % (str(env_node_num), str(node_num)))
            sys.exit(-1)

    if check_share_disk_num:
        if not check_share_disk_fault():
            log.warn("share disk num < replica num, can't make meta disk fault!!!")
            sys.exit(-1)
    return


def test_prepare(filename, env_check=True, **kwargs):
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

    if env_check:
        """检查环境是否符合脚本条件"""
        check_env_config(**kwargs)

        """检查坏对象"""
        check_func("badobj")

        """检查vset是否展平"""
        check_func("vset")

        """检查ds是否提供服务"""
        check_func("ds")

        """检查jnl是否正常"""
        check_func("jnl")

        """检查磁盘状态是否正常"""
        for cnt in range(11):
            rc = common.check_alldisks_health()
            if rc:
                log.info("check disks state OK")
                break
            else:
                if cnt == 10:
                    common.judge_rc(rc, True, 'check all disks state')
            log.info("wait 60s ")
            time.sleep(60)

        """检查服务状态是否正常"""
        for cnt in range(11):
            rc = common.check_service_state()
            if rc:
                log.info("check service state OK")
                break
            else:
                if cnt == 10:
                    log.error('check all services state')
            log.info("wait 60s ")
            time.sleep(60)

    return


def x1000_test_prepare(filename, **kwargs):
    """
    :author:         wuyuqiao
    :param filename: 脚本名字
    :param funcs:    要执行的函数
    :param **kwargs: 检查环境是否符合脚本要求的参数，check_env_config中的参数
    :return:
    :date  :         2018.1.15
    :description:    每个脚本前要执行的准备操作，脚本跑case前调用
    """
    """初始化日志"""
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
        if check_num == 5:
            break

    common.judge_rc(rc, True, 'check all disks state')

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

    return

def rel_check_before_run(file_name, jnl_rep=None, data_rep=None, free_jnl_num=None, switch='ON', **kwargs):
    """
    :Usage:用例执行前运行前检查环境
    :param filename: 日志文件
    :param node_num:集群内节点数
    :param jnl_rep:日志副本数
    :param data_rep:数据副本数
    :return: None
    """
    if switch == 'ON':
        time.sleep(15)
        # 检查进程是否正常，节点个数是否满足测试要求,检查逻辑盘是否有坏对象
        x1000_test_prepare(file_name, **kwargs)
        # 检查oSan是否有坏对象
        breakdown.disk().check_bad_obj()
        # 检查逻辑节点是否有异常状态
        breakdown.disk().check_lnode_state()
        # 检查日志副本数是否满足测试要求
        cur_jnl_rep = breakdown.disk().get_jnl_replica(s_ip=NODE_IP_1)
        cur_data_rep = breakdown.disk().get_min_lun_replica(s_ip=NODE_IP_1)
        cur_jnl_num = 0
        if None != breakdown.disk().get_free_jnl_id():
            cur_jnl_num = len(breakdown.disk().get_free_jnl_id())
        if jnl_rep != None and cur_jnl_rep < jnl_rep:
            log.error(
                "I found you need jnl replica: %d [cur: %d]isn't euqal with the test request." % (jnl_rep, cur_jnl_rep))
            os._exit(-1)

        # 检查数据副本数是否满足测试要求
        elif data_rep != None and cur_data_rep < data_rep:
            log.error("I found you need  data replica: %d [cur: %d]isn't euqal with the test request." % (
            data_rep, cur_data_rep))
            os._exit(-1)
        elif free_jnl_num != None and cur_jnl_num < free_jnl_num:
            log.error("I found you need free jnl number: %d [cur: %d]isn't euqal with the test request." % (
            free_jnl_num, cur_jnl_num))
            os._exit(-1)
    else:
        return


def test_clean(fault=False):
    """
    :author:         baoruobing
    :return:
    :date  :         2018.06.06
    :description:    每个脚本运行完执行的清理操作，脚本跑case后调用
    """
    if fault:
        log.info("wait 30s")
        time.sleep(30)

        """检查坏对象"""
        check_func("badobj")

        """检查vset是否展平"""
        check_func("vset")

        """检查ds是否提供服务"""
        check_func("ds")

        """检查jnl是否正常"""
        check_func("jnl")

        """检查磁盘状态是否正常"""
        for cnt in range(11):
            rc = common.check_alldisks_health()
            if rc:
                log.info("check disks state OK")
                break
            else:
                if cnt == 10:
                    common.judge_rc(rc, True, 'check all disks state')
            log.info("wait 60s ")
            time.sleep(60)

        """检查服务状态是否正常"""
        for cnt in range(11):
            rc = common.check_service_state()
            if rc:
                log.info("check service state OK")
                break
            else:
                if cnt == 10:
                    common.judge_rc(rc, True, 'check all services state')
            log.info("wait 60s ")
            time.sleep(60)
    return


def snap_test_prepare(filename, env_check=True, **kwargs):
    """
    :author:         baoruobing
    :param filename: 脚本名字
    :return: 
    :date  :         2018.06.07
    :description:    每个snap脚本前要执行的准备操作，脚本跑case前调用
    """
    """公共准备函数"""
    test_prepare(filename, env_check=env_check, **kwargs)

    snap_true_path = os.path.join(snap_common.SNAP_PATH, filename)             # /mnt/liyao/snap/snap_13_0_1_1
    snap_common.cleaning_environment(filename, snap_true_path)
    snap_common.create_snap_path(snap_true_path)
    log.info("\n****************************** snap prepare finish ******************************\n")
    return


def snap_test_clean(filename, fault=False):
    """
    :author:         baoruobing
    :param filename: 脚本名字
    :return: 
    :date  :         2018.06.07
    :description:    每个snap脚本运行完执行的清理操作，脚本跑case后调用
    """
    log.info("\n****************************** snap clean begin ******************************\n")
    """公共检查环境函数"""
    test_clean(fault)

    snap_true_path = os.path.join(snap_common.SNAP_PATH, filename)  # /mnt/liyao/snap/snap_13_0_1_1
    snap_common.cleaning_environment(filename, snap_true_path, False)

    """等待快照完全删除"""
    snap_common.wait_snap_del_by_name(filename)

    """等待策略完全删除"""
    snap_common.wait_snapstrategy_del_by_name(filename)
    log.info("\n****************************** snap clean finish ******************************\n")
    return


def event_test_prepare(filename, env_check=True, **kwargs):
    '''
    :author:         liyao
    :param filename: 脚本名字
    :return:
    :date  :         2018.08.11
    :description:    每个告警/事件脚本前要执行的准备操作，脚本跑case前调用
    '''
    """公共准备函数"""
    test_prepare(filename, env_check=env_check, **kwargs)

    event_true_path = os.path.join(event_common.EVENT_TEST_PATH, filename)  # /mnt/volume1/event/events_5_3_1_1
    event_common.cleaning_environment(event_true_path)
    event_common.create_event_path(event_true_path)
    log.info("\n****************************** event prepare finish ******************************\n")
    return


def event_test_clean(filename, fault=False):
    """
    author: liyao
    date: 2018.8.11
    description: 执行完事件/告警后，清理环境
    :param filename: 脚本名称
    :param fault:
    :return:
    """
    log.info("\n****************************** event clean begin ******************************\n")
    """公共检查环境函数"""
    test_clean(fault)

    event_true_path = os.path.join(event_common.EVENT_TEST_PATH, filename)  # /mnt/volume1/event/events_5_3_1_1
    event_common.cleaning_environment(event_true_path)
    log.info("\n****************************** snap clean finish ******************************\n")
    return


def defect_test_prepare(filename, env_check=True, **kwargs):
    """
    :author:         baoruobing
    :param filename: 脚本名字
    :return:
    :date  :         2018.06.07
    :description:    每个缺陷脚本前要执行的准备操作，脚本跑case前调用
    """
    """公共准备函数"""
    test_prepare(filename, env_check=env_check, **kwargs)

    defect_true_path = os.path.join(DEFECT_PATH, filename)             # /mnt/volume1/defect_case/P300-1
    """删除本脚本运行目录"""
    common.rm_exe(CLIENT_IP_1, defect_true_path)

    """创建缺陷总路径"""
    common.mkdir_path(CLIENT_IP_1, DEFECT_PATH)
    """创建本脚本运行目录"""
    common.mkdir_path(CLIENT_IP_1, defect_true_path)
    log.info("\n****************************** defect prepare finish ******************************\n")
    return


def defect_test_clean(filename, fault=False):
    """
    :author:         baoruobing
    :param filename: 脚本名字
    :return:
    :date  :         2018.06.07
    :description:    每个缺陷脚本运行完执行的清理操作，脚本跑case后调用
    """
    log.info("\n****************************** defect clean begin ******************************\n")
    """公共检查环境函数"""
    test_clean(fault)

    defect_true_path = os.path.join(DEFECT_PATH, filename)  # /mnt/volume1/defect_case/P300-1
    """删除本脚本运行目录"""
    common.rm_exe(CLIENT_IP_1, defect_true_path)
    log.info("\n****************************** defect clean finish ******************************\n")
    return


def minicase_test_prepare(filename, env_check=True, **kwargs):
    """
    :author:         baoruobing
    :param filename: 脚本名字
    :return:
    :date  :         2018.06.07
    :description:    每个最小用例脚本前要执行的准备操作，脚本跑case前调用
    """
    """公共准备函数"""
    test_prepare(filename, env_check=env_check, **kwargs)

    minicase_true_path = os.path.join(MINICASE_PATH, filename)             # /mnt/volume1/mini_case/P300-1
    """删除本脚本运行目录"""
    common.rm_exe(CLIENT_IP_1, minicase_true_path)

    """创建缺陷总路径"""
    common.mkdir_path(CLIENT_IP_1, MINICASE_PATH)
    """创建本脚本运行目录"""
    common.mkdir_path(CLIENT_IP_1, minicase_true_path)
    log.info("\n****************************** minicase prepare finish ******************************\n")
    return


def minicase_test_clean(filename, fault=False):
    """
    :author:         baoruobing
    :param filename: 脚本名字
    :return:
    :date  :         2018.06.07
    :description:    每个最小用例脚本运行完执行的清理操作，脚本跑case后调用
    """
    log.info("\n****************************** minicase clean begin ******************************\n")
    """公共检查环境函数"""
    test_clean(fault)

    minicase_true_path = os.path.join(MINICASE_PATH, filename)  # /mnt/volume1/mini_case/P300-1
    """删除本脚本运行目录"""
    common.rm_exe(CLIENT_IP_1, minicase_true_path)
    log.info("\n****************************** minicase clean finish ******************************\n")
    return


def nas_test_prepare(filename, env_check=False, **kwargs):
    """
    :author:         zhangchengyu
    :param filename: 脚本名字
    :return:
    :date  :         2018.08.13
    :description:    每个NAS用例脚本前要执行的准备操作，脚本跑case前调用
    :changelog:      删除目录和创建目录都选用的随机ip，若配置文件错误，节点不在同一集群，可能rm-ls-mkdir都成功，不符合预期（ls失败），给出提醒
                    @liangxy 2019.03.20
    """
    """公共准备函数"""
    test_prepare(filename, env_check=env_check, **kwargs)
    log.info("\n****************************** nas prepare begin ******************************\n")
    """删除所有NAS的配置文件"""
    nas_common.delete_all_nas_config()
    """删除所有的NAS目录"""
    common.rm_exe(NAS_RANDOM_NODE_IP, nas_common.NAS_PATH)
    mk_rc = nas_common.mkdir_nas_path()
    common.judge_rc(mk_rc, 0,
                    "Warning:nas path should remove first, why still be here when mkdir?Check nodes info in xml", False)
    log.info("\n****************************** nas prepare finish ******************************\n")
    return


def nas_test_clean(fault=False):
    """
    :author:         zhangchengyu
    :param filename: 脚本名字
    :return:
    :date  :         2018.08.13
    :description:    NAS环境清理，建议跑NAS脚本前、后都做一次环境的清理
    """
    log.info("\n****************************** nas clean begin ******************************\n")
    """公共检查环境函数"""
    test_clean(fault)
    """删除所有NAS的配置文件"""
    nas_common.delete_all_nas_config()
    """删除所有的NAS目录"""
    common.rm_exe(NAS_RANDOM_NODE_IP, nas_common.NAS_PATH)
    log.info("\n****************************** nas clean finish ******************************\n")
    return


def s3_test_prepare(filename, email_lst=None, env_check=True, **kwargs):
    """
    :author:         baourobing
    :date:           2018.08.29
    :description:    s3脚本准备函数
    :param filename: (str)脚本名
    :param kwargs:   脚本环境限制参数
    :return:
    """
    log.info("\n****************************** s3 prepare begin ******************************\n")
    """公共准备函数"""
    test_prepare(filename, env_check=env_check, **kwargs)
    if email_lst:
        s3_common.cleaning_environment(email_lst)
    rc, opt = s3_common.set_oss_http_auth("0")
    common.judge_rc(rc, 0, 'set_oss_http_auth = 0 failed')
    log.info("\n****************************** s3 prepare finish ******************************\n")
    return


def s3_test_clean(email_lst, fault=False):
    """
    :author:          baourobing
    :date:            2018.08.29
    :description:     s3脚本清理函数
    :param email_lst: (list)账户邮箱
    :param fault:     (bool)是否检查环境
    :return:
    """
    log.info("\n****************************** s3 clean begin ******************************\n")
    """公共检查环境函数"""
    test_clean(fault)
    s3_common.cleaning_environment(email_lst)
    log.info("\n****************************** s3 clean finish ******************************\n")
    return


def quota_test_prepare(filename, env_check=True, **kwargs):
    """
    :author:         chenjy1
    :param filename: 脚本名字
    :return:
    :date  :         2018.08.13
    :description:    每个quota用例脚本前要执行的准备操作，脚本跑case前调用
    """
    log.info("\n****************************** quota prepare begin ******************************\n")
    """公共准备函数"""
    test_prepare(filename, env_check=env_check, **kwargs)
    """删除所有quota"""
    quota_common.delete_all_quota_config()
    """删除所有NAS的配置"""
    nas_common.delete_all_nas_config()
    """删除本脚本运行目录"""
    quota_true_path = os.path.join(QUOTA_PATH, filename)  # /mnt/volume1/qouta_test_dir/xxx
    common.rm_exe(common.SYSTEM_IP, quota_true_path)
    """创建本脚本运行目录"""
    quota_common.creating_dir(common.SYSTEM_IP, quota_true_path)
    log.info("\n****************************** quota prepare finish ******************************\n")
    return


def quota_test_clean(filename, fault=False):
    """
    :author:         chenjy1
    :param filename: 脚本名字
    :return:
    :date  :         2018.08.13
    :description:    每个quota用例脚本前要执行的准备操作，脚本跑case前调用
    """
    log.info("\n****************************** quota clean begin ******************************\n")
    """公共检查环境函数"""
    test_clean(fault)
    """删除所有quota"""
    quota_common.delete_all_quota_config()
    """删除所有NAS的配置"""
    nas_common.delete_all_nas_config()
    """删除本脚本运行目录"""
    quota_true_path = os.path.join(QUOTA_PATH, filename)  # /mnt/volume1/qouta_test_dir/xxx
    common.rm_exe(common.SYSTEM_IP, quota_true_path)

    log.info("\n****************************** quota clean finish ******************************\n")
    return


def preperty_test_prepare(filename, env_check=True, **kwargs):
    """
    :author:         chenjy1
    :date:           2018.11.13
    :description:    每个性能用例脚本前要执行的准备操作，脚本跑case前调用
    :[aram filename: 脚本名字
    :param kwargs:
    :return:
    """
    log.info("\n****************************** preperty prepare begin ******************************\n")
    """公共准备函数"""
    test_prepare(filename, env_check=env_check, **kwargs)
    """删除本脚本运行目录"""
    preperty_true_path = os.path.join(PROPERTY_PATH, filename)  # /mnt/volume1/preperty_true_path/xxx
    common.rm_exe(common.SYSTEM_IP, preperty_true_path)
    """创建本脚本运行目录"""
    common.mkdir_path(CLIENT_IP_1, PROPERTY_PATH)
    common.mkdir_path(CLIENT_IP_1, preperty_true_path)
    log.info("\n****************************** preperty prepare finish ******************************\n")
    return


def preperty_test_clean(filename, fault=False):
    log.info("\n****************************** preperty clean begin ******************************\n")
    """公共检查环境函数"""
    test_clean(fault)
    """删除本脚本运行目录"""
    # preperty_true_path = os.path.join(PROPERTY_PATH, filename)  # /mnt/volume1/preperty_true_path/xxx
    # common.rm_exe(common.SYSTEM_IP, preperty_true_path)
    log.info("\n****************************** preperty clean finish ******************************\n")
    return


def rep_test_prepare(filename, env_check=True, clean_all_flag=True,  **kwargs):
    """
    :author:         chenjy1
    :param filename: 脚本名字
    :return:
    :date  :         2018.12.18
    :description:    每个rep脚本前要执行的准备操作，脚本跑case前调用
    """
    """公共准备函数"""
    test_prepare(filename, env_check=env_check, **kwargs)
    rep_common.delete_all_rep_config(clean_all_flag, **kwargs)
    """删除本脚本运行目录"""
    master_rep_true_path = os.path.join(rep_common.MASTER_PAIR_PATH, filename)  # /mnt/parastor/rep_test_dir/xxx
    salve_rep_true_path = os.path.join(rep_common.SLAVE_PAIR_PATH, filename)    # /mnt/(salve)parastor/(salve)rep_test
    # _dir/xxx
    common.rm_exe(common.SYSTEM_IP, master_rep_true_path)
    common.rm_exe(common.SYSTEM_IP, salve_rep_true_path, run_cluster=rep_common.SLAVE)
    """创建本脚本运行目录"""
    common.mkdir_path(rep_common.MASTER_NODE_LST[0], master_rep_true_path)
    common.mkdir_path(rep_common.SLAVE_NODE_LST[0], salve_rep_true_path, run_cluster=rep_common.SLAVE)

    log.info("\n****************************** rep prepare finish ******************************\n")
    return


def rep_test_clean(filename, fault=False, clean_all_flag=True, **kwargs):
    """
    :author:         zhangchengyu
    :param filename: 脚本名字
    :return:
    :date  :         2018.08.13
    :description:    NAS环境清理，建议跑NAS脚本前、后都做一次环境的清理
    """
    log.info("\n****************************** rep clean begin ******************************\n")
    """公共检查环境函数"""
    test_clean(fault)
    """删除所有rep的配置文件"""
    rep_common.delete_all_rep_config(clean_all_flag, **kwargs)
    """删除本脚本运行目录"""
    master_rep_true_path = os.path.join(rep_common.MASTER_PAIR_PATH, filename)  # /mnt/parastor/rep_test_dir/xxx
    salve_rep_true_path = os.path.join(rep_common.SLAVE_PAIR_PATH, filename)    # /mnt/(salve)parastor/(salve)rep_test
    # _dir/xxx
    common.rm_exe(common.SYSTEM_IP, master_rep_true_path)
    common.rm_exe(common.SYSTEM_IP, salve_rep_true_path, run_cluster=rep_common.SLAVE)
    log.info("\n****************************** rep clean finish ******************************\n")
    return
