#!/usr/bin/python
# -*- encoding=utf8 -*-

#######################################################
# 脚本作者：姜晓光
# 脚本说明：配额公共函数
#######################################################

import os
import time

import log
import get_config
import common
import nas_common

DEBUG = "off"

NOTE_IP_1 = get_config.get_parastor_ip(0)
NOTE_IP_2 = get_config.get_parastor_ip(1)
NOTE_IP_3 = get_config.get_parastor_ip(2)

CLIENT_IP_1 = get_config.get_parastor_ip(0)
CLIENT_IP_2 = get_config.get_parastor_ip(1)
CLIENT_IP_3 = get_config.get_parastor_ip(2)

VOLUME_NAME = get_config.get_one_volume_name()

# 测试全路径，注意：quota_test_dir右侧不要加"/"
QUOTA_PATH = get_config.get_one_quota_test_path()   # QUOTA_PATH = "/mnt/parastor/quota_test_dir"
BASE_QUOTA_PATH = os.path.dirname(QUOTA_PATH)       # BASE_QUOTA_PATH = "/mnt/parastor"
QUOTA_PATH_BASENAME = os.path.basename(QUOTA_PATH)  # QUOTA_PATH_BASENAME = "quota_test_dir"
QUOTA_PATH_ABSPATH = os.path.abspath(QUOTA_PATH)    # QUOTA_PATH_ABSPATH = "/mnt/parastor/quota_test_dir"

QUOTA_USER = "quota_user"
QUOTA_OTHER_USER = "quota_other_user"
QUOTA_GROUP = "quota_group"
QUOTA_OTHER_GROUP = "quota_other_group"
QUOTA_ACCESS_ZONE = "testzone"

TYPE_GROUP = 'USERTYPE_GROUP'
TYPE_USER = 'USERTYPE_USER'
TYPE_CATALOG = 'USERTYPE_NONE'
CAL_TYPE_COMPUTE = 'QUOTA_COMPUTE'
CAL_TYPE_LIMIT = 'QUOTA_LIMIT'
SOFT_TIME_FILENR = 'filenr_soft_threshold_over_time'
SOFT_TIME_LOGICAL = 'logical_soft_threshold_over_time'
SOFT_TIME_PHYSICAL = 'physical_soft_threshold_over_time'

flag_slow_machine = True


FILE_SIZE_1G = 1073741824
FILE_SIZE_2G = 2147483648
FILE_SIZE_3G = 3221225472
FILE_SIZE_4G = 4294967296
FILE_SIZE_1M = 1048576


#######################################################
# 函数功能：根据节点id获取节点ip
# 函数入参：
#       node_ip：执行cmd命令的节点ip
#       node_id：要查取ip的节点id
# 函数返回值：
#       node_ip_by_id：根据节点id获取到的节点ip
#######################################################
def get_node_ip_by_id(node_id):
    log.info("\t[ get_node_ip_by_id ]")

    rc, stdout = common.get_nodes(ids=node_id)
    common.judge_rc(rc, 0, "Execute command: get_nodes failed. \n stdout: %s" % stdout)
    msg = common.json_loads(stdout)
    node_ip_by_id = msg['result']['nodes'][0]['ctl_ips'][0]['ip_address']
    return node_ip_by_id


#######################################################
# 函数功能：获取主进程所在的节点id
# 函数入参：
#       node_ip：执行cmd命令的节点ip
#       process_name：只能为oJmgs、oJob、oRole或oPara
# 函数返回值：节点id
#       若入参正确，则返回主oJmgs、oJob、oRole或oPara所在的节点id
#       若入参错误，则返回250
#######################################################
def get_master_process_node_id(process_name):
    log.info("\t[ get_master_process_node_id ]")

    if process_name == "oJmgs":
        rc, stdout = common.get_master()
        common.judge_rc(rc, 0, "Execute command: get_master failed. \nstdout: %s" % stdout)
        ojmgs_result = common.json_loads(stdout)
        ojmgs_node_id = ojmgs_result["result"]["node_id"]
        return int(ojmgs_node_id)

    elif process_name == "oJob":
        cmd = "/home/parastor/tools/nWatch -t oJob -i 1 -c JOB#jobinfo"
        rc, stdout = common.pscli_run_command(cmd)
        common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        return int(stdout.split()[2].split(',')[0])

    elif process_name == "oRole":
        cmd = "/home/parastor/tools/nWatch -t oRole -i 1 -c oRole#rolemgr_master_dump"
        rc, stdout = common.pscli_run_command(cmd)
        common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        return int(stdout.split(':')[1].split()[0])
    elif process_name == "oPara":
        cmd = "/home/parastor/tools/nWatch -t oRole -i 1 -c oRole#rolemgr_view_dump | " \
              "grep \"lnodeid: 1\" -B 1 | grep node_id | uniq"
        rc, stdout = common.pscli_run_command(cmd)
        common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \n stdout: %s" % (cmd, stdout))
        return int(stdout.split()[4].split(',')[0])
    else:
        log.info("\t process_name is wrong!")
    return 250


#######################################################
# 函数功能：开启配额全局开关
# 函数入参：
#       node_ip：执行cmd命令的节点ip
# 函数返回值：无
#######################################################
def open_quota_global_switch():
    log.info("\t[ open_quota_global_switch ]")
    rc, stdout = common.update_param(section='MGR', name='quota_global_switch', current=1)
    common.judge_rc(rc, 0, "Execute command: update_param failed. \n stdout: %s" % stdout)
    return


#######################################################
# 函数功能：关闭配额全局开关
# 函数入参：
#       node_ip：执行cmd命令的节点ip
# 函数返回值：无
#######################################################
def close_quota_global_switch():
    log.info("\t[ close_quota_global_switch ]")
    rc, stdout = common.update_param(section='MGR', name='quota_global_switch', current=0)
    common.judge_rc(rc, 0, "Execute command: update_param failed. \n stdout: %s" % stdout)
    return


#######################################################
# 函数功能：查询配额全局开关
# 函数入参：
#       node_ip：执行cmd命令的节点ip
# 函数返回值：
#       quota_global_switch：配额全局开关，1表示开启，0表示关闭
#######################################################
def get_quota_global_switch():
    log.info("\t[ get_quota_global_switch ]")
    rc, stdout = common.get_params(section='MGR', name='quota_global_switch')
    common.judge_rc(rc, 0, "Execute command: get params failed. \nstdout: %s" % stdout)
    quota_global_switch_info = common.json_loads(stdout)
    quota_global_switch = quota_global_switch_info['result']["parameters"][0]["current"]

    log.info("quota_global_switch = %s" % (quota_global_switch))
    return quota_global_switch


#######################################################
# 函数功能：获取指定格式的配额id列表
# 函数入参：
#       quota_id_list，格式如下：[1,2,3,4]
# 函数返回值：
#       format_quota_id_list，格式如下：1,2,3,4
#######################################################
def format_quota_id_list(quota_id_list):
    log.info("\t[ format_quota_id_list ]")

    # 把数字列表[1,2,3,4]转换成字符串列表['1','2','3','4']
    quota_id_string_list = []
    for tmp in quota_id_list:
        quota_id_string_list.append(str(tmp))

    # 把列表['1','2','3','4']转换成元祖('1','2','3','4')
    seq = tuple(quota_id_string_list)

    # 把元祖中元素拼接成：1,2,3,4
    comma = ","
    format_quota_id_list = comma.join(seq)
    return format_quota_id_list


#######################################################
# 函数功能：获取全部配额id列表
# 函数入参：
#       node_ip：执行cmd命令的节点ip
# 函数返回值：
#       quota_id_list，格式如下：[1,2,3,4]
#######################################################
def get_quota_id_list():
    log.info("\t[ get_quota_id_list ]")

    quota_id_list = []
    rc, stdout = get_all_quota_info()
    common.judge_rc(rc, 0, "get quota failed")
    data_get_quota = stdout

    if data_get_quota["result"]["total"] > 10000:
        total_get_int = data_get_quota["result"]["total"] // 10000
        log.info("total = %s" % (data_get_quota["result"]["total"]))
        log.info("total_int = %s" % (total_get_int))

        for i in range(0, total_get_int + 1):
            start = i * 10000
            limit = 10000
            rc, stdout = common.get_quota(start=start, limit=limit)
            common.judge_rc(rc, 0, "Execute command: get_quota failed. \nstdout: %s" % stdout)
            data_get_quota_more = common.json_loads(stdout)

            for j in range(1, len(data_get_quota_more['result']['quotas']) + 1):
                quota_id = data_get_quota_more['result']['quotas'][j - 1]['id']
                quota_id_list.append(quota_id)
    else:
        for i in range(1, data_get_quota["result"]["total"] + 1):
            quota_id = data_get_quota['result']['quotas'][i - 1]['id']
            quota_id_list.append(quota_id)

    log.info("quota_id_list = %s" % (quota_id_list))
    return quota_id_list


#######################################################
# 函数功能：删除单个配额
# 函数入参：
#       node_ip：执行cmd命令的节点ip
#       quota_id：待删除的quota id
# 函数返回值：
#######################################################
def delete_single_quota_config(quota_id):
    log.info("\t[ delete_single_quota_config ]")

    rc, stdout = delete_one_quota(quota_id)
    common.judge_rc(rc, 0, "delete quota failed\nstdout: %s" % stdout)
    return


#######################################################
# 函数功能：删除所有配额
# 函数入参：
#       node_ip：执行cmd命令的节点ip
# 函数返回值：
#######################################################
def delete_all_quota_config():
    log.info("\t[ delete_all_quota_config ]")

    quota_id_list = get_quota_id_list()
    new_quota_id_list = format_quota_id_list(quota_id_list)

    if len(new_quota_id_list) != 0:
        rc, stdout = delete_one_quota(new_quota_id_list)
        common.judge_rc(rc, 0, "delete quota failed\nstdout: %s" % stdout)
        check_result = stdout
    else:
        log.info("delete_all_quota_config -> new_quota_id_list = []")
        check_result = "no quota config"
    return check_result


