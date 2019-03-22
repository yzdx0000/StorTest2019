#!/usr/bin/python
# -*- encoding=utf8 -*-

#######################################################
# 脚本作者：陈津宇
# 脚本说明：远程复制公共函数
#######################################################

import os
import time
import random

import log
import get_config
import common
import tool_use


'''模拟枚举'''
MASTER, SLAVE, THIRD = range(3)  # 选择集群
ALL, THREE = range(2)
REP_DOMAIN = random.choice([ALL, THREE])  # 复制域节点

'''主、从端集群ip列表'''
MASTER_NODE_LST = get_config.get_allparastor_ips()
MASTER_CLIENT_LST = get_config.get_allclient_ip()
SLAVE_NODE_LST = get_config.get_slave_node_lst()
SLAVE_CLIENT_LST = get_config.get_slave_client_lst()
THIRD_NODE_LST = get_config.get_third_cluster_nodes_lst()
MASTER_RANDOM_NODE = random.choice(MASTER_NODE_LST)
SLAVE_RANDOM_NODE = random.choice(SLAVE_NODE_LST)

'''主从卷名'''
MASTER_VOLUME_NAME = get_config.get_one_volume_name()   # parastor
SLAVE_VOLUME_NAME = get_config.get_slave_volume_name()  # slaveparastor


"""测试路径"""
REP_PATH = get_config.get_rep_master_test_path()
MASTER_PAIR_PATH = REP_PATH
SLAVE_PAIR_PATH = get_config.get_rep_slave_test_path()

"""环境检查标志"""
ENV_CHECK=True

'''策略秒数'''
A_WEEK = 604800
HALF_MINUTE = 30
A_MINUTE = 60

'''pair状态名称'''
PAIR_SPLIT = 'split'
PAIR_NORMAL = 'normal'
PAIR_RUNNING = 'running'
PAIR_FAULT = 'fault'
PAIR_PAUSE = 'pause'
PAIR_UNCONNECT = 'unconnected'

'''策略周期'''
BY_YEAR = 'BY_YEAR'
BY_MONTH = 'BY_MONTH'
BY_WEEK = 'BY_WEEK'
BY_DAY = 'BY_DAY'

'''复制域是否允许小于3节点'''
REP_AREA_ONE_NODE = True


"""****************************** rep pscli 命令 ******************************"""


def enable_rep_server(node_ids=None, print_flag=True, fault_node_ip=None, run_cluster=MASTER):
    enable_rep_server_timeout = 600  # todo 待开发确认超时间多少合适
    start_time = time.time()
    rc, stdout = common.enable_rep_server(node_ids=node_ids, print_flag=print_flag, fault_node_ip=fault_node_ip,
                                          run_cluster=run_cluster)
    if rc != 0:
        return rc, {}
    else:
        exist_time = int(time.time() - start_time)
        if exist_time > enable_rep_server_timeout:
            return -1, {}
        else:
            pscli_info = common.json_loads(stdout)
        return rc, pscli_info


def disable_rep_server(node_ids=None, print_flag=True, fault_node_ip=None, run_cluster=MASTER):
    rc, stdout = common.disable_rep_server(node_ids=node_ids, print_flag=print_flag, fault_node_ip=fault_node_ip,
                                           run_cluster=run_cluster)
    if rc != 0:
        return rc, {}
    else:
        pscli_info = common.json_loads(stdout)
        return rc, pscli_info


def get_rep_area(print_flag=True, fault_node_ip=None, run_cluster=MASTER):
    rc, stdout = common.get_rep_area(print_flag=print_flag, fault_node_ip=fault_node_ip, run_cluster=run_cluster)
    if rc != 0:
        return rc, {}
    else:
        pscli_info = common.json_loads(stdout)
        return rc, pscli_info


def create_rep_channel(name=None, ip=None, print_flag=True, fault_node_ip=None, run_cluster=MASTER):
    rc, stdout = common.create_rep_channel(name=name, ip=ip, print_flag=print_flag, fault_node_ip=fault_node_ip,
                                           run_cluster=run_cluster)
    if rc != 0:
        return rc, {}
    else:
        pscli_info = common.json_loads(stdout)
        return rc, pscli_info


def delete_rep_channel(channel_id=None, print_flag=True, fault_node_ip=None, run_cluster=MASTER):
    rc, stdout = common.delete_rep_channel(channel_id=channel_id, print_flag=print_flag, fault_node_ip=fault_node_ip,
                                           run_cluster=run_cluster)
    if rc != 0:
        return rc, {}
    else:
        pscli_info = common.json_loads(stdout)
        return rc, pscli_info


