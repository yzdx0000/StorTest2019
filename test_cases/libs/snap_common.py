#!/usr/bin/python
# -*- encoding=utf8 -*-

#######################################################
# 脚本作者：鲍若冰
# 脚本说明：快照公共函数
#######################################################

import os
import time
import log
import get_config
import common

SNAP_PATH = get_config.get_one_snap_test_path()
BASE_SNAP_PATH = os.path.dirname(SNAP_PATH)   # BASE_QUOTA_PATH = "/mnt/volume1"
SNAP_PATH_BASENAME = os.path.basename(SNAP_PATH)  # QUOTA_PATH_BASENAME = "snap"
SNAP_PATH_ABSPATH = os.path.abspath(SNAP_PATH)    # QUOTA_PATH_ABSPATH = "/mnt/volume1/snap"

SNAPSHOT_PAHT = os.path.join(BASE_SNAP_PATH, '.snapshot')   # SNAPSHOT_PAHT = "/mnt/volume1/.snapshot"

SNAP_USER = "snap_user"
SNAP_OTHER_USER = "snap_other_user"
SNAP_GROUP = "snap_group"
SNAP_OTHER_GROUP = "snap_other_group"

'''结群节点ip'''
SYSTEM_IP = get_config.get_parastor_ip()

'''客户端节点ip'''
CLIENT_IP_1 = get_config.get_client_ip()
CLIENT_IP_2 = get_config.get_client_ip(1)
CLIENT_IP_3 = get_config.get_client_ip(2)

'''快照卷'''
VOLUME_NAME = get_config.get_one_volume_name()


##############################################################################
# ##name  :      get_current_time
# ##parameter:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 获取环境的当前时间
##############################################################################
def get_current_time(ext_node_ip=None):
    cmd = 'date +%s'
    if ext_node_ip == None:
        ext_node_ip = SYSTEM_IP
    rc, stdout = common.run_command(ext_node_ip, cmd)
    return rc, stdout


##############################################################################
# ##name  :      create_snapshot
# ##parameter:   name:快照名字, path:路径, expire_time:超时时间，默认为0，不超时
# ##             description:快照描述
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 创建快照
##############################################################################
def create_snapshot(name, path, expire_time=0, description=None, fault_node_ip=None):
    rc, stdout = common.create_snapshot(name=name, path=path, expire_time=expire_time, description=description,
                                        fault_node_ip=fault_node_ip)
    return rc, stdout


##############################################################################
# ##name  :      get_snapshot_by_name
# ##parameter:   name:快照名字
# ##return:      -1:没有找到快照 snapshot:快照信息，字典
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 通过名字获取快照信息
##############################################################################
def get_snapshot_by_name(name, fault_node_ip=None):
    rc, stdout = common.get_snapshot(param_name='name', param_value=name, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, "Execute command: get snapshot failed. \nstdout: %s" % (stdout))
    stdout = common.json_loads(stdout)
    if stdout['result']['total'] == 0:
        return -1
    else:
        snapshots = stdout['result']['snapshots']
        for snapshot in snapshots:
            if snapshot['name'] != name:
                continue
            else:
                return snapshot
    return -1


##############################################################################
# ##name  :      get_snapshot_by_path
# ##parameter:   path:快照路径
# ##return:      -1:没有找到快照 snapshot:快照信息，字典
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 通过路径获取快照信息
##############################################################################
def get_snapshot_by_path(path):
    rc, stdout = common.get_snapshot(param_name='path', param_value=path)
    common.judge_rc(rc, 0, "Execute command: get_snapshot failed. \nstdout: %s" % (stdout))
    stdout = common.json_loads(stdout)
    if stdout['result']['total'] == 0:
        return -1
    else:
        snapshots = stdout['result']['snapshots']
        for snapshot in snapshots:
            if snapshot['path'] != path:
                continue
            else:
                return snapshot
    return -1


##############################################################################
# ##name  :      get_snapshot_ids_by_name
# ##parameter:   name:快照名字
# ##return:      -1:没有找到快照 snapshot_id_lst:名字包含name的所有快照id
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 通过名字获取快照id
##############################################################################
def get_snapshot_ids_by_name(name, fault_node_ip=None):
    snapshot_id_lst = []
    rc, stdout = common.get_snapshot(param_name='name', param_value=name, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, "Execute command: get_snapshot failed. \nstdout: %s" % (stdout))
    stdout = common.json_loads(stdout)
    if stdout['result']['total'] == 0:
        return -1, []
    else:
        snapshots = stdout['result']['snapshots']
        for snapshot in snapshots:
            if snapshot['state'] != 'SNAPSHOT_DELETING':
                snapshot_id_lst.append(snapshot['id'])
        return 0, snapshot_id_lst