def create_one_quota(path, auth_provider_id=None, user_type=None, user_or_group_name=None,
                     logical_quota_cal_type=None, logical_hard_threshold=None, logical_soft_threshold=None,
                     logical_grace_time=None, logical_suggest_threshold=None, physical_quota_cal_type=None,
                     physical_hard_threshold=None, physical_soft_threshold=None, physical_grace_time=None,
                     physical_suggest_threshold=None, physical_count_snapshot=None, physical_count_redundant_space=None,
                     filenr_quota_cal_type=None, filenr_hard_threshold=None, filenr_soft_threshold=None,
                     filenr_grace_time=None, filenr_suggest_threshold=None, description=None):
    """
    auth:chenjy1
    date :180907
    :param all:       pscli参数
    :return:         rc , pscli_info
    """
    rc, stdout = common.create_quota(path=path, auth_provider_id=auth_provider_id,  user_type=user_type,
                                     user_or_group_name=user_or_group_name,
                                     logical_quota_cal_type=logical_quota_cal_type,
                                     logical_hard_threshold=logical_hard_threshold,
                                     logical_soft_threshold=logical_soft_threshold,
                                     logical_grace_time=logical_grace_time,
                                     logical_suggest_threshold=logical_suggest_threshold,
                                     physical_quota_cal_type=physical_quota_cal_type,
                                     physical_hard_threshold=physical_hard_threshold,
                                     physical_soft_threshold=physical_soft_threshold,
                                     physical_grace_time=physical_grace_time,
                                     physical_suggest_threshold=physical_suggest_threshold,
                                     physical_count_snapshot=physical_count_snapshot,
                                     physical_count_redundant_space=physical_count_redundant_space,
                                     filenr_quota_cal_type=filenr_quota_cal_type,
                                     filenr_hard_threshold=filenr_hard_threshold,
                                     filenr_soft_threshold=filenr_soft_threshold,
                                     filenr_grace_time=filenr_grace_time,
                                     filenr_suggest_threshold=filenr_suggest_threshold,
                                     description=description)
    if rc != 0:
        return rc, {}
    pscli_info = common.json_loads(stdout)
    return rc, pscli_info


def update_one_quota(id, logical_quota_cal_type=None, logical_hard_threshold=None, logical_soft_threshold=None,
                     logical_grace_time=None, logical_suggest_threshold=None, physical_quota_cal_type=None,
                     physical_hard_threshold=None, physical_soft_threshold=None, physical_grace_time=None,
                     physical_suggest_threshold=None, physical_count_snapshot=None,
                     physical_count_redundant_space=None, filenr_quota_cal_type=None,
                     filenr_hard_threshold=None, filenr_soft_threshold=None,
                     filenr_grace_time=None, filenr_suggest_threshold=None, description=None):
    """
    auth:chenjy1
    date :180907
    :param all:       pscli参数
    :return:         rc , pscli_info
    """
    rc, stdout = common.update_quota(id=id, logical_quota_cal_type=logical_quota_cal_type,
                                     logical_hard_threshold=logical_hard_threshold,
                                     logical_soft_threshold=logical_soft_threshold,
                                     logical_grace_time=logical_grace_time,
                                     logical_suggest_threshold=logical_suggest_threshold,
                                     physical_quota_cal_type=physical_quota_cal_type,
                                     physical_hard_threshold=physical_hard_threshold,
                                     physical_soft_threshold=physical_soft_threshold,
                                     physical_grace_time=physical_grace_time,
                                     physical_suggest_threshold=physical_suggest_threshold,
                                     physical_count_snapshot=physical_count_snapshot,
                                     physical_count_redundant_space=physical_count_redundant_space,
                                     filenr_quota_cal_type=filenr_quota_cal_type,
                                     filenr_hard_threshold=filenr_hard_threshold,
                                     filenr_soft_threshold=filenr_soft_threshold,
                                     filenr_grace_time=filenr_grace_time,
                                     filenr_suggest_threshold=filenr_suggest_threshold,
                                     description=description)
    if rc != 0:
        return rc, {}
    pscli_info = common.json_loads(stdout)
    return rc, pscli_info


def delete_one_quota(quota_id):
    """
    auth:chenjy1
    date 20180906
    :param node_ip:           (str)执行节点
    :return:
    """
    rc, stdout = common.delete_quota(ids=quota_id)
    if rc != 0:
        return rc, {}
    else:
        pscli_info = common.json_loads(stdout)
        return rc, pscli_info


def get_all_quota_info():
    """
    auth:chenjy1
    date 20180906
    :param node_ip:           (str)执行节点
    :return:
    """
    rc, stdout = common.get_quota()
    if rc != 0:
        return rc, {}
    else:
        pscli_info = common.json_loads(stdout)
        return rc, pscli_info


def get_one_quota_info(quota_id, print_flag=True):
    """
    auth:chenjy1
    date 20180906
    :param node_ip:           执行节点
    :param quota_id:          id
    :return:
    """
    quota_info = {}
    rc, stdout = common.get_quota(ids=quota_id, print_flag=print_flag)
    if rc != 0:
        return rc, quota_info
    else:
        quota_info = common.json_loads(stdout)
        return rc, quota_info


def get_one_quota_id(path, u_or_g_type, u_or_g_name=None, is_count_snapshot=False, is_redundant_space=False):
    """
    auth:chenjy1
    date 20180906
    :param path:              (str)配额路径
    :param u_or_g_type:       (str)用户（组）类型 ：quota_common.TYPE_GROUP  TYPE_USER  TYPE_CATALOG 三选一
    :param u_or_g_name:       (str)用户（组）名
    :param is_count_snapshot: (bool)是否快照统计 仅对物理空间有效
    :param is_redundant_space:(bool)是否冗余统计 仅对物理空间有效
    :return:                   rc , quota_id
    """
    quota_id = 0
    rc, stdout = common.get_quota(param_name='path', param_value=path)
    if rc != 0:
        return rc, quota_id
    else:
        pscli_info = common.json_loads(stdout)
        for quota in pscli_info['result']['quotas']:
            if quota['path'] == path and quota['user_type'] == u_or_g_type \
                    and (quota['user_or_group_name'] == (quota['user_or_group_name'] if (u_or_g_name is None) else u_or_g_name)) \
                    and (quota['physical_count_redundant_space'] == (quota['physical_count_redundant_space'] if (is_redundant_space is None) else is_redundant_space))\
                    and (quota['physical_count_snapshot'] == (quota['physical_count_snapshot'] if (is_count_snapshot is None) else is_count_snapshot)):
                quota_id = quota['id']
                break
        else:
            return 1, quota_id
        return rc, quota_id


def wait_quota_work(quota_id, print_flag=True):
    """
    :Author: chenjy1
    :Date:180910
    :param node_ip:           执行节点
    :param quota_id:          id
    :return:
    """
    start_time = time.time()
    while True:
        rc, quota_info = get_one_quota_info(quota_id, print_flag=print_flag)
        if rc != 0:
            log.info("get_one_quota_info failed")
            return rc
        if quota_info['result']['quotas'][0]['state'] == 'QUOTA_WORK':
            break
        time.sleep(10)
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        log.info('wait quota work exist %dh:%dm:%ds  now quota state is %s' %
                 (h, m, s, quota_info['result']['quotas'][0]['state']))
    return 0


#######################################################
# 函数功能：创建目录
# 函数入参：
#       node_ip —— 创建目录的节点ip
#       quota_path —— 要创建目录的全路径
# 函数返回值：无
#######################################################
def creating_dir(node_ip, quota_path):
    log.info("\t[ creating_dir ]")

    # mkdir创建目录，并授权777权限
    cmd = "mkdir -p %s; chmod 777 %s" % (quota_path, quota_path)
    rc, stdout = common.run_command(node_ip, cmd)
    common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    return


#######################################################
# 函数功能：使用指定用户或用户组创建若干指定大小的文件，最小为1M
# 函数入参：
#       node_ip —— 创建文件的节点ip
#       quota_path —— 创建文件的全路径
#       file_count —— 创建文件个数
#       file_size —— 每个待创建文件的大小，单位是M
#       file_name_identifier —— 文件名标识
#       designated_user：指定用户或用户组的用户名称，比如quota_user,quota_other_user等
# 函数返回值：无
#######################################################
def creating_1k_files_by_designated_user_or_group(node_ip, quota_path, file_count, file_size,
                                                  file_name_identifier, designated_user):
    log.info("\t[ creating_1k_files_by_designated_user_or_group ]")

    # dd创建文件
    # for i in {1..100}; do dd if=/dev/zero of=test_$i bs=100K count=1000; done
    cmd = ("cd %s; for i in {1..%s}; do su %s -c \"dd if=/dev/zero of=file_%s_%s_$i bs=1024 count=%s\"; done") % (
        quota_path, file_count, designated_user, node_ip, file_name_identifier, file_size)

    rc, stdout = common.run_command(node_ip, cmd)
    common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)

    # 版本限制，临时添加
    time.sleep(10)
    return


def get_quota_id_list_by_path(path):
    quota_id_list = []
    rc, stdout = common.get_quota(param_name='path', param_value=path, print_flag=False)
    if rc != 0:
        return rc, quota_id_list
    else:
        pscli_info = common.json_loads(stdout)
        for quota in pscli_info['result']['quotas']:
            if quota['path'] == path:
                quota_id_list.append(quota['id'])
                break
        return rc, quota_id_list


#######################################################
# 函数功能：创建若干指定大小的文件，最小为1K
# 函数入参：
#       node_ip —— 创建文件的节点ip
#       quota_path —— 创建文件的全路径
#       file_count —— 创建文件个数
#       file_size —— 每个待创建文件的大小，单位是K
#       file_name_identifier —— 文件名标识
# 函数返回值：无
#######################################################
def creating_1k_files(node_ip, quota_path, file_count, file_size, file_name_identifier):
    log.info("\t[ creating_1k_files ]")

    # dd创建文件
    # for i in {1..100}; do dd if=/dev/zero of=test_$i bs=100K count=1000; done
    cmd = ("cd %s; for i in {1..%s}; do dd if=/dev/zero of=file_%s_%s_$i bs=1024 count=%s; done") % (
        quota_path, file_count, node_ip, file_name_identifier, file_size)

    rc, stdout = common.run_command(node_ip, cmd)
    common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)

    # 版本限制，临时添加
    time.sleep(10)
    return