def get_rep_channels(ids=None, print_flag=True, fault_node_ip=None, run_cluster=MASTER):
    rc, stdout = common.get_rep_channels(ids=ids, print_flag=print_flag, fault_node_ip=fault_node_ip,
                                         run_cluster=run_cluster)
    if rc != 0:
        return rc, {}
    else:
        pscli_info = common.json_loads(stdout)
        return rc, pscli_info


def get_rep_remote_dir(channel_id=None, parent_dir=None, page_number=None, print_flag=True, fault_node_ip=None,
                       run_cluster=MASTER):
    rc, stdout = common.get_rep_remote_dir(channel_id=channel_id, parent_dir=parent_dir, page_number=page_number,
                                           print_flag=print_flag, fault_node_ip=fault_node_ip, run_cluster=run_cluster)
    if rc != 0:
        return rc, {}
    else:
        pscli_info = common.json_loads(stdout)
        return rc, pscli_info


def create_rep_pair(rep_channel_id=None, source_directory=None, destination_directory=None, print_flag=True,
                    fault_node_ip=None, run_cluster=MASTER):
    rc, stdout = common.create_rep_pair(rep_channel_id=rep_channel_id, source_directory=source_directory,
                                        destination_directory=destination_directory,
                                        print_flag=print_flag, fault_node_ip=fault_node_ip, run_cluster=run_cluster)
    if rc != 0:
        return rc, {}
    else:
        pscli_info = common.json_loads(stdout)
        return rc, pscli_info


def split_rep_pair(id=None, print_flag=True, fault_node_ip=None, run_cluster=MASTER):
    rc, stdout = common.split_rep_pair(id=id, print_flag=print_flag, fault_node_ip=fault_node_ip,
                                       run_cluster=run_cluster)
    if rc != 0:
        return rc, {}
    else:
        pscli_info = common.json_loads(stdout)
        return rc, pscli_info


def recover_rep_pair(id=None, print_flag=True, fault_node_ip=None, run_cluster=MASTER):
    rc, stdout = common.recover_rep_pair(id=id, print_flag=print_flag, fault_node_ip=fault_node_ip,
                                         run_cluster=run_cluster)
    if rc != 0:
        return rc, {}
    else:
        pscli_info = common.json_loads(stdout)
        return rc, pscli_info


def delete_rep_pair(id=None, print_flag=True, fault_node_ip=None, run_cluster=MASTER):
    rc, stdout = common.delete_rep_pair(id=id, print_flag=print_flag, fault_node_ip=fault_node_ip,
                                        run_cluster=run_cluster)
    if rc != 0:
        return rc, {}
    else:
        pscli_info = common.json_loads(stdout)
        return rc, pscli_info


def get_rep_pairs(ids=None, print_flag=True, fault_node_ip=None, run_cluster=MASTER):
    rc, stdout = common.get_rep_pairs(ids=ids, print_flag=print_flag, fault_node_ip=fault_node_ip,
                                      run_cluster=run_cluster)
    if rc != 0:
        return rc, {}
    else:
        pscli_info = common.json_loads(stdout)
        return rc, pscli_info


def create_rep_policy(name=None, rep_pair_id=None, period_type=None, months=False, week_days=None, days=None,
                      hours=None, minute=None, expire_time=None, print_flag=True, fault_node_ip=None,
                      run_cluster=MASTER):
    rc, stdout = common.create_rep_policy(name=name, rep_pair_id=rep_pair_id, period_type=period_type,
                                          months=months, week_days=week_days, days=days, hours=hours, minute=minute,
                                          expire_time=expire_time, print_flag=print_flag, fault_node_ip=fault_node_ip,
                                          run_cluster=run_cluster)
    if rc != 0:
        return rc, {}
    else:
        pscli_info = common.json_loads(stdout)
        return rc, pscli_info


def delete_rep_policies(ids=None, print_flag=True, fault_node_ip=None, run_cluster=MASTER):
    rc, stdout = common.delete_rep_policies(ids=ids, print_flag=print_flag, fault_node_ip=fault_node_ip,
                                            run_cluster=run_cluster)
    if rc != 0:
        return rc, {}
    else:
        pscli_info = common.json_loads(stdout)
        return rc, pscli_info


def update_rep_policy(id=None, name=None, rep_pair_id=None, period_type=None, months=False, week_days=None, days=None,
                      hours=None, minute=None, expire_time=None, print_flag=True, fault_node_ip=None,
                      run_cluster=MASTER):
    rc, stdout = common.update_rep_policy(id=id, name=name, rep_pair_id=rep_pair_id,
                                          period_type=period_type, months=months, week_days=week_days, days=days,
                                          hours=hours,minute=minute, expire_time=expire_time, print_flag=print_flag,
                                          fault_node_ip=fault_node_ip, run_cluster=run_cluster)
    if rc != 0:
        return rc, {}
    else:
        pscli_info = common.json_loads(stdout)
        return rc, pscli_info


