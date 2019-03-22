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
# date 2018-05-23
# @summary：
#    对目录创建配额（文件数，硬阈值），配额限制等于初始文件数，创建快照并查看回滚结果
# @steps:
#    1、在/mnt/volume1/snap/下创建100个非空文件；
#    2、对上述目录创建filenr为100的硬阈值；
#    3、对目录创建快照；
#    4、删除目录下的50个文件；
#    5、在目录/mnt/volume1/snap/下尝试创建60个文件；
#    6、执行revert并查看回滚结果；
#    7、删除配额；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             # /mnt/volume1/snap/snap_13_0_8_1
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  # /snap/snap_13_0_8_1


def case():
    # 1> 目录下创建100个非空文件
    tem_name = 'test_liyao'
    for i in range(100):
        file_name = tem_name + str(i)
        file_path = os.path.join(SNAP_TRUE_PATH, file_name)
        cmd = 'echo 111 > %s' % file_path
        common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 2> 对目录创建配额（文件数，硬阈值）
    quota_path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, check_result = quota_common.create_one_quota(path=quota_path,
                                                     filenr_quota_cal_type='QUOTA_LIMIT',
                                                     filenr_hard_threshold=100)
    common.judge_rc(rc, 0, "create quota failed", exit_flag=False)

    rc, quota_id = quota_common.get_one_quota_id(path=quota_path,
                                                 u_or_g_type=quota_common.TYPE_CATALOG)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    # 3> 对目录创建快照
    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name)
        raise Exception('create_snapshot %s failed!!!' % snap_name)

    # 4> 删除目录下的50个文件
    for i in range(50):
        file_name = tem_name + str(i)
        file_path = os.path.join(SNAP_TRUE_PATH, file_name)
        common.rm_exe(snap_common.CLIENT_IP_1, file_path)

    # 5> 目录下尝试创建60个文件
    tem_again_name = tem_name + '_again'
    for i in range(60):
        file_name = tem_again_name + str(i)
        file_path = os.path.join(SNAP_TRUE_PATH, file_name)
        cmd = 'echo 222 > %s' % file_path
        rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
        if 0 != rc:
            count = i + 1
            specific_file = tem_again_name + str(count)
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

    cmd = 'ls %s | grep %s | wc -l' % (SNAP_TRUE_PATH, tem_name)
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if stdout.strip() != '100':
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