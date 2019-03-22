# -*- encoding=utf8 -*-

#######################################################
# 脚本作者：liujx
# 脚本说明：升级公共函数
#######################################################

from multiprocessing import Process
import os
import json
import time

import log
import get_config
import common


upgrade_item_default = 'server'


##############################################################################
# ##name  :      get_system_version
# ##parameter:   node_ip:节点ip
# ##author:      liujx
# ##date  :      2018.07.19
# ##Description: 查看系统版本号
##########################################################################
def get_system_version():
    rc, stdout = common.get_system_version()
    result = common.json_loads(stdout)
    system_version = result["result"]["system_version"]
    return system_version


##############################################################################
# ##name  :      set_system_version
# ##parameter:   system_version:要设置的版本号, node_ip:节点ip
# ##author:      liujx
# ##date  :      2018.07.23
# ##Description: 修改系统版本号
##############################################################################
def set_system_version(system_version):
    rc, stdout = common.set_system_version(system_version=system_version)
    common.judge_rc(rc, 0, "Execute command: set_system_version failed. \nstdout: %s" % (stdout))
    return


##############################################################################
# ##name  :      check_before_upgrade
# ##parameter:   node_ip:节点ip
# ##author:      liujx
# ##date  :      2018.07.19
# ##Description: 升级前检查
##############################################################################
def check_before_upgrade():
    rc, stdout = common.check_before_upgrade()
    common.judge_rc(rc, 0, "Execute command: check_before_upgrade failed. \nstdout: %s" % (stdout))
    result = common.json_loads(stdout)
    return result


##############################################################################
# ##name  :      distribute_package
# ##parameter:   package_ip:升级包所在节点ip
#                package_path:升级包存放的位置
#                例：/root/ofs3.0/ParaStor3.0.0_20180720/parastor-3.0.0-centos7.5
#                -feature_XSTOR1000-113-2018-01-cnas_8be330c_20180720_103801-2-1.tar.xz
# ##author:      liujx
# ##date  :      2018.07.23
# ##Description: 分发安装包
##############################################################################
def distribute_package(package_ip, package_path):
    upgade_version = int(package_path[-10])
    rc, stdout = common.distribute_package(host_ips=package_ip, path=package_path, upgrade_version=upgade_version)
    common.judge_rc(rc, 0, "Execute command: distribute_package failed. \nstdout: %s" % (stdout))
    return


##############################################################################
# ##name  :      online_upgrade
# ##parameter:   node_ip
#                package_name, e.g.parastor-3.0.0-centos7.5-feature_XSTOR1000-
#                113-2018-01-cnas_8be330c_20180720_103801-2-1.tar.xz
#                upgrade_item, e.g. server, client, all; default: server
# ##be care:     distribute_package() must be executed before this function
# ##author:      liujx
# ##date  :      2018.07.23
# ##Description: 执行在线升级（）
##############################################################################
def ext_online_upgrade(node_ip, package_name, package_time, upgrade_item=upgrade_item_default):
    version = package_name[-10]
    min_version = package_name[-8]
    node = common.Node()
    if upgrade_item == 'server':
        upgrade_num = int(node.get_nodes_num())
    elif upgrade_item == 'client':
        upgrade_num = len(node.get_external_client_ips())
    else:
        upgrade_num = int(node.get_nodes_num()) + len(node.get_external_client_ips())
    upgrade_timeout = upgrade_num * 3600  # upgrade_num*60min

    rc, stdout = common.online_upgrade(version=version, min_version=min_version, package_time=package_time,
                                       upgrade_item=upgrade_item, timeout_pscli=upgrade_timeout)
    result = common.json_loads(stdout)
    return rc, result


##############################################################################
# ##name  :      check_upgrade_info
# ##parameter:   node_ip
#
# ##author:      liujx
# ##date  :      2018.07.26
# ##Description: 检查升级状态
##############################################################################
def get_upgrade_info():
    timeout = 120
    rc, stdout = common.get_upgrade_info(timeout_pscli=timeout)
    common.judge_rc(rc, 0, "Execute command: get_upgrade_info failed. \nstdout: %s" % (stdout))
    result = json.loads(stdout)
    return result