def get_rep_policies(ids=None, print_flag=True, fault_node_ip=None, run_cluster=MASTER):
    rc, stdout = common.get_rep_policies(ids=ids, print_flag=print_flag, fault_node_ip=fault_node_ip,
                                         run_cluster=run_cluster)
    if rc != 0:
        return rc, {}
    else:
        pscli_info = common.json_loads(stdout)
        return rc, pscli_info


def start_rep_task(id=None, print_flag=True, fault_node_ip=None, run_cluster=MASTER):
    rc, stdout = common.start_rep_task(id=id, print_flag=print_flag, fault_node_ip=fault_node_ip,
                                       run_cluster=run_cluster)
    if rc != 0:
        return rc, {}
    else:
        pscli_info = common.json_loads(stdout)
        return rc, pscli_info


def pause_rep_task(id=None, print_flag=True, fault_node_ip=None, run_cluster=MASTER):
    rc, stdout = common.pause_rep_task(id=id, print_flag=print_flag, fault_node_ip=fault_node_ip,
                                       run_cluster=run_cluster)
    if rc != 0:
        return rc, {}
    else:
        pscli_info = common.json_loads(stdout)
        return rc, pscli_info


def resume_rep_task(id=None, print_flag=True, fault_node_ip=None, run_cluster=MASTER):
    rc, stdout = common.resume_rep_task(id=id, print_flag=print_flag, fault_node_ip=fault_node_ip,
                                        run_cluster=run_cluster)
    if rc != 0:
        return rc, {}
    else:
        pscli_info = common.json_loads(stdout)
        return rc, pscli_info


def delete_abnormal_rep_task(id=None, print_flag=True, fault_node_ip=None, run_cluster=MASTER):
    rc, stdout = common.delete_abnormal_rep_task(id=id, print_flag=print_flag, fault_node_ip=fault_node_ip,
                                                 run_cluster=run_cluster)
    if rc != 0:
        return rc, {}
    else:
        pscli_info = common.json_loads(stdout)
        return rc, pscli_info


def start_rep_task_scp(pair_id=None, print_flag=True, fault_node_ip=None, run_cluster=MASTER):
    # todo 起即时任务未实现查看任务的功能，先用scp替代
    """
    author:chenjy1
    description:起pair任务
    date:20181218
    :param pair_id:
    :param print_flag:
    :param fault_node_ip:
    :param run_cluster:
    :return:
    """
    #todo return rc, {} 中的{}以后替代为 start_rep_task的json串
    rc, pscli_info = get_rep_pairs(ids=pair_id)
    if rc !=0:
        return rc, {}
    m_dir = pscli_info['result']['source_directory']
    s_dir = pscli_info['result']['destination_directory']
    cmd = 'scp -rp %s root@%s:%s' % (m_dir, SLAVE_RANDOM_NODE, s_dir)
    rc, stdout = common.run_command(MASTER_RANDOM_NODE, cmd)
    if rc !=0:
        return rc, {}
    return rc, {}


def check_data_consistency(anchor_path, journal_path, source_node_lst, destination_node_lst):
    '''
    author:chenjy1
    description:校验数据一致
    date:20181218
    :param anchor_path:
    :param journal_path:
    :param source_node_lst:
    :param destination_node_lst:
    :return:
    '''
    rc = scp_journal(journal_path, source_node_lst, destination_node_lst)
    if rc !=0:
        return rc
    rc = vdb_check(anchor_path, journal_path, destination_node_lst)
    if rc !=0:
        return rc
    return rc


def md5sum(ip, file):
    '''
    author:chenjy1
    description:计算md5
    date:20181218
    :param ip:
    :param file:
    :return:
    '''
    cmd = 'md5sum %s' % (file)
    rc, stodut = common.run_command(ip, cmd)
    if rc!= 0:
        return rc, stodut
    return rc, stodut


def compare_md5(ip1, file1, ip2, file2):
    '''
    author:chenjy1
    description:比较两节点两文件md5
    date:20181218
    :param ip1:
    :param file1:
    :param ip2:
    :param file2:
    :return:
    '''
    cmd = 'md5sum %s' % (file1)
    rc, md5_1 = common.run_command(ip1, cmd)
    if rc != 0:
        return rc
    cmd = 'md5sum %s' % (file2)
    rc, md5_2 = common.run_command(ip2, cmd)
    if rc != 0:
        return rc
    if md5_1 != md5_2:
        log.info('two file md5 not equal')
        return -1
    return 0


