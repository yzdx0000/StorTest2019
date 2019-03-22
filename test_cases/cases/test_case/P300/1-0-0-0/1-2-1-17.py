# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import json
import random

import utils_path
import common
import log
import get_config
import prepare_clean
import quota_common
import tool_use
import uninstall

####################################################################################
#
# author 刘俊鑫
# date 2019-1-24
# @summary：
#   客户端配额测试
# @steps:
#   step1: 客户端授权、安装、挂载
#   step2: 文件系统下创建目录A，设置容量配额为200g，目录A下创建目录B
#   step3: 客户端向目录A下创建100个1g文件
#   step4: 客户端向目录B中创建60个1g文件
#   step5: 客户端向目录A中创建50个1g文件
#   step6: 客户端向目录B中创建50个1g文件
#   step7: 客户端读取A下的文件，观察读操作是否成功
#   step8: 客户端删除B目录下的30g文件
#   step9: 修改目录A容量配额为300g
#   step19: 客户端在向A中写入100g文件
#   ps.需要将客户端安装包解压后放到配置文件中的client_install_path
#
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
PACKAGE_PATH = get_config.get_client_install_path()
CLIENT_IP = get_config.get_allclient_ip()
SERVER_IP = get_config.get_allparastor_ips()
VDBENCH_PATH = get_config.get_mount_paths()[0] + '/A'
# VDBENCH_JN_PATH = get_config.get_mount_paths()[0] + '/jn'
VDBENCH_JN_PATH = '/tmp/jn'
client_auth_id = 0
# testlink case: 3.0-55150

def delete_quota_by_name(volume_name):
    rc, result = quota_common.get_all_quota_info()
    for quota in result['result']['quotas']:
        if quota['path'].find(volume_name) != -1:
            quota_common.delete_one_quota(quota['id'])


