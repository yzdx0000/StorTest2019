# -*-coding:utf-8 -*
import os
import time
import json

import utils_path
import common
import snap_common
import log
import shell
import get_config
import prepare_clean
import random

"""
 Author:liangxy
 date 2018-09-05
 @summary：
    缺陷自动化——验证pscli命令get_jobengine_state的ids参数是否起作用。
 @steps:
    1、查询当下系统的后台任务状态(使用命令pscli --command=get_jobengine_state  total值)；
    2、如果没有后台任务，开启一个后台删盘(使用函数pscli --command=get_snapshot )；
    3、获取后台任务id，得到确实有job的id，假设此id为A（使用命令pscli --command=get_jobengine_state 值ids)；
    4、生成一个不存在的id号B，且B!=A(使用)；
    5、查询id号为B的后台任务状态(使用命令pscli --command=get_snapshot)；
 @changelog：
"""
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]


def delete_disk_random_beta(ob_node, ob_disk, ob_storage_pool):
    """
    name  :      delete_disk_random_beta
    parameter:   node类，disk类，存储池类
    author:      LiangXiaoyu
    date  :      2018.07.13
    Description: 为了起一个后台删盘任务，循环调用方便而封成函数,返回加盘需要的值
    @changelog：
    """
    storage_pool_id = 0
    nodeid_list = ob_node.get_nodes_id()
    '''随机选一个节点'''
    fault_node_id = random.choice(nodeid_list)
    fault_node_ip = ob_node.get_node_ip_by_id(fault_node_id)
    '''获取节点内的所有数据盘的物理id'''
    share_disk_names, monopoly_disk_names = ob_disk.get_share_monopoly_disk_names(fault_node_id)

    ''' 随机选一个数据盘'''
    while storage_pool_id == 0:
        fault_disk_name = random.choice(monopoly_disk_names)
        fault_disk_id = ob_disk.get_diskid_by_name(fault_node_id, fault_disk_name)
        fault_disk_uuid = ob_disk.get_disk_uuid_by_name(fault_node_id, fault_disk_name)
        fault_disk_usage = ob_disk.get_disk_usage_by_name(fault_node_id, fault_disk_name)
        storage_pool_id = ob_disk.get_storage_pool_id_by_diskid(fault_node_id, fault_disk_id)

    # print "4 int %s %s %s %s" % (fault_disk_id,fault_disk_uuid,fault_disk_usage,storage_pool_id)
    ''' 删除'''
    log.info("to delete:uuid:%s,fault_node_id:%s,storage_pool_id:%s,fault_disk_usage=%s"
             % (fault_disk_uuid, fault_node_id, storage_pool_id, fault_disk_usage))
    ob_disk.remove_disks_asyn(fault_disk_id)
    return fault_node_id, fault_disk_name, fault_disk_uuid, fault_disk_usage, storage_pool_id


def add_disk_recover_env_beta(have_delete_flag, ob_disk, ob_storage_pool, fault_node_id, fault_disk_name,
                              fault_disk_uuid, fault_disk_usage, storage_pool_id):
    """
    name  :      delete_disk_random_beta
    parameter:   nodeid_list节点列表
    author:      LiangXiaoyu
    date  :      2018.07.13
    Description: 对应后台删盘任务，循环调用方便而封成函数,返回加盘需要的值
    @changelog：
    """
    add_disk_flag = 0
    """如果盘没删除完，则不断检查重建任务是否存在,确定删盘成功则跳出循环准备加盘"""
    while True:
        id_state = ob_disk.get_diskid_by_name(fault_node_id, fault_disk_name)

        if 0 == id_state:
            log.info('delete job finish!!! id_state %s' % id_state)
            add_disk_flag = 1
            break
        print("jugue dele,id_state 0 != %s" % id_state)
        time.sleep(20)
    add_disk_flag += have_delete_flag

    while (2 == add_disk_flag):
        '''加盘，恢复环境'''
        log.info("add_disk_flag:%s,enter add disk loop" % add_disk_flag)
        ob_disk.add_disks(fault_node_id, fault_disk_uuid, fault_disk_usage)
        fault_disk_id_new = ob_disk.get_disk_id_by_uuid(fault_node_id, fault_disk_uuid)
        ob_storage_pool.expand_storage_pool(storage_pool_id, fault_disk_id_new)
        time.sleep(20)
        id_state_add = ob_disk.get_diskid_by_name(fault_node_id, fault_disk_name)
        '''检查添加盘成功，id不为0，跳出循环，打印log'''
        if 0 != id_state_add:
            log.info("id_state_add:%s,fault_disk_uuid:%s,fault_node_id:%s\nadd disk succeed,break add disk loop"
                     % (id_state_add, fault_disk_uuid, fault_node_id))
            break
    return None