def get_inode(ip, file):
    '''
    author:chenjy1
    description:获取inode值
    date:20181218
    :param ip:
    :param file:
    :return:
    '''
    cmd = 'ls -i %s' % file
    rc, stdout = common.run_command(ip, cmd)
    if rc != 0:
        return rc, 0
    inode = stdout.strip().split()[0]
    return rc, inode


def get_current_time(ip=None):
    """
    author:chenjy1
    description:获取环境当前时间
    :param ip:执行ip
    :return:
    """
    cmd = 'date +%s'
    rc, stdout = common.run_command(ip, cmd, print_flag=True)
    return rc, stdout


def create_rep_policy_by_time(name, after_time, rep_pair_id=None, expire_time=None, print_flag=True,
                              fault_node_ip=None, run_cluster=MASTER):
    '''
    author:chenjy1
    description:创建策略任务，执行时间为after_time之后
    date:20181218
    :param name:
    :param after_time:
    :param rep_pair_id:
    :param expire_time:
    :param print_flag:
    :param fault_node_ip:
    :param run_cluster:
    :return:
    '''
    if after_time < 1:
        return -1, 0, {}
    nodeip = MASTER_RANDOM_NODE
    left_second = 0
    hour = 0
    minute = 0
    second = 0
    cmd = 'date -d "%s minute"' % (after_time - 1) + ' +%T'
    rc, stdout = common.run_command(nodeip, cmd)
    if rc != 0:
        return rc, 0, {}
    moment_str = stdout.strip()
    second = int(moment_str.split(':')[2])
    if (60 - second) <= 30:
        left_second = (120 - second) + (after_time - 1) * 60
        hour = int(moment_str.split(':')[0])
        minute = int(moment_str.split(':')[1]) + 1
        if minute >= 60:
            minute -= 60
            hour += 1
            if hour >= 24:
                hour -= 24
    else:
        left_second = 60 - second + (after_time - 1) * 60
        hour = int(moment_str.split(':')[0])
        minute = int(moment_str.split(':')[1])

    rc, pscli_info = create_rep_policy(name=None, rep_pair_id=None, period_type='BY_DAY', hours=hour, minute=minute,
                                       run_cluster=run_cluster)
    if rc != 0:
        return rc, 0, {}
    return rc, left_second, pscli_info


def create_dir_tree(ip, anchor_path, depth, width, journal_path='/tmp', files=1, size='4k', threads=8,
                    xfersize='4k', elapsed=10):
    '''
    author:chenjy1
    description:创建目录+文件
    date:20181218
    :param ip:
    :param anchor_path:
    :param depth:
    :param width:
    :param journal_path:
    :param files:
    :param size:
    :param threads:
    :param xfersize:
    :param elapsed:
    :return:
    '''
    ob_vdb = tool_use.Vdbenchrun(depth=depth, width=width, files=files, size=size, threads=threads,
                                 xfersize=xfersize, elapsed=elapsed)
    rc = ob_vdb.run_create(anchor_path, journal_path, ip)
    return rc


def vdb_create(anchor_path, journal_path='/tmp', *args):
    '''
    author:chenjy1
    description:创建文件
    date:20181218
    :param anchor_path:
    :param journal_path:
    :param args:
    :return:
    '''
    obj_vdbench = tool_use.Vdbenchrun(depth=2, width=2, files=10, size='4k', threads=8, xfersize='4k', elapsed=20)
    rc = obj_vdbench.run_create(anchor_path, journal_path, *args)
    return rc


def scp_journal(journal_path, source_node_lst, destination_node_lst):
    '''
    author:chenjy1
    description:复制校验文件
    date:20181218
    :param journal_path:
    :param source_node_lst:
    :param destination_node_lst:
    :return:
    '''
    for i in range(len(source_node_lst)):
        cmd = 'scp %s root@%s:%s' % (journal_path, destination_node_lst[i], journal_path)
        rc, stdout = common.run_command(source_node_lst[i], cmd)
        if rc !=0:
            return rc
    return 0


def vdb_check(anchor_path, journal_path='/tmp', *args):
    '''
    author:chenjy1
    description:vdbench检验一致性
    date:20181218
    :param anchor_path:
    :param journal_path:
    :param args:
    :return:
    '''
    obj_vdbench = tool_use.Vdbenchrun(depth=2, width=2, files=10, size='4k', threads=8, xfersize='4k', elapsed=20)
    rc = obj_vdbench.run_check(anchor_path, journal_path, *args)
    return rc


def convert_abs_to_cmd(path):
    '''
    author:        chenjy1
    date:          20181218
    description:   格式转换:/mnt/parastor --> parastor:/
    :param path:  (str)/mnt/parastor格式路径
    :return:      (str)parastor:/格式字符
    '''
    dir_lst = path.split('/')
    dir_lst = dir_lst[2:]
    return dir_lst[1] + ':' + '/'.join(dir_lst)


