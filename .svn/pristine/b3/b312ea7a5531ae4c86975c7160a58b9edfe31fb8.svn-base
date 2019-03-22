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
#   客户端挂验证atime
# @steps:
#   step1: 客户端授权，安装（打开atime功能）客户端创建文件
#   step2: 客户端访问文件，记录服务端和客户端的该文件atime，检查是否一致
#   step3：服务端创建文件
#   step4：服务端访问文件，检查服务端和客户端的该文件atime是否一致
#   step5：卸载客户端，客户端重新授权，关闭atime
#   step4：查看atime功能是否关闭

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
# testlink case: 3.0-55123

def atime_check(file_creater, file_receiver, file_name):

    file_path = get_config.get_mount_paths()[0] + '/%s' %file_name

    cmd = 'touch %s' % file_path
    rc, stdout = common.run_command(file_creater, cmd)
    common.judge_rc(rc, 0, '%s touch file failed' % file_creater)
    time.sleep(5)
    cmd = 'cat %s' % file_path
    rc, stdout = common.run_command(file_creater, cmd)
    common.judge_rc(rc, 0, '%s cat file failed' % file_creater)

    cmd = 'stat %s|grep Access' % file_path
    rc, stdout = common.run_command(file_receiver, cmd)
    common.judge_rc(rc, 0, '%s stat file failed' % file_receiver)
    receiver_atime = stdout.split(' ')[-2]
    rc, stdout = common.run_command(file_creater, cmd)
    common.judge_rc(rc, 0, '%s stat file failed' % file_creater)
    creater_atime = stdout.split(' ')[-2]
    common.judge_rc(receiver_atime, creater_atime, 'atimes are not same, file atime on %s and %s are %s and %s'
                    % (file_creater, file_receiver, creater_atime, receiver_atime), exit_flag=False)

    if receiver_atime == creater_atime:
        return 0
    else:
        return 1


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
                                           atime='true', acl='false', user_xattr='true', sync='false') # 打开atime
    common.judge_rc(rc, 0, '\t[create_client_auth failed, stdout = %s]' % stdout)
    result = common.json_loads(stdout)
    global client_auth_id
    client_auth_id = result['result']['ids'][0]

    '''客户端安装'''
    install_cmd = PACKAGE_PATH + '/install.py --ips=%s' % SERVER_IP[0]
    rc, stdout = common.run_command(CLIENT_IP[0], install_cmd)
    common.judge_rc(rc, 0, '\t[Install client failed, stdout=%s]' % stdout)

    ret_list = common.wait_df_find_volume([CLIENT_IP[0]], get_config.get_volume_names()[0], 1800, 1800)
    common.judge_rc(ret_list[0], 0, 'can not find volume in 600 seconds')

    rc = atime_check(CLIENT_IP[0], SERVER_IP[1], 'client1')
    common.judge_rc(rc, 0, 'atime check failed')
    rc = atime_check(SERVER_IP[2], CLIENT_IP[0], 'server')
    common.judge_rc(rc, 0, 'atime check failed')

    '''客户端卸载'''
    unistall_cmd = '/cliparastor/uninstall.py'
    rc, stdout = common.run_command(CLIENT_IP[0], unistall_cmd)
    common.judge_rc(rc, 0, '\t[uninstall client failed, stdout=%s]' % stdout)

    '''更新客户端授权, 关闭atime'''
    common.update_client_auth(client_auth_id, CLIENT_IP[0], volume_id, auto_mount='true',
                              atime='false', acl='false', user_xattr='true', sync='false' )

    '''客户端安装'''
    install_cmd = PACKAGE_PATH + '/install.py --ips=%s' % SERVER_IP[0]
    rc, stdout = common.run_command(CLIENT_IP[0], install_cmd)
    common.judge_rc(rc, 0, '\t[Install client failed, stdout=%s]' % stdout)

    ret_list = common.wait_df_find_volume([CLIENT_IP[0]], get_config.get_volume_names()[0], 1800, 1800)
    common.judge_rc(ret_list[0], 0, 'can not find volume in 600 seconds')

    rc = atime_check(CLIENT_IP[0], SERVER_IP[1], 'client2')
    common.judge_rc(rc, 1, 'atime moudle worked, allthough the atime=false has been set')



def case_clean():

    rc, stdout = common.delete_client_auth(client_auth_id)
    common.judge_rc(rc, 0, 'delete client auth failed')

    cmd = 'rm -rf %s/*' % get_config.get_mount_paths()[0]
    rc, stdout = common.run_command(SERVER_IP[0], cmd)
    common.judge_rc(rc, 0, 'rm failed')


def main():
    prepare_clean.test_prepare(FILE_NAME)
    uninstall.case()
    case()
    case_clean()
    prepare_clean.test_clean()


if __name__ == '__main__':
    common.case_main(main)