def extract_stdout_field(stdout, field1, field2):
    """
    name  :      extract_stdout_field
    parameter:   stdout:命令的输出内容；field1:字段1（如"result"），field2：字段2（如"total"）
    author:      LiangXiaoyu
    date  :      2018.07.12
    Description: 提取pscli命令输出信息
    @changelog：
    """
    msg = common.json_loads(stdout)
    field_extracted = msg[field1][field2]
    return field_extracted


def get_ids_total():
    """
    name  :      get_ids_total
    parameter:
    author:      LiangXiaoyu
    date  :      2018.07.13
    Description: 提取pscli命令get_jobengine_state在没有ids参数\
                 的输出信息中有后台任务的id总数total：xx
    @changelog：
    """
    rc_cmd1, stdout_cmd1 = common.get_jobengine_state()
    jobids_org = extract_stdout_field(stdout_cmd1, "result", "total")
    log.info("get_jobengine_state total: %d" % jobids_org)
    return jobids_org


def case():
    log.info("case begin")
    fault_node_id = 0
    fault_disk_name = ""
    fault_disk_uuid = 0
    fault_disk_usage = ""
    storage_pool_id = 0
    '''获取集群内所有节点的id，以备开启删盘的后台任务'''
    ob_node = common.Node()
    ob_disk = common.Disk()
    ob_storage_pool = common.Storagepool()
    """
    获得后台任务总数jobids_org，判断有无后台任务；
    没有后台的话，加一个删盘的后台任务参照3_0019_里的函数；
    have_delete_flag为删盘标记，当have_delete_flag与成功删盘标记add_disk_flag相加为2的时候，具备恢复环境条件
    """
    jobids_org = get_ids_total()

    have_delete_flag = 0
    if 0 == jobids_org:
        fault_node_id, fault_disk_name, fault_disk_uuid, fault_disk_usage, storage_pool_id\
            = delete_disk_random_beta(ob_node, ob_disk, ob_storage_pool)
        have_delete_flag = 1

    """
    if结束删盘,获取现有任务的id;
    随机指定一个后台测试id：jobids_test,对比现在有的jobids_exit，打印到log;
    当指定id相同就自加2，与现有id不相等时跳出循环，jobids_test生成ok
    """
    jobids_test = 3
    wait_times = 0
    while True:

        jobids_exit = get_ids_total()
        log.info("jobids_test = %s" % (jobids_test))

        ids_cmp = cmp(jobids_exit, jobids_test)
        if 0 == ids_cmp:

            jobids_test += 2
            log.info("jobids_test = %d" % jobids_test)
            continue

        if 0 != jobids_exit:
            break
        else:
            wait_times += 1
            time.sleep(20)
            if wait_times > 6:
                log.error("cannot get job in time:id=%d" % (jobids_exit))
                break
            else:
                log.info("wait_times = %d" % wait_times)
                continue

    log.info("jobids_exit:%d,jobids_test:%d,ids_cmp:%d" % (jobids_exit, jobids_test, ids_cmp))
    """
    场景测试点——
    使用不存在的后台测试id：jobids_test测试命令参数ids，
    测试结果结果保存在 rc_random_ids
    """
    rc_random_ids, stdout_random_ids = common.get_jobengine_state(ids=jobids_test)
    std_js = json.loads(stdout_random_ids)
    rst = std_js['result']['job_engines']

    ''' 先加盘恢复环境,检查系统，再判断结果是否符合测试预期'''
    if 1 == have_delete_flag:
        add_disk_recover_env_beta(have_delete_flag, ob_disk, ob_storage_pool, fault_node_id,
                                  fault_disk_name, fault_disk_uuid, fault_disk_usage, storage_pool_id)
    common.ckeck_system()
    """
    预期：
    测试命令返回值rc_random_ids不为0；
    则赋值为不存在的id未能执行成功，说明--ids参数生效
    """
    print type(rst)
    print rst
    if rst or std_js["err_no"] != 0:
        common.except_exit("%s should be empty" % std_js)
    else:
        log.info("case succeed")
    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)