def convert_lst_to_str(id_list):
    '''
    author:          chenjy1
    date:            20181218
    description:     列表转换为','分割的字符串
    :param id_list: (lst)列表
    :return:        (str)','分割的字符串
    '''
    id_str = ','.join(str(i) for i in id_list)
    return id_str


def convert_lst_to_str_by_other_symbol(id_list, symbol):
    '''
    author:          chenjy1
    date:            20181218
    description:     列表转换为symbol分割的字符串
    :param id_list: (lst)列表
    :param symbol:  (str)字符
    :return:        (str)symbol分割的字符串
    '''
    id_str = symbol.join(str(i) for i in id_list)
    return id_str


def generate_special_symbol_name():
    '''
    author:          chenjy1
    date:            20181218
    description:     生成特殊字符
    :return:
    '''
    special_symbol = "~@#$%^*-=+?!,."
    n = random.choice(range(2, 7))
    wrong_lst = random.sample(special_symbol, n)
    wrong_str = ''.join(wrong_lst)
    return wrong_str


def generate_wrong_id():
    '''
    author:          chenjy1
    date:            20181218
    description:     生成错误id
    :return:
    '''
    wrong_lst = [chr(i) for i in range(97, 123)]
    special_symbol = "~@#$%^*-=+?!,."
    wrong_lst.extend(special_symbol)
    n = random.choice(range(1, 7))
    wrong_lst = random.sample(wrong_lst, n)
    wrong_str = convert_lst_to_str(wrong_lst)
    return wrong_str


def create_dir(ip, basedir, basename, count):
    '''
    author:            chenjy1
    date:              20181218
    description:       在basedir下创建basename名开头的count个目录
    :param ip:        (str)ip
    :param basedir:   (str)basedir
    :param basename:  (str)basename
    :param count:     (int)个数
    :return:
    '''
    dir_lst = []
    for i in range(count):
        common.mkdir_path(ip, os.path.join(basedir, basename + '_' + str(count)))
        dir_lst.append(os.path.join(basedir, basename + '_' + str(count)))
    return dir_lst


def create_file(ip, path, basename, file_count, file_size):
    '''
    author:            chenjy1
    date:              20181218
    description:       创建文件
    :param ip:        (str)创建文件的ip
    :param path:      (str)创建文件的路径
    :param basename:  (str)basename
    :param file_count:(int)文件数量
    :param file_size: (int)多少MB
    :return:          rc值
    '''
    cmd = ("cd %s; for i in {1..%s}; do dd if=/dev/zero of=%s_$i bs=1M count=%s; done") % (
        path, file_count, basename, file_size)
    rc, stdout = common.run_command(ip, cmd, print_flag=True)
    return rc


def create_soft_link(ip, des_dentry, soft_link):
    '''
    author:chenjy1
    description:创建软连接
    date:20181218
    :param ip:
    :param des_dentry:
    :param soft_link:
    :return:
    '''
    cmd = 'ln -s %s %s' % (des_dentry, soft_link)
    rc, stdout = common.run_command(ip)
    if rc !=0:
        return rc, ''
    return rc, stdout


def create_one_volume(name, run_cluster=MASTER):
    '''
    author:chenjy1
    description:创建一个卷
    date:20181218
    :param name:
    :param run_cluster:
    :return:
    '''
    ob_volume = common.Volume()
    same_name_volume_id_lst = []
    rc, stdout = common.get_volumes(run_cluster=run_cluster, print_flag=False)
    if rc != 0:
        return rc, 0
    pscli_info = common.json_loads(stdout)
    same_name_volume_id = 0
    for volume in pscli_info['result']['volumes']:
        if name in volume['name']:
            same_name_volume_id = volume['id']
            same_name_volume_id_lst.append(same_name_volume_id)
    for id in same_name_volume_id_lst:
        rc, stdout = common.delete_volumes(id)
        if rc != 0:
            return rc, 0

    """获取默认卷的信息"""
    volumename = ''
    if run_cluster == MASTER:
        volumename = MASTER_VOLUME_NAME
    elif run_cluster == SLAVE:
        volumename = MASTER_VOLUME_NAME
    one_volume = {}
    rc, stdout = common.get_volumes()
    if rc != 0:
        return rc, 0
    pscli_info = common.json_loads(stdout)
    for volume in pscli_info['result']['volumes']:
        if volume['name'] == volumename:
            one_volume = volume
            break

    rc, json_info = ob_volume.create_volume(name, one_volume['storagepool_id'], one_volume['layout']['stripe_width'],
                                            one_volume['layout']['disk_parity_num'],
                                            one_volume['layout']['node_parity_num'],
                                            one_volume['layout']['replica_num'])
    common.judge_rc(rc, 0, "create volume failed")

    volume_id = 0
    rc, stdout = common.get_volumes(run_cluster=run_cluster, print_flag=False)
    if rc != 0:
        return rc, 0
    pscli_info = common.json_loads(stdout)
    for volume in pscli_info['result']['volumes']:
        if volume['name'] == name:
            volume_id = volume['id']
    return rc, volume_id