##############################################################################
# ##name  :      get_snapshot_ids_by_path
# ##parameter:   path:快照路径
# ##return:      -1:没有找到快照 snapshot_id_lst:名字包含name的所有快照id
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 通过路径获取快照id
##############################################################################
def get_snapshot_ids_by_path(path, fault_node_ip=None):
    snapshot_id_lst = []
    rc, stdout = common.get_snapshot(param_name='path', param_value=path, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, "Execute command: get_snapshot failed. \nstdout: %s" % (stdout))
    stdout = common.json_loads(stdout)
    if stdout['result']['total'] == 0:
        return -1, []
    else:
        snapshots = stdout['result']['snapshots']
        for snapshot in snapshots:
            if snapshot['state'] != 'SNAPSHOT_DELETING':
                snapshot_id_lst.append(snapshot['id'])
        return 0, snapshot_id_lst


##############################################################################
# ##name  :      get_snapshot_num
# ##parameter:
# ##return:      集群中快照个数
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 获取集群中快照的个数
##############################################################################
def get_snapshot_num(fault_node_ip=None):
    rc, stdout = common.get_snapshot(fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, "Execute command: get_snapshot failed. \nstdout: %s" % (stdout))
    stdout = common.json_loads(stdout)
    return stdout['result']['total']


def get_all_snapshot(ids=None, param_name=None, param_value=None):
    """
    :name:        baoruobing
    :date:        2018.11.03
    :description: 获取所有快照内容
    :return:
    """
    rc, stdout = common.get_snapshot(ids=ids, param_name=param_name, param_value=param_value)
    common.judge_rc(rc, 0, "Execute command: get_snapshot failed. \nstdout: %s" % (stdout))
    stdout = common.json_loads(stdout)
    return stdout


##############################################################################
# ##name  :      update_snapshot
# ##parameter:   id:快照id, expire_time:超时时间, description:快照描述
# ##return:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 修改快照
##############################################################################
def update_snapshot(id, expire_time=0, description=None, fault_node_ip=None):
    rc, stdout = common.update_snapshot(id=id, expire_time=expire_time, description=description,
                                        fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, "Execute command: update_snapshot failed. \nstdout: %s" % (stdout), exit_flag=False)
    return rc


##############################################################################
# ##name  :      delete_snapshot_by_ids
# ##parameter:   ids:快照id
# ##return:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 根据id删除快照
##############################################################################
def delete_snapshot_by_ids(ids, fault_node_ip=None):
    rc, stdout = common.delete_snapshot(ids=ids, fault_node_ip=fault_node_ip)
    return rc, stdout


##############################################################################
# ##name  :      delete_snapshot_by_name
# ##parameter:   name:快照名字
# ##return:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 根据名字删除快照
##############################################################################
def delete_snapshot_by_name(name, fault_node_ip=None):
    rc, snapshot_id_lst = get_snapshot_ids_by_name(name, fault_node_ip=fault_node_ip)
    if -1 == rc or snapshot_id_lst == []:
        return 0, None
    snapshot_id_str = ','.join(str(i) for i in snapshot_id_lst)
    rc, stdout = delete_snapshot_by_ids(snapshot_id_str, fault_node_ip=fault_node_ip)
    return rc, stdout


##############################################################################
# ##name  :      delete_snapshot_by_path
# ##parameter:   path:快照路径
# ##return:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 根据路径删除快照
##############################################################################
def delete_snapshot_by_path(path):
    rc, snapshot_id_lst = get_snapshot_ids_by_path(path)
    if -1 == rc:
        return 0, None
    snapshot_id_str = ','.join(str(i) for i in snapshot_id_lst)
    rc, stdout = delete_snapshot_by_ids(snapshot_id_str)
    return rc, stdout


def check_snap_exist(name):
    """
    :author:            baoruobing
    :param name:        快照名字
    :return:            True:快照存在 False:快照不存在
    :date  :            2018.06.08
    :description:       检查包含name的快照是否存在
    """
    rc, stdout = common.get_snapshot(param_name='name', param_value=name)
    common.judge_rc(rc, 0, "Execute command: get_snapshot failed. \nstdout: %s" % (stdout))
    stdout = common.json_loads(stdout)
    if stdout['result']['total'] == 0:
        return False
    else:
        snapshots = stdout['result']['snapshots']
        for snapshot in snapshots:
            if name not in snapshot['name']:
                continue
            else:
                return True
    return False


