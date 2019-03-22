# -*-coding:utf-8 -*
import os
import time

import utils_path
import common
import snap_common
import log
import get_config
import prepare_clean

####################################################################################
#
# Author: liyao
# date 2018-05-05
# @summary：
#    多文件系统创建快照，浏览快照内容
# @steps:
#    1、在文件系统fs1的挂载根目录/mnt/parastor/创建快照a1，(使用命令pscli --command=create_snapshot)；
#    2、在文件系统fs2的挂载根目录/mnt/parastor1/创建快照a1，(使用命令pscli --command=create_snapshot)；
#    3、在文件系统fs3的挂载根目录/mnt/parastor2/创建快照a2，(使用命令pscli --command=create_snapshot)；
#    4、到各自的挂载路径下的./snapshot浏览快照内容；
#    5、修改三个根目录下的内容；
#    6、到各自的挂载路径下的./snapshot浏览快照内容；
#    7、删除快照；
#    8、查看是否有快照入口路径；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              # /mnt/volume1/snap/snap_13_0_2_27
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   # /snap/snap_13_0_2_27


def volume_info():
    # 从配置文件中获取一个存储卷信息
    volume = common.Volume()
    volume_name = get_config.get_volume_names()
    volume_name = volume_name[0]
    volume_id = volume.get_volume_id(volume_name)
    rc, stdout = volume.get_volumeinfo_by_id(volume_id)

    # 获取存储池id 及文件系统配比信息
    para_list = [0, 0, 0, 0, 0]
    para_list[0] = stdout['result']['volumes'][0]['storage_pool_id']
    para_list[1] = stdout['result']['volumes'][0]['layout']['disk_parity_num']
    para_list[2] = stdout['result']['volumes'][0]['layout']['stripe_width']
    para_list[3] = stdout['result']['volumes'][0]['layout']['replica_num']
    para_list[4] = stdout['result']['volumes'][0]['layout']['node_parity_num']

    return para_list


def create_multi_sys(storage_pool_id, n, m, b, r):        # 创建多个存储卷，并在各个文件系统中授权私有客户端
    volume = common.Volume()
    client_obj = common.Client()
    volume_ids = []
    client_auth = common.Clientauth()
    mount_path_list = []
    volume_name_list = []
    for i in range(4):
        volume_name = 'wahaha_%s' % str(i)
        rc, json_info = volume.create_volume(volume_name, storage_pool_id, n, m, b, r)
        common.judge_rc(rc, 0, "create volume failed")
        log.info('waiting for 10s to complete the volume creation')
        time.sleep(10)
        volume_id = volume.get_volume_id(volume_name)
        volume_ids.append(volume_id)
        client_ip_lst = get_config.get_allclient_ip()
        mount_path = '/mnt/%s' % volume_name
        for client_ip in client_ip_lst:
            client_auth.create_client_auth(client_ip, volume_id)
            # client_obj.mount_client(client_ip, mount_path, volume_name)
            cmd = 'df'
            rc, mount_judge_info = common.run_command(snap_common.SYSTEM_IP, cmd)
            if volume_name not in mount_judge_info:
                client_obj.mount_client(client_ip, mount_path, volume_name)

        mount_path_list.append(mount_path)        # 获取不同存储卷的挂载路径并返回，方便创建快照路径
        volume_name_list.append(volume_name)
    return mount_path_list, volume_name_list


def delete_multi_sys():
    volume = common.Volume()
    client_obj = common.Client()
    client_auth = common.Clientauth()
    volume_id = [0]
    for i in range(4):
        volume_name = 'wahaha_%s' % str(i)
        volume_id[0] = volume.get_volume_id(volume_name)
        volume_ids = volume_id[0]
        client_ip_lst = get_config.get_allclient_ip()
        mount_path = '/mnt/%s' % volume_name
        for client_ip in client_ip_lst:
            client_obj.umount_client(client_ip, mount_path)
            client_auth_id = client_auth.get_client_auth_id(client_ip, volume_id)

            log.info('waiting for 10s')
            time.sleep(10)
            client_auth.delete_client_auth(client_auth_id)
        rc, stdout = common.rm_exe(snap_common.SYSTEM_IP, mount_path + '/*')
        common.judge_rc(rc, 0, 'rm failed')
        rc = volume.delete_volume(volume_ids)
        common.judge_rc(rc, 0, "delete_volume failed")
    return