def get_all_policies_ids(print_flag=True, run_cluster=MASTER):
    """
    author:chenjy1
    date:20181218
    description:获取某集群所有策略
    :param print_flag:
    :param run_cluster:
    :return:
    """
    rc, pscli_info = get_rep_policies(print_flag=print_flag, run_cluster=run_cluster)
    if rc != 0:
        return rc, ''
    id_list = []
    for policy in pscli_info['result']:
        id_list.append(policy['id'])
    id_str = ','.join(str(i) for i in id_list)
    return rc, id_str


def get_all_channel_idlst(print_flag=True, run_cluster=MASTER):
    """
    author:chenjy1
    date:20181218
    description:获取某集群所有通道id
    :param print_flag:
    :param run_cluster:
    :return:
    """
    rc, pscli_info = get_rep_channels(print_flag=print_flag, run_cluster=run_cluster)
    if rc != 0:
        return rc, []
    id_list = []
    for channel in pscli_info['result']:
        id_list.append(channel['id'])
    return rc, id_list


def get_all_pair_idlst(print_flag=True, run_cluster=MASTER):
    """
    author:chenjy1
    date:20181218
    description:获取某集群所有pair
    :param print_flag:
    :param run_cluster:
    :return:
    """
    rc, pscli_info = get_rep_pairs(print_flag=print_flag, run_cluster=run_cluster)
    if rc != 0:
        return rc, ''
    id_list = []
    for pair in pscli_info['result']:
        id_list.append(pair['id'])
    return rc, id_list


def get_one_pair_id(rep_channel_id, source_directory, destination_directory):
    """
    author:chenjy1
    date:20181218
    description:获取单个pair的id
    :param rep_channel_id:
    :param source_directory:
    :param destination_directory:
    :return:
    """
    ret_id = 0
    rc, pscli_info = get_rep_pairs()
    if rc != 0:
        return rc, 0
    same_cnt = 0
    for pair in pscli_info['result']:
        if pair['rep_channel_id'] == rep_channel_id  and pair['source_directory'] == source_directory and \
                        pair['destination_directory'] == destination_directory:
            ret_id = pair['id']
            same_cnt += 1
    if same_cnt >1:
        common.except_exit('more than two pair have same info')
    return rc, ret_id


def get_one_pair_stat(ids=None, print_flag=True, run_cluster=MASTER):
    """
    author:chenjy1
    date:20181218
    description:获取单个pair的状态
    :param ids:
    :param print_flag:
    :param run_cluster:
    :return:
    """
    rc, pscli_info = get_rep_pairs(ids=ids, print_flag=print_flag, run_cluster=run_cluster)
    if rc != 0:
        return rc, ''
    return rc, pscli_info['rep_pair_stat']


def disable_all_rep_server(run_cluster=MASTER, print_flag=True):
    """
    author:chenjy1
    date:20181218
    description:关闭某集群复制域
    :param run_cluster:
    :param print_flag:
    :return:
    """
    rep_idlst = []
    idstr = ''
    rc, pscli_info = get_rep_area(print_flag=print_flag, run_cluster=run_cluster)
    if rc != 0:
        return rc
    else:
        if pscli_info['result'] == '':
            return rc
        else:
            rep_idlst = pscli_info['result']['node_ids']
            idstr = convert_lst_to_str(rep_idlst)
    if idstr != '':
        rc, pscli_info = disable_rep_server(idstr, print_flag=True, run_cluster=run_cluster)
        return rc
    return rc


def get_node_id_lst(run_cluster=MASTER):
    """
    author:chenjy1
    date:20181218
    description:获取某集群所有节点id列表
    :param run_cluster:
    :return:
    """
    id_lst = []
    rc, stdout = common.get_nodes(run_cluster=run_cluster, print_flag=False)
    if rc != 0:
        return rc, id_lst
    pscli_info = common.json_loads(stdout)
    for node in pscli_info['result']['nodes']:
        id_lst.append(node['node_id'])
    return rc, id_lst


