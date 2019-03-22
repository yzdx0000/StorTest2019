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
# date 2018-05-24
# @summary：
#    对目录创建配额（文件数，软阈值），宽限时间外创建非空文件，创建快照并查看回滚结果
# @steps:
#    1、对目录/mnt/volume1/snap/创建配额（文件数，软阈值），配额限制为100，宽限时间2分钟；
#    2、在宽限时间内创建120个文件，宽限时间外尝试创建30个文件；
#    3、对目录创建快照；
#    4、删除50个文件；
#    5、在/mnt/volume1/snap/目录下继续尝试创建50个文件；
#    6、执行revert并查看回滚结果；
#    7、删除配额；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             # /mnt/volume1/snap/snap_13_0_8_4
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  # /snap/snap_13_0_8_4


def case():
    # 1> 对目录创建配额（文件数，软阈值）
    quota_path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, check_result = quota_common.create_one_quota(path=quota_path,
                                                     filenr_quota_cal_type='QUOTA_LIMIT',
                                                     filenr_soft_threshold=100,
                                                     filenr_grace_time=120)
    common.judge_rc(rc, 0, "create quota failed", exit_flag=False)

    rc, quota_id = quota_common.get_one_quota_id(path=quota_path,
                                                 u_or_g_type=quota_common.TYPE_CATALOG)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    # 2> 目录下创建120个非空文件
    tmp_name = 'test_liyao'
    for i in range(120):
        file_name = tmp_name + str(i)
        file_path = os.path.join(SNAP_TRUE_PATH, file_name)
        cmd = 'echo 111 > %s' % file_path
        common.run_command(snap_common.CLIENT_IP_1, cmd)

    log.info('waiting for 140s')
    time.sleep(140)

    # 尝试创建30个文件
    tmp_name_again = tmp_name + '_again'
    for i in range(30):
        file_name = tmp_name_again + str(i)
        file_path = os.path.join(SNAP_TRUE_PATH, file_name)
        cmd = 'echo 222 > %s' % file_path
        rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
        if 0 != rc:
            count = i + 1
            specific_file = tmp_name_again + str(count)
            print specific_file
            if count != 1:
                log.error('quota limitation is incorrect !!!')
                raise Exception('quota limitation is incorrect !!!')
            else:
                break

    # 3> 对目录创建快照
    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name)
        raise Exception('create_snapshot %s failed!!!' % snap_name)

    # 4> 删除目录下的50个文件
    for i in range(50):
        file_name = tmp_name + str(i)
        file_path = os.path.join(SNAP_TRUE_PATH, file_name)
        common.rm_exe(snap_common.CLIENT_IP_1, file_path)

    # 5> 目录下尝试创建50个文件
    for i in range(50):
        file_name = tmp_name_again + str(i)
        file_path = os.path.join(SNAP_TRUE_PATH, file_name)
        cmd = 'echo 222 > %s' % file_path
        rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
        if 0 != rc:
            count = i + 1
            specific_file = tmp_name_again + str(count)
            print specific_file
            if count != 31:
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

    cmd = 'ls %s | grep %s | wc -l' % (SNAP_TRUE_PATH, tmp_name)
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if stdout.strip() != '120':
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