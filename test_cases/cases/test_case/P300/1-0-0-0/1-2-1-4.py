# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import json

import utils_path
import DAC_path
import common
import log
import get_config
import prepare_clean
import upgrade_common
import tool_use
import dac_posix_acl_all

####################################################################################
#
# author 刘俊鑫
# date 2019-1-22
# @summary：
#   客户端acl验证
# @steps:
#   step1: 客户端授权、安装、挂载，打开acl功能
#   step2: 调用acl脚本

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
client_auth_id = 0
# testlink case: 3.0-54776

def check_host(host_ip):
    cmd = 'ssh %s hostname' % host_ip
    rc = os.system(cmd)
    if rc == 0:
        return True
    else:
        return False


def case():
    cmd = 'mkdir -p %s' % VDBENCH_PATH
    rc, stdout = common.run_command(SERVER_IP[0],cmd)
    common.judge_rc(rc, 0, '\t[command %s excuted faield, stdout=%s]' %(cmd, stdout))

    cmd = 'mkdir -p %s' % VDBENCH_JN_PATH
    rc, stdout = common.run_command(SERVER_IP[0], cmd)
    common.judge_rc(rc, 0, '\t[command %s excuted faield, stdout=%s]' % (cmd, stdout))

    '''客户端授权'''
    volume = common.Volume()
    volume_name = get_config.get_volume_names()
    volume_id = volume.get_volume_id(volume_name[0])
    rc, stdout = common.create_client_auth(CLIENT_IP[0], volume_id, auto_mount='true',
                                           atime='false', acl='true', user_xattr='true', sync='false')
    common.judge_rc(rc, 0, '\t[create_client_auth failed, stdout = %s]' % stdout)
    result = common.json_loads(stdout)
    global client_auth_id
    client_auth_id = result['result']['ids'][0]
    '''客户端安装'''
    install_cmd = PACKAGE_PATH + '/install.py --ips=%s' % SERVER_IP[0]
    rc, stdout = common.run_command(CLIENT_IP[0], install_cmd)
    common.judge_rc(rc, 0, '\t[Install client failed, stdout=%s]' % stdout)
    ret_list = common.wait_df_find_volume([CLIENT_IP[0]], get_config.get_volume_names()[0], 20, 60)
    common.judge_rc(ret_list[0], 0, 'can not file volume in 60 seconds')
    '''调用dac脚本'''
    dac_posix_acl_all.case()
    '''客户端卸载'''
    unistall_cmd = '/cliparastor/uninstall.py'
    rc, stdout = common.run_command(CLIENT_IP[0], unistall_cmd, timeout=120)
    common.judge_rc(rc, 0, '\t[uninstall client failed, stdout=%s]' % stdout)

def case_clean():

    rc, stdout = common.delete_client_auth(client_auth_id)
    common.judge_rc(rc, 0, 'delete client auth failed')

    cmd = 'rm -rf %s/*' % get_config.get_mount_paths()[0]
    rc, stdout = common.run_command(SERVER_IP[0], cmd)
    common.judge_rc(rc, 0, 'rm failed')


def main():
    prepare_clean.test_prepare(FILE_NAME)
    case()
    case_clean()
    prepare_clean.test_clean()


if __name__ == '__main__':
    common.case_main(main)