def generate_noexist_idstr(real_id_lst):
    """
    author:chenjy1
    date:20181218
    description:生成不存在的id，以,分割
    :param real_id_lst:
    :return:
    """
    large_lst = range(100, 200)
    for id in real_id_lst:
        if id in large_lst:
            large_lst.remove(id)
    ids = random.choice(large_lst)
    number_lst = range(3, 90)
    failid_number = random.choice(number_lst)
    no_exist_ids = convert_lst_to_str(large_lst[0:failid_number])
    return no_exist_ids


def get_channel_id_by_ip(ip, run_cluster=MASTER):
    """
    author:chenjy1
    date：20181218
    description:通过通道的ip获取id
    :param ip:
    :param run_cluster:
    :return:
    """
    rc, pscli_info = get_rep_channels()
    if rc != 0:
        log.info('get_rep_channels failed')
        return rc, ''
    else:
        for channel in pscli_info['result']:
            if channel['ip'] == ip:
                return rc, channel['ip']
    return 1, ''


def ip_for_create_channel(id_lst, run_cluster=MASTER):
    """
    author:chenjy1
    description:根据某集群的复制域idlst ,获取域内随机节点的随机数据网或管理网
    :param id_lst:
    :param run_cluster:
    :return:
    """
    #todo 管理网p300暂没实现
    nodeid = random.choice(id_lst)
    rc, stdout = common.get_nodes(nodeid, run_cluster=run_cluster)
    if rc != 0:
        return rc, ''
    pscli_info = common.json_loads(stdout)
    dataip_lst = []
    for dataip in pscli_info['result']['nodes'][0]['data_ips']:
        dataip_lst.append(dataip)
    return rc, (random.choice(dataip_lst))['ip_address']


def get_cluster_all_ip(run_cluster):
    '''
    author:chenjy1
    description:获取集群所有ip，以字典形式返回
    date:20181218
    :param run_cluster:
    :return:
    '''
    ip_dic = {}
    #ip_dic[1]  ip_dic[1]['ctlip']
    #ip_dic['2']  ip_dic[2]['ctlip']
    rc, id_lst = get_node_id_lst(run_cluster=run_cluster)
    if rc !=0:
        return rc, {}
    for nodeid in id_lst:
        ip_dic[nodeid] = {}
        ip_dic[nodeid]['ctlip'] = []
        ip_dic[nodeid]['dataip'] = []
        rc, stdout = common.get_nodes(print_flag=False,ids=nodeid,run_cluster=run_cluster)
        if rc !=0:
            return rc, {}
        pscli_info = common.json_loads(stdout)
        for ctlip in pscli_info['result']['nodes'][0]['ctl_ips']:
            ip_dic[nodeid]['ctlip'].append(ctlip['ip_address'])
        for dataip in pscli_info['result']['nodes'][0]['data_ips']:
            ip_dic[nodeid]['dataip'].append(dataip['ip_address'])
    return rc, ip_dic


def get_rep_policy_id(name, run_cluster=MASTER):
    '''
    author:chenjy1
    description:获取策略id
    date:20181218
    :param name:
    :param run_cluster:
    :return:
    '''
    same_cnt = 0
    policyid = 0
    rc, pscli_info = get_rep_policies(run_cluster=run_cluster)
    if rc != 0:
        return rc, 0
    for policy in pscli_info['result']['rep_policies']:
        if policy['name'] == name:
            policyid = policy['id']
            same_cnt += 1
    if same_cnt > 1 :
        common.except_exit('more than two policy have same name ')
    if same_cnt == 0:
        log.warn('cannot find the policy with name %s' % name)
        return -1, 0
    return rc, policyid