##############################################################################
# ##name  :      get_version_baseon_package_name
# ##parameter:   package_name, e.g.parastor-3.0.0-centos7.5-feature_XSTOR1000-
#                113-2018-01-cnas_8be330c_20180720_103801-2-1.tar.xz
#
# ##author:      liujx
# ##date  :      2018.07.23
# ##Description: 根据升级包的名字得到升级版本和兼容的最小版本
##############################################################################
def get_version_baseon_package_name(package_name):
    version = int(package_name[-10])
    min_version = int(package_name[-8])
    return version, min_version


##############################################################################
# ##name  :      get_system_package_time
# ##parameter:
# ##author:      liujx
# ##date  :      2017.08.02
# ##Description: 获取系统正在运行的包的日期版本 e.g. 20180801_174109
##############################################################################
def get_system_package_time():
    rc, stdout = common.get_package_time()
    common.judge_rc(rc, 0, "Execute command: get_package_time failed. \nstdout: %s" % (stdout))
    result = common.json_loads(stdout)
    system_package_time_str = result['result']['package_time']
    system_package_time = system_package_time_str.split('_')[0] + '_' + system_package_time_str.split('_')[1]
    return system_package_time


##############################################################################
# ##name  :      set_system_package_time
# ##parameter:
# ##author:      liujx
# ##date  :      2017.08.02
# ##Description: 修改系统包的时间戳 e.g. 20180801_174109 ->20170101_000000
##############################################################################
def set_system_package_time(system_package_time='20170101_000000'):
    rc, stdout = common.set_package_time(package_time=system_package_time)
    common.judge_rc(rc, 0, "Execute command: set_package_time failed. \nstdout: %s" % (stdout))
    return


##############################################################################
# ##name  :      delete_upgrade
# ##parameter:
# ##author:      liujx
# ##date  :      2017.07.27
# ##Description: 删除/home/parastor/upgrade/目录
##############################################################################
def delete_upgrade():
    nodes = get_config.get_allparastor_ips()
    cmd = 'rm -rf /home/parastor/upgrade/*'
    for node in nodes:
        rc, stdout = common.run_command(node, cmd)
        if rc != 0:
            raise Exception('run_command failed\ncmd=%s\nstdout=%s' % (cmd, stdout))
    return


def get_nonupgrade_list():
    """
    :author:            liujx
    :date:              2018.07.30
    :description:       获取未升级节点
    :return:
    """
    stdout = get_upgrade_info()
    nodes_nonupgrade_id = []
    nodes_for_upgrade = stdout['result']['nodes_for_upgrade']
    for node in nodes_for_upgrade:
        if node['node_upgrade_stage'] == 'NODE_UPGRADE_STAGE_INIT':
            nodes_nonupgrade_id.append(node['node_id'])
    if nodes_nonupgrade_id == []:
        log.info("there is no nonupgrade node")
        return -1
    return nodes_nonupgrade_id


def get_upgraded_list():
    """
    :author:            liujx
    :date:              2018.07.30
    :description:       获取已升级节点
    :return:
    """
    stdout = get_upgrade_info()
    nodes_upgraded_id = []
    nodes_for_upgrade = stdout['result']['nodes_for_upgrade']
    for node in nodes_for_upgrade:
        if node['node_upgrade_stage'] == 'NODE_UPGRADE_STAGE_COMPLETED':
            nodes_upgraded_id.append(node['node_id'])
    if nodes_upgraded_id == []:
        log.info("there is no upgraded node")
        return -1
    return nodes_upgraded_id


def get_upgrading_list():
    """
    :author:            liujx
    :date:              2018.07.30
    :description:       获取正在升级的节点
    :return:
    """
    stdout = get_upgrade_info()
    nodes_upgrading_id = []
    nodes_for_upgrade = stdout['result']['nodes_for_upgrade']
    for node in nodes_for_upgrade:
        if node['node_upgrade_stage'] == 'NODE_UPGRADE_STAGE_AUTO_UPGRADE' \
                or node['node_upgrade_stage'] == 'NODE_UPGRADE_STAGE_MAINTAIN_OFFLINE':
            nodes_upgrading_id.append(node['node_id'])
    if nodes_upgrading_id == []:
        log.info("there is no upgrading node")
        return -1
    return nodes_upgrading_id


