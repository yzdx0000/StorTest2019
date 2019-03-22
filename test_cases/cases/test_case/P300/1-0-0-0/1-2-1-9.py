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
import rep_common
import tool_use
import uninstall

####################################################################################
#
# author 刘俊鑫
# date 2019-2-19
# @summary：
#   一台客户端连接两套集群
# @steps:
#   step1: 客户端连接第一套集群
#   step2：修改第二套集群的客户端端口
#   step3：客户端连接第二套集群
#   step4：连接上后跑一段时间读写
#
#   ps.需要将客户端安装包放到PACKAGE_PATH中,并保证该目录下只有这一个安装包
#
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
PACKAGE_PATH = get_config.get_client_install_path()
CLIENT_IP = get_config.get_allclient_ip()
SERVER_IP = get_config.get_allparastor_ips()
SEC_SERVER_IP = get_config.get_slave_node_lst()
VDBENCH_PATH = get_config.get_mount_paths()[0] + '/data'
VDBENCH_SEC_PATH = get_config.get_rep_slave_test_path() + '/data'
client_auth_id = 0
# testlink case: 3.0-54773


def get_client_auth_id_base_volumename(volume_name, run_cluster):
    rc, stdout = common.get_client_auth(run_cluster=run_cluster)
    results = common.json_loads(stdout)
    client_auth_id = ''
    for result in results['result']:
        if result['volumes'][0]['volume_name'] == volume_name:
            client_auth_id = result['id']
    if client_auth_id == '':
        log.info('do not find auth about volume:%s' % volume_name)
    return rc, client_auth_id

def case_prepare():

    log.info('*******clear environment begin*******')
    unistall_cmd = '/cliparastor/uninstall.py'
    rc, stdout = common.run_command(CLIENT_IP[0], unistall_cmd)
    common.judge_rc(rc, 0, 'uninstall client failed')

    '''删除第一套集群的客户端授权'''
    rc, master_client_auth_id = get_client_auth_id_base_volumename(get_config.get_volume_names()[0], common.MASTER)
    common.judge_rc(rc, 0, 'delete client auth failed', exit_flag=False)
    rc,stdout = common.delete_client_auth(master_client_auth_id)
    common.judge_rc(rc, 0, 'delete client auth about %s failed' % get_config.get_volume_names()[0], exit_flag=False)

    log.info('删除第二套集群的客户端授权')
    rc, slave_client_auth_id = get_client_auth_id_base_volumename(get_config.get_slave_volume_name(0), common.SLAVE)
    common.judge_rc(rc, 0, 'delete client auth failed', exit_flag=False)
    rc, stdout = common.delete_client_auth(slave_client_auth_id, run_cluster=common.SLAVE)
    common.judge_rc(rc, 0, 'delete client auth about %s failed' % get_config.get_slave_volume_name(0), exit_flag=False)

    '''删除卷下的所有文件'''
    cmd = 'rm -rf %s/*' % get_config.get_mount_paths()[0]
    rc, stdout = common.run_command(SERVER_IP[0], cmd)
    common.judge_rc(rc, 0, '%s failed' % cmd)

    cmd = 'rm -rf /mnt/%s/*' % get_config.get_slave_volume_name(0)
    rc, stdout = common.run_command(SEC_SERVER_IP[0], cmd)
    common.judge_rc(rc, 0, '%s failed' % cmd)