#######################################################
# 函数功能：使用指定用户或用户组创建若干指定大小的文件，最小为1M
# 函数入参：
#       node_ip —— 创建文件的节点ip
#       quota_path —— 创建文件的全路径
#       file_count —— 创建文件个数
#       file_size —— 每个待创建文件的大小，单位是M
#       file_name_identifier —— 文件名标识
#       designated_user：指定用户或用户组的用户名称，比如quota_user,quota_other_user等
# 函数返回值：无
#######################################################
def creating_files_by_designated_user_or_group(node_ip, quota_path, file_count, file_size,
                                               file_name_identifier, designated_user, quota_id=None):
    log.info("\t[ creating_files_by_designated_user_or_group ]")

    # 找到QMGR所在的物理节点
    """
    cmd = "cd /home/parastor/tools;./nWatch -t oPara -i 1 -c QMGR#getqmgr"
    rc, stdout = common.run_command(NOTE_IP_1, cmd)
    common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
    ruleid = stdout.split("[")[1].split("]")[0]
    """
    ob_node = common.Node()
    node_id_lst = ob_node.get_nodes_id()

    # 提取quota_id
    quota_id_list = get_quota_id_list()
    path_quota_id_list = []
    # 判断是否可以换客户端操作(只对最后一个配额判断)，若可以则dd写文件
    can_or_cannot = "empty"
    can_or_cannot = "empty"
    if len(quota_id_list) != 0:
        path_quota_id_list = []
        quota_path = quota_path.strip()
        if quota_path[-1] != '/':
            quota_path = quota_path + '/'
        t_path = quota_path.split('/')  # /mnt/volume/a/b/c/
        print t_path
        for i in range(len(t_path[3:])):  # t_path[3:] = a b c
            pscli_path = t_path[2] + ':/' + '/'.join(t_path[3:-(i + 1)])
            print pscli_path
            rc, tmp_path_quota_id_list = get_quota_id_list_by_path(pscli_path)
            common.judge_rc(rc, 0, 'failed')
            if tmp_path_quota_id_list != []:
                path_quota_id_list.extend(tmp_path_quota_id_list)
        # dd创建文件
        # for i in {1..100}; do dd if=/dev/zero of=test_$i bs=100K count=1000; done
        cmd = ("cd %s; for i in {1..%s}; do su %s -c \"dd if=/dev/zero of=file_%s_%s_$i bs=1M count=%s\"; "
               "done") % (quota_path, file_count, designated_user, node_ip, file_name_identifier, file_size)
        rc, stdout = common.run_command(node_ip, cmd)
        common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
        # for quota_ruleid in quota_id_list:
        if quota_id is None:
            quota_ruleid = quota_id_list[-1]
        else:
            quota_ruleid = quota_id
        for qid in path_quota_id_list:
            count = 0
            while True:
                for ruleid in node_id_lst:
                    cmd = "cd /home/parastor/tools;./nWatch -t oPara -i %s -c QMGR#chkmult_client -a \"ruleid=%s\"" % \
                          (ruleid, qid)
                    rc, stdout = common.pscli_run_command(cmd)
                    common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
                    if "qmgr is not here" not in stdout:
                        can_or_cannot = stdout.split()[4]
                        break
                if can_or_cannot == "empty":
                    common.except_exit(info="all node say: qmgr is not here")
                if can_or_cannot == "can":
                    print "can_or_cannot = %s" % (can_or_cannot)

                    break
                else:
                    if count > 150:
                        log.info("### chkmult over 5 min !!!")
                        raise Exception("chkmult over 5 min")
                    print "can_or_cannot = %s, sleep(2)" % (can_or_cannot)
                    time.sleep(2)
                    count = count + 1
    else:
        # dd创建文件
        # for i in {1..100}; do dd if=/dev/zero of=test_$i bs=100K count=1000; done，未加oflag=sync
        cmd = ("cd %s; for i in {1..%s}; do su %s -c \"dd if=/dev/zero of=file_%s_%s_$i bs=1M count=%s\"; "
               "done") % (quota_path, file_count, designated_user, node_ip, file_name_identifier, file_size)
        rc, stdout = common.run_command(node_ip, cmd)
        common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
    return


def creating_files_by_designated_user_or_group_beifen(node_ip, quota_path, file_count, file_size,
                                                      file_name_identifier, designated_user, quota_id=None):
    log.info("\t[ creating_files_by_designated_user_or_group ]")

    # 找到QMGR所在的物理节点
    """
    cmd = "cd /home/parastor/tools;./nWatch -t oPara -i 1 -c QMGR#getqmgr"
    rc, stdout = common.run_command(NOTE_IP_1, cmd)
    common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
    ruleid = stdout.split("[")[1].split("]")[0]
    """
    ob_node = common.Node()
    node_id_lst = ob_node.get_nodes_id()

    # 提取quota_id
    quota_id_list = get_quota_id_list()

    # 判断是否可以换客户端操作(只对最后一个配额判断)，若可以则dd写文件
    can_or_cannot = "empty"
    if len(quota_id_list) != 0:
        # for quota_ruleid in quota_id_list:
        if quota_id is None:
            quota_ruleid = quota_id_list[-1]
        else:
            quota_ruleid = quota_id
        while True:
            for ruleid in node_id_lst:
                cmd = "cd /home/parastor/tools;./nWatch -t oPara -i %s -c QMGR#chkmult_client -a \"ruleid=%s\"" % \
                      (ruleid, quota_ruleid)
                rc, stdout = common.pscli_run_command(cmd)
                common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
                if "qmgr is not here" not in stdout:
                    can_or_cannot = stdout.split()[4]
                    break
            if can_or_cannot == "empty":
                common.except_exit(info="all node say: qmgr is not here")

            if can_or_cannot == "can":
                print "can_or_cannot = %s" % (can_or_cannot)
                # dd创建文件
                # for i in {1..100}; do dd if=/dev/zero of=test_$i bs=100K count=1000; done
                cmd = ("cd %s; for i in {1..%s}; do su %s -c \"dd if=/dev/zero of=file_%s_%s_$i bs=1M count=%s\"; "
                       "done") % (quota_path, file_count, designated_user, node_ip, file_name_identifier, file_size)
                rc, stdout = common.run_command(node_ip, cmd)
                common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
                break
            else:
                print "can_or_cannot = %s, sleep(2)" % (can_or_cannot)
                time.sleep(2)
    else:
        # dd创建文件
        # for i in {1..100}; do dd if=/dev/zero of=test_$i bs=100K count=1000; done，未加oflag=sync
        cmd = ("cd %s; for i in {1..%s}; do su %s -c \"dd if=/dev/zero of=file_%s_%s_$i bs=1M count=%s\"; "
               "done") % (quota_path, file_count, designated_user, node_ip, file_name_identifier, file_size)
        rc, stdout = common.run_command(node_ip, cmd)
        common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
    return


#######################################################
# 函数功能：使用指定用户或用户组创建若干指定大小的文件，最小为1M
# 函数入参：
#       node_ip —— 创建文件的节点ip
#       quota_path —— 创建文件的全路径
#       file_count —— 创建文件个数
#       file_size —— 每个待创建文件的大小，单位是M
#       file_name_identifier —— 文件名标识
#       designated_user：指定用户或用户组的用户名称，比如quota_user,quota_other_user等
# 函数返回值：无
#######################################################
def creating_files_by_designated_user_or_group_with_oflag_sync(node_ip, quota_path, file_count, file_size,
                                                               file_name_identifier, designated_user, quota_id=None):
    log.info("\t[ creating_files_by_designated_user_or_group ]")

    # 找到QMGR所在的物理节点
    """
    cmd = "cd /home/parastor/tools;./nWatch -t oPara -i 1 -c QMGR#getqmgr"
    rc, stdout = common.run_command(NOTE_IP_1, cmd)
    common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
    ruleid = stdout.split("[")[1].split("]")[0]
    """
    ob_node = common.Node()
    node_id_lst = ob_node.get_nodes_id()
    # 提取quota_id
    quota_id_list = get_quota_id_list()

    # 判断是否可以换客户端操作(只对最后一个配额判断)，若可以则dd写文件
    can_or_cannot = "empty"
    can_or_cannot = "empty"
    if len(quota_id_list) != 0:
        path_quota_id_list = []
        quota_path = quota_path.strip()
        if quota_path[-1] != '/':
            quota_path = quota_path + '/'
        t_path = quota_path.split('/')  # /mnt/volume/a/b/c/
        print t_path
        for i in range(len(t_path[3:])):  # t_path[3:] = a b c
            pscli_path = t_path[2] + ':/' + '/'.join(t_path[3:-(i + 1)])
            print pscli_path
            rc, tmp_path_quota_id_list = get_quota_id_list_by_path(pscli_path)
            common.judge_rc(rc, 0, 'failed')
            if tmp_path_quota_id_list != []:
                path_quota_id_list.extend(tmp_path_quota_id_list)
        # dd创建文件
        # for i in {1..100}; do dd if=/dev/zero of=test_$i bs=100K count=1000; done
        cmd = ("cd %s; for i in {1..%s}; do su %s -c \"dd if=/dev/zero of=file_%s_%s_$i "
               "bs=1M count=%s oflag=sync \"; done") % \
              (quota_path, file_count, designated_user, node_ip, file_name_identifier, file_size)

        rc, stdout = common.run_command(node_ip, cmd)
        common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
        # for quota_ruleid in quota_id_list:
        if quota_id is None:
            quota_ruleid = quota_id_list[-1]
        else:
            quota_ruleid = quota_id
        for qid in path_quota_id_list:
            while True:
                for ruleid in node_id_lst:
                    cmd = "cd /home/parastor/tools;./nWatch -t oPara -i %s -c QMGR#chkmult_client -a \"ruleid=%s\"" % \
                          (ruleid, qid)
                    rc, stdout = common.pscli_run_command(cmd)
                    common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
                    if "qmgr is not here" not in stdout:
                        can_or_cannot = stdout.split()[4]
                        break
                if can_or_cannot == "empty":
                    common.except_exit(info="all node say: qmgr is not here")

                if can_or_cannot == "can":
                    print "can_or_cannot = %s" % (can_or_cannot)
                    break
                else:
                    print "can_or_cannot = %s, sleep(2)" % (can_or_cannot)
                    time.sleep(2)
    else:
        # dd创建文件
        # for i in {1..100}; do dd if=/dev/zero of=test_$i bs=100K count=1000; done，未加oflag=sync
        cmd = ("cd %s; for i in {1..%s}; do dd if=/dev/zero of=file_%s_%s_$i bs=1M count=%s oflag=sync ; done") % (
            quota_path, file_count, node_ip, file_name_identifier, file_size)
        rc, stdout = common.run_command(node_ip, cmd)
        common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
    return