def online_upgrade(upgrade_stat_output=True):
    """
    :author:  liujx
    :date:  2018.08.13
    :description:  online_upgrade
    :param upgrade_stat_output:   选择是否显示升级状态
    :return:
    """
    nodes = get_config.get_allparastor_ips()  # 获取集群ip
    package_ip = get_config.get_upgrade_package_ip()  # 升级包所在ip
    package_path = get_config.get_upgrade_package_path()
    # 升级包路径 e.g./root/ofs3.0/ParaStor3.0.0_20180801_2/
    #              parastor-3.0.0-centos7.5-feature_ofs3.0_lastdebug_96d473b_20180801_174109-2-1.tar.xz
    package_name = os.path.basename(package_path)
    # 升级包名称 e.g.parastor-3.0.0-centos7.5-feature_ofs3.0_lastdebug_96d473b_20180801_174109-2-1.tar.xz
    version, min_version = get_version_baseon_package_name(package_name)
    # 根据升级包获取version以及最小兼容版本minversion
    system_version = int(get_system_version())  # 获取系统运行包的版本
    upgrade_package_time = get_config.get_upgrade_package_time()  # 升级包时间 e.g.20180801174109
    system_package_time = get_system_package_time()  # 系统运行包日期版本 e.g.20180801768

    """
        先检查升级包版本是否新与当前版本
        若包的日期小于系统包日期，则不进行升级
        若两者一致，则修改当前系统版本号进行同包更新
        若包的日期大于系统包日期，则判断是否兼容
        """
    if upgrade_package_time < system_package_time:
        log.info("#########版本过低，请检查升级包版本##########")
        return -2
    elif upgrade_package_time == system_package_time:
        log.info("##########修改系统包日期，即将升级##########")
        set_system_package_time()
    elif upgrade_package_time > system_package_time:
        if system_version < min_version:
            log.info("system version:%d is lowwer than the package's min compatible version of package: %d"
                     % (system_version, min_version))
            return -2
        elif system_version >= min_version and system_version > version:
            log.info("this package's capatible version is %s, but you system version is %s" % (version,
                                                                                               system_version))
            return -2
        elif system_version >= min_version and system_version <= version:
            log.info("###############系统即将升级###############")

    """升级前检查"""
    log.info("################升级前检查#################")
    stdout = check_before_upgrade()
    # check_result = common.json_loads(stdout)
    error_info = []
    for item in stdout['result']['service_items']:
        if item['items'][0]['suggestion'] != "":
            info = json.dumps(item)
            error_info.append(info)
    if error_info != []:
        log.info("###there is some problems in the system may cause upgrade failed###")
        for item in error_info:
            log.info(item)

    """分发安装包"""
    log.info("################分发安装包#################")
    distribute_package(package_ip, package_path)

    """执行升级"""
    # upgrade_common.online_upgrade(package_ip, package_name, upgrade_package_time)
    log.info("################开始在线升级###############")
    process_upgrade_online = Process(target=ext_online_upgrade, args=(package_ip, package_name,
                                                                      upgrade_package_time))
    process_upgrade_online.start()
    time.sleep(10)

    """检查升级状态"""
    if upgrade_stat_output is True:
        log.info("################检查升级状态###############")
        upgrade_time = 10
        time_begin = time.time()
        while process_upgrade_online.is_alive():
            upgrade_info = get_upgrade_info()
            if upgrade_info['result']['upgrade_state'] == 'UPGRADE_STATE_UPGRADING':
                log.info("################系统正在升级中###############")
                log.info("#############升级进度：%s percent############" % upgrade_info['result']['upgraded_percent'])
                log.info("################升级用时：%ds###############" % upgrade_time)
            elif upgrade_info['result']['upgrade_state'] == 'UPGRADE_STATE_PREPARE':
                break
            time.sleep(120)
            upgrade_time = time.time() - time_begin

    process_upgrade_online.join()
    if process_upgrade_online.exitcode != 0:
        return -1

    log.info("################升级结束################")

    return 0


