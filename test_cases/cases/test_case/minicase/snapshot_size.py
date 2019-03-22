#!/usr/bin/python
# -*- encoding=utf8 -*-

import os
import time

import utils_path
import common
import log
import get_config
import tool_use
import commands
import prepare_clean
import quota_common
import snap_common

##############################################################################
"""
1.创建卷，授权客户端
2、创建卷统计配额
3、循环n次
创建快照
写数据，文件大小可控，文件数量可控
再创建快照，输出卷空间使用情况
删除文件的10%，修改10%，新建10%
再创建快照，当快照数量大于5的时候，删除最早快照，输出卷空间使用情况
删除文件的10%，修改10%，新建10%、
"""
##############################################################################
FILENUM = 500      # 文件数量 注意：需要大于10个
FILESIZE = '1m'    # 文件大小
RUNTIME = 15       # 运行次数
DELAY_TIME = 10    # 创建快照间隔时间 （秒）
THREADS = 10       # fwd线程数 需要小于 FILENUM /10

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]          # 本脚本名字

NEW_VOLUME_NAME = FILE_NAME
CREATE_DIR_NAME = "/mnt/%s/snap_test" % NEW_VOLUME_NAME
CREAE_SNAP_PATH = "%s:/snap_test" % NEW_VOLUME_NAME

ob_vdbench = tool_use.Vdbenchrun(elapsed=100, threads=THREADS)

ANC_PATH_LST = []
for i in range(10):
    ANC_PATH_LST.append(os.path.join(CREATE_DIR_NAME, str(i)))


def file_count(num):
    list = []
    for i in range(10):
        list.append(0)
    for i in range(num):
        list[i % 10] += 1
    return list


def files_del(num, size, path_index):
    log.info("delete 10 percent files ; now delete %s" % path_index)

    file_cnt_lst = file_count(num)
    client_lst = [get_config.get_allclient_ip()[0]]
    VDB_FILE_STRU_LST = []
    for i in file_cnt_lst:
        tmp = [1, 1, i, size]
        VDB_FILE_STRU_LST.append(tmp)
    rc = ob_vdbench.run_clean_one_fsd_snapsize(ANC_PATH_LST, ANC_PATH_LST, client_lst, VDB_FILE_STRU_LST, path_index)

    # rm_dir = os.path.join(ANC_PATH_LST[path_index])
    # rc = ob_vdbench.run_clean(rm_dir, get_config.get_allparastor_ips()[0])
    # rc = common.rm_exe(get_config.get_allparastor_ips()[0], rm_dir)
    return rc


def files_creat_init(num, size):
    log.info("~file_creat num=%s , size=%s~" % (num, size))
    file_cnt_lst = file_count(num)
    client_lst = [get_config.get_allclient_ip()[0]]
    VDB_FILE_STRU_LST = []
    for i in file_cnt_lst:
        tmp = [1, 1, i, size]
        VDB_FILE_STRU_LST.append(tmp)
    rc = ob_vdbench.run_create_mulpath_diff_snap_size(ANC_PATH_LST, ANC_PATH_LST, client_lst, VDB_FILE_STRU_LST)
    return rc


def files_creat(num, size, path_index):
    log.info("~file_creat num=%s , size=%s~" % (num, size))
    file_cnt_lst = file_count(num)
    client_lst = [get_config.get_allclient_ip()[0]]
    VDB_FILE_STRU_LST = []
    for i in file_cnt_lst:
        tmp = [1, 1, i, size]
        VDB_FILE_STRU_LST.append(tmp)
    rc = ob_vdbench.run_create_mulpath_diff(ANC_PATH_LST, ANC_PATH_LST, client_lst, VDB_FILE_STRU_LST, path_index)
    return rc


def files_change(num, size, path_index):
    log.info("change 10percent files now change %s"%path_index)
    file_cnt_lst = file_count(num)
    client_lst = [get_config.get_allclient_ip()[0]]
    VDB_FILE_STRU_LST = []
    for i in file_cnt_lst:
        tmp = [1, 1, i, size]
        VDB_FILE_STRU_LST.append(tmp)
    rc = ob_vdbench.run_change_one_fsd(ANC_PATH_LST, ANC_PATH_LST, client_lst, VDB_FILE_STRU_LST, path_index)
    return rc


def dir_total_file_size(node_ip, path):
    cmd = ("ssh %s ls -alR %s |grep '^-' | awk -F \" \" '{print $5}'") % (node_ip, path)
    rc, stdout = commands.getstatusoutput(cmd)
    common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    file_size_list = stdout.split()

    new_file_size_list = []
    for file_size in file_size_list:
        new_file_size_list.append(int(file_size))

    total_file_size = sum(new_file_size_list)

    log.info("\t total_file_size = %s" % total_file_size)
    return total_file_size