def creating_files_by_designated_user_or_group_with_oflag_sync_beifen(node_ip, quota_path, file_count, file_size,
                                                                      file_name_identifier, designated_user,
                                                                      quota_id=None):
    log.info("\t[ creating_files_by_designated_user_or_group ]")

    # 找到QMGR所在的物理节点
    """
    cmd = "cd /home/parastor/tools;./nWatch -t oPara -i 1 -c QMGR#getqmgr"
    rc, stdout = common.run_command(NOTE_IP_1, cmd)
    common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
    ruleid = stdout.split("[")[1].split("]")[0]
    """
    ob_node = common.Node()
    node_id_lst = ob_node.get_nodes_id()
    # 提取quota_id
    quota_id_list = get_quota_id_list()

    # 判断是否可以换客户端操作(只对最后一个配额判断)，若可以则dd写文件
    can_or_cannot = "empty"
    if len(quota_id_list) != 0:
        # for quota_ruleid in quota_id_list:
        if quota_id is None:
            quota_ruleid = quota_id_list[-1]
        else:
            quota_ruleid = quota_id
        while True:
            for ruleid in node_id_lst:
                cmd = "cd /home/parastor/tools;./nWatch -t oPara -i %s -c QMGR#chkmult_client -a \"ruleid=%s\"" % \
                      (ruleid, quota_ruleid)
                rc, stdout = common.pscli_run_command(cmd)
                common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
                if "qmgr is not here" not in stdout:
                    can_or_cannot = stdout.split()[4]
                    break
            if can_or_cannot == "empty":
                common.except_exit(info="all node say: qmgr is not here")

            if can_or_cannot == "can":
                print "can_or_cannot = %s" % can_or_cannot
                # dd创建文件
                # for i in {1..100}; do dd if=/dev/zero of=test_$i bs=100K count=1000; done
                cmd = ("cd %s; for i in {1..%s}; do su %s -c \"dd if=/dev/zero of=file_%s_%s_$i "
                       "bs=1M count=%s oflag=sync \"; done") % \
                      (quota_path, file_count, designated_user, node_ip, file_name_identifier, file_size)

                rc, stdout = common.run_command(node_ip, cmd)
                common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
                break
            else:
                print "can_or_cannot = %s, sleep(2)" % can_or_cannot
                time.sleep(2)
    else:
        # dd创建文件
        # for i in {1..100}; do dd if=/dev/zero of=test_$i bs=100K count=1000; done，未加oflag=sync
        cmd = "cd %s; for i in {1..%s}; do dd if=/dev/zero of=file_%s_%s_$i bs=1M count=%s oflag=sync ; done" % \
              (quota_path, file_count, node_ip, file_name_identifier, file_size)
        rc, stdout = common.run_command(node_ip, cmd)
        common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
    return


#######################################################
# 函数功能：加oflag=sync参数创建若干指定大小的文件，最小为1M
# 函数入参：
#       node_ip —— 创建文件的节点ip
#       quota_path —— 创建文件的全路径
#       file_count —— 创建文件个数
#       file_size —— 每个待创建文件的大小，单位是M
#       file_name_identifier —— 文件名标识
# 函数返回值：无
#######################################################
def creating_files_with_oflag_sync(node_ip, quota_path, file_count, file_size, file_name_identifier):
    log.info("\t[ creating_files_with_oflag_sync ]")

    # dd创建文件
    # for i in {1..100}; do dd if=/dev/zero of=test_$i bs=100K count=1000; done，加oflag=sync参数
    cmd = ("cd %s; for i in {1..%s}; do dd if=/dev/zero of=file_%s_%s_$i bs=1M count=%s oflag=sync; done") % (
        quota_path, file_count, node_ip, file_name_identifier, file_size)
    log.info(cmd)
    rc, stdout = common.run_command(node_ip, cmd)
    common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)

    # 版本限制，临时添加
    time.sleep(10)
    return


def get_qmgr_id(quote_id):
    """
    auth chenjy1
    date:180911
    :param quote_id:  任意一个配额的id
    :return:     rc ,qmgrid  如果qmgrid=0则三个节点都说自己不是qmgr节点
    """
    qmgr_id = 0
    ob_node = common.Node()
    node_id_lst = ob_node.get_nodes_id()
    for ruleid in node_id_lst:
        cmd = "cd /home/parastor/tools;./nWatch -t oPara -i %s -c QMGR#chkmult_client -a \"ruleid=%s\"" % \
              (ruleid, quote_id)
        rc, stdout = common.pscli_run_command(cmd, print_flag=False)
        if rc != 0:
            return rc, qmgr_id
        if "qmgr is not here" not in stdout:
            qmgr_id = ruleid
            break
    log.info('qmgrid = %s ' % qmgr_id)
    return 0, qmgr_id


def get_node_time(node_ip):
    cmd = "date +%s"
    rc, stdout = common.run_command(node_ip, cmd, print_flag=False)
    return rc, stdout


def get_quota_soft_threshold_over_time(node_ip, quota_id, type):
    rc, stdout = common.get_quota(ids=quota_id, print_flag=False)
    if rc != 0:
        return rc, stdout
    else:
        pscli_info = common.json_loads(stdout)
        cmd = "date -d '%s' " % pscli_info['result']['quotas'][0][type]
        cmd += ' +%s'
        rc, stdout = common.run_command(node_ip, cmd)
        return rc, stdout


def wait_soft_threshold_over_time(qmgr_ip, quota_id, type):
    start_time = time.time()
    while True:
        rc, cur_time = get_node_time(qmgr_ip)
        common.judge_rc(rc, 0, "get_node_time failed")
        rc, ovet_time = get_quota_soft_threshold_over_time(qmgr_ip, quota_id, type)
        common.judge_rc(rc, 0, "get_quota_soft_threshold_over_time failed")
        rc, quota_info = get_one_quota_info(quota_id, print_flag=False)
        common.judge_rc(rc, 0, "get_one_quota_info failed ")
        gracetime = 0
        if type == SOFT_TIME_FILENR:
            gracetime = quota_info['result']['quotas'][0]['filenr_grace_time']
        elif type == SOFT_TIME_LOGICAL:
            gracetime = quota_info['result']['quotas'][0]['logical_grace_time']
        else:
            gracetime = quota_info['result']['quotas'][0]['physical_grace_time']
        if int(ovet_time) != 0 and int(cur_time) > (int(ovet_time)+gracetime):
            break
        time.sleep(10)
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        log.info('wait soft_threshold_over_time exist %dh:%dm:%ds' % (h, m, s))
        log.info('soft_threshold_over_time: %s  qmgr current time : %s' % (ovet_time, cur_time))
    return


def chkmult_client_all_dir_on_path(dir, fault_node_ip=None):
    """
    auth chenjy1
    date 181011
    description:    查看从卷根目录至dir目录这一条路线中所有有配额的目录chkmult_client,直到全能换则退出
    :param node_ip: 执行命令的ip
    :param path:    想查的目录
    :return:        rc
    """
    rc = 0
    ob_node = common.Node()
    node_id_lst = ob_node.get_nodes_id()
    path_quota_id_list = []
    path = dir.strip()
    if path[-1] != '/':
        path = path + '/'
    t_path = path.split('/')  # /mnt/volume/a/b/c/
    log.info(t_path)
    for i in range(len(t_path[3:])):  # t_path[3:] = a b c
        pscli_path = t_path[2] + ':/' + '/'.join(t_path[3:-(i + 1)])
        log.info(pscli_path)
        rc, tmp_path_quota_id_list = get_quota_id_list_by_path(pscli_path)
        if rc != 0:
            return rc
        if tmp_path_quota_id_list != []:
            path_quota_id_list.extend(tmp_path_quota_id_list)

    for qid in path_quota_id_list:
        while True:
            for ruleid in node_id_lst:
                cmd = "cd /home/parastor/tools;./nWatch -t oPara -i %s -c QMGR#chkmult_client -a \"ruleid=%s\"" % \
                      (ruleid, qid)
                rc, stdout = common.pscli_run_command(cmd, fault_node_ip=fault_node_ip)
                common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
                if "qmgr is not here" not in stdout:
                    can_or_cannot = stdout.split()[4]
                    break
            if can_or_cannot == "empty":
                log.info("all node say: qmgr is not here")
                return rc
            if can_or_cannot == "can":
                break
            else:
                print "can_or_cannot = %s, sleep(2)" % (can_or_cannot)
                time.sleep(2)
    return rc


def chkmult_client_one_dir_on_path(dir, fault_node_ip=None):
    """
    auth chenjy1
    date 181011
    description: 查看从卷根目录至path目录这一条路线中距离dir最近的（包括自身）包含配额的目录chkmult_client,
    直到全可换则退出
    :param node_ip: 执行命令的ip
    :param path:    想查的目录
    :return:
    """
    rc = 0
    ob_node = common.Node()
    node_id_lst = ob_node.get_nodes_id()
    path_quota_id_list = []
    path = dir.strip()
    if path[-1] != '/':
        path = path + '/'
    t_path = path.split('/')  # /mnt/volume/a/b/c/
    log.info(t_path)

    for i in range(len(t_path[3:])):  # t_path[3:] = a b c
        pscli_path = t_path[2] + ':/' + '/'.join(t_path[3:-(i + 1)])
        log.info(pscli_path)
        rc, tmp_path_quota_id_list = get_quota_id_list_by_path(pscli_path)
        if rc != 0:
            return rc
        if tmp_path_quota_id_list != []:
            path_quota_id_list.extend(tmp_path_quota_id_list)
            break

    for qid in path_quota_id_list:
        while True:
            for ruleid in node_id_lst:
                cmd = "cd /home/parastor/tools;./nWatch -t oPara -i %s -c QMGR#chkmult_client -a \"ruleid=%s\"" % \
                      (ruleid, qid)
                rc, stdout = common.pscli_run_command(cmd, fault_node_ip=fault_node_ip)
                common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
                if "qmgr is not here" not in stdout:
                    can_or_cannot = stdout.split()[4]
                    break
            if can_or_cannot == "empty":
                log.info("all node say: qmgr is not here")
                return rc
            if can_or_cannot == "can":
                break
            else:
                print "can_or_cannot = %s, sleep(2)" % (can_or_cannot)
                time.sleep(2)
    return rc