def case():
    '''删除相关配额'''
    delete_quota_by_name(get_config.get_volume_names()[0])
    cmd = 'mkdir -p %s' % VDBENCH_PATH
    rc, stdout = common.run_command(SERVER_IP[0], cmd)
    common.judge_rc(rc, 0, '\t[command %s excuted faield, stdout=%s]' % (cmd, stdout))

    #cmd = 'mkdir -p %s' % VDBENCH_JN_PATH
    #rc, stdout = common.run_command(CLIENT_IP[0], cmd)
    #common.judge_rc(rc, 0, '\t[command %s excuted faield, stdout=%s]' % (cmd, stdout))

    '''客户端授权'''
    volume = common.Volume()
    volume_name = get_config.get_volume_names()
    volume_id = volume.get_volume_id(volume_name[0])
    rc, stdout = common.create_client_auth(CLIENT_IP[0], volume_id, auto_mount='true',
                                           atime='false', acl='false', user_xattr='true', sync='false')
    common.judge_rc(rc, 0, '\t[create_client_auth failed, stdout = %s]' % stdout)
    result = common.json_loads(stdout)
    global client_auth_id
    client_auth_id = result['result']['ids'][0]

    '''客户端安装'''
    install_cmd = PACKAGE_PATH + '/install.py --ips=%s' % SERVER_IP[0]
    rc, stdout = common.run_command(CLIENT_IP[0], install_cmd)
    common.judge_rc(rc, 0, '\t[Install client failed, stdout=%s]' % stdout)
    ret_list = common.wait_df_find_volume([CLIENT_IP[0]], get_config.get_volume_names()[0], 1800, 1800)
    common.judge_rc(ret_list[0], 0, 'can not file volume in 60 seconds')
    '''设置A目录200g配额'''
    quota_logical = quota_common.FILE_SIZE_4G * 50  # 200g
    path_lst = VDBENCH_PATH.split("/")
    quota_path = path_lst[2] + ":/" + path_lst[3]
    rc, stdout = quota_common.create_one_quota(path=quota_path,  logical_quota_cal_type='QUOTA_LIMIT',
                                               logical_hard_threshold=quota_logical)
    common.judge_rc(rc, 0, 'create quota failed')
    log.info("******利用creating files函数检测配额是否生效**********")
    quota_common.creating_files_beifen(CLIENT_IP[0], VDBENCH_PATH, 1, 0, 'a')  # 目的是检测配额是否生效
    log.info("******检测结束**********")
    VDBENCH_B_PATH = VDBENCH_PATH + '/B'
    common.judge_rc(rc, 0, '\t[command %s excuted faield, stdout=%s]' % (cmd, stdout))
    '''写文件'''
    cmd = 'mkdir -p %s %s %s %s %s %s' % (VDBENCH_JN_PATH+'/100g_1', VDBENCH_JN_PATH + '/30g_1', VDBENCH_JN_PATH + '/30g_2',
                                          VDBENCH_JN_PATH + '/50g_A', VDBENCH_JN_PATH + '/50g_B', VDBENCH_JN_PATH + '/100g_2')
    rc, stdout = common.run_command(CLIENT_IP[0], cmd)
    common.judge_rc(rc, 0, '\t[command %s excuted faield, stdout=%s]' % (cmd, stdout))

    cmd = 'mkdir -p %s %s %s %s %s %s' % (VDBENCH_PATH + '/100g_1', VDBENCH_B_PATH + '/30g_1', VDBENCH_B_PATH + '/30g_2',
                                          VDBENCH_PATH + '/50g_A', VDBENCH_B_PATH + '/50g_B', VDBENCH_PATH + '/100g_2')
    rc, stdout = common.run_command(CLIENT_IP[0], cmd)
    common.judge_rc(rc, 0, '\t[command %s excuted faield, stdout=%s]' % (cmd, stdout))


    #vdbench_100g = tool_use.Vdbenchrun(depth=1, width=1, files=100, size='1g', threads=50, xfersize=None)
    #rc = vdbench_100g.run_create(VDBENCH_PATH+'/100g_1', VDBENCH_JN_PATH + '/100g_1', CLIENT_IP[0])
    #common.judge_rc(rc, 0, 'vdbench run_create failed')

    quota_common.creating_files_beifen(SERVER_IP[0], VDBENCH_PATH+'/100g_1', 1, 100*1024, '100g')


    vdbench_30g = tool_use.Vdbenchrun(depth=1, width=1, files=30, size='1g', threads=50, xfersize=None)
    #rc = vdbench_30g.run_create(VDBENCH_B_PATH+'/30g_1', VDBENCH_JN_PATH + '/30g_1', CLIENT_IP[0])
    #common.judge_rc(rc, 0, 'vdbench run_create failed')
    quota_common.creating_files_beifen(CLIENT_IP[0], VDBENCH_B_PATH+'/30g_1', 1, 30*1024, '30g')


    #rc = vdbench_30g.run_create(VDBENCH_B_PATH + '/30g_2', VDBENCH_JN_PATH + '/30g_2', CLIENT_IP[0])
    #common.judge_rc(rc, 0, 'vdbench run_create failed')
    quota_common.creating_files_beifen(CLIENT_IP[0], VDBENCH_B_PATH + '/30g_2', 1, 30 * 1024, '30g')


    #vdbench_50g = tool_use.Vdbenchrun(depth=1, width=1, files=50, size='1g', threads=40, xfersize=None)
    #rc = vdbench_50g.run_create(VDBENCH_PATH + '/50g', VDBENCH_JN_PATH + '/50g_A', CLIENT_IP[0])
    #common.judge_rc_unequal(rc, 0, 'quota did not work')
    rc, stdout = quota_common.creating_files_beifen(CLIENT_IP[0], VDBENCH_PATH + '/50g_A', 1, 50 * 1024, '50g')
    if stdout.find('No space left on device') == -1:
        common.except_exit('quota did not work')

    #rc = vdbench_50g.run_create(VDBENCH_B_PATH + '/50g', VDBENCH_JN_PATH + '/50g_B', CLIENT_IP[0])
    #common.judge_rc_unequal(rc, 0, 'quota did not work')
    rc, stdout = quota_common.creating_files_beifen(CLIENT_IP[0], VDBENCH_B_PATH + '/50g_B', 1, 50 * 1024, '50g')
    if stdout.find('No space left on device') == -1:
        common.except_exit('quota did not work')
    '''修改A配额'''
    rc, quota_id = quota_common.get_one_quota_id(quota_path, quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, 'get quota id failed')
    quota_logical = quota_common.FILE_SIZE_4G * 75 # 300g
    rc, stdout = quota_common.update_one_quota(quota_id, logical_quota_cal_type='QUOTA_LIMIT',
                                               logical_hard_threshold=quota_logical)
    common.judge_rc(rc, 0, 'update quota failed')
    log.info("******利用creating files函数检测配额是否生效**********")
    quota_common.creating_files_beifen(CLIENT_IP[0], VDBENCH_B_PATH + '/30g_1', 1, 0, 'a') #目的是检测配额是否生效
    log.info("******检测结束**********")
    #rc = vdbench_30g.run_clean(VDBENCH_B_PATH+'/30g_1', CLIENT_IP[0])
    #common.judge_rc(rc, 0, 'vdbench run_clean failed')
    cmd = 'rm -rf %s/*' % (VDBENCH_B_PATH+'/30g_1')
    rc, stdout = common.run_command(CLIENT_IP[0], cmd)
    common.judge_rc(rc, 0, cmd + ' failed')


    #rc = vdbench_100g.run_check(VDBENCH_PATH+'/100g_1', VDBENCH_JN_PATH + '/100g_1', CLIENT_IP[0])
    #common.judge_rc(rc, 0, 'vdbench run_check failed')

    #rc = vdbench_100g.run_create(VDBENCH_PATH+'/100g_2', VDBENCH_JN_PATH + '/100g_2', CLIENT_IP[0])
    #common.judge_rc(rc, 0, 'vdbench run_create failed')
    quota_common.creating_files_beifen(CLIENT_IP[0], VDBENCH_PATH+'/100g_2', 1, 100 * 1024, '100g')



    #vdbench_30g.run_clean(VDBENCH_B_PATH+'/30g_2', CLIENT_IP[0])
    #dbench_50g.run_clean(VDBENCH_B_PATH + '/50g', CLIENT_IP[0])
    #vdbench_50g.run_clean(VDBENCH_PATH + '/50g', CLIENT_IP[0])
    #vdbench_100g.run_clean(VDBENCH_PATH+'/100g_1', CLIENT_IP[0])






def case_clean():
    '''删除相关配额'''
    delete_quota_by_name(get_config.get_volume_names()[0])

    rc, stdout = common.delete_client_auth(client_auth_id)
    common.judge_rc(rc, 0, 'delete client auth failed')

    cmd = 'rm -rf %s/*' % get_config.get_mount_paths()[0]
    rc, stdout = common.run_command(SERVER_IP[0], cmd)
    common.judge_rc(rc, 0, 'rm failed')


def main():
    prepare_clean.defect_test_prepare(FILE_NAME, env_check=False)
    uninstall.case()
    case()
    case_clean()
    prepare_clean.defect_test_clean(FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)