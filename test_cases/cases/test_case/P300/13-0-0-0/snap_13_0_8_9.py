# -*-coding:utf-8 -*
import os
import time

import utils_path
import common
import snap_common
import log
import get_config
import json
import quota_common
import prepare_clean
import quota_common
import sys

####################################################################################
#
# Author: liyao
# date 2018-05-25
# @summary：
#    对根目录创建配额（文件数，硬阈值），配额限制等于初始文件数，创建快照并查看回滚结果
# @steps:
#    1、在/mnt/volume1/下创建100个非空文件；
#    2、对上述目录创建filenr为100的硬阈值；
#    3、对目录创建快照；
#    4、删除目录下的50个文件；
#    5、在目录/mnt/volume1/下尝试创建60个文件；
#    6、执行revert并查看回滚结果；
#    7、删除配额、快照及所创建的文件；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             # /mnt/volume1/snap/snap_13_0_8_9
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  # /snap/snap_13_0_8_9
SNAP_PATH = get_config.get_one_snap_test_path()
BASE_SNAP_PATH = os.path.dirname(SNAP_PATH)                                 # BASE_SNAP_PATH = "/mnt/volume1"


def prepare_new_volume():
    """
    auth:chenjy1
    description:创建新卷
    :return:none
    """

    nodeip_lst = get_config.get_allparastor_ips()
    clientip_lst = get_config.get_allclient_ip()
    ob_volume = common.Volume()
    ob_storagepool = common.Storagepool()
    ob_clientauth = common.Clientauth()

    rc, stdout = ob_volume.ready_to_del_volume(FILE_NAME)
    common.judge_rc(rc, 0, 'ready_to_del_volume failed')

    auth_ip = ob_clientauth.get_all_clientip_str(clientip_lst)
    same_name_volume_id = ob_volume.get_volume_id(FILE_NAME)
    same_name_volume_id_lst = [same_name_volume_id]
    auth_id = ob_clientauth.get_client_auth_id(auth_ip, same_name_volume_id_lst, print_flag=True)

    if auth_id != None and same_name_volume_id != None:
        return same_name_volume_id, auth_id

    rc, pscli_info = ob_storagepool.get_storagepool_info()
    common.judge_rc(rc, 0, "get_all_storagepools failed")

    storagepool_id = 0
    storagepool_name = ''
    for storage_pool in pscli_info['result']['storage_pools']:
        if storage_pool['name'] != 'shared_storage_pool' and storage_pool['type'] == 'FILE':
            storagepool_id = storage_pool['id']
            storagepool_name = storage_pool['name']
            break

    """获取此存储池上一个已有的卷的信息"""
    one_volume = {}
    rc, pscli_info = ob_volume.get_all_volumes()
    common.judge_rc(rc, 0, "get_all_volumes failed")
    for volume in pscli_info['result']['volumes']:
        if volume['storage_pool_name'] == 'system_volume':
            continue
        if volume['storage_pool_name'] == storagepool_name:
            one_volume = volume
            break

    rc, json_info = ob_volume.create_volume(FILE_NAME, storagepool_id, one_volume['layout']['stripe_width'],
                                            one_volume['layout']['disk_parity_num'],
                                            one_volume['layout']['node_parity_num'],
                                            one_volume['layout']['replica_num'])
    common.judge_rc(rc, 0, "create volume failed")
    rc, pscli_info = ob_volume.get_all_volumes()
    common.judge_rc(rc, 0, "get_all_volumes failed")
    my_volume_id = 0
    for volume in pscli_info['result']['volumes']:
        if volume['name'] == FILE_NAME:
            my_volume_id = volume['id']
            break

    log.info('wait 30s')
    time.sleep(30)

    rc, stdout = ob_clientauth.create_client_auth(auth_ip, my_volume_id)
    common.judge_rc(rc, 0, 'create_client_auth failed')
    auth_id = common.json_loads(stdout)['result']['ids'][0]
    ret_lst = common.wait_df_find_volume(clientip_lst, FILE_NAME, 300, 1800)

    rcflag = False
    for i in ret_lst:
        if i != 0:
            log.info("ip = %s  state is %s" % (clientip_lst[i], i))
            rcflag = True
    common.judge_rc(rcflag, False, 'some client mount state failed')

    return my_volume_id, auth_id