#######################################################
# 函数功能：创建若干指定大小的文件，最小为1M
# 函数入参：
#       node_ip —— 创建文件的节点ip
#       quota_path —— 创建文件的全路径
#       file_count —— 创建文件个数
#       file_size —— 每个待创建文件的大小，单位是M
#       file_name_identifier —— 文件名标识
# 函数返回值：无
#######################################################
def creating_files(node_ip, quota_path, file_count, file_size, file_name_identifier, quota_id=None):
    log.info("\t[ creating_files ]")
    # 找到QMGR所在的物理节点
    """
    cmd = "cd /home/parastor/tools;./nWatch -t oPara -i 1 -c QMGR#getqmgr"
    rc, stdout = common.run_command(NOTE_IP_1, cmd)
    common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
    ruleid = stdout.split("[")[1].split("]")[0]
    """
    ob_node = common.Node()
    node_id_lst = ob_node.get_nodes_id()
    # 提取quota_id
    quota_id_list = get_quota_id_list()

    # 判断是否可以换客户端操作(只对最后一个配额判断)，若可以则dd写文件
    can_or_cannot = "empty"
    if len(quota_id_list) != 0:
        path_quota_id_list = []
        quota_path = quota_path.strip()
        if quota_path[-1] != '/':
            quota_path = quota_path + '/'
        t_path = quota_path.split('/')  # /mnt/volume/a/b/c/
        print t_path
        for i in range(len(t_path[3:])):  # t_path[3:] = a b c
            pscli_path = t_path[2] + ':/' + '/'.join(t_path[3:-(i + 1)])
            print pscli_path
            rc, tmp_path_quota_id_list = get_quota_id_list_by_path(pscli_path)
            common.judge_rc(rc, 0, 'failed')
            if tmp_path_quota_id_list != []:
                path_quota_id_list.extend(tmp_path_quota_id_list)
        # if path_quota_id_list == []:
        #    common.judge_rc(-1, 0, 'failed')
        # dd创建文件
        # for i in {1..100}; do dd if=/dev/zero of=test_$i bs=100K count=1000; done，未加oflag=sync
        cmd = ("cd %s; for i in {1..%s}; do dd if=/dev/zero of=file_%s_%s_$i bs=1M count=%s; done") % (
            quota_path, file_count, node_ip, file_name_identifier, file_size)
        rc, stdout = common.run_command(node_ip, cmd)
        common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
        # for quota_ruleid in quota_id_list:
        if quota_id is None:
            quota_ruleid = quota_id_list[-1]
        else:
            quota_ruleid = quota_id
        for qid in path_quota_id_list:
            while True:
                for ruleid in node_id_lst:
                    cmd = "cd /home/parastor/tools;./nWatch -t oPara -i %s -c QMGR#chkmult_client -a \"ruleid=%s\"" % \
                          (ruleid, qid)
                    rc, stdout = common.pscli_run_command(cmd)
                    common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
                    if "qmgr is not here" not in stdout:
                        can_or_cannot = stdout.split()[4]
                        break
                if can_or_cannot == "empty":
                    common.except_exit(info="all node say: qmgr is not here")
                if can_or_cannot == "can":
                    break
                else:
                    print "can_or_cannot = %s, sleep(2)" % (can_or_cannot)
                    time.sleep(2)
    else:
        # dd创建文件
        # for i in {1..100}; do dd if=/dev/zero of=test_$i bs=100K count=1000; done，未加oflag=sync
        cmd = ("cd %s; for i in {1..%s}; do dd if=/dev/zero of=file_%s_%s_$i bs=1M count=%s; done") % (
            quota_path, file_count, node_ip, file_name_identifier, file_size)
        rc, stdout = common.run_command(node_ip, cmd)
        common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
    return


def creating_files_beifen(node_ip, quota_path, file_count, file_size, file_name_identifier, quota_id=None):
    log.info("\t[ creating_files ]")
    # 找到QMGR所在的物理节点
    """
    cmd = "cd /home/parastor/tools;./nWatch -t oPara -i 1 -c QMGR#getqmgr"
    rc, stdout = common.run_command(NOTE_IP_1, cmd)
    common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
    ruleid = stdout.split("[")[1].split("]")[0]
    """
    ob_node = common.Node()
    node_id_lst = ob_node.get_nodes_id()
    # 提取quota_id
    quota_id_list = get_quota_id_list()

    # 判断是否可以换客户端操作(只对最后一个配额判断)，若可以则dd写文件
    can_or_cannot = "empty"
    if len(quota_id_list) != 0:
        # for quota_ruleid in quota_id_list:
        if quota_id is None:
            quota_ruleid = quota_id_list[-1]
        else:
            quota_ruleid = quota_id
        while True:
            for ruleid in node_id_lst:
                cmd = "cd /home/parastor/tools;./nWatch -t oPara -i %s -c QMGR#chkmult_client -a \"ruleid=%s\"" % \
                      (ruleid, quota_ruleid)
                rc, stdout = common.pscli_run_command(cmd)
                common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
                if "qmgr is not here" not in stdout:
                    can_or_cannot = stdout.split()[4]
                    break
            if can_or_cannot == "empty":
                common.except_exit(info="all node say: qmgr is not here")

            if can_or_cannot == "can":
                # dd创建文件
                # for i in {1..100}; do dd if=/dev/zero of=test_$i bs=100K count=1000; done，未加oflag=sync
                cmd = ("cd %s; for i in {1..%s}; do dd if=/dev/zero of=file_%s_%s_$i bs=1M count=%s; done") % (
                    quota_path, file_count, node_ip, file_name_identifier, file_size)
                rc, stdout = common.run_command(node_ip, cmd)
                common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
                break
            else:
                print "can_or_cannot = %s, sleep(2)" % (can_or_cannot)
                time.sleep(2)
    else:
        # dd创建文件
        # for i in {1..100}; do dd if=/dev/zero of=test_$i bs=100K count=1000; done，未加oflag=sync
        cmd = ("cd %s; for i in {1..%s}; do dd if=/dev/zero of=file_%s_%s_$i bs=1M count=%s; done") % (
            quota_path, file_count, node_ip, file_name_identifier, file_size)
        rc, stdout = common.run_command(node_ip, cmd)
        common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
    return


def creating_files_for_volume_capacity(node_ip, quota_path, file_count, file_size, file_name_identifier, volume_id):
    """
    auth:chenjy1
    date 180907
    :param node_ip:                   ip
    :param quota_path:                写文件路径
    :param file_count:                文件数
    :param file_size:                 文件大小
    :param file_name_identifier:      文件特定名字
    :param volume_id:                 volume_id
    :return:
    """
    log.info("\t[ creating_files ]")

    ob_node = common.Node()
    node_id_lst = ob_node.get_nodes_id()

    can_or_cannot = "empty"
    while True:
        for ruleid in node_id_lst:
            cmd = "cd /home/parastor/tools;./nWatch -t oPara -i %s -c QMGR#fs_chkmult_client -a fsid=%s" % \
                  (ruleid, volume_id)
            rc, stdout = common.pscli_run_command(cmd)
            common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
            if "qmgr is not here" not in stdout:
                can_or_cannot = stdout.split()[4]
                break
        if can_or_cannot == "empty":
            common.except_exit(info="all node say: qmgr is not here")

        if can_or_cannot == "can":
            # dd创建文件
            # for i in {1..100}; do dd if=/dev/zero of=test_$i bs=100K count=1000; done，未加oflag=sync
            cmd = ("cd %s; for i in {1..%s}; do dd if=/dev/zero of=file_%s_%s_$i bs=1M count=%s; done") % (
                quota_path, file_count, node_ip, file_name_identifier, file_size)
            rc, stdout = common.run_command(node_ip, cmd)
            common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
            break
        else:
            print "can_or_cannot = %s, sleep(2)" % (can_or_cannot)
            time.sleep(2)
    return


#######################################################
# 函数功能：获取指定目录下的文件列表
# 函数入参：
#       client_ip —— 执行cmd命令的节点ip
#       quota_path —— ls文件的全路径
#       file_name_identifier —— 用于过滤文件列表的标识符，一般为"a", "b", "c"
# 函数返回值：
#       file_list —— 满足指定条件的文件列表：["file1", "file2", ...]
#######################################################
def get_file_list(client_ip, quota_path, file_name_identifier):
    log.info("\t[ get_file_list ]")

    file_name_identifier = "_" + file_name_identifier + "_"
    cmd = ("ls %s | grep %s") % (quota_path, file_name_identifier)
    rc, stdout = common.run_command(client_ip, cmd)
    common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))

    file_list = stdout.split()
    return file_list


#######################################################
# 函数功能：计算指定目录下指定用户组的inode总数(包括所有子目录及
#         子目录下文件)
# 函数入参：
#       client_ip —— 执行cmd命令的节点ip
#       quota_path —— ls文件的全路径
#       quota_group —— 用户组名称
# 函数返回值：
#       指定目录下指定用户组的inode总数
#######################################################
def group_total_inodes(client_ip, quota_path, quota_group):
    log.info("\t[ group_total_inodes ]")
    cmd = ('ls -l %s') % quota_path
    common.run_command(client_ip, cmd)
    # 计算总inode数：ls /root/test_quota_dir/ -liR | grep quota_group | wc -l
    cmd = ("ls %s -liR | grep %s | wc -l") % (quota_path, quota_group)
    rc, stdout = common.run_command(client_ip, cmd)
    common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))

    log.info("\t group_total_inodes = %s" % stdout)
    return int(stdout)


#######################################################
# 函数功能：计算指定目录下指定用户的inode总数(包括所有子目录及子
#         目录下文件)
# 函数入参：
#       client_ip —— 执行cmd命令的节点ip
#       quota_path —— ls文件的全路径
#       quota_user —— 用户名称
# 函数返回值：
#       指定目录下指定用户的inode总数
#######################################################
def user_total_inodes(client_ip, quota_path, quota_user):
    log.info("\t[ user_total_inodes ]")
    cmd = ('ls -l %s') % quota_path
    common.run_command(client_ip, cmd)
    # 计算总inode数：ls /root/test_quota_dir/ -liR | grep quota_user | wc -l
    cmd = ("ls %s -liR | grep %s | wc -l") % (quota_path, quota_user)
    rc, stdout = common.run_command(client_ip, cmd)
    common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))

    log.info("\t user_total_inodes = %s" % stdout)
    return int(stdout)


