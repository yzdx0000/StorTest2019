# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import json

import utils_path
import common
import log
import get_config
import prepare_clean
import upgrade_common
import tool_use
import uninstall

####################################################################################
#
# author 刘俊鑫
# date 2019-1-19
# @summary：
#   客户端挂载卸载100次（使用默认参数）
# @steps:
#   step1: 客户端挂载
#   step2：客户端检查
#   step3：客户端卸载
#
#   ps.需要将客户端安装包放到PACKAGE_PATH中,并保证该目录下只有这一个安装包
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
# testlink case: 3.0-54773

def case_prepare():

    cmd = 'mkdir -p %s' % VDBENCH_PATH
    rc, stdout = common.run_command(SERVER_IP[0],cmd)
    common.judge_rc(rc, 0, '\t[command %s excuted faield, stdout=%s]' %(cmd, stdout))

    cmd = 'mkdir -p %s' % VDBENCH_JN_PATH
    rc, stdout = common.run_command(SERVER_IP[0], cmd)
    common.judge_rc(rc, 0, '\t[command %s excuted faield, stdout=%s]' % (cmd, stdout))

    vdbench = tool_use.Vdbenchrun(depth=1, width=1, files=100, size='1m', threads=50)
    rc = vdbench.run_create(VDBENCH_PATH, VDBENCH_JN_PATH, CLIENT_IP[0])
    common.judge_rc(rc, 0, 'vdbench create failed')


def client_install():

    uninstall.case()
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
    common.judge_rc(ret_list[0], 0, 'can not file volume in 600 seconds')


def case():
    '''客户端写文件'''
    vdbench = tool_use.Vdbenchrun(depth=1, width=1, files=100, size='1m', threads=20, elapsed=20)
    rc = vdbench.run_write(VDBENCH_PATH, CLIENT_IP[0])
    common.judge_rc(rc, 0, 'vdbench write failed')
    time.sleep(3)

    '''客户端卸载'''
    unistall_cmd = '/cliparastor/uninstall.py'
    rc, stdout = common.run_command(CLIENT_IP[0], unistall_cmd)
    common.judge_rc(rc, 0, '\t[uninstall client failed, stdout=%s]' % stdout)

    # test try
    #common.except_exit('test try')
    #raise Exception('test try')

    '''客户端安装'''
    install_cmd = PACKAGE_PATH + '/install.py --ips=%s' % SERVER_IP[0]
    rc, stdout = common.run_command(CLIENT_IP[0], install_cmd)
    common.judge_rc(rc, 0, '\t[Install client failed, stdout=%s]' % stdout)
    ret_list = common.wait_df_find_volume([CLIENT_IP[0]], get_config.get_volume_names()[0], 1800, 1800)
    common.judge_rc(ret_list[0], 0, 'can not file volume in 600 seconds')

    '''客户端检查数据'''
    #rc = vdbench.run_check(VDBENCH_PATH, VDBENCH_JN_PATH, SERVER_IP[1])
    #common.judge_rc(rc, 0, 'vdbench check failed')


def case_clean():

    rc, stdout = common.delete_client_auth(client_auth_id)
    common.judge_rc(rc, 0, 'delete client auth failed')

    cmd = 'rm -rf %s/*' % get_config.get_mount_paths()[0]
    rc, stdout = common.run_command(SERVER_IP[0], cmd)
    common.judge_rc(rc, 0, 'rm failed')


def main():
    prepare_clean.test_prepare(FILE_NAME)
    client_install()
    case_prepare()
    try:
        for i in range(1, 101):
            case()
            log.info('*************************the %s times is done***********************' % i)
    except SystemExit, error:
        log.info(error)
        log.info('脚本失败，清理并恢复环境')
        client_install()
        common.except_exit('%s failed' % FILE_NAME)
    except Exception, error:
        log.info(error)
        log.info('脚本失败，清理并恢复环境')
        client_install()
        common.except_exit('%s failed' % FILE_NAME)
    else:
        case_clean()
        log.info('%s succeed!' % FILE_NAME)
        prepare_clean.test_clean()


if __name__ == '__main__':
    common.case_main(main)