def wait_snap_del_by_name(part_name):
    """
    :author:          baoruobing
    :param part_name: 名字包含part_name的快照
    :return: 
    :date  :          2018.06.08
    :description:     等待名字包含part_name的快照完全删除
    """
    start_time = time.time()
    while True:
        time.sleep(5)
        rc = check_snap_exist(part_name)
        if rc:
            exist_time = int(time.time() - start_time)
            m, s = divmod(exist_time, 60)
            h, m = divmod(m, 60)
            log.info('%dh:%dm:%ds, snapshot %s still not delete!' % (h, m, s, part_name))
        else:
            break
    return


def create_snapstrategy(name, path, period_type, months=None, week_days=None, days=None, hours=None, minute=None,
                        expire_time=None, description=None):
    """
    :author:            baoruobing
    :date  :            2018.06.08
    :description:       创建快照策略
    :param name:        快照策略名字
    :param path:        创建快照策略的路径
    :param period_type: 周期策略
    :param months:      月份
    :param week_days:   星期几
    :param days:        日期
    :param hours:       小时
    :param minute:      分钟
    :param expire_time: 超时时间
    :param description: 描述
    :return:
    """
    rc, stdout = common.create_snapshot_strategy(name=name, path=path, period_type=period_type, months=months,
                                                 week_days=week_days, days=days, hours=hours, minute=minute,
                                                 expire_time=expire_time, description=description)
    return rc, stdout


def update_snapstrategy(id, period_type, months=None, week_days=None, days=None, hours=None, minute=None,
                        expire_time=None, description=None):
    """
    :author:            baoruobing
    :date  :            2018.06.08
    :description:       创建快照策略
    :param id:          快照策略id
    :param period_type: 周期策略
    :param months:      月份
    :param week_days:   星期几
    :param days:        日期
    :param hours:       小时
    :param minute:      分钟
    :param expire_time: 超时时间
    :param description: 描述
    :return:
    """
    rc, stdout = common.update_snapshot_strategy(id=id, period_type=period_type, months=months, week_days=week_days,
                                                 days=days, hours=hours, minute=minute, expire_time=expire_time,
                                                 description=description)
    return rc, stdout


def check_snapstrategy_exist(name):
    """
    :author:            baoruobing
    :param name:        快照策略名字
    :return:            True:快照策略存在 False:快照策略不存在
    :date  :            2018.06.08
    :description:       等待名字包含part_name的快照策略完全删除
    """
    rc, stdout = common.get_snapshot_strategy(param_name='name', param_value=name)
    common.judge_rc(rc, 0, "Execute command: get_snapshot_strategy failed. \nstdout: %s" % (stdout))
    stdout = common.json_loads(stdout)
    if stdout['result']['total'] == 0:
        return False
    else:
        snapstrategys = stdout['result']['snapshot_strategies']
        for snapstrategy in snapstrategys:
            if name not in snapstrategy['name']:
                continue
            else:
                return True
    return False


def wait_snapstrategy_del_by_name(part_name):
    """
    :author:          baoruobing
    :param part_name: 名字包含part_name的快照策略
    :return: 
    :date  :          2018.06.08
    :description:     等待名字包含part_name的快照策略完全删除
    """
    start_time = time.time()
    while True:
        time.sleep(5)
        rc = check_snapstrategy_exist(part_name)
        if rc:
            exist_time = int(time.time() - start_time)
            m, s = divmod(exist_time, 60)
            h, m = divmod(m, 60)
            log.info('%dh:%dm:%ds, snapshotstrategy %s still not delete!' % (h, m, s, part_name))
        else:
            break
    return


def get_all_snapshotstrategy(fault_node_ip=None):
    """
    name: get_all_snapshotstrategy
    author: liyao
    description: 获取集群中所有快照策略的信息
    :return:
    """
    rc, stdout = common.get_snapshot_strategy(fault_node_ip=fault_node_ip)
    if rc != 0:
        log.error('Execute command: get_snapshot_strategy failed. \nstdout: %s' % stdout)
        return -1
    stdout = common.json_loads(stdout)
    return stdout


##############################################################################
# ##name  :      get_snapshotstrategy_by_name
# ##parameter:   name:快照策略名字
# ##return:      -1:没有找到快照 snapshot:快照策略信息，字典
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 通过名字获取快照策略信息
##############################################################################
def get_snapshotstrategy_by_name(name, fault_node_ip=None):
    rc, stdout = common.get_snapshot_strategy(param_name='name', param_value=name, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, "Execute command: get_snapshot_strategy failed. \nstdout: %s" % (stdout))
    stdout = common.json_loads(stdout)
    if stdout['result']['total'] == 0:
        return -1
    else:
        snapshot_strategys = stdout['result']['snapshot_strategies']
        for snapshot_strategy in snapshot_strategys:
            if snapshot_strategy['name'] != name:
                continue
            else:
                return snapshot_strategy
    return -1