def case():
    new_volume_id, auth_id = prepare_new_volume()
    nodeip_lst = get_config.get_allparastor_ips()
    ob_volume = common.Volume()
    ob_storagepool = common.Storagepool()
    rc, pscli_info = ob_storagepool.get_storagepool_info()
    common.judge_rc(rc, 0, "get_all_storagepools failed")

    # 1> 目录下创建100个非空文件
    temp_name = 'test_liyao'
    for i in range(100):
        file_name = temp_name + str(i)
        file_path = os.path.join('/mnt/%s' % FILE_NAME, file_name)
        cmd = 'echo 111 > %s' % file_path
        common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 2> 对目录创建配额（文件数，硬阈值）
    quota_path = FILE_NAME + ':/'
    rc, check_result = quota_common.create_one_quota(path=quota_path,
                                                     filenr_quota_cal_type='QUOTA_LIMIT',
                                                     filenr_hard_threshold=100)
    common.judge_rc(rc, 0, "create quota failed", exit_flag=False)

    log.info('wait 10s')
    time.sleep(10)
    rc, quota_id = quota_common.get_one_quota_id(path=quota_path,
                                                 u_or_g_type=quota_common.TYPE_CATALOG)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    # 3> 对目录创建快照
    snap_name = FILE_NAME + '_snapshot1'
    snap_path = FILE_NAME + ':/'
    rc, stdout = snap_common.create_snapshot(snap_name, snap_path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name)
        raise Exception('create_snapshot %s failed!!!' % snap_name)

    # 4> 删除目录下的50个文件
    for i in range(50):
        file_name = temp_name + str(i)
        file_path = os.path.join('/mnt/%s' % FILE_NAME, file_name)
        common.rm_exe(snap_common.CLIENT_IP_1, file_path)

    log.info('waiting for 10s')
    time.sleep(10)
    rc, quota_id = quota_common.get_one_quota_id(path=quota_path,
                                                 u_or_g_type=quota_common.TYPE_CATALOG)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    # 5> 目录下尝试创建60个文件
    temp_name_again = temp_name + '_again'
    for i in range(60):
        file_name = temp_name_again + str(i)
        file_path = os.path.join('/mnt/%s' % FILE_NAME, file_name)
        cmd = 'echo 222 > %s' % file_path
        rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
        if 0 != rc:
            count = i + 1
            specific_file = temp_name_again + str(count)
            print specific_file
            if count != 51:
                log.error('quota limitation is incorrect !!!')
                raise Exception('quota limitation is incorrect !!!')
            else:
                break

    # 6> 执行回滚操作
    snap_info = snap_common.get_snapshot_by_name(snap_name)
    snap_id = snap_info['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id)
    if rc != 0:
        log.error("revert snapshot %s failed!!!" % snap_name)
        raise Exception("revert snapshot %s failed!!!" % snap_name)
    snap_common.check_revert_finished(snap_id)

    cmd = 'ls %s | grep %s | wc -l' % ('/mnt/%s'%FILE_NAME, temp_name)
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    print stdout
    if stdout.strip() != '100':
        log.error('revert snapshot %s failed' % snap_name)
        raise Exception('revert snapshot %s failed' % snap_name)

    # 7> 删除配额、快照及创建的文件
    rc, stdout = quota_common.delete_one_quota(quota_id)
    common.judge_rc(rc, 0, "delete quota failed")

    snap_common.delete_snapshot_by_path(snap_path)

    file_wait_delete = os.path.join('/mnt/%s' % FILE_NAME, temp_name + '*')
    common.rm_exe(snap_common.CLIENT_IP_1, file_wait_delete)
    # rc, stdout = common.delete_client_auth(auth_id)
    # common.judge_rc(rc, 0, 'delete_client_auth failed')
    # rc, stdout = common.delete_volumes(new_volume_id)
    # common.judge_rc(rc, 0, 'delete_volumes failed')
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)