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
import make_fault
import tool_use

####################################################################################
#
# author 刘俊鑫
# date 2019-1-24
# @summary：
#   引用其他人脚本时清理环境用
# @steps:
#   step1: 卸载客户端，删除授权


#   ps.需要将客户端安装包解压后放到配置文件中的client_install_path
#
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
PACKAGE_PATH = get_config.get_client_install_path()
CLIENT_IP = get_config.get_allclient_ip()
SERVER_IP = get_config.get_allparastor_ips()
VDBENCH_PATH = get_config.get_mount_paths()[0] + '/data'
VDBENCH_JN_PATH = get_config.get_mount_paths()[0] + '/jn'
PROPERTY_TRUE_PATH = os.path.join(prepare_clean.PROPERTY_PATH, FILE_NAME)
File_Size = '500G'


def get_client_auth_id_base_volumename(volume_name):
    rc, stdout = common.get_client_auth()
    results = common.json_loads(stdout)
    client_auth_id = ''
    for result in results['result']:
        if result['volumes'][0]['volume_name'] == volume_name:
            client_auth_id = result['id']
    if client_auth_id == '':
        log.info('do not find auth about volume:%s' % volume_name)
    return rc, client_auth_id

def case():

    rc, client_auth_id = get_client_auth_id_base_volumename(get_config.get_volume_names()[0])
    common.judge_rc(rc, 0, 'get client auth failed')
    '''客户端卸载'''
    unistall_cmd = '/cliparastor/uninstall.py'
    rc, stdout = common.run_command(CLIENT_IP[0], unistall_cmd, timeout=120)
    common.judge_rc(rc, 0, '\t[uninstall client failed, stdout=%s]' % stdout, exit_flag=False)
    if client_auth_id != '':
        rc, stdout = common.delete_client_auth(client_auth_id)
        common.judge_rc(rc, 0, 'delete client auth failed', exit_flag=False)
    cmd = 'rm -rf %s/*' % get_config.get_mount_paths()[0]
    rc, stdout = common.run_command(SERVER_IP[1], cmd)
    common.judge_rc(rc, 0, 'rm failed')


def main():
    prepare_clean.test_prepare(FILE_NAME)
    case()
    prepare_clean.test_clean()


if __name__ == '__main__':
    common.case_main(main)