##############################################################################
# ##name  :      get_snapshotstrategy_ids_by_name
# ##parameter:   name:快照名字
# ##return:      -1:没有找到快照策略 snapshotstrategy_id_lst:名字包含name的所有快照策略id
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 通过名字获取快照策略id
##############################################################################
def get_snapshotstrategy_ids_by_name(name):
    snapshot_strategy_id_lst = []
    rc, stdout = common.get_snapshot_strategy(param_name='name', param_value=name)
    common.judge_rc(rc, 0, "Execute command: get_snapshot_strategy failed. \nstdout: %s" % (stdout))
    stdout = common.json_loads(stdout)
    if stdout['result']['total'] == 0:
        return -1, []
    else:
        snapshot_strategies = stdout['result']['snapshot_strategies']
        for snapshot_strategy in snapshot_strategies:
            snapshot_strategy_id_lst.append(snapshot_strategy['id'])
        return 0, snapshot_strategy_id_lst


##############################################################################
# ##name  :      get_snapshotstrategy_ids_by_path
# ##parameter:   path:快照路径
# ##return:      -1:没有找到快照策略 snapshotstrategy_id_lst:名字包含name的所有快照策略id
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 通过路径获取快照策略id
##############################################################################
def get_snapshotstrategy_ids_by_path(path):
    snapshot_strategy_id_lst = []
    rc, stdout = common.get_snapshot_strategy(param_name='path', param_value=path)
    common.judge_rc(rc, 0, "Execute command: get_snapshot_strategy failed. \nstdout: %s" % (stdout))
    stdout = common.json_loads(stdout)
    if stdout['result']['total'] == 0:
        return -1, []
    else:
        snapshot_strategies = stdout['result']['snapshot_strategies']
        for snapshot_strategy in snapshot_strategies:
            snapshot_strategy_id_lst.append(snapshot_strategy['id'])
        return 0, snapshot_strategy_id_lst


##############################################################################
# ##name  :      delete_snapshotstrategy_by_ids
# ##parameter:   ids:快照策略id
# ##return:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 根据id删除快照策略
##############################################################################
def delete_snapshotstrategy_by_ids(ids):
    rc, stdout = common.delete_snapshot_strategy(ids=ids)
    return rc, stdout


##############################################################################
# ##name  :      delete_snapshotstrategy_by_name
# ##parameter:   name:快照策略名字
# ##return:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 根据名字删除快照策略
##############################################################################
def delete_snapshotstrategy_by_name(name):
    rc, snapshotstrategy_id_lst = get_snapshotstrategy_ids_by_name(name)
    if -1 == rc:
        return rc, None
    snapshotstrategy_id_str = ','.join(str(i) for i in snapshotstrategy_id_lst)
    rc, stdout = delete_snapshotstrategy_by_ids(snapshotstrategy_id_str)
    return rc, stdout


##############################################################################
# ##name  :      delete_snapshotstrategy_by_path
# ##parameter:   path:快照路径
# ##return:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 根据路径删除快照策略
##############################################################################
def delete_snapshotstrategy_by_path(path):
    rc, snapshotstrategy_id_lst = get_snapshotstrategy_ids_by_path(path)
    if -1 == rc:
        return
    snapshotstrategy_id_str = ','.join(str(i) for i in snapshotstrategy_id_lst)
    rc, stdout = delete_snapshotstrategy_by_ids(snapshotstrategy_id_str)
    return rc, stdout


##############################################################################
# ##name  :      revert_snapshot_by_id
# ##parameter:   snap_id:快照id
# ##return:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 根据快照id对快照进行revert
##############################################################################
def revert_snapshot_by_id(snap_id, fault_node_ip=None):
    rc, stdout = common.revert_snapshot(snapshot_id=snap_id, fault_node_ip=fault_node_ip)
    return rc, stdout


##############################################################################
# ##name  :      revert_snapshot_by_name
# ##parameter:   snap_name:快照名字
# ##return:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 根据快照名字对快照进行revert
##############################################################################
def revert_snapshot_by_name(snap_name):
    snap_info = get_snapshot_by_name(snap_name)
    snap_id = snap_info['id']
    rc, stdout = revert_snapshot_by_id(snap_id)
    return rc, stdout


##############################################################################
# ##name  :      check_revert_finished
# ##parameter:   snap_id:快照id
# ##return:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 不断检查快照revert是否完成
##############################################################################
def check_revert_finished(snap_id, fault_node_ip=None):
    num = 0
    while True:
        rc, stdout = common.get_revert_snapshot(fault_node_ip=fault_node_ip)
        common.judge_rc(rc, 0, "Execute command: get_revert_snapshot failed. \nstdout: %s" % (stdout), exit_flag=False)
        stdout = common.json_loads(stdout)
        revertsnapshots = stdout['result']['revertSnapshots']
        for revertSnapshot in revertsnapshots:
            if revertSnapshot['snapshot_id'] != int(snap_id):
                continue
            if revertSnapshot['state'] != 'FINISHED':
                log.info('wait %ds state is not FINISHED' % num)
                time.sleep(2)
                num += 1
                break
        else:
            return