#######################################################
# 函数功能：计算指定目录下的inode总数
# 函数入参：
#       client_ip —— 执行cmd命令的节点ip
#       quota_path —— ls文件的全路径
# 函数返回值：
#       指定目录下的inode总数(包括所有子目录及子目录下文件)
#######################################################
def dir_total_inodes(client_ip, quota_path):
    log.info("\t[ dir_total_inodes ]")
    cmd = ('ls -l %s') % quota_path
    common.run_command(client_ip, cmd)

    # 计算总inode数：ls /root/test_quota_dir/ -iR | grep -v "./" | grep -v ".:" | grep  -v "^\s*$" | wc -l
    cmd = ("ls %s -iR | grep -v \"./\" | grep -v \".:\" | grep  -v \"^\\s*$\" | wc -l") % (quota_path)
    rc, stdout = common.run_command(client_ip, cmd)
    common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))

    log.info("\t dir_total_inodes = %s" % stdout)
    return int(stdout)


#######################################################
# 函数功能：计算指定目录下指定用户或指定用户组的文件总大小（含所有
#         文件及目录）
# 函数入参：
#       client_ip —— 创建目录的节点ip
#       quota_path —— ls文件的全路径
#       filter_name —— 用户名或用户组名
# 函数返回值：
#       total_file_size：总文件大小，单位是字节
# 说明：【du命令被废弃，改用ls -l】
#######################################################
def user_or_group_total_file_size(client_ip, quota_path, filter_name):
    log.info("\t[ user_or_group_total_file_size ]")

    total_file_size = 0
    cmd = "cd %s; ls -lR | grep '^-'| grep %s" % (quota_path, filter_name)
    rc, stdout = common.run_command(client_ip, cmd)
    if stdout.strip() == '':
        return 0
    # common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        for file_size in stdout.strip().split("\n"):
            size = int(file_size.strip().split()[4])
            total_file_size = size + total_file_size

        log.info("\t total_file_size = %s" % total_file_size)
        return total_file_size


#######################################################
# 函数功能：计算指定目录下的文件总大小（含所有文件及目录）
# 函数入参：
#       node_ip —— 执行cmd命令的节点ip
#       quota_path —— 执行ls命令的全路径
# 函数返回值：
#       total_file_size：总文件大小，单位是字节
#######################################################
def dir_total_file_size(node_ip, quota_path):
    # 改为使用ls -l计算总文件大小
    total_file_size = 0
    cmd = "cd %s; ls -lR | grep '^-'" % quota_path
    rc, stdout = common.run_command(node_ip, cmd)
    if stdout.strip() == '':
        return 0
    # common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        for file_size in stdout.strip().split("\n"):
            size = int(file_size.strip().split()[4])
            total_file_size = size + total_file_size

        log.info("\t total_file_size = %s" % total_file_size)
        return total_file_size


#######################################################
# 函数功能：删除所有文件及目录
# 函数入参：
#       node_ip —— 创建目录的节点ip
#       quota_path —— 要创建目录的全路径
# 函数返回值：无
#######################################################
def delete_all_files_and_dir(node_ip, quota_path):
    log.info("\t[ delete_all_files_and_dir ]")

    # 清空目录
    common.rm_exe(node_ip, os.path.join(quota_path, '*'))
    return


#######################################################
# 函数功能：获取全部节点和客户端的ip
# 函数入参：
#       node_ip：执行cmd命令的节点ip
# 函数返回值：
#       clients_ip：全部节点和客户端的ip列表
#######################################################
def get_all_clients_and_nodes_ip():
    log.info("\t[ get_all_clients_and_nodes_ip ]")

    clients_ip = []
    rc, stdout = common.get_clients()
    common.judge_rc(rc, 0, "Execute command: get_clients failed. \nstdout: %s" % stdout)
    node_info = common.json_loads(stdout)
    nodes = node_info['result']
    for node in nodes:
        clients_ip.append(node['ip'])
    return clients_ip


#######################################################
# 函数功能：scp保存的/etc/passwd和/etc/group文件到指定节点
# 函数入参：
#       node_ip —— 执行cmd命令的节点ip
#       user_and_group —— "yes"代表拷贝含有自己创建的用户和用户组的passwd和group文件到其他节点
#                      —— "no"代表拷贝不含有自己创建的用户和用户组的passwd和group文件到其他节点
# 函数返回值：无
#######################################################
def scp_saved_passwd_and_group_to_all_other_nodes(node_ip, user_and_group):
    log.info("\t[ scp_saved_passwd_and_group_to_all_other_nodes ]")

    # 拷贝含有自己创建的用户和用户组的passwd和group文件到其他节点
    if user_and_group == "yes":
        all_clients_and_nodes_ip = get_all_clients_and_nodes_ip()
        for other_node_ip in all_clients_and_nodes_ip:
            cmd = "scp /opt/jiangxg/user_group_new/* %s:/etc/" % other_node_ip
            rc, stdout = common.run_command(node_ip, cmd)
            common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    # 拷贝不含有自己创建的用户和用户组的passwd和group文件到其他节点
    elif user_and_group == "no":
        all_clients_and_nodes_ip = get_all_clients_and_nodes_ip()
        for other_node_ip in all_clients_and_nodes_ip:
            cmd = "scp /opt/jiangxg/user_group_old/* %s:/etc/" % other_node_ip
            rc, stdout = common.run_command(node_ip, cmd)
            common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    return


#######################################################
# 函数功能：scp /etc/passwd, /etc/group到指定节点
# 函数入参：
#       node_ip —— 执行cmd命令的节点ip
# 函数返回值：无
#######################################################
def scp_passwd_and_group_to_all_other_nodes(node_ip):
    log.info("\t[ scp_passwd_and_group_to_all_other_nodes ]")

    all_clients_and_nodes_ip = get_all_clients_and_nodes_ip()
    for other_node_ip in all_clients_and_nodes_ip:
        cmd = "scp /etc/passwd /etc/group %s:/etc/" % other_node_ip
        rc, stdout = common.run_command(node_ip, cmd)
        common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    return


#######################################################
# 函数功能：修改文件所属的用户
# 函数入参：
#       client_ip —— 执行操作的节点ip
#       quota_dir —— 执行操作的目录
#       file_list —— 要修改属主的文件列表：["file1", "file2", ...]
#       user_name —— 要修改的属主名称：quota_user, quota_other_user, root
# 函数返回值：无
#######################################################
def change_file_user(client_ip, quota_dir, file_list, user_name):
    log.info("\t[ change_file_user ]")

    file_name_list = ""
    for file_name_tmp in file_list:
        file_name_list = file_name_tmp + " " + file_name_list

    cmd = "cd %s; chown %s %s" % (quota_dir, user_name, file_name_list)
    rc, stdout = common.run_command(client_ip, cmd)
    common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
    return


#######################################################
# 函数功能：修改文件所属的用户组
# 函数入参：
#       node_ip —— 执行操作的节点ip
#       quota_dir —— 执行操作的目录
#       file_list —— 要修改属主的文件列表："file1 file2 ..."
#       group_name —— 要修改的属主名称：quota_group, quota_other_group, root
# 函数返回值：无
#######################################################
def change_file_group(node_ip, quota_dir, file_list, group_name):
    log.info("\t[ change_file_group ]")

    file_name = ""
    for file_name_tmp in file_list:
        file_name = file_name_tmp + " " + file_name

    cmd = "cd %s; chgrp %s %s" % (quota_dir, group_name, file_name)
    rc, stdout = common.run_command(node_ip, cmd)
    common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
    return


#######################################################
# 函数功能：删除指定名称的用户
# 函数入参：
#       node_ip —— 执行cmd命令的节点ip
#       user_name —— 待删除的用户名称
# 函数返回值：无
#######################################################
def delete_quota_user(node_ip, user_name):
    log.info("\t[ delete_quota_user ]")

    if len(user_name) != 0:
        cmd = "userdel -r -f %s" % user_name
        rc, stdout = common.run_command(node_ip, cmd)
        try:
            if rc != 0:
                log.info("rc = %s" % (rc))
                raise Exception()
        except:
            log.info("WARNING: \ncmd = %s\nstdout = %s" % (cmd, stdout))
    else:
        log.info("user_name is null!")
    return


#######################################################
# 函数功能：创建指定名称、指定组的用户
# 函数入参：
#       node_ip —— 创建目录的节点ip
#       user_group —— 待创建的指定名称、指定组的用户
# 函数返回值：无
#######################################################
def create_quota_user(node_ip, user_name, user_group):
    log.info("\t[ create_quota_user ]")

    cmd = "useradd %s -g %s" % (user_name, user_group)
    rc, stdout = common.run_command(node_ip, cmd)
    common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    return


#######################################################
# 函数功能：删除指定名称的用户组
# 函数入参：
#       node_ip —— 创建目录的节点ip
#       group_name —— 待删除的用户组名称
# 函数返回值：无
#######################################################
def delete_quota_group(node_ip, group_name):
    log.info("\t[ delete_quota_group ]")

    if len(group_name) != 0:
        cmd = "groupdel %s" % (group_name)
        rc, stdout = common.run_command(node_ip, cmd)
        common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        log.info("group_name is null!")
    return


#######################################################
# 函数功能：创建指定名称的用户组
# 函数入参：
#       node_ip —— 创建目录的节点ip
#       group_name —— 待创建的用户组名称
# 函数返回值：无
#######################################################
def create_quota_group(node_ip, group_name):
    log.info("\t[ create_quota_group ]")

    cmd = "groupadd %s" % (group_name)
    rc, stdout = common.run_command(node_ip, cmd)
    common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    return


#######################################################
# 函数功能：删除特定的用户和用户组
# 函数入参：
#       node_ip —— 执行cmd命令的节点ip
# 函数返回值：无
#######################################################
def delete_designated_quota_user_and_group(node_ip):
    log.info("\t[ delete_designated_quota_user_and_group ]")

    # 删除用户：quota_user（属于组quota_group）和quota_other_user（属于组quota_other_group）
    cmd1 = "userdel -r %s; userdel -r %s" % (QUOTA_USER, QUOTA_OTHER_USER)
    rc, stdout = common.run_command(node_ip, cmd1)
    common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd1, stdout))

    # 删除用户组：quota_group和quota_other_group
    cmd2 = "groupdel %s; groupdel %s" % (QUOTA_GROUP, QUOTA_OTHER_GROUP)
    rc, stdout = common.run_command(node_ip, cmd2)
    common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd2, stdout))
    return


#######################################################
# 函数功能：使用pscli创建指定名称的用户组
# 函数入参：
#       node_ip —— 执行cmd命令的节点ip
#       quota_group_name - - 需要创建的组名
# 函数返回值：无
#######################################################
def create_designated_quota_group(quota_group_name, auth_provider_id):
    log.info("\t[ create_designated_quota_group %s ]" % quota_group_name)
    # 创建用户组：quota_group_name
    rc, stdout = common.create_auth_group(auth_provider_id=auth_provider_id, name=quota_group_name)
    common.judge_rc(rc, 0, "create_auth_group\nstdout = %s" % (stdout), exit_flag=False)
    return


