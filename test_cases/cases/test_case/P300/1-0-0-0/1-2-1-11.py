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
import uninstall

####################################################################################
#
# author 刘俊鑫
# date 2019-1-28
# @summary：
#   文件和目录规格测试
# @steps:
#   step1: 文件最大长度255
#   step2: 文件名字符集
#   step3：文件名全路径长度4096
#   step4：目录最大长度255
#   step5：目录名字符集
#   step6: ??单目录下文件数 （由inode数和磁盘空间决定）

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
# testlink case: 3.0-55129~55134


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

    '''文件名最大路径,255'''
    cmd1 = 'touch %s/Aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' \
          'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' \
          'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' % get_config.get_mount_paths()[0]
    cmd2 = 'touch %s/Aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' \
           'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' \
           'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' % get_config.get_mount_paths()[0]
    rc1, stdout1 = common.run_command(CLIENT_IP[0], cmd1, print_flag=False)
    rc2, stdout2 = common.run_command(CLIENT_IP[0], cmd2, print_flag=False)
    common.judge_rc(rc1, 0, 'create 255len file failed')
    common.judge_rc_unequal(rc2, 0, 'create 256len file succeed, but should not')

    '''目录名最大长度，255'''
    cmd1 = 'mkdir %s/Baaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' \
           'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' \
           'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' % get_config.get_mount_paths()[0]
    cmd2 = 'mkdir %s/Baaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' \
           'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' \
           'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' % get_config.get_mount_paths()[0]
    rc1, stdout1 = common.run_command(CLIENT_IP[0], cmd1, print_flag=False)
    common.judge_rc(rc1, 0, 'mkdir 255len file failed')
    rc2, stdout2 = common.run_command(CLIENT_IP[0], cmd2, print_flag=False)
    common.judge_rc_unequal(rc2, 0, 'mkdir 256len file succeed, but should not')

    '''文件名和目录字符集'''
    cmd1 = 'touch {}/@#\$\!\%^*_+=-0987654321~[]\|{{}}:?,'.format(get_config.get_mount_paths()[0])
    cmd2 = 'rm -rf {}/@#\$\!\%^*_+=-0987654321~[]\|{{}}:?,'.format(get_config.get_mount_paths()[0])
    cmd3 = 'mkdir {}/@#\$\!\%^*_+=-0987654321~[]\|{{}}:?,'.format(get_config.get_mount_paths()[0])
    cmd4 = 'rm -rf {}/@#\$\!\%^*_+=-0987654321~[]\|{{}}:?,'.format(get_config.get_mount_paths()[0])
    rc1, stdout1 = common.run_command(CLIENT_IP[0], cmd1, print_flag=False)
    common.judge_rc(rc1, 0, 'touch failed')
    rc2, stdout2 = common.run_command(CLIENT_IP[0], cmd2, print_flag=False)
    common.judge_rc(rc2, 0, 'rm failed')
    rc3, stdout3 = common.run_command(CLIENT_IP[0], cmd3, print_flag=False)
    common.judge_rc(rc3, 0, 'mkdir failed')
    rc4, stdout4 = common.run_command(CLIENT_IP[0], cmd4, print_flag=False)
    common.judge_rc(rc4, 0, 'rm failed')

    '''文件名全路径长度'''
    path = '%s/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          'aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/aaaaaaaaaaaaaaaaaaa/' \
          % get_config.get_mount_paths()[0]
    print 'path = %s' % path
    cmd1 = 'mkdir -p %s' % (path + 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/')
    rc, stdout = common.run_command(CLIENT_IP[0], cmd1, print_flag=False)
    common.judge_rc(rc, 0, 'mkdir failed')
    cmd2 = 'touch ' + path + '1'
    cmd3 = 'touch' + path + 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/' + '1'
    rc, stdout = common.run_command(CLIENT_IP[0], cmd2, print_flag=False)
    common.judge_rc(rc, 0, 'touch failed')
    rc, stdout = common.run_command(CLIENT_IP[0], cmd3, print_flag=False)
    common.judge_rc_unequal(rc, 0, 'should not touch succeed')

def case_clean():

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