def ext_offline_upgrade(node_ip, package_name, package_time, upgrade_item=upgrade_item_default):
    """
    :author:  liujx
    :date:  2018.08.13
    :description: 执行离线升级命令
    :param node_ip:   执行命令的节点
    :param package_name:   升级包的名字
    :param package_time:   升级包的时间
    :param upgrade_item:   升级项
    :return:
    """
    version = package_name[-10]
    min_version = package_name[-8]
    # node = common.Node()
    # if upgrade_item == 'server':
    #    upgrade_num = int(node.get_nodes_num())
    # elif upgrade_item == 'client':
    #    upgrade_num = len(node.get_external_client_ips())
    # else:
    #     upgrade_num = int(node.get_nodes_num()) + len(node.get_external_client_ips())
    upgrade_timeout = 3600  # upgrade_num*30min
    rc, stdout = common.offline_upgrade(version=version, min_version=min_version, package_time=package_time,
                                        upgrade_item=upgrade_item, timeout_pscli=upgrade_timeout)
    result = common.json_loads(stdout)
    return rc, result


def offline_upgrade():
    """
    :author:  liujx
    :date:  2018.08.13
    :description:  offline_upgrade
    :return:
    """
    package_ip = get_config.get_upgrade_package_ip()  # 升级包所在ip
    package_path = get_config.get_upgrade_package_path()
    # 升级包路径 e.g./root/ofs3.0/ParaStor3.0.0_20180801_2/
    #              parastor-3.0.0-centos7.5-feature_ofs3.0_lastdebug_96d473b_20180801_174109-2-1.tar.xz
    package_name = os.path.basename(package_path)
    # 升级包名称 e.g.parastor-3.0.0-centos7.5-feature_ofs3.0_lastdebug_96d473b_20180801_174109-2-1.tar.xz
    version, min_version = get_version_baseon_package_name(package_name)
    # 根据升级包获取version以及最小兼容版本minversion
    system_version = int(get_system_version())  # 获取系统运行包的版本
    upgrade_package_time = get_config.get_upgrade_package_time()  # 升级包时间 e.g.20180801174109
    system_package_time = get_system_package_time()  # 系统运行包日期版本 e.g.20180801768

    """
    先检查升级包版本是否新与当前版本
    若包的日期小于系统包日期，则不进行升级
    若两者一致，则修改当前系统版本号进行同包更新
    若包的日期大于系统包日期，则判断是否兼容
    """
    if upgrade_package_time < system_package_time:
        log.info("#########版本过低，请检查升级包版本##########")
        return -2
    elif upgrade_package_time == system_package_time:
        log.info("##########修改系统包日期，即将升级##########")
        set_system_package_time()
    elif upgrade_package_time > system_package_time:
        if system_version < min_version:
            log.info("system version:%d is lowwer than the package's min compatible version of package: %d"
                     % (system_version, min_version))
            return -2
        elif system_version >= min_version and system_version > version:
            log.info("this package's capatible version is %s, but you system version is %s" % (version,
                                                                                               system_version))
            return -2
        elif system_version >= min_version and system_version <= version:
            log.info("###############系统即将升级###############")
    """shutdown系统"""
    log.info("###############关闭系统###############")
    cmd = 'pscli --command=shutdown'
    rc, stdout = common.pscli_run_command(cmd)
    if rc != 0:
        common.except_exit('shutdown failed, stdout=%s' % stdout)

    """分发安装包"""
    log.info("################分发安装包#################")
    distribute_package(package_ip, package_path)

    """离线升级系统"""
    process_upgrade_offline = Process(target=ext_offline_upgrade, args=(package_ip, package_name, upgrade_package_time))
    process_upgrade_offline.start()

    """检查升级状态"""
    log.info("################检查升级状态###############")
    upgrade_time = 10
    time_begin = time.time()
    while process_upgrade_offline.is_alive():
        upgrade_info = get_upgrade_info()
        if upgrade_info['result']['upgrade_stage'] == 'UPGRADE_STAGE_UPGRADING':
            log.info("################系统正在离线升级中###############")
            log.info("################升级用时：%ds###############" % upgrade_time)
        elif upgrade_info['result']['upgrade_stage'] == 'UPGRADE_STATE_PREPARE':
            break
        time.sleep(60)
        upgrade_time = time.time() - time_begin

    process_upgrade_offline.join()
    if process_upgrade_offline.exitcode != 0:
        common.except_exit('online_upgrade failed')

    log.info("################升级结束################")
    if process_upgrade_offline.exitcode != 0:
        return -1

    """startup系统"""
    log.info("###############关闭系统###############")
    cmd = 'pscli --command=startup'
    rc, stdout = common.pscli_run_command(cmd)
    if rc != 0:
        common.except_exit('startup failed, stdout=%s' % stdout)

    return 0