#######################################################
# 函数功能：使用pscli创建指定名称的用户
# 函数入参：
#       node_ip —— 执行cmd命令的节点ip
#       quota_user_name - - 需要创建的用户名
#       quota_group_name - - 属组
# 函数返回值：无
#######################################################
def create_designated_quota_user(quota_user_name, quota_group_name, auth_provider_id):
    log.info("\t[ create_designated_quota_user %s]" % quota_user_name)
    # 创建用户：quota_user_name

    rc, stdout = common.get_auth_groups(auth_provider_id=auth_provider_id)
    common.judge_rc(rc, 0, "get_auth_groups\nstdout = %s" % (stdout), exit_flag=False)

    quota_group_id = 0
    data_get_groups = common.json_loads(stdout)
    for i in range(1, data_get_groups["result"]["total"] + 1):
        if quota_group_name == data_get_groups['result']['auth_groups'][i - 1]['name']:
            quota_group_id = data_get_groups['result']['auth_groups'][i - 1]['id']
            break

    rc, stdout = common.create_auth_user(auth_provider_id=auth_provider_id, name=quota_user_name, password=111111,
                                         primary_group_id=quota_group_id)
    common.judge_rc(rc, 0, "create_auth_user\nstdout = %s" % (stdout), exit_flag=False)

    nodeip_list = [NOTE_IP_1, NOTE_IP_2, NOTE_IP_3]
    for node_ip_tmp in nodeip_list:
        cmd = "mkdir /home/%s " % (quota_user_name)
        rc, stdout = common.run_command(node_ip_tmp, cmd)
        common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
    return


#######################################################
# 函数功能：使用pscli删除指定名称的用户
# 函数入参：
#       node_ip —— 执行cmd命令的节点ip
#       quota_user_name - - 需要删除的用户名
# 函数返回值：无
#######################################################
def delete_designated_quota_user(quota_user_name, auth_provider_id):
    log.info("\t[ delete_designated_quota_user %s]" % quota_user_name)

    rc, stdout = common.get_auth_users(auth_provider_id=auth_provider_id)
    common.judge_rc(rc, 0, "get_auth_users\nstdout = %s" % (stdout), exit_flag=False)

    quota_user_id = 0
    data_get_users = common.json_loads(stdout)
    for i in range(1, data_get_users["result"]["total"] + 1):
        if quota_user_name == data_get_users['result']['auth_users'][i - 1]['name']:
            quota_user_id = data_get_users['result']['auth_users'][i - 1]['id']
            break

    rc, stdout = common.delete_auth_users(ids=quota_user_id)
    common.judge_rc(rc, 0, "delete_auth_users\nstdout = %s" % stdout, exit_flag=False)

    nodeip_list = [NOTE_IP_1, NOTE_IP_2, NOTE_IP_3]
    for node_ip_tmp in nodeip_list:
        cmd = "rm -rf /home/%s " % quota_user_name
        rc, stdout = common.run_command(node_ip_tmp, cmd)
        common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
    return


#######################################################
# 函数功能：使用pscli删除指定名称的用户组
# 函数入参：
#       node_ip —— 执行cmd命令的节点ip
#       quota_user_name - - 需要删除的用户组名
# 函数返回值：无
#######################################################
def delete_designated_quota_group(quota_group_name, auth_provider_id):
    log.info("\t[ delete_designated_quota_group %s]" % quota_group_name)

    rc, stdout = common.get_auth_groups(auth_provider_id=auth_provider_id)
    common.judge_rc(rc, 0, "get_auth_groups\nstdout = %s" % stdout, exit_flag=False)

    quota_group_id = 0
    data_get_groups = common.json_loads(stdout)
    for i in range(1, data_get_groups["result"]["total"] + 1):
        if quota_group_name == data_get_groups['result']['auth_groups'][i - 1]['name']:
            quota_group_id = data_get_groups['result']['auth_groups'][i - 1]['id']
            break

    rc, stdout = common.delete_auth_groups(ids=quota_group_id)
    common.judge_rc(rc, 0, "delete_auth_groups\nstdout = %s" % stdout, exit_flag=False)
    return


#######################################################
# 函数功能：创建特定的用户和用户组
# 函数入参：
#       node_ip —— 执行cmd命令的节点ip
# 函数返回值：无
#######################################################
def create_designated_quota_user_and_group_new(node_ip, auth_provider_id):
    log.info("\t[ create_designated_quota_user_and_group ]")
    create_designated_quota_group(QUOTA_GROUP, auth_provider_id)
    create_designated_quota_group(QUOTA_OTHER_GROUP, auth_provider_id)
    create_designated_quota_user(QUOTA_USER, QUOTA_GROUP, auth_provider_id)
    create_designated_quota_user(QUOTA_OTHER_USER, QUOTA_OTHER_GROUP, auth_provider_id)
    # 防止刚创建的用户不能su 所以添加sleep40秒
    # time.sleep(40)
    return


#######################################################
# 函数功能：删除特定的用户和用户组
# 函数入参：
#       node_ip —— 执行cmd命令的节点ip
# 函数返回值：无
#######################################################
def delete_designated_quota_user_and_group_new(auth_provider_id):
    log.info("\t[ delete_designated_quota_user_and_group_new ]")
    delete_designated_quota_user(QUOTA_USER, auth_provider_id)
    delete_designated_quota_user(QUOTA_OTHER_USER, auth_provider_id)
    delete_designated_quota_group(QUOTA_GROUP, auth_provider_id)
    delete_designated_quota_group(QUOTA_OTHER_GROUP, auth_provider_id)
    return


#######################################################
# 函数功能：变换格式
# 函数入参：
#       user_id_list，格式如下：[1,2,3,4]
# 函数返回值：
#       format_id_list，格式如下：1,2,3,4
#######################################################
def format_id_list(id_list):
    log.info("\t[ format_id_list ]")

    # 把数字列表[1,2,3,4]转换成字符串列表['1','2','3','4']
    id_string_list = []
    for tmp in id_list:
        id_string_list.append(str(tmp))

    # 把列表['1','2','3','4']转换成元祖('1','2','3','4')
    seq = tuple(id_string_list)

    # 把元祖中元素拼接成：1,2,3,4
    comma = ","
    format_id_list = comma.join(seq)
    return format_id_list


#######################################################
# 函数功能：获取全部user_id列表
# 函数入参：
#       node_ip：执行cmd命令的节点ip
# 函数返回值：
#       user_id_list，格式如下：[1,2,3,4]
#######################################################
def get_user_id_list(auth_provider_id):
    log.info("\t[ get_user_id_list ]")

    user_id_list = []
    rc, stdout = common.get_auth_users(auth_provider_id=auth_provider_id)
    common.judge_rc(rc, 0, "Execute command: auth_provider_id failed. \nstdout: %s" % stdout)

    data_get_user = common.json_loads(stdout)
    for i in range(1, data_get_user["result"]["total"] + 1):
        user_id = data_get_user['result']['auth_users'][i - 1]['id']
        user_id_list.append(user_id)

    log.info("user_id_list = %s" % (user_id_list))
    return user_id_list


#######################################################
# 函数功能：删除所有用户
# 函数入参：
#       node_ip：执行cmd命令的节点ip
# 函数返回值：
#######################################################
def delete_all_user(auth_provider_id):
    log.info("\t[ delete_all_user ]")
    if auth_provider_id == -1:
        log.info("no user")
        return
    user_id_list = get_user_id_list(auth_provider_id)
    new_user_id_list = format_id_list(user_id_list)
    if len(new_user_id_list) != 0:
        rc, stdout = common.delete_auth_users(ids=new_user_id_list)
        common.judge_rc(rc, 0, "Execute command: delete_auth_users failed. \nstdout: %s" % stdout)
        check_result = common.json_loads(stdout)
    else:
        log.info("delete_all_user -> new_user_id_list = []")
        check_result = "no user"

    nodeip_list = [NOTE_IP_1, NOTE_IP_2, NOTE_IP_3]
    for node_ip_tmp in nodeip_list:
        cmd = "rm -rf /home/%s " % ('quota_*')
        rc, stdout = common.run_command(node_ip_tmp, cmd)
        common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
    return check_result


#######################################################
# 函数功能：获取全部group_id列表
# 函数入参：
#       node_ip：执行cmd命令的节点ip
# 函数返回值：
#       group_id_list，格式如下：[1,2,3,4]
#######################################################
def get_group_id_list(auth_provider_id):
    log.info("\t[ get_group_id_list ]")

    group_id_list = []
    rc, stdout = common.get_auth_groups(auth_provider_id=auth_provider_id)
    common.judge_rc(rc, 0, "Execute command: get_auth_groups failed. \nstdout: %s" % stdout)

    data_get_group = common.json_loads(stdout)
    for i in range(1, data_get_group["result"]["total"] + 1):
        group_id = data_get_group['result']['auth_groups'][i - 1]['id']
        group_id_list.append(group_id)

    log.info("group_id_list = %s" % group_id_list)
    return group_id_list


#######################################################
# 函数功能：删除所有用户组
# 函数入参：
#       node_ip：执行cmd命令的节点ip
# 函数返回值：
#######################################################
def delete_all_group(auth_provider_id):
    log.info("\t[ delete_all_group ]")
    if auth_provider_id == -1:
        log.info("no group")
        return
    group_id_list = get_group_id_list(auth_provider_id)
    new_group_id_list = format_id_list(group_id_list)
    if len(new_group_id_list) != 0:
        rc, stdout = common.delete_auth_groups(ids=new_group_id_list)
        common.judge_rc(rc, 0, "Execute command: delete_auth_groupsfailed. \nstdout: %s" % stdout)
        check_result = common.json_loads(stdout)
    else:
        log.info("delete_all_group -> new_group_id_list = []")
        check_result = "no group"

    return check_result