##############################################################################
# ##name  :      get_revert_snapshot_ids
# ##parameter:
# ##return:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 获取revert_snapshot的id
##############################################################################
def get_revert_snapshot_ids():
    revert_snapshot_ids = []
    rc, stdout = common.get_revert_snapshot()
    common.judge_rc(rc, 0, "Execute command: get_revert_snapshot failed. \nstdout: %s" % (stdout))
    stdout = common.json_loads(stdout)
    if stdout['result']['total'] == 0:
        return -1, []
    else:
        revert_snapshots = stdout['result']['revertSnapshots']
        for revert_snapshot in revert_snapshots:
            revert_snapshot_ids.append(revert_snapshot['revert_id'])
        return 0, revert_snapshot_ids


def get_revert_snapshot():
    """
    Author:liangxy
    date:2018-08-11
    description:获取快照回滚信息
    :param ext_node_ip:执行命令的ip
    :return:命令执行的返回值和标准输出内容的自典型变量
    """
    rc, stdout = common.get_revert_snapshot()
    stdout = common.json_loads(stdout)
    if 0 != rc:
        return rc, stdout
    else:
        return 0, stdout


##############################################################################
# ##name  :      delete_revert_snapshot
# ##parameter:
# ##return:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 删除所有revert_snapshot
##############################################################################
def delete_revert_snapshot():
    rc, revert_snapshot_ids = get_revert_snapshot_ids()
    if -1 == rc:
        return
    revert_snapshot_id_str = ','.join(str(i) for i in revert_snapshot_ids)
    rc, stdout = common.delete_revert_snapshot(ids=revert_snapshot_id_str)
    return rc, stdout


def delete_revert_snapshot_by_id(id):
    """
    :author:      baoruobing
    :date:        2018.08.11
    :description: 通过id删除快照revert记录
    :param id:    快照revert id
    :return:
    """
    rc, stdout = common.delete_revert_snapshot(ids=id)
    return rc, stdout


##############################################################################
# ##name  :      get_all_clients_ip
# ##parameter:
# ##return:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 获取所有客户端的节点ip
##############################################################################
def get_all_clients_ip():
    clients_ip = []
    rc, stdout = common.get_clients()
    common.judge_rc(rc, 0, "Execute command: get_clients failed. \nstdout: %s" % (stdout))
    node_info = common.json_loads(stdout)
    nodes = node_info['result']
    for node in nodes:
        clients_ip.append(node['ip'])
    return clients_ip


##############################################################################
# ##name  :      mkdir_snap_path
# ##parameter:
# ##return:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 创建快照总目录
##############################################################################
def mkdir_snap_path():
    cmd = 'ls %s' % SNAP_PATH
    rc, stdout = common.run_command(CLIENT_IP_1, cmd)
    if 0 == rc:
        log.info('%s is exist!' % SNAP_PATH)
        return
    cmd = 'mkdir %s' % SNAP_PATH
    rc, stdout = common.run_command(CLIENT_IP_1, cmd)
    common.judge_rc(rc, 0, '%s mkdir faild!!!' % SNAP_PATH)
    return


##############################################################################
# ##name  :      create_snap_path
# ##parameter:   path:快照路径
# ##return:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 创建用例快照目录
##############################################################################
def create_snap_path(path):
    # 创建快照总路径
    mkdir_snap_path()

    # 创建本用例的快照路径
    cmd = 'mkdir %s' % path
    rc, stdout = common.run_command(CLIENT_IP_1, cmd)
    common.judge_rc(rc, 0, '%s failed!!!' % cmd)
    return


##############################################################################
# ##name  :      delete_snap_path
# ##parameter:   path:快照路径
# ##return:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 删除用例快照目录
##############################################################################
def delete_snap_path(path):
    # 删除本用例创建的目录
    # if '13' not in path:
    #    log.error('%s is not right' % path)
    #    return
    common.rm_exe(CLIENT_IP_1, path)
    return


##############################################################################
# ##name  :      cleaning_environment
# ##parameter:   snap_path:创建快照时写的路径
# ##             true_path:快照路径的完整路径
# ##return:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 清理本脚本的环境
##############################################################################
def cleaning_environment(snap_name, true_path, wait_flag=True):
    # 删除快照策略
    delete_snapshotstrategy_by_name(snap_name)
    # 删除快照
    delete_snapshot_by_name(snap_name)
    # 删除所有revert记录
    delete_revert_snapshot()

    if wait_flag is True:
        log.info("wait 10s")
        time.sleep(10)

    # 删除本用例快照目录
    delete_snap_path(true_path)
    # 删除客户端1上的用户和用户组
    # delete_all_snap_user_and_group(CLIENT_IP_1)
    # 用户和用户组文件拷到其他客户端
    # scp_passwd_and_group_to_all_other_nodes(CLIENT_IP_1)
    return


