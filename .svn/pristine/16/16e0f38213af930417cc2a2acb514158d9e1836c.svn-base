#!/usr/bin/python
# -*- encoding=utf8 -*-

#######################################################
# 脚本作者：李瑶
# 脚本说明：事件公共函数
#######################################################

import os
import time
import log
import get_config
import common

'''集群节点ip'''
SYSTEM_IP_0 = get_config.get_parastor_ip()
SYSTEM_IP_1 = get_config.get_parastor_ip(1)
SYSTEM_IP_2 = get_config.get_parastor_ip(2)


'''客户端节点ip'''
CLIENT_IP_1 = get_config.get_client_ip()
CLIENT_IP_2 = get_config.get_client_ip(1)
CLIENT_IP_3 = get_config.get_client_ip(2)


'''数据存放相关路径'''
EVENT_TEST_BASE_PATH = get_config.get_event_test_base_path()    # /mnt/volume1
EVENT_TEST_PATH = os.path.join(EVENT_TEST_BASE_PATH, 'event')   # /mnt/volume1/event


'''从命令下发到get_events可以查询到所需的时间'''
DELAY_TIME = 180


def mkdir_event_path():
    """
    author: liyao
    date: 2018.8.11
    description: 创建告警/事件总路径
    :return:
    """
    cmd = 'ls %s' % EVENT_TEST_PATH
    rc, stdout = common.run_command(CLIENT_IP_1, cmd)
    if 0 == rc:
        log.info('%s is exist!' % EVENT_TEST_PATH)
        return
    cmd = 'mkdir %s' % EVENT_TEST_PATH
    rc, stdout = common.run_command(CLIENT_IP_1, cmd)
    if rc != 0:
        raise Exception('%s mkdir faild!!!' % EVENT_TEST_PATH)
    return


def create_event_path(path):
    """
    author: liyao
    date: 2018.8.11
    description: 创建各脚本对应的数据存放目录
    :param path:待创建目录的绝对路径
    :return:
    """
    # 创建事件/告警总路径
    mkdir_event_path()

    # 创建本用例的事件/告警数据存放路径
    cmd = 'mkdir %s' % path
    rc, stdout = common.run_command(CLIENT_IP_1, cmd)
    if 0 != rc:
        log.error('%s failed!!!' % cmd)
        raise Exception('%s failed!!!' % cmd)
    return


def cleaning_environment(true_path):
    """
    author: liyao
    date: 2018.8.11
    description: 删除各脚本对应的数据存放路径
    :param true_path:脚本对应的绝对路径
    :return:
    """
    common.rm_exe(CLIENT_IP_1, true_path)
    return


def get_current_time(ext_node_ip=None):
    """
    name: get_current_time
    params:
    author: liyao
    date: 2018.7.30
    description: 获取环境当前时间
    """
    cmd = 'date +%s'
    rc, stdout = common.run_command(ext_node_ip, cmd)
    return rc, stdout


def get_events(code=None):
    """
    name: get_events
    params: 事件编码code, 各脚本对应的数据存放路径
    author:liyao
    date: 2018.7.30
    description: 获取特定/所有事件的信息
    """
    rc, stdout = common.get_events(event_code=code)
    if 0 != rc:
        log.error('get_events failed !!!')
    stdout = common.json_loads(stdout)
    events_info = stdout['result']['events']
    return rc, events_info


def get_event_ids_by_code(code, data_limit=None):
    """
    name: get_event_ids
    params: 事件编码code, 事件个数限制data_limit, 信息紧急水平level, 执行节点ext_node_ip
    author: liyao
    date: 2018.7.30
    description: 获取环境当前时间
    """
    rc, stdout = common.get_events(event_code=code, data_limit=data_limit)
    if 0 != rc:
        log.error('get events infomation failed !!!')
    stdout = common.json_loads(stdout)
    events_info = stdout['result']['events']
    event_ids = []
    for event in events_info:
        event_ids.append(event['id'])
    return rc, event_ids


