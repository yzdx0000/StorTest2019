# -*-coding:utf-8 -*
import os
import time

import utils_path
import common
import snap_common
import log
import get_config
import prepare_clean
import json
import quota_common

####################################################################################
#
# Author: liyao
# date 2018-07-13
# @summary：
#    查看配额目录下创建的文件数与filenr_used_nr是否对应
# @steps:
#    1、部署3节点集群；
#    2、对/mnt/volume1/defect_case/qc_663/test/目录创建文件数硬阈值配额10,逻辑空间硬阈值100M；
#    3、配额目录下写入小于硬阈值的文件；
#    4、统计文件数目及总容量并与filenr_used_nr比较；
#    5、尝试写入文件至超过硬阈值；
#    6、统计文件数目及总容量并与filenr_used_nr比较
#    7、删除配额
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]        # 本脚本名字
DEFECT_PATH = get_config.get_one_defect_test_path()                # "/mnt/volume1/defect_case"
DEFECT_TRUE_PATH = os.path.join(DEFECT_PATH, FILE_NAME)            # "/mnt/volume1/defect_case/qc_663"
BASE_DEFECT_PATH = os.path.dirname(DEFECT_PATH)                    # "/mnt/volume1"
DEFECT_PATH_BASENAME = os.path.basename(DEFECT_PATH)               # "defect"
DEFECT_PATH_ABSPATH = os.path.abspath(DEFECT_PATH)                 # "/mnt/volume1/defect"
SNAPSHOT_PAHT = os.path.join(BASE_DEFECT_PATH, '.snapshot')      # "/mnt/volume1/.snapshot"
CREATE_SNAP_PATH = os.path.join(DEFECT_PATH_BASENAME, FILE_NAME)   # "/defect/qc_663"


def cmp_filenr(actual_filenr, actual_logical):
    quota_path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH + '/test'
    rc, quota_id = quota_common.get_one_quota_id(path=quota_path,
                                                 u_or_g_type=quota_common.TYPE_CATALOG)
    rc, stdout = quota_common.get_one_quota_info(quota_id)
    quota_filenr = stdout['result']['quotas'][0]['filenr_used_nr']
    quota_logical = stdout['result']['quotas'][0]['logical_used_capacity']

    log.info(quota_filenr)
    log.info(quota_logical)

    if actual_filenr != quota_filenr or actual_logical != quota_logical:
        log.error('quota displayed wrong !!!')
        raise Exception('quota displayed wrong !!!')
    return


def case():
    # 2> 对特定目录创建配额
    test_dir = os.path.join(DEFECT_TRUE_PATH, 'test')
    common.mkdir_path(snap_common.CLIENT_IP_1, test_dir)

    # 创建配额
    quota_path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH + '/test'
    rc, check_result = quota_common.create_one_quota(path=quota_path,
                                                     filenr_quota_cal_type='QUOTA_LIMIT',
                                                     filenr_hard_threshold=10,
                                                     logical_quota_cal_type='QUOTA_LIMIT',
                                                     logical_hard_threshold=104857600)
    common.judge_rc(rc, 0, "create quota failed")

    # 检查配额是否生效
    rc, quota_id = quota_common.get_one_quota_id(path=quota_path,
                                                 u_or_g_type=quota_common.TYPE_CATALOG)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    # 3> 配额目录下写入小于硬阈值的文件
    actual_filenr = 5
    for i in range(actual_filenr):
        test_file = os.path.join(test_dir, 'file_%d' % i)
        cmd = 'dd if=%s of=%s bs=1M count=10' % (snap_common.get_system_disk(common.SYSTEM_IP), test_file)
        rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
        if rc != 0:
            log.error('quota did not work well !!!')
            raise Exception('quota did not work well !!!')

    log.info('waiting for 20s')
    time.sleep(20)

    # 4> 统计文件数目并与filenr_used_nr比较
    actual_filenr = quota_common.dir_total_inodes(common.SYSTEM_IP, test_dir)
    actual_logical = quota_common.dir_total_file_size(common.SYSTEM_IP, test_dir)
    """
    cmd = "ls -l %s |grep '^-'|wc -l" % test_dir
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    actual_filenr = int(stdout)
    cmd = 'du -s %s' % test_dir
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    actual_logical = stdout.strip().split()[0]
    print (actual_logical)
    cmd = 'expr \( %s \- 4 \) \* 1024' % actual_logical
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    actual_logical = int(stdout)
    """
    log.info('waiting for 5s')
    time.sleep(5)

    cmp_filenr(actual_filenr, actual_logical)

    # 5> 尝试写入文件至超过硬阈值
    for i in range(9):
        test_file_again = os.path.join(test_dir, 'file_again_%d' % i)
        cmd = 'dd if=%s of=%s bs=1M count=10' % (snap_common.get_system_disk(common.SYSTEM_IP), test_file_again)
        rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
        if rc != 0:
            log.info('filenr reached quota limitation !!!')
            break
    log.info('waiting for 20s')
    time.sleep(20)

    # 6> 统计文件数目并与filenr_used_nr比较

    actual_filenr = quota_common.dir_total_inodes(common.SYSTEM_IP, test_dir)
    actual_logical = quota_common.dir_total_file_size(common.SYSTEM_IP, test_dir)
    """
    cmd = "ls -l %s |grep '^-'|wc -l" % test_dir
    rc, stdout = common.run_command(common.SYSTEM_IP, cmd)
    actual_filenr = int(stdout)
    print (actual_filenr)
    cmd = 'du -s %s' % test_dir
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    actual_logical = stdout.strip().split()[0]
    print (actual_logical)
    cmd = 'expr \( %s \- 4 \) \* 1024' % actual_logical
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    actual_logical = int(stdout)
    """
    cmp_filenr(actual_filenr, actual_logical)

    # 7> 删除配额
    rc, stdout = quota_common.delete_one_quota(quota_id)
    common.judge_rc(rc, 0, "delete quota failed")
    return


def main():
    quota_common.delete_all_quota_config()
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)