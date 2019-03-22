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
#   客户端挂载卸载100次（关闭自动挂载，使用手动挂载）
# @steps:
#   step1: 客户端授权安装（关闭自动挂载）
#   step2：手动mount，检查卷是否正常
#   step3：手动umount
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
# testlink case: 3.0-54775

def case_prepare():
    cmd = 'mkdir -p %s' % VDBENCH_PATH
    rc, stdout = common.run_command(SERVER_IP[1],cmd)
    common.judge_rc(rc, 0, '\t[command %s excuted faield, stdout=%s]' %(cmd, stdout))

    cmd = 'mkdir -p %s' % VDBENCH_JN_PATH
    rc, stdout = common.run_command(SERVER_IP[1], cmd)
    common.judge_rc(rc, 0, '\t[command %s excuted faield, stdout=%s]' % (cmd, stdout))

    '''客户端授权'''
    volume = common.Volume()
    volume_name = get_config.get_volume_names()
    volume_id = volume.get_volume_id(volume_name[0])
    rc, stdout = common.create_client_auth(CLIENT_IP[0], volume_id, auto_mount='false')
    common.judge_rc(rc, 0, '\t[create_client_auth failed, stdout = %s]' % stdout)
    result = common.json_loads(stdout)
    global client_auth_id
    client_auth_id = result['result']['ids'][0]

    '''客户端安装'''
    install_cmd = PACKAGE_PATH + '/install.py --ips=%s' % SERVER_IP[1]
    rc, stdout = common.run_command(CLIENT_IP[0], install_cmd)
    common.judge_rc(rc, 0, '\t[Install client failed, stdout=%s]' % stdout)

    '''手动mount'''
    cmd = 'mount -t parastor nodev %s -o sysname=P300 -o fsname=%s' % (get_config.get_mount_paths()[0],
                                                                       get_config.get_volume_names()[0])
    rc, stdout = common.run_command(CLIENT_IP[0], cmd)
    common.judge_rc(rc, 0, 'mount failed')

    ret_list = common.wait_df_find_volume([CLIENT_IP[0]], get_config.get_volume_names()[0], 1800, 1800)
    common.judge_rc(ret_list[0], 0, 'can not file volume in 600 seconds')




def case():

    '''客户端写文件'''
    vdbench = tool_use.Vdbenchrun(depth=1, width=1, files=100, size='1m', threads=50)
    rc = vdbench.run_create(VDBENCH_PATH, VDBENCH_JN_PATH, CLIENT_IP[0])
    common.judge_rc(rc, 0, 'vdbench create failed')
    time.sleep(3)

    '''手动umount'''
    cmd = 'umount %s' % get_config.get_mount_paths()[0]
    rc, stdout = common.run_command(CLIENT_IP[0], cmd)
    common.judge_rc(rc, 0, 'umount faield')
    '''客户端卸载'''
    unistall_cmd = '/cliparastor/uninstall.py'
    rc, stdout = common.run_command(CLIENT_IP[0], unistall_cmd)
    common.judge_rc(rc, 0, '\t[uninstall client failed, stdout=%s]' % stdout)

    '''客户端安装'''
    install_cmd = PACKAGE_PATH + '/install.py --ips=%s' % SERVER_IP[1]
    rc, stdout = common.run_command(CLIENT_IP[0], install_cmd)
    common.judge_rc(rc, 0, '\t[Install client failed, stdout=%s]' % stdout)
    '''手动mount'''
    cmd = 'mount -t parastor nodev %s -o sysname=P300 -o fsname=%s' % (get_config.get_mount_paths()[0],
                                                                       get_config.get_volume_names()[0])
    rc, stdout = common.run_command(CLIENT_IP[0], cmd)
    common.judge_rc(rc, 0, 'mount failed')
    ret_list = common.wait_df_find_volume([CLIENT_IP[0]], get_config.get_volume_names()[0], 1800, 1800)
    common.judge_rc(ret_list[0], 0, 'can not file volume in 600 seconds')
    '''客户端检查数据'''
    #rc = vdbench.run_check(VDBENCH_PATH, VDBENCH_JN_PATH, SERVER_IP[1])
    #common.judge_rc(rc, 0, 'vdbench check failed')

    '''删除文件'''
    rc = vdbench.run_clean(VDBENCH_PATH, CLIENT_IP[0])
    common.judge_rc(rc, 0, 'vdbench clean failed')


def case_clean():

    rc, stdout = common.delete_client_auth(client_auth_id)
    common.judge_rc(rc, 0, 'delete client auth failed')

    cmd = 'rm -rf %s/*' % get_config.get_mount_paths()[0]
    rc, stdout = common.run_command(SERVER_IP[1], cmd)
    common.judge_rc(rc, 0, 'rm failed')

def main():
    prepare_clean.test_prepare(FILE_NAME)
    uninstall.case()
    case_prepare()
    for i in range(1, 21):
        case()
        log.info('****************The %s times finished***************' % i)
    case_clean()
    prepare_clean.test_clean()


if __name__ == '__main__':
    common.case_main(main)