##############################################################################
# ##name  :      get_file_md5
# ##parameter:   nodeip:节点ip
# ##             file_path:文件完整路径
# ##return:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 获取一个文件的md5值
##############################################################################
def get_file_md5(nodeip, file_path):
    cmd = 'md5sum %s' % file_path
    rc, stdout = common.run_command(nodeip, cmd)
    md5 = stdout.strip().split()[0]
    return rc, md5


##############################################################################
# ##name  :      check_snap_md5
# ##parameter:   md5_value:md5的值
# ##             file_path:文件完整路径
# ##return:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 比较三个客户端的快照文件的md5值和源文件的md5值
##############################################################################
def check_snap_md5(md5_value, file_path):
    rc, file_md5_1_1 = get_file_md5(CLIENT_IP_1, file_path)
    common.judge_rc(file_md5_1_1, md5_value,
                    "md5_source is %s, md5_snap is %s\n%s %s is not right!!!"
                    % (md5_value, file_md5_1_1, CLIENT_IP_1, file_path))
    rc, file_md5_1_2 = get_file_md5(CLIENT_IP_2, file_path)
    common.judge_rc(file_md5_1_2, md5_value,
                    "md5_source is %s, md5_snap is %s\n%s %s is not right!!!"
                    % (md5_value, file_md5_1_2, CLIENT_IP_2, file_path))
    rc, file_md5_1_3 = get_file_md5(CLIENT_IP_3, file_path)
    common.judge_rc(file_md5_1_3, md5_value,
                    "md5_source is %s, md5_snap is %s\n%s %s is not right!!!"
                    % (md5_value, file_md5_1_3, CLIENT_IP_3, file_path))
    return


##############################################################################
# ##name  :      get_file_permission
# ##parameter:   nodeip:节点ip
# ##             file_path:文件完整路径
# ##return:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 获取一个文件的数字权限
##############################################################################
def get_file_permission(nodeip, file_path):
    cmd = 'stat -c %a ' + file_path
    rc, stdout = common.run_command(nodeip, cmd)
    return rc, stdout.strip()


##############################################################################
# ##name  :      check_snap_entry
# ##parameter:   snap_path:快照路径入口
# ##return:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 3个客户端检查快照路径入口是否存在
##############################################################################
def check_snap_entry(snap_path):
    time.sleep(15)
    check_snap_cmd = 'ls %s' % snap_path
    rc, stdout = common.run_command(CLIENT_IP_1, check_snap_cmd)
    common.judge_rc_unequal(rc, 0, 'snap deleted, but %s %s is exist!!!' % (CLIENT_IP_1, snap_path))
    rc, stdout = common.run_command(CLIENT_IP_2, check_snap_cmd)
    common.judge_rc_unequal(rc, 0, 'snap deleted, but %s %s is exist!!!' % (CLIENT_IP_2, snap_path))
    rc, stdout = common.run_command(CLIENT_IP_3, check_snap_cmd)
    common.judge_rc_unequal(rc, 0, 'snap deleted, but %s %s is exist!!!' % (CLIENT_IP_3, snap_path))
    return


##############################################################################
# ##name  :      create_user_group
# ##parameter:   group_name:用户组名字
# ##return:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 创建用户组
##############################################################################
def create_user_group(node_ip, user_group):
    cmd = "groupadd %s" % (user_group)
    rc, stdout = common.run_command(node_ip, cmd)
    return rc, stdout


##############################################################################
# ##name  :      delete_user_group
# ##parameter:   group_name:用户组名字
# ##return:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 删除用户组
##############################################################################
def delete_user_group(node_ip, user_group):
    cmd = "groupdel %s" % (user_group)
    rc, stdout = common.run_command(node_ip, cmd)
    return rc, stdout


##############################################################################
# ##name  :      create_user
# ##parameter:   user_name:用户 user_group:用户组
# ##return:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 创建用户
##############################################################################
def create_user(node_ip, user_name, user_group):
    cmd = "useradd %s -g %s" % (user_name, user_group)
    rc, stdout = common.run_command(node_ip, cmd)
    return rc, stdout


##############################################################################
# ##name  :      delete_user
# ##parameter:   user_name:用户 user_group:用户组
# ##return:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 删除用户
##############################################################################
def delete_user(node_ip, user_name):
    cmd = "userdel -r -f %s" % (user_name)
    rc, stdout = common.run_command(node_ip, cmd)
    return rc, stdout