def create_designated_quota_user_and_group_old(node_ip):
    log.info("\t[ create_designated_quota_user_and_group_old ]")

    # 创建用户组：quota_group和quota_other_group
    cmd1 = "groupadd %s; groupadd %s" % (QUOTA_GROUP, QUOTA_OTHER_GROUP)
    rc, stdout = common.run_command(node_ip, cmd1)
    common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd1, stdout), exit_flag=False)

    # 创建用户：quota_user（属于组quota_group）和quota_other_user（属于组quota_other_group）
    cmd2 = "useradd %s -g %s; useradd %s -g %s" % (QUOTA_USER, QUOTA_GROUP, QUOTA_OTHER_USER, QUOTA_OTHER_GROUP)
    rc, stdout = common.run_command(node_ip, cmd2)
    common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd2, stdout), exit_flag=False)
    return


#######################################################
# 函数功能：删除所有的用户和用户组
# 函数入参：
#       node_ip —— 执行cmd命令的节点ip
# 函数返回值：无
#######################################################
def delete_all_quota_user_and_group(node_ip):
    log.info("\t[ delete_all_quota_user_and_group ]")

    # cat /etc/passwd | grep quota | cut -d ":" -f 1
    # cat /etc/group | grep quota | cut -d ":" -f 1

    cmd1 = "cat /etc/passwd | grep quota | cut -d \":\" -f 1"
    rc, stdout = common.run_command(node_ip, cmd1)
    common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd1, stdout))

    user_name_list = stdout.split()

    for user_name in user_name_list:
        delete_quota_user(node_ip, user_name)

    cmd2 = "cat /etc/group | grep quota | cut -d \":\" -f 1"
    rc, stdout = common.run_command(node_ip, cmd2)
    common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd2, stdout))

    group_name_list = stdout.split()

    for group_name in group_name_list:
        delete_quota_group(node_ip, group_name)
    return


#######################################################
# 函数功能：创建访问区
# 函数入参：无
# 函数返回值：无
#######################################################
def create_zone(node_ids):
    log.info("\t[ create_zone ]")
    rc, stdout = common.create_access_zone(name='testzone', node_ids=node_ids)
    common.judge_rc(rc, 0, "create_access_zone\nstdout = %s" % (stdout), exit_flag=False)
    errno = common.json_loads(stdout)['err_no']
    common.judge_rc(errno, 0, "Execute command: create_access_zone failed. \nstdout: %s" % stdout)
    time.sleep(10)
    return


#######################################################
# 函数功能：激活nas
# 函数入参：无
# 函数返回值：无
#######################################################
def enable_nas(access_zone_id):
    log.info("\t[ enable_nas ]")
    rc, stdout = common.enable_nas(access_zone_id=access_zone_id)
    common.judge_rc(rc, 0, "enable_nas\nstdout = %s" % (stdout), exit_flag=False)
    errno = common.json_loads(stdout)['err_no']
    common.judge_rc(errno, 0, "Execute command: enable_nas failed. \nstdout: %s" % stdout)
    return


def preparing_zone_nas():
    log.info("\t[ preparing_zone_nas ]")
    ob_node = common.Node()
    node_id_lst = ob_node.get_nodes_id()
    new_node_id_lst = format_id_list(node_id_lst)
    # 创建访问区
    pscli_info = nas_common.create_access_zone(new_node_id_lst, "testzone", auth_provider_id=None, isns_address=None)
    common.judge_rc(pscli_info['err_no'], 0, "create_access_zone failed")
    access_zone_id = pscli_info['result']
    pscli_info = nas_common.enable_nas(access_zone_id)
    common.judge_rc(pscli_info['err_no'], 0, "enable_nas failed")
    return access_zone_id


#######################################################
# 函数功能：准备访问区且enable_nas
# 函数入参：无
# 函数返回值：无
#######################################################
def preparing_zone_nas_old():
    log.info("\t[ preparing_zone_nas ]")
    ob_node = common.Node()
    node_id_lst = ob_node.get_nodes_id()
    new_node_id_lst = format_id_list(node_id_lst)
    auth_provider_id_flag = 0
    access_zone_id = 0
    # 创建访问区
    rc, stdout = common.get_access_zones()
    common.judge_rc(rc, 0, "get_access_zones\nstdout = %s" % stdout, exit_flag=False)
    if common.json_loads(stdout)['result']['access_zones'] == []:
        create_zone(new_node_id_lst)
        auth_provider_id_flag = 1
        access_zone_id = 1
    else:
        for i in range(common.json_loads(stdout)['result']['total']):
            if common.json_loads(stdout)['result']['access_zones'][i]['auth_provider_id'] == 4:
                auth_provider_id_flag = 1
                access_zone_id = common.json_loads(stdout)['result']['access_zones'][i]['id']
                break
    if auth_provider_id_flag == 0:
        create_zone(new_node_id_lst)
        auth_provider_id_flag = 1
        rc, stdout = common.get_access_zones()
        common.judge_rc(rc, 0, "get_access_zones\nstdout = %s" % (stdout), exit_flag=False)
        for i in range(common.json_loads(stdout)['result']['total']):
            if common.json_loads(stdout)['result']['access_zones'][i]['auth_provider_id'] == 4:
                access_zone_id = common.json_loads(stdout)['result']['access_zones'][i]['id']
                break
    rc, stdout = common.get_access_zones(ids=access_zone_id)
    common.judge_rc(rc, 0, "Execute command: get_access_zones failed. \nstdout: %s" % stdout)
    print common.json_loads(stdout)['result']['access_zones'][0]['nas_service_enabled']
    if common.json_loads(stdout)['result']['access_zones'][0]['nas_service_enabled'] is False:
        enable_nas(access_zone_id)
    return


def disable_all_nas():
    """
    Author:      chenjy1
    Date:        2018.08.19
    :return:
    """
    msg = nas_common.get_access_zones()
    access_zones = msg['result']['access_zones']
    if access_zones != "":
        for access_zone in access_zones:
            nas_service_enabled = access_zone["nas_service_enabled"]
            if nas_service_enabled is True:
                access_zone_id = access_zone["id"]
                check_result = nas_common.disable_nas(access_zone_id)
                if check_result["detail_err_msg"] != "":
                    log.error("disable_nas Failed")
                    raise Exception("disable_nas Failed")


def delete_all_zones():
    """
    Author:     chenjy1
    Date:       2018.08.19
    :return:
    """
    msg = nas_common.get_access_zones()
    access_zones = msg['result']['access_zones']
    for access_zone in access_zones:
        print access_zone['id']
        check_result = nas_common.delete_access_zone(access_zone['id'])
        if check_result["detail_err_msg"] != "":
            log.error("delete_access_zone Failed")
            raise Exception("delete_access_zone Failed")
    else:
        log.info("access_zone_id is Empty.")


def get_auth_provider_id_with_access_zone_name(access_zone_name):
    log.info("\t[ get_auth_provider_id_with_access_zone_name ]")
    rc, stdout = common.get_access_zones()
    common.judge_rc(rc, 0, 'get_access_zones failed', exit_flag=False)
    access_zone_id = -1
    pscli_info = common.json_loads(stdout)
    for az in pscli_info['result']['access_zones']:
        if az['name'] == access_zone_name:
            access_zone_id = az['id']
    if access_zone_id == -1:
        return -1
    auth_provider_id = nas_common.get_access_zones(access_zone_id)['result']['access_zones'][0]['auth_provider_id']
    return auth_provider_id


#######################################################
# 函数功能：清空环境，以备测试
# 函数入参：无
# 函数返回值：无
#######################################################
def cleaning_environment():
    log.info("（*）cleaning_environment（*）")

    '''
    1、删除所有配额相关的配置信息
    2、删除所有配额测试相关的文件和目录
    '''
    delete_all_quota_config()
    delete_all_files_and_dir(NOTE_IP_1, BASE_QUOTA_PATH)
    nas_common.delete_all_nas_config()
    # auth_provider_id = get_auth_provider_id_with_access_zone_name(QUOTA_ACCESS_ZONE)
    # delete_all_user(NOTE_IP_1, auth_provider_id)
    # delete_all_group(NOTE_IP_1, auth_provider_id)
    # disable_all_nas()
    # delete_all_zones()
    return


def wait_quota_work_after_mv(quota_dir, quota_type):
    """
    author: liyi
    date: 2018-10-13
    description:移动操作后等待10s 待quota_dir变成work状态
    :param quota_dir: 配额路径
    :param quota_type:配额类型
    :return:
    """
    rc, quota_dir = get_one_quota_id(quota_dir, quota_type)
    common.judge_rc(rc, 0, "get_one_quota_id failed")
    log.info("等待配额：%s 生效" % quota_dir)
    rc = wait_quota_work(quota_dir)
    common.judge_rc(rc, 0, "get quota info failed")
    return


def get_quota_filenr_used_nr(quota_id):
    """
    author:liyi
    date:2018-10-12
    description:获取quota_id文件使用个数
    :return:
    """
    rc, stdout = common.get_quota(ids=quota_id)
    stdout = common.json_loads(stdout)
    list_quotas = stdout["result"]["quotas"]
    for quota in list_quotas:
            filenr_used_nr = quota["filenr_used_nr"]
            return filenr_used_nr


def get_quota_logical_used_capacity(quota_id):
    """
    author:liyi
    date:2018-10-10
    description:获取quota_id逻辑配额使用容量
    :return:
    """
    rc, stdout = common.get_quota(ids=quota_id)
    stdout = common.json_loads(stdout)
    list_quotas = stdout["result"]["quotas"]
    for quota in list_quotas:
        logical_used_capacity = quota["logical_used_capacity"]
        return logical_used_capacity


def chkmult_client_volume(volume_id, fault_node_ip=None):
    """
    author:liyi
    date:2018-11-1
    description:检测卷是否可以切客户端写，直到可以才退出
    :param volume_id:
    :return:
    """
    ob_node = common.Node()
    node_id_lst = ob_node.get_nodes_id()
    count = 0
    while True:
        for ruleid in node_id_lst:
            cmd = "cd /home/parastor/tools;./nWatch -t oPara -i %s -c QMGR#fs_chkmult_client -a fsid=%s" % \
                  (ruleid, volume_id)
            rc, stdout = common.pscli_run_command(cmd, fault_node_ip=fault_node_ip)
            common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)
            if "qmgr is not here" not in stdout:
                can_or_cannot = stdout.split()[4]
                print("can_or_cannot", can_or_cannot)
                break
        if can_or_cannot == "empty":
            log.info("all node say: qmgr is not here")
            return rc
        if can_or_cannot == "can":
            break
        else:
            print "can_or_cannot = %s, sleep(2)" % (can_or_cannot)
            time.sleep(2)
            if count > 150:
                log.info("### chkmult over 5 min !!!")
                raise Exception("chkmult over 5 min")
            count = count + 1
