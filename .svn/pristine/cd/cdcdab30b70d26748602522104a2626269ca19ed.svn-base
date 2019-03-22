# -*-coding:utf-8 -*
import os
import time

import utils_path
import common
import snap_common
import log
import json
import quota_common
import prepare_clean
import quota_common

####################################################################################
#
# Author: liyao
# date 2018-05-25
# @summary：
#    对目录创建配额（逻辑空间，软阈值），宽限时间外创建非空文件，创建快照并查看回滚结果
# @steps:
#    1、对目录/mnt/volume1/snap/创建配额（逻辑空间，软阈值），配额限制为1G，宽限时间2分钟；
#    2、宽限时间内创建1.2G文件，宽限时间外尝试创建0.3G文件；
#    3、对目录创建快照；
#    4、超过宽限时间后，删除容量大小为500M的文件；
#    5、在目录/mnt/volume1/snap/下尝试写入400M的文件；
#    6、执行revert并查看回滚结果；
#    7、删除配额；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             # /mnt/volume1/snap/snap_13_0_8_8
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  # /snap/snap_13_0_8_8


def case():
    # 1> 对目录创建配额（逻辑空间，硬阈值）
    quota_path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, check_result = quota_common.create_one_quota(path=quota_path,
                                                     logical_quota_cal_type='QUOTA_LIMIT',
                                                     logical_soft_threshold=1048576000,
                                                     logical_grace_time=120)
    common.judge_rc(rc, 0, "create quota failed", exit_flag=False)

    rc, quota_id = quota_common.get_one_quota_id(path=quota_path,
                                                 u_or_g_type=quota_common.TYPE_CATALOG)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    # 2> 宽限时间内创建1.2G的文件
    tmp_name = 'test_liyao'
    for i in range(12):
        file_name = tmp_name + str(i)
        file_path = os.path.join(SNAP_TRUE_PATH, file_name)
        cmd = 'dd if=%s of=%s bs=1M count=100' % (snap_common.get_system_disk(snap_common.CLIENT_IP_1), file_path)
        common.run_command(snap_common.CLIENT_IP_1, cmd)

    log.info('waiting for 150s')
    time.sleep(150)

    # 宽限时间外尝试创建0.3G的文件
    extra_file_path = os.path.join(SNAP_TRUE_PATH, (tmp_name + '_extra'))
    cmd = 'dd if=%s of=%s bs=1M count=300' % (snap_common.get_system_disk(snap_common.CLIENT_IP_1), extra_file_path)
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    print stdout
    if rc == 0:
        log.error('logical quota worked incorrectly !!!')
        raise Exception('logical quota worked incorrectly !!!')

    # 3> 对目录创建快照
    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name)
        raise Exception('create_snapshot %s failed!!!' % snap_name)

    # 4> 删除目录下的500M文件
    for i in range(5):
        file_name = tmp_name + str(i)
        file_path = os.path.join(SNAP_TRUE_PATH, file_name)
        common.rm_exe(snap_common.CLIENT_IP_1, file_path)

    log.info('waiting for 10s')
    time.sleep(10)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")
    # 5> 目录下尝试创建总容量为400M的文件
    tmp_name_again = tmp_name + '_again'
    file_path = os.path.join(SNAP_TRUE_PATH, tmp_name_again)
    cmd = 'dd if=%s of=%s bs=1M count=400' % (snap_common.get_system_disk(snap_common.CLIENT_IP_1), file_path)
    # 执行完创建文件的操作后，检查目录下文件总空间;预期400M文件无法全部写入，目录下文件占用的总空间为配额限制的空间
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    log.info('waiting for 20s')
    time.sleep(20)
    cmd = 'du -BM %s' % SNAP_TRUE_PATH
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)

    stdout = stdout.split()
    expected_count = stdout[0]
    if expected_count != '1101M':
        log.error('logical quota worked incorrectly !!!')
        raise Exception('logical quota worked incorrectly !!!')

    # 6> 执行回滚操作
    snap_info = snap_common.get_snapshot_by_name(snap_name)
    snap_id = snap_info['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id)
    if rc != 0:
        log.error("revert snapshot %s failed!!!" % snap_name)
        raise Exception("revert snapshot %s failed!!!" % snap_name)
    snap_common.check_revert_finished(snap_id)

    cmd = 'ls %s | grep %s | wc -l' % (SNAP_TRUE_PATH, tmp_name)
    rc, stdout = common.run_command(snap_common.SYSTEM_IP, cmd)
    if stdout.strip() != '12':
        log.error('revert snapshot %s failed' % snap_name)
        raise Exception('revert snapshot %s failed' % snap_name)

    # 7> 删除配额
    rc, stdout = quota_common.delete_one_quota(quota_id)
    common.judge_rc(rc, 0, "delete quota failed")
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)