# -*-coding:utf-8 -*
import os
import time

import utils_path
import common
import snap_common
import log
import prepare_clean

####################################################################################
#
# Author: liyao
# date 2018-04-26
# @summary：
#    创建单个文件快照后，查看快照空间统计的正确性。
# @steps:
#    1、部署3个客户端；
#    2、/mnt/liyao/snap下创建大小为1500M的非空文件test_file1；
#    3、对目录创建快照；
#    4、在文件test_file1中继续写入内容；
#    5、查看快照空间统计的正确性；
#    6、删除快照；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             # /mnt/volume1/snap/snap_13_0_3_6
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  # /snap/snap_13_0_3_6


def case():
    '''2>创建文件'''
    file_path = os.path.join(SNAP_TRUE_PATH, 'test_file1')
    cmd = 'dd if=%s of=%s bs=1M count=1500' % (snap_common.get_system_disk(snap_common.CLIENT_IP_1), file_path)
    common.run_command(snap_common.CLIENT_IP_1, cmd)
    file_size = 1500 * 1024 * 1024

    '''3> 创建快照'''
    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name, path)
    common.judge_rc(rc, 0, 'create_snapshot %s failed!!!' % snap_name)

    '''4> 文件中添加内容'''
    cmd = 'echo a >> %s' % file_path
    common.run_command(snap_common.SYSTEM_IP, cmd)
    log.info('waiting for 500s')
    time.sleep(500)

    '''5>查看快照空间统计的正确性'''
    snapshot_info = snap_common.get_snapshot_by_name(snap_name)
    actual_snap_size = int(snapshot_info['size'])

    obj_volume = common.Volume()
    rc, stdout = obj_volume.get_all_volumes()
    total_volumes = stdout['result']['volumes']
    for volume_info in total_volumes:
        name = volume_info['name']
        if name == snap_common.VOLUME_NAME:
            sys_deploy = volume_info['layout']['replicaMode']
            stripe_width = volume_info['layout']['stripe_width']
            disk_parity_num = volume_info['layout']['disk_parity_num']
            replica_num = volume_info['layout']['replica_num']

    '''获取期望的快照空间统计'''

    if sys_deploy is True:
        expect_snap_size = snap_common.replica_snap_size(file_size, replica_num, stripe_width)
    else:
        expect_snap_size = snap_common.erasure_snap_size(file_size, stripe_width, disk_parity_num)

    '''判断空间统计的正确性'''
    log.info('actual_snap_size = %d' % actual_snap_size)
    log.info('expect_snap_size = %d' % expect_snap_size)
    if actual_snap_size == expect_snap_size:
        log.info('snap size statistic is correct.')
    else:
        log.error('snap size statistic is wrong !!!')
        raise Exception('snap size statistic is wrong !!!')

    '''6>删除快照'''
    rc, stdout = snap_common.delete_snapshot_by_path(path)
    common.judge_rc(rc, 0, '%s delete failed!!!' % (path))

    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)