##############################################################################
# ##name  :      chown_file_user
# ##parameter:   file_name:文件全路径名字 user_name:用户
# ##return:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 修改文件用户
##############################################################################
def chown_file_user(node_ip, file_name, user_name):
    cmd = "chown %s %s" % (user_name, file_name)
    rc, stdout = common.run_command(node_ip, cmd)
    return rc, stdout


##############################################################################
# ##name  :      chgrp_file_user_group
# ##parameter:   file_name:文件全路径名字 user_name:用户
# ##return:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 修改文件用户组
##############################################################################
def chgrp_file_user_group(node_ip, file_name, group_name):
    cmd = "chgrp %s %s" % (group_name, file_name)
    rc, stdout = common.run_command(node_ip, cmd)
    return rc, stdout


##############################################################################
# ##name  :      get_file_user_and_group
# ##parameter:   file_name:文件全路径名字
# ##return:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 获取文件的用户和用户组
##############################################################################
def get_file_user_and_group(node_ip, file_name):
    cmd = 'ls -l %s' % file_name
    rc, stdout = common.run_command(node_ip, cmd)
    common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    user = stdout.strip().split()[2]
    user_group = stdout.strip().split()[3]
    return user, user_group


##############################################################################
# ##name  :      get_dir_user_and_group
# ##parameter:   dir_name:目录全路径名字
# ##return:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 获取目录的用户和用户组
##############################################################################
def get_dir_user_and_group(node_ip, dir_name):
    parent_dir_path = os.path.dirname(dir_name)
    current_dir = os.path.basename(dir_name)
    cmd = 'ls -l %s' % parent_dir_path
    rc, stdout = common.run_command(node_ip, cmd)
    common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    line_lst = stdout.splitlines()
    for line in line_lst:
        if current_dir in line:
            user = line.strip().split()[2]
            user_group = line.strip().split()[3]
            return user, user_group
    return None, None


##############################################################################
# ##name  :      scp_passwd_and_group_to_all_other_nodes
# ##parameter:
# ##return:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 将用户、用户组文件拷到其他节点
##############################################################################
def scp_passwd_and_group_to_all_other_nodes(node_ip):
    all_clients_and_nodes_ip = get_all_clients_ip()
    for other_node_ip in all_clients_and_nodes_ip:
        cmd = "scp /etc/passwd /etc/group %s:/etc/" % (other_node_ip)
        rc, stdout = common.run_command(node_ip, cmd)
        common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    return


##############################################################################
# ##name  :      delete_all_snap_user_and_group
# ##parameter:
# ##return:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 删除快照的用户和用户组
##############################################################################
def delete_all_snap_user_and_group(node_ip):
    cmd1 = "cat /etc/passwd | grep snap | cut -d \":\" -f 1"
    rc, stdout = common.run_command(node_ip, cmd1)
    common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd1, stdout))
    user_name_list = stdout.split()

    for user_name in user_name_list:
        delete_user(node_ip, user_name)

    cmd2 = "cat /etc/group | grep snap | cut -d \":\" -f 1"
    rc, stdout = common.run_command(node_ip, cmd2)
    common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd2, stdout))
    group_name_list = stdout.split()

    for group_name in group_name_list:
        delete_user_group(node_ip, group_name)
    return


##############################################################################
# ##name  :      get_lmos_node_id
# ##parameter:
# ##return:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 获取lmos节点id
##############################################################################
def get_lmos_node_id():
    rc, stdout = common.get_nodes()
    common.judge_rc(rc, 0, "Execute command: get_nodes failed. \nstdout: %s" % (stdout))
    stdout = common.json_loads(stdout)
    node_id = stdout['result']['nodes'][0]['node_id']
    cmd = "/home/parastor/tools/nWatch -t oRole -i %d -c oRole#rolemgr_view_dump" % node_id
    rc, stdout = common.pscli_run_command(cmd)
    result_lst = stdout.split('\n')
    for line in result_lst:
        if 'node_sn: 0' in line:
            mem_lst = line.split(',')
            for mem in mem_lst:
                if 'node_id' in mem:
                    return mem.split(':')[-1].strip()
    log.warn("There is not mos node!!!")
    return None


##############################################################################
# ##name  :      setfattr_file
# ##parameter:   node_ip:节点ip，file_name:文件名字
#                attribute_name:属性名字， attribute_value:属性内容
# ##return:
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 修改文件的扩展属性
##############################################################################
def setfattr_file(node_ip, file_name, attribute_name, attribute_value):
    cmd = 'setfattr -n %s -v %s %s' % (attribute_name, attribute_value, file_name)
    rc, stdout = common.run_command(node_ip, cmd)
    return rc, stdout