def format_area_channel():
    '''
    ready_info:
    ready_info['area'] = get_area的pscli_info
    ready_info['channel'] = get_channel的pscli_info
    '''
    '''先检查环境中是否有复制域和通道'''
    ready_info = {}
    create_flag = False
    for cluster in [MASTER, SLAVE]:
        rc, pscli_info = get_rep_area(run_cluster=cluster)
        if rc != 0:
            return rc, {}
        if pscli_info['result'] == '':  # 判断无复制域
            create_flag = True
            break
        rep_area_id_lst = pscli_info['result']['node_ids']
        if not REP_AREA_ONE_NODE:
            if len(rep_area_id_lst) < 3:
                create_flag = True
                break

    rc, pscli_info = get_rep_channels(run_cluster=MASTER)
    if rc != 0:
        return rc, {}
    if pscli_info['result'] == "":  # 判断无通道
        create_flag = True

    find_slave_ip_flag = False
    rc, ip_dic = get_cluster_all_ip(run_cluster=SLAVE)
    if rc != 0:
        return rc, {}

    ip_lst = []
    for nodeid in ip_dic:
        for ctlip in ip_dic[nodeid]['ctlip']:
            ip_lst.append(ctlip)
        for dataip in ip_dic[nodeid]['dataip']:
            ip_lst.append(dataip)
    for channel in pscli_info['result']:
        if channel['ip'] in ip_lst:
            find_slave_ip_flag = True
            break
    if find_slave_ip_flag is False:
        create_flag = True

    master_id_lst = []
    slave_id_lst = []
    '''没有则创建'''
    if create_flag:
        delete_all_rep_config(True, clusters=[MASTER, SLAVE])
        rc, master_all_id_lst = get_node_id_lst()
        if rc !=0:
            return rc, {}
        rc, salve_all_id_lst = get_node_id_lst(run_cluster=SLAVE)
        if rc !=0:
            return rc, {}
        if REP_DOMAIN == ALL:
            master_id_lst = master_all_id_lst
            slave_id_lst = salve_all_id_lst
        else:
            master_id_lst = random.sample(master_all_id_lst, 3)
            slave_id_lst = random.sample(salve_all_id_lst, 3)
            master_left_id_lst = master_all_id_lst
            salve_left_id_lst = salve_all_id_lst
            for i in master_all_id_lst:
                master_left_id_lst.remove(i)
            for i in salve_all_id_lst:
                salve_left_id_lst.remove(i)

        log.info('[主从]创建复制域')
        if REP_AREA_ONE_NODE:
            master_id_lst = [master_all_id_lst[0]]
            slave_id_lst = [salve_all_id_lst[0]]
        master_nodeid_str = convert_lst_to_str(master_id_lst)
        rc, pscli_info = enable_rep_server(node_ids=master_nodeid_str, run_cluster=MASTER)
        common.judge_rc(rc, 0, 'enable_rep_server failed')

        slave_nodeid_str = convert_lst_to_str(slave_id_lst)
        rc, pscli_info = enable_rep_server(node_ids=slave_nodeid_str, run_cluster=SLAVE)
        common.judge_rc(rc, 0, 'enable_rep_server failed')


        log.info('[主]创建通道')
        rc, create_channel_ip = ip_for_create_channel(slave_id_lst, run_cluster=SLAVE)
        common.judge_rc(rc, 0, 'ip_for_create_channel failed')
        rc, pscli_info = create_rep_channel(ip=create_channel_ip)
        common.judge_rc_unequal(rc, 0, 'create_rep_channel failed')

    rc, pscli_info = get_rep_area()
    if rc != 0:
        return rc, {}
    ready_info['area'] = pscli_info
    rc, pscli_info = get_rep_channels()
    if rc != 0:
        return rc, {}
    ready_info['channel'] = pscli_info

    return rc, ready_info


def delete_all_rep_config(clean_all_flag, **kwargs):
    """
    author:chenjy1
    description:清理远程复制环境
    date:20181218
    :param clean_all_flag:  清理通道及复制域的标志
    :param kwargs:
    :return:
    """
    log.info('清理远程复制环境')

    for cluster in kwargs['clusters']:
        print '%s' % cluster
    log.info('1、先删除策略及pair')
    for cluster in kwargs['clusters']:
        log.info('  删除策略及pair - 集群%s' % cluster)
        rc, policies_ids = get_all_policies_ids(run_cluster=cluster, print_flag=False)
        common.judge_rc(rc, 0, 'get_all_policies_ids failed')
        if policies_ids != '':
            rc, stdout = delete_rep_policies(policies_ids, run_cluster=cluster)
            common.judge_rc(rc, 0, 'delete_rep_policies failed')
        '''删除pair'''
        rc, pair_lst = get_all_pair_idlst(run_cluster=cluster, print_flag=False)
        common.judge_rc(rc, 0, 'get_all_pairs_ids failed')
        for id in pair_lst:
            rc, stdout = delete_rep_pair(id=id, run_cluster=cluster, print_flag=True)
            common.judge_rc(rc, 0, 'delete_rep_policies failed')
    log.info('###########pair及策略处理完毕##############')
    if clean_all_flag is True:
        log.info('2、删除通道')
        for cluster in kwargs['clusters']:
            rc, channel_idlst = get_all_channel_idlst(run_cluster=cluster, print_flag=True)
            common.judge_rc(rc, 0, 'get_all_channel_idlst failed')
            for id in channel_idlst:
                rc, pscli_info = delete_rep_channel(id, print_flag=True, run_cluster=cluster)
                common.judge_rc(rc, 0, 'delete_rep_channel failed')
    log.info('###########通道处理完毕##############')
    if clean_all_flag is True:
        log.info('3、删除复制域')
        for cluster in kwargs['clusters']:
            disable_all_rep_server(run_cluster=cluster)
    log.info('###########复制域处理完毕##############')
    return