def case():

    log.info("********第一套集群的授权与安装***************")
    '''第一套集群客户端授权'''
    volume = common.Volume()
    volume_name = get_config.get_volume_names()
    volume_id = volume.get_volume_id(volume_name[0])
    rc, stdout = common.create_client_auth(CLIENT_IP[0], volume_id, auto_mount='true',
                                           atime='false', acl='false', user_xattr='true', sync='false')
    common.judge_rc(rc, 0, '\t[create_client_auth failed, stdout = %s]' % stdout)
    result = common.json_loads(stdout)
    global client_auth_id
    client_auth_id = result['result']['ids'][0]
    '''第一套集群客户端安装'''
    install_cmd = PACKAGE_PATH + '/install.py --ips=%s' % SERVER_IP[0]
    rc, stdout = common.run_command(CLIENT_IP[0], install_cmd)
    common.judge_rc(rc, 0, '\t[Install client failed, stdout=%s]' % stdout)

    ret_list = common.wait_df_find_volume([CLIENT_IP[0]], get_config.get_volume_names()[0], 1800, 1800)
    common.judge_rc(ret_list[0], 0, 'can not file volume in 600 seconds')

    log.info("********第二套集群的授权与安装***************")
    '''改变第二套集群的客户端端口'''
    cmd = '/home/parastor/tools/pscli_setparam.sh NAL#tcp_port_client_server=9100'
    rc, stdout = common.run_command(SEC_SERVER_IP[0], cmd)
    common.judge_rc(rc, 0, 'change clinet port failed')

    '''第二套集群客户端授权'''
    rc, stdout = common.get_volumes(run_cluster=common.SLAVE)
    common.judge_rc(rc, 0, 'get_volumes failed')

    result = common.json_loads(stdout)
    volume_name_sec = get_config.get_slave_volume_name(0)
    volume_ids_sec = []
    for volume in result['result']['volumes']:
        if volume['name'] == volume_name_sec:
            volume_ids_sec.append(volume['id'])
    for volume_id_sec in volume_ids_sec:
        rc, stdout = common.create_client_auth(CLIENT_IP[0], volume_id_sec, auto_mount='true', atime='false',
                                               acl='false', user_xattr='true', sync='false', run_cluster=common.SLAVE)
        common.judge_rc(rc, 0, '\t[create_client_auth failed, stdout = %s]' % stdout)

    '''第二套集群客户端安装'''
    install_cmd = '/cliparastor/install.py --ips=%s' % SEC_SERVER_IP[0]
    rc, stdout = common.run_command(CLIENT_IP[0], install_cmd)
    common.judge_rc(rc, 0, '\t[Install client to second cluster failed, stdout=%s]' % stdout)

    ret_list = common.wait_df_find_volume([CLIENT_IP[0]], get_config.get_slave_volume_name(0), 1800, 1800)
    common.judge_rc(ret_list[0], 0, 'can not file slave volume in 600 seconds')

    cmd = 'mkdir -p %s' % VDBENCH_PATH
    rc, stdout = common.run_command(SERVER_IP[0], cmd)
    common.judge_rc(rc, 0, '\t[command %s excuted faield, stdout=%s]' % (cmd, stdout))

    cmd = 'mkdir -p %s' % VDBENCH_SEC_PATH
    rc, stdout = common.run_command(SEC_SERVER_IP[0], cmd)
    common.judge_rc(rc, 0, '\t[command %s excuted faield, stdout=%s]' % (cmd, stdout))

    '''在两个卷上进行vdbench业务'''
    vdbench = tool_use.Vdbenchrun(depth=1, width=1, files=100, size='1m', threads=50)
    p1 = Process(target=vdbench.run_create, args=(VDBENCH_PATH, VDBENCH_PATH, CLIENT_IP[0]))
    p2 = Process(target=vdbench.run_create, args=(VDBENCH_SEC_PATH, VDBENCH_SEC_PATH, CLIENT_IP[0]))

    p1.start()
    time.sleep(5)
    p2.start()
    p1.join()
    p2.join()
    if p1.exitcode != 0 or p2.exitcode != 0:
        common.except_exit('vdbench create failed')


def case_clean():

    rc, stdout = common.delete_client_auth(client_auth_id)
    common.judge_rc(rc, 0, 'delete client auth failed')

    cmd = 'rm -rf %s/*' % get_config.get_mount_paths()[0]
    rc, stdout = common.run_command(SERVER_IP[0], cmd)
    common.judge_rc(rc, 0, 'rm failed')


def main():
    prepare_clean.test_prepare(FILE_NAME)
    case_prepare()
    case()
    case_prepare()
    log.info('%s succeed!' % FILE_NAME)
    prepare_clean.test_clean()


if __name__ == '__main__':
    common.case_main(main)