def get_events_in_limit_period(limit_time, code=None):
    """
    name: get_events_in_limit_period
    params: 指定判断某类事件是否执行成功的时间起点（保证获取到的为最新发生的特定类别事件）, 事件编码code
    author: liyao
    date: 2018.7.30
    description: 获取一段时间内的事件
    """
    rc, events_info = get_events(code)
    events_in_limit_period = []
    for event in events_info:
        if limit_time <= event['startTimeShort']:
            events_in_limit_period.append(event)
    return rc, events_in_limit_period


def check_events_result(start_time, code, description):
    start_time -= 10
    rc, lately_events = get_events_in_limit_period(start_time)
    lately_event_codes = []
    for event in lately_events:
        lately_event_codes.append(event['code'])
    typical_event_code = code   # 事件常对应的编号
    if typical_event_code in lately_event_codes:
        log.info('%s displayed correct' % description)
        return 0
    else:
        common.except_exit('%s displayed wrong !!!' % description)


def delete_events(ids):
    """
    name: delete_events
    params: 事件的id
    author:liyao
    date: 2018.7.30
    description: 删除特定id对应的事件
    """
    rc, stdout = common.delete_events(ids=ids)
    if 0 != rc:
        log.error('deleting events failed !!!')
    return rc, stdout


def delete_events_by_code(code):
    """
    name: delete_events_by_code
    params: 事件编号code
    author: liyao
    date: 2018.7.30
    description: 根据事件编号删除特定事件
    """
    rc, event_ids_lst = get_event_ids_by_code(code)
    if -1 == rc or event_ids_lst == []:
        return -1, None
    event_ids_str = ','.join(str(i) for i in event_ids_lst)
    rc, stdout = delete_events(event_ids_str)
    if 0 != rc:
        log.error('deleting events failed !!!')
        return -2, stdout
    return rc, stdout


def get_alarms(fault_node_ip=None):
    """
        name: get_alarms
        params: 执行操作的节点ip
        author:liyao
        date: 2018.8.11
        description: 获取集群中所有事件的告警信息
    """
    alarms_info = {}
    rc, stdout = common.get_alarms(fault_node_ip=fault_node_ip)
    if 0 != rc:
        log.error('get_alarms failed !!!')
        return rc, alarms_info
    stdout = common.json_loads(stdout)
    alarms_info = stdout['result']['alarms']
    return rc, alarms_info


def check_alarms_result(code, description, fault_node_ip=None):
    """
        name: check_alarms_result
        params: 告警对应的编号code，告警对应的描述信息
        author:liyao
        date: 2018.8.11
        description: 检查是否正确获取实时告警信息
    """
    err_code_list = []
    step_time = 5     # 每次执行get_alarms的时间间隔
    limit_count = 50   # 执行get_alarms的最大次数，用以限制告警显示需要的时间

    for i in range(limit_count):
        log.info('check for %d times' % (i + 1))
        time.sleep(step_time)
        rc, err_alarms = get_alarms(fault_node_ip=fault_node_ip)
        common.judge_rc(rc, 0, 'get alarms failed !!!')

        for alarm in err_alarms:
            err_code_list.append(alarm['code'])
        if code in err_code_list:
            log.info('%s' % description)
            break
        if i == limit_count - 1:
            common.except_exit('alarms information displayed wrong !!!')
    return


def delete_all_events():
    """
        name: delete_all_events
        author:duyuli
        date: 2018.8.20
        description: 删除所有的事件信息
    """
    id_list = []
    rc, stdout = common.get_events()
    common.judge_rc(rc, 0, "get events failed!!!")

    stdout = common.json_loads(stdout)
    events = stdout["result"]["events"]
    for event in events:
        id_list.append(event["id"])
    ids = ",".join(str(i) for i in id_list)   # 1,2,3

    rc, stdout = common.delete_events(ids=ids)
    if rc != 0:
        raise Exception("get events failed!!!")
    return


def clean_alarms(alarm_id=None):
    """
        name: clean_alarms
        author:chenjy1
        date: 2018.11.06
        description: 删除单个告警
    """
    rc, stdout = common.clean_alarms(ids=alarm_id)
    if rc != 0:
        return rc, {}
    else:
        pscli_info = common.json_loads(stdout)
        return rc, pscli_info
