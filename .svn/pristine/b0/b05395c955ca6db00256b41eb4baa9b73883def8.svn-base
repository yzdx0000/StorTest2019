# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import re
import time
import json

import utils_path
import common
import log
import get_config
import prepare_clean
import upgrade_common
import quota_common
import nas_common
import tool_use
import online_upgrade

####################################################################################
#
# author 刘俊鑫
# date 2018-08-06
# @summary：
#   三节点，升级中以及升级后查看针对某用户设置的inode数硬阈值配额的有效性
# @steps:
#   step1: 创建访问分区，启动nas，创建用户组和用户
#   step2：针对该用户配置inode数为2000的硬阈值配额
#   step3：执行在线升级过程中不断检查配额的有效性
#   step4：升级完成后，再检查配额的有效性
#
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
DEFECT_PATH = get_config.get_one_defect_test_path()                         # DEFECT_PATH = /mnt/vo/defect_case
DEFECT_TRUE_PATH = os.path.join(DEFECT_PATH, FILE_NAME)                     # DEFECT_TRUE_PATH= /mnt/vo/defect_case/p300
VOLUME_NAME = get_config.get_one_volume_name()                              # 卷名vo
QUOTA_TRUE_PATH = DEFECT_TRUE_PATH
QUOTA_PATH = VOLUME_NAME \
              + ':/' \
              + os.path.join(os.path.basename(DEFECT_PATH),
                             os.path.basename(DEFECT_TRUE_PATH))            # vo：/defect_case/p300
QUOTA_PATH_WITHOUT_VOLUME = re.sub('[%s:]' % VOLUME_NAME, '', QUOTA_PATH)   # /defect_case/p300
client_ip_lst = get_config.get_allclient_ip()                               # 客户端ip列表
server_ip_lst = get_config.get_allparastor_ips()
auth_group_name = quota_common.QUOTA_GROUP
auth_user_name = quota_common.QUOTA_USER
auth_other_user_name = quota_common.QUOTA_OTHER_USER


def auth_user_quota_check(path, inode_quota):
    log.info('##########auth_user_quota_check begin##########')
    """
    【su方式】
    针对该目录用户先写入2000个文件
    """
    quota_common.creating_files_by_designated_user_or_group(server_ip_lst[0], path, inode_quota, 1, "a", auth_user_name)

    """再尝试继续写入文件"""
    """(1)先写100个属主为root的文件，预期写入成功"""
    quota_common.creating_files_by_designated_user_or_group(server_ip_lst[1], path, 100, 1, "b", "root")

    """(2)之后写100个属主为quota_other_user的文件，预期写入成功"""
    quota_common.creating_files_by_designated_user_or_group(server_ip_lst[0], path, 100, 1, "c", auth_other_user_name)

    """"(3)最后尝试写2个属主为quota_user的文件，预期写入失败"""
    quota_common.creating_files_by_designated_user_or_group(server_ip_lst[0], path, 1, 1, "d", auth_user_name)
    quota_common.creating_files_by_designated_user_or_group(server_ip_lst[1], path, 1, 1, "e", auth_user_name)

    """检查配额是否生效"""
    user_total_inodes = quota_common.user_total_inodes(server_ip_lst[0], path, auth_user_name)
    if user_total_inodes != inode_quota:
        raise Exception("auth_user_quota_check failed, %s's quota is %d, but the user_total_inodes is %d"
                        % (auth_user_name, inode_quota, user_total_inodes))
    else:
        log.info("auth_user_quota_check Succeed")

    common.rm_exe(server_ip_lst[0], os.path.join(path, '*'))

    return


def case():
    """
    :author: liujx
    :date: 2018.08.06
    :description:
    :return:
    """
    quota_common.delete_all_quota_config()
    common.mkdir_path(client_ip_lst[1], DEFECT_PATH)
    common.mkdir_path(client_ip_lst[1], DEFECT_TRUE_PATH)
    """创建访问分区，启动nas"""
    node_id = '1,2,3'
    result1 = nas_common.create_access_zone(node_id, 'az1')
    access_zone_id = int(result1['result'])
    nas_common.enable_nas(access_zone_id)

    """创建用户组upgrade_group与用户upgrade_user"""
    result2 = nas_common.get_access_zones(access_zone_id)
    auth_provide_id = result2['result']['access_zones'][0]['auth_provider']['id']
    result3 = nas_common.create_auth_group(auth_provide_id, auth_group_name)
    password = '111111'
    auth_group_id = result3['result']
    result4 = nas_common.create_auth_user(auth_provide_id, auth_user_name, password, auth_group_id)
    result5 = nas_common.create_auth_user(auth_provide_id, auth_other_user_name, password, auth_group_id)

    """修改测试脚本目录权限"""
    cmd = 'chmod 777 %s' % DEFECT_TRUE_PATH
    common.run_command(client_ip_lst[0], cmd)

    """针对upgrade_user用户设置inode数为2000的硬阈值配额, 并检查其有效性"""
    inode_quota = 2000
    rc, pscli_info = quota_common.create_one_quota(path=QUOTA_PATH,
                                                   auth_provider_id=auth_provide_id,
                                                   filenr_quota_cal_type='QUOTA_LIMIT',
                                                   filenr_hard_threshold=inode_quota,
                                                   user_type='USERTYPE_USER',
                                                   user_or_group_name=auth_user_name)
    common.judge_rc(rc, 0, "create  quota failed")
    auth_user_quota_check(QUOTA_TRUE_PATH, inode_quota)

    """执行在线升级，并同时不断检查配额的有效性"""
    process_upgrade = Process(target=online_upgrade.case, args=())
    process_upgrade.start()
    while process_upgrade.is_alive():
        log.info('this check is during online upgrade')
        auth_user_quota_check(QUOTA_TRUE_PATH, inode_quota)
    process_upgrade.join()
    log.info('this check is after online upgrade')
    auth_user_quota_check(QUOTA_TRUE_PATH, inode_quota)

    """清理环境：删除配额，删除用户，用户组，关闭nas，删除访问分区，删除测试目录"""
    quota_common.delete_all_quota_config()
    nas_common.delete_all_nas_config()
    common.rm_exe(client_ip_lst[0], DEFECT_TRUE_PATH)


def main():
    upgrade_common.delete_upgrade()
    prepare_clean.nas_test_prepare(FILE_NAME)
    case()
    upgrade_common.delete_upgrade()
    nas_common.delete_all_nas_config()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
