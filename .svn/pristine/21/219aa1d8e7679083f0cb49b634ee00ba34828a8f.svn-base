# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-3-1-6 【稳定性】配置删除过程中删除掉任意节点
# 修改时间：20181109 duyuli:新增添加删除的节点恢复环境
#######################################################

import os
import time
import utils_path
import common
import quota_common
import get_config
import log
import prepare_clean
from multiprocessing import Process, Value

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
def delete_quota_when_delete_node():
    time.sleep(5)
    quota_common.delete_all_quota_config()
    return


def delete_node_when_delete_quota():
    # 注意：delete的节点不能是脚本执行的节点
    node = common.Node()
    node_id = node.get_node_id_by_ip(quota_common.NOTE_IP_3)
    rc, stdout = common.remove_node(node_id, remove_mode="AUTO_REBOOT")
    common.judge_rc(rc, 0, "remove node failed")
    return

def add_node(node_ip):
    # 添加节点，以node_ip.xml命名的配置文件
    log.info("add node please waite...")
    config_file_path = os.path.join(get_config.config_path, "%s.xml" % node_ip)
    rc, stdout = common.add_nodes(config_file_path)
    common.judge_rc(rc, 0, "add node failed")

    # 扩容到到节点池
    node = common.Node()
    rc, stdout = common.get_node_pools()
    common.judge_rc(rc, 0, "get_node_pools failed")

    node_pool = common.json_loads(stdout)["result"]["node_pools"][0]
    node_id = node.get_node_id_by_ip(node_ip)
    node_ids_list = node_pool["node_ids"]
    node_ids_list.append(node_id)
    node_ids = ','.join(map(str, node_ids_list))  # 列表中不全是字符串会报错
    rc, stdout = common.update_node_pool(node_pool["id"], node_pool["name"], node_ids)
    common.judge_rc(rc, 0, "update node pool failed")

    # 扩容到存储池
    rc, stdout = common.get_storage_pools()
    common.judge_rc(rc, 0, "get_storage_pools failed")
    storage_pool = common.json_loads(stdout)["result"]["storage_pools"][1]  # 0为共享池
    rc, stdout = common.expand_storage_pool(storage_pool["id"], node_pool["id"])
    common.judge_rc(rc, 0, "expand storage pool failed")

    # 启动系统
    rc, stdout = common.startup()
    common.judge_rc(rc, 0, "start up sys failed")
    return

#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def executing_case():
    print "（2）executing_case"

    '''
    1、测试执行
    2、结果检查
    '''
    # 测试执行

    p1 = Process(target=delete_quota_when_delete_node, args=())
    p2 = Process(target=delete_node_when_delete_quota, args=())
    # p2.daemon = True  # p2设置守护程序，主进程执行完就退出
    p1.start()
    p2.start()

    p1.join()
    log.info("delete node please waite...")
    p2.join()

    # 恢复环境
    time.sleep(600)  # 等待重建任务完成，等待删除的节点重启
    while True:
        flag = common.check_ping(quota_common.CLIENT_IP_3)
        if flag:
            add_node(quota_common.CLIENT_IP_3)
            break
        else:
            time.sleep(60)

    if p1.exitcode != 0:
        raise Exception("11-3-1-6 Failed")
    else:
        print "11-3-1-6 Succeed"
    return


#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def preparing_environment():
    print "（1）preparing_environment"

    quota_common.preparing_zone_nas()
    auth_provider_id = quota_common.get_auth_provider_id_with_access_zone_name(quota_common.QUOTA_ACCESS_ZONE)
    quota_common.create_designated_quota_user_and_group_new(quota_common.CLIENT_IP_1, auth_provider_id)

    '''
    1、下发配额相关的配置
    2、创建配额测试相关的目录和文件
    '''

    # 创建30个配额，用于后面删除
    count = 1
    success_count = 0
    for i in range(1, count + 1):
        dir = "%s%s" % (quota_common.QUOTA_PATH, i)
        quota_common.creating_dir(quota_common.CLIENT_IP_1, dir)
        quota_dir = os.path.basename(dir)

        rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                         filenr_quota_cal_type='QUOTA_LIMIT',
                                                         filenr_suggest_threshold=1000,
                                                         filenr_soft_threshold=2000,
                                                         filenr_grace_time=1,
                                                         filenr_hard_threshold=3000,
                                                         logical_quota_cal_type='QUOTA_LIMIT',
                                                         logical_suggest_threshold=1073741824,
                                                         logical_soft_threshold=2147483648,
                                                         logical_grace_time=1,
                                                         logical_hard_threshold=3221225472)
        common.judge_rc(rc, 0, "create quota failed", exit_flag=False)
        if check_result["err_no"] == 0:
            success_count = success_count + 1

        quota_dir = os.path.basename(dir)
        rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                         auth_provider_id=auth_provider_id,
                                                         filenr_quota_cal_type='QUOTA_LIMIT',
                                                         filenr_suggest_threshold=1000,
                                                         filenr_soft_threshold=2000,
                                                         filenr_grace_time=1,
                                                         filenr_hard_threshold=3000,
                                                         logical_quota_cal_type='QUOTA_LIMIT',
                                                         logical_suggest_threshold=1073741824,
                                                         logical_soft_threshold=2147483648,
                                                         logical_grace_time=1,
                                                         logical_hard_threshold=3221225472,
                                                         user_type='USERTYPE_USER',
                                                         user_or_group_name='quota_user')
        common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)
        if check_result["err_no"] == 0:
            success_count = success_count + 1

        quota_dir = os.path.basename(dir)
        rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                         auth_provider_id=auth_provider_id,
                                                         filenr_quota_cal_type='QUOTA_LIMIT',
                                                         filenr_suggest_threshold=1000,
                                                         filenr_soft_threshold=2000,
                                                         filenr_grace_time=1,
                                                         filenr_hard_threshold=3000,
                                                         logical_quota_cal_type='QUOTA_LIMIT',
                                                         logical_suggest_threshold=1073741824,
                                                         logical_soft_threshold=2147483648,
                                                         logical_grace_time=1,
                                                         logical_hard_threshold=3221225472,
                                                         user_type='USERTYPE_GROUP',
                                                         user_or_group_name='quota_group')
        common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)
        if check_result["err_no"] == 0:
            success_count = success_count + 1

    # 结果检查
    if success_count != 3:
        raise Exception("create quota is failed!")
    return


#######################################################
# 函数功能：本用例入口函数
# 函数入参：无
# 函数返回值：无
#######################################################
def quota_main():
    prepare_clean.test_prepare(FILE_NAME)
    quota_common.cleaning_environment()
    preparing_environment()
    executing_case()
    if quota_common.DEBUG != "on":
        quota_common.cleaning_environment()
    return


class Quota_Class_11_3_1_6():
    def quota_method_11_3_1_6(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    common.case_main(quota_main)