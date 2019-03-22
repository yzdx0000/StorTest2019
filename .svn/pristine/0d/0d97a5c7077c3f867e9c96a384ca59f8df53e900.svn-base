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
import nas_common
import tool_use
import uninstall

####################################################################################
#
# author 刘俊鑫
# date 2019-1-23
# @summary：
#   单客户端多个文件系统
# @steps:
#   step1: 创建42个文件系统
#   step2: 客户端授权、安装、挂载
#   step3: 给客户端授权2个文件系统并安装客户端，自动挂载
#   step4: 循环增加2个文件系统授权，并检查挂载是否成功
#   step5: 每个文件系统创建10个1m文件，删除10个1m文件
#   step6：随机取消其中5个文件系统的授权
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
client_auth_ids = []
volume_id_lst = []
volume_name_lst = []
volume_base_name = get_config.get_volume_names()[0] + 'bbb'
# testlink case: 3.0-55128


def delete_client_auth_id_base_volumename(volume_name):
    rc, stdout = common.get_client_auth()
    results = common.json_loads(stdout)
    client_auth_id = ''
    for result in results['result']:
        if result['volumes'][0]['volume_name'].find(volume_name) != -1:
            client_auth_id = result['id']
            common.delete_client_auth(client_auth_id)
    if client_auth_id == '':
        log.info('do not find auth about volume:%s' % volume_name)


def case_prepare():
    Volume = common.Volume()
    for i in range(1, 43):
        volume_name = volume_base_name + str(i)
        if Volume.get_volume_id(volume_name) is not None:
            delete_client_auth_id_base_volumename(volume_name)
            cmd = 'rm -rf /mnt/%s/*' % volume_name
            rc, stdout = common.run_command(SERVER_IP[0], cmd)
            common.judge_rc(rc, 0, 'rm -rf %s failed' % volume_name)
            Volume.delete_volume(Volume.get_volume_id(volume_name))


def case():

    log.info('1.create 42 volumes')

    cmd = 'pscli --command=get_storage_pool_stat|grep FILE'
    rc, stdout = common.run_command(SERVER_IP[0], cmd)
    common.judge_rc(rc ,0, 'get_storage_pool_stat failed')
    storage_pool_id = stdout.split()[0]
    nodepool = common.Nodepool()
    nodepool_ids = nodepool.get_all_node_pool_ids()
    nodepool_id = random.choice(nodepool_ids)
    rc, stdout = common.get_node_pools(nodepool_id)
    result = common.json_loads(stdout)
    stripe_width = result['result']['node_pools'][0]['stripe_width']
    disk_parity_num = result['result']['node_pools'][0]['disk_parity_num']
    node_parity_num = result['result']['node_pools'][0]['node_parity_num']
    replica_num = result['result']['node_pools'][0]['replica_num']

    volume = common.Volume()
    for i in range(1, 43):
        volume_name = volume_base_name + str(i)
        common.create_volume(volume_name, storage_pool_id, stripe_width, disk_parity_num, node_parity_num, replica_num,
                  total_bytes=None, dir_slice_num=None, chunk_size=None, obj_size=None, object_size=None,
                  remark=None, print_flag=False, fault_node_ip=None)
        volume_id_lst.append(volume.get_volume_id(volume_name))
        volume_name_lst.append(volume_name)

    log.info('2.Create client auth, Install client , check volume mount and write files')

    global client_auth_ids

    volume_ids = str(volume.get_volume_id(volume_base_name+'1')) + ',' + str(volume.get_volume_id(volume_base_name+'2'))
    rc, stdout = common.create_client_auth(CLIENT_IP[0], volume_ids, auto_mount='true',
                                           atime='false', acl='false', user_xattr='true', sync='false')
    common.judge_rc(rc, 0, '\t[create_client_auth failed, stdout = %s]' % stdout)
    result = common.json_loads(stdout)
    client_auth_ids.append(result['result']['ids'][0])

    '''客户端安装'''
    install_cmd = PACKAGE_PATH + '/install.py --ips=%s' % SERVER_IP[0]
    rc, stdout = common.run_command(CLIENT_IP[0], install_cmd)
    common.judge_rc(rc, 0, '\t[Install client failed, stdout=%s]' % stdout)

    for i in range(1, 3):

        ret_list = common.wait_df_find_volume([CLIENT_IP[0]], volume_base_name+str(i), 1800, 1800)
        common.judge_rc(ret_list[0], 0, 'can not file volume in 600 seconds')

    for i in range(3, 43, 2):
        volume_ids = str(volume.get_volume_id(volume_base_name+str(i))) \
                     + ',' \
                     + str(volume.get_volume_id(volume_base_name+str(i+1)))
        rc, stdout = common.create_client_auth(CLIENT_IP[0], volume_ids, auto_mount='true',
                                               atime='false', acl='false', user_xattr='true', sync='false')
        common.judge_rc(rc, 0, '\t[create_client_auth failed, stdout = %s]' % stdout)
        result = common.json_loads(stdout)
        global client_auth_ids
        client_auth_ids.append(result['result']['ids'][0])
        ret_list = common.wait_df_find_volume([CLIENT_IP[0]], volume_base_name+str(i), 1800, 1800)
        common.judge_rc(ret_list[0], 0, 'can not file %s in 600 seconds' % volume_base_name + str(i))
        ret_list = common.wait_df_find_volume([CLIENT_IP[0]], volume_base_name+str(i+1), 1800, 1800)
        common.judge_rc(ret_list[0], 0, 'can not file %s in 600 seconds' % volume_base_name+str(i+1))

    vdbench = tool_use.Vdbenchrun(depth=1, width=1, files=10, size='1m', threads=5)
    for i in range(1, 43):
        volume_name = volume_base_name + str(i)
        file_create_path = '/mnt/' + volume_name
        vdbench.run_create(file_create_path, file_create_path, CLIENT_IP[0])

    log.info('3.cancel 5 client auths randomly')
    cancle_auth_ids = random.sample(client_auth_ids, 5)
    for id in cancle_auth_ids:
        client_auth_ids.remove(id)
    cancle_auth_ids_new = [str(x) for x in cancle_auth_ids]
    rc, stdout = common.delete_client_auth(",".join(cancle_auth_ids_new))
    common.judge_rc(rc, 0, 'delete client auth failed')


def case_clean():
    global client_auth_ids
    for client_auth_id in client_auth_ids:
        common.delete_client_auth(client_auth_id)

    for volume in volume_name_lst:
        cmd = "rm -rf /mnt/%s/*" % volume
        rc, stdout = common.run_command(SERVER_IP[0], cmd)
        common.judge_rc(rc, 0, 'rm failed')

    volume = common.Volume()
    volume_id_lst_new = [str(x) for x in volume_id_lst]
    volume.delete_volume(','.join(volume_id_lst_new))
    cmd = 'rm -rf %s/*' % get_config.get_mount_paths()[0]
    rc, stdout = common.run_command(SERVER_IP[0], cmd)
    common.judge_rc(rc, 0, 'rm failed')


def main():
    prepare_clean.defect_test_prepare(FILE_NAME, env_check=False)
    uninstall.case()
    case_prepare()
    case()
    case_clean()
    prepare_clean.defect_test_clean(FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