##############################################################################
# ##name  :      getfattr_file
# ##parameter:   node_ip:节点ip，file_name:文件名字
#                attribute_name:属性名字
# ##return:      attribute_value:属性内容
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 获取文件的扩展属性
##############################################################################
def getfattr_file(node_ip, file_name, attribute_name):
    cmd = 'getfattr -n %s %s' % (attribute_name, file_name)
    rc, stdout = common.run_command(node_ip, cmd)
    if rc != 0:
        return rc, stdout
    stdout_lst = stdout.splitlines()
    for line in stdout_lst:
        if attribute_name in line:
            return rc, line.split('=')[-1].strip('"')
    return rc, stdout


##############################################################################
# ##name  :      get_system_disk
# ##parameter:   node_ip:节点ip
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 获取节点系统盘
##############################################################################
def get_system_disk(node_ip):
    cmd = 'df -l'
    rc, stdout = common.run_command(node_ip, cmd)
    common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    line_lst = stdout.splitlines()
    return line_lst[1].split()[0].strip()


##############################################################################
# ##name  :      erasure_snap_size
# ##parameter:   file_size 文件大小
#                stripe_width 条带宽度
#                disk_parity_num 冗余磁盘数
# ##author:      liyao
# ##date  :      2018.05.02
# ##Description: 根据纠删码计算期望的快照空间
##############################################################################
OBJSIZE = 4 * 1024 * 1024    # 各个对象大小为4m
BLOCKSIZE = 4 * 1024         # 一个数据块大小为4k


def erasure_snap_size(file_size, stripe_width, disk_parity_num):
    '''根据纠删码计算期望的快照空间'''

    segment_size = OBJSIZE * (stripe_width + disk_parity_num)   # 包含冗余磁盘的完整段空间大小　
    segment_storage_size = OBJSIZE * stripe_width               # 各段中数据存储容量

    """获取文件 余 段数据大小的值"""
    file_size = file_size % segment_storage_size
    if 0 == file_size:
        return 0

    '''计算全部数据块的数量'''
    block_num_integer = file_size // BLOCKSIZE
    block_num_residue = file_size % BLOCKSIZE
    if block_num_integer <= stripe_width:
        if block_num_residue != 0:
            block_num = block_num_integer + 1
            total_block_num = block_num + disk_parity_num
        else:
            block_num = block_num_integer
            total_block_num = block_num + disk_parity_num
    else:
        '''计算各个对象中数据段均匀分布的层数'''
        block_round_integer = block_num_integer // stripe_width
        block_round_residue = block_num_integer % stripe_width
        if block_num_residue != 0:
            if block_round_residue != 0:
                block_num = stripe_width * block_round_integer + block_round_residue + 1
                total_block_num = block_num + (block_round_integer + 1) * disk_parity_num
            else:
                block_num = stripe_width * block_round_integer + 1
                total_block_num = block_num + (block_round_integer + 1) * disk_parity_num
        else:
            if block_round_residue != 0:
                block_num = stripe_width * block_round_integer + block_round_residue
                total_block_num = block_num + (block_round_integer + 1) * disk_parity_num
            else:
                block_num = stripe_width * block_round_integer
                total_block_num = block_num + block_round_integer * disk_parity_num
    expect_snap_size = total_block_num * BLOCKSIZE
    log.info('the total block num is %d' % total_block_num)
    log.info('the expect snap size is %d' % expect_snap_size)
    return expect_snap_size


##############################################################################
# ##name  :      replica_snap_size
# ##parameter:   file_size 文件大小
#                stripe_width 条带宽度
#                replica_num 副本数
# ##author:      liyao
# ##date  :      2018.05.02
# ##Description: 根据副本计算期望的快照空间
##############################################################################
def replica_snap_size(file_size, replica_num, stripe_width):
    '''根据副本计算期望的快照空间'''

    segment_size = OBJSIZE * stripe_width * replica_num
    segment_storage_size = OBJSIZE * stripe_width

    """获取文件 余 段数据大小的值"""
    file_size = file_size % segment_storage_size
    if 0 == file_size:
        return 0

    '''计算全部数据块的数量'''
    block_num_integer = file_size // BLOCKSIZE
    block_num_residue = file_size % BLOCKSIZE

    if block_num_residue != 0:
        block_num = block_num_integer + 1
        total_block_num = block_num * replica_num
    else:
        block_num = block_num_integer
        total_block_num = block_num * replica_num

    expect_snap_size = total_block_num * BLOCKSIZE
    log.info('the total block num is %d' % total_block_num)
    log.info('the expect snap size is %d' % expect_snap_size)
    return expect_snap_size