def case():
    # 获取存储池id 及存储卷配比等参数，创建多个文件系统
    para_list = volume_info()
    pool_id = para_list[0]
    n = para_list[2]
    m = para_list[1]
    b = para_list[4]
    r = para_list[3]
    mount_path_list, volume_name_list = create_multi_sys(pool_id, n, m, b, r)
    dir = [0, 0, 0, 0]
    file_test = [0, 0, 0, 0]
    name_0 = FILE_NAME + '_snap_1'
    name_1 = FILE_NAME + '_snap_2'
    snapshot_name = [name_0, name_0, name_0, name_1]
    snapshot_path = [0, 0, 0, 0]
    snap_path = [0, 0, 0, 0]
    file_md5 = [0, 0, 0, 0]
    snap_test_file = [0, 0, 0, 0]
    for i in range(4):
        # 各文件系统中创建目录并在目录下创建文件
        dir[i] = os.path.join(mount_path_list[i], 'snap')
        cmd = 'mkdir %s' % dir[i]
        common.run_command(snap_common.CLIENT_IP_1, cmd)
        file_test[i] = os.path.join(dir[i], 'file_test_%d' % i)
        cmd = 'dd if=%s of=%s bs=1k count=8' % (snap_common.get_system_disk(snap_common.CLIENT_IP_1), file_test[i])
        common.run_command(snap_common.CLIENT_IP_1, cmd)

        log.info('waiting for 10s')
        time.sleep(10)
        rc, file_md5[i] = snap_common.get_file_md5(snap_common.CLIENT_IP_1, file_test[i])

        # 各文件系统中创建快照
        snapshot_path[i] = volume_name_list[i] + ':/snap'
        rc, stdout = snap_common.create_snapshot(snapshot_name[i], snapshot_path[i])
        if 0 != rc:
            log.error('create_snapshot %s failed!!!' % snapshot_name[i])
            raise Exception('create_snapshot %s failed!!!' % snapshot_name[i])

        log.info('waiting for 15s')
        time.sleep(15)

        # 查询快照创建结果
        snap_path[i] = '/mnt/%s/.snapshot' % volume_name_list[i]
        snap_path[i] = os.path.join(snap_path[i], snapshot_name[i])
        snap_test_file[i] = os.path.join(snap_path[i], 'file_test_%d' % i)
        snap_common.check_snap_md5(file_md5[i], snap_test_file[i])

    # 修改文件内容并在隐藏目录下察看快照内容
    for i in range(4):
        cmd = 'echo aaa >> %s' % file_test[i]
        common.run_command(snap_common.SYSTEM_IP, cmd)

        log.info('waiting for 10s')
        time.sleep(10)
        snap_common.check_snap_md5(file_md5[i], snap_test_file[i])

    # 删除快照并查看入口
    for i in range(4):
        rc, stdout = snap_common.delete_snapshot_by_name(snapshot_name[i])
        if 0 != rc:
            log.error('%s delete failed!!!' % (snapshot_name[i]))
            raise Exception('%s delete failed!!!' % (snapshot_name[i]))

        log.info('waiting for 10s')
        time.sleep(10)

        snap_common.check_snap_entry(snap_path[i])

    # 清理环境，删除各文件系统上的/snap/目录
    for i in range(4):
        rc, stdout = common.rm_exe(snap_common.SYSTEM_IP, dir[i])
        if 0 != rc:
            log.error('%s clean failed!!!' % dir[i])
            raise Exception('%s clean failed!!!' % dir[i])
        snap_common.delete_snapshot_by_path(snapshot_path[i])

    # 删除脚本创建出的各文件系统
    delete_multi_sys()
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)