def check_snap_work(snap_name):
    start_time = time.time()
    work_flag = False
    while True:
        pscli_info = snap_common.get_all_snapshot()
        for snap in pscli_info['result']['snapshots']:
            if snap['name'] == snap_name:
                if snap['state'] == 'SNAPSHOT_WORKING':
                    work_flag = True
                    break
                else:
                    time.sleep(10)
                    exist_time = int(time.time() - start_time)
                    m, s = divmod(exist_time, 60)
                    h, m = divmod(m, 60)
                    log.info('wait snap SNAPSHOT_WORKING exist %dh:%dm:%ds' % (h, m, s))
                break
        if work_flag is True:
            log.info('snap %s SNAPSHOT_WORKING' % snap_name)
            break


def check_snap_exist_by_id(snap_id):
    pscli_info = snap_common.get_all_snapshot(ids=snap_id)
    if pscli_info['result']['total'] == 0:
        return False
    else:
        return True


def wait_snap_delete_by_id(snap_id):
    start_time = time.time()
    while True:
        if check_snap_exist_by_id(snap_id) is False:
            break
        else:
            time.sleep(10)
            exist_time = int(time.time() - start_time)
            m, s = divmod(exist_time, 60)
            h, m = divmod(m, 60)
            log.info('wait snap delete exist %dh:%dm:%ds' % (h, m, s))
    log.info('snap delete success')


def case():
    log.info("==========snap_size_test start==========")
    ob_volume = common.Volume()
    ob_storagepool = common.Storagepool()
    client_lst = get_config.get_allclient_ip()[0:1]
    exe_client = client_lst[0]
    rc, pscli_info = ob_volume.get_all_volumes()
    common.judge_rc(rc, 0, "get_all_volumes failed")
    delete_id = 0
    for volumeinfo in pscli_info['result']['volumes']:
        if volumeinfo['name'] == FILE_NAME:
            delete_id = volumeinfo['id']
    if delete_id != 0:
        snap_common.delete_snapshot_by_name(FILE_NAME)
        snap_common.wait_snap_del_by_name(FILE_NAME)
        volume_id_list = [delete_id]
        ob_auth_clinet = common.Clientauth()
        for client_ip in client_lst:
            client_auth_id = ob_auth_clinet.get_client_auth_id(client_ip, volume_id_list)
            ob_auth_clinet.delete_client_auth(client_auth_id)
        rc = ob_volume.delete_volume(delete_id)
        common.judge_rc(rc, 0, 'delete_volume failed')

    log.info("1、创建卷，并授权客户端")

    '''获取存储池的信息'''
    obj_storage_pool = common.Storagepool()
    rc, storage_pools = obj_storage_pool.get_storagepool_info()
    common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (rc, storage_pools))
    storage_name = ''
    for storage_pool in storage_pools['result']['storage_pools']:
        if storage_pool['name'] != 'shared_storage_pool':
            storage_name = storage_pool['name']
            break

    rc, storagepool_id = ob_storagepool.get_storagepool_id(storage_name)  # 获取此存储池的ID
    common.judge_rc(rc, 0, 'get_storagepool_id failed')

    '''获取该存储池上一个已有的卷的信息'''
    one_volume = {}
    obj_volume = common.Volume()
    rc, volume_info = obj_volume.get_all_volumes()
    common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (rc, volume_info))
    volume_num = volume_info['result']['total']
    common.judge_rc_unequal(volume_num, 0, 'your storage_pool need a volume!')
    for volume in volume_info['result']['volumes']:
        if volume['storage_pool_name'] == storage_name:
            one_volume = volume

    """创建一个新卷"""
    rc, json_info = obj_volume.create_volume(name=FILE_NAME, storage_pool_id=storagepool_id,
                             stripe_width=one_volume['layout']['stripe_width'],
                             disk_parity_num=one_volume['layout']['disk_parity_num'],
                             node_parity_num=one_volume['layout']['node_parity_num'],
                             replica_num=one_volume['layout']['replica_num'])
    common.judge_rc(rc, "create volume failed")
    """获取此卷所有信息"""
    old_volume = {}
    rc, volume_info = obj_volume.get_all_volumes()
    for volume in volume_info['result']['volumes']:
        if volume['name'] == FILE_NAME:
            old_volume = volume

    """添加授权"""
    auth_info = {}
    auth_info['auto_mount'] = 'true'
    obj_client_auth = common.Clientauth()
    for client_ip in client_lst:
        rc, stdout = obj_client_auth.create_client_auth(ip=client_ip,
                                                        volume_ids=old_volume['id'],
                                                        auto_mount=auth_info['auto_mount'])
        common.judge_rc(rc, 0, "client_ip : %s Execute command: \"%s\" failed. \nstdout: %s" % (client_ip, rc, stdout))

    '''检查是否能发现挂载卷'''
    flag_ip_volume = 1
    for i in range(len(client_lst) - 1):
        flag_ip_volume = (flag_ip_volume << 1) + 1  # 111111
    res_ip_volume = flag_ip_volume  # 111111
    start_time = time.time()
    while True:
        for i, ip in enumerate(client_lst):
            if (flag_ip_volume & (1 << i)) != 0:  # 仅看还未发现卷的节点
                res = common.check_client_state(ip, FILE_NAME, timeout=300)  # 使用判断客户端超时的函数
                if 0 == res:
                    flag_ip_volume &= (res_ip_volume ^ (1 << i))  # 将i对应的标志位置0
                elif -1 == res:
                    raise Exception('ssh failed !!!  please check node!!!')
                elif -2 == res:
                    raise Exception('client is blockup !!!')
                else:
                    log.info('still waiting %s' % ip)
        if flag_ip_volume & res_ip_volume == 0:  # 全0则通过
            break
        time.sleep(10)
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        log.info('not found volume exist %dh:%dm:%ds' % (h, m, s))

    log.info('wait 10s')
    time.sleep(10)

    common.mkdir_path(exe_client, CREATE_DIR_NAME)

    log.info("2> 创建卷根目录统计配额")

    log.info("3> 创建文件")
    rc = files_creat_init(FILENUM, FILESIZE)
    common.judge_rc(rc, 0, "file_creat failed ")

    for i in range(RUNTIME):
        """创建快照"""
        snap_name = FILE_NAME + '%s' % i
        rc, stdout = snap_common.create_snapshot(snap_name, CREAE_SNAP_PATH)
        common.judge_rc(rc, 0, "create_snapshot failed")
        check_snap_work(snap_name)
        """快照数量大于5 删除最早的"""
        if i >= 5:
            rc, snapshot_id_lst = snap_common.get_snapshot_ids_by_name(FILE_NAME + '%s' % (i-5))
            snap_id = snapshot_id_lst[0]
            rc, stdout = snap_common.delete_snapshot_by_ids(snap_id)
            common.judge_rc(rc, 0, "delete_snapshot_by_ids id : %s  failed " % snap_id)
            wait_snap_delete_by_id(snap_id)

        rc, stdout = snap_common.get_snapshot_ids_by_name(FILE_NAME)
        log.info('now snap lst:')
        log.info(stdout)
        """删除10%  创建10%  修改10%"""
        rm_add_idndex = i % 10  # 0-----9
        change_index = (rm_add_idndex + 1) % 10  # 1-----10(0)
        """删除10%"""
        rc = files_del(FILENUM, FILESIZE, rm_add_idndex+1)
        common.judge_rc(rc, 0, "files_del failed")
        # time.sleep(10)
        """创建10%"""
        files_creat(FILENUM, FILESIZE, rm_add_idndex+1)
        common.judge_rc(rc, 0, "files_creat failed")
        # time.sleep(10)
        """修改10%"""
        files_change(FILENUM, FILESIZE, change_index+1)
        common.judge_rc(rc, 0, "files_change failed")

        log.info("wait %s s" % DELAY_TIME)
        time.sleep(DELAY_TIME)

        vsize = dir_total_file_size(common.SYSTEM_IP, "/mnt/" + FILE_NAME)
        log.info("the %s time running: volume logical_used_capacity is %s" % (i, vsize))

        '''
        rc, pscli_info = quota_common.get_all_quota_info()
        common.judge_rc(rc, 0, "get quota failed")
        pscli_info = common.json_loads(stdout)
        log.info("the %s time running: volume logical_used_capacity is %s"
                 % (i, pscli_info['result']['quotas'][0]['logical_used_capacity']))
        '''
    log.info("恢复环境")
    """删除配额"""
    '''
    rc, pscli_info = quota_common.delete_one_quota(quota_id)
    common.judge_rc(rc, 0, "delete quota failed", exit_flag=False)
    '''
    """删除快照"""
    rc, stdout = snap_common.get_snapshot_ids_by_name(FILE_NAME)
    if rc == -1:
        log.info('cannot delete snap  because  not exist any snapname include %s' % FILE_NAME)
    for id in stdout:
        rc, stdout = snap_common.delete_snapshot_by_ids(id)
        common.judge_rc(rc, 0, "delete_snapshot_by_ids id : %s  failed " % id)
        wait_snap_delete_by_id(id)

    """删除授权"""
    volume_id_list = [old_volume['id']]
    ob_auth_clinet = common.Clientauth()
    for client_ip in client_lst:
        client_auth_id = ob_auth_clinet.get_client_auth_id(client_ip, volume_id_list)
        ob_auth_clinet.delete_client_auth(client_auth_id)
    """删除卷"""
    rc = ob_volume.delete_volume(old_volume['id'])
    common.judge_rc(rc, 0, "delete_volume failed")

    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
