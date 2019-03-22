# -*-coding:utf-8 -*
import os

import utils_path
import common
import log
import get_config
import prepare_clean
import quota_common

####################################################################################
#
# Author: chenjinyu
# date: 2018-08-07
# @summary：
#    配额在rename后，创建旧目录配额提示存在
# @steps:
#    1、创建一个目录A
#    2、创建目录A文件数2000硬阈值配额
#    3、重命名该目录A-->B
#    4、再次创建目录A后仍对A创建配额
#    现象：创建失败，提示已经存在
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]               # 本脚本名字
DEFECT_PATH = get_config.get_one_defect_test_path()                       # DEFECT_PATH = "/mnt/volume1/defect_case
QUOTA_TRUE_PATH = os.path.join(DEFECT_PATH, FILE_NAME)                    # /mnt/volume1/defect_case/P300-2667
DEFECT_PATH_BASENAME = os.path.basename(DEFECT_PATH)                      # defect_case
QUOTA_CREATE_PATH = os.path.join(DEFECT_PATH_BASENAME, FILE_NAME)         # defect_case/P300-2667
OLD_NAME = 'A'  # 旧目录
NEW_NAME = 'B'  # 新目录


def case():
    log.info("case begin")

    ob_node = common.Node()
    log.info("1> 创建一个目录A")
    cmd = "cd %s; mkdir %s" % (QUOTA_TRUE_PATH, OLD_NAME)
    rc, stdout = common.run_command(quota_common.NOTE_IP_1, cmd)
    common.judge_rc(rc, 0, 'mkdir failed')

    log.info("2> 目录A创建文件数2000硬阈值的配额")
    quota_path1 = os.path.join(QUOTA_CREATE_PATH, OLD_NAME)
    rc, check_result1 = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_path1)),
                                                      filenr_quota_cal_type='QUOTA_LIMIT',
                                                      filenr_hard_threshold=2000)
    common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    if check_result1['err_no'] != 0:
        common.except_exit(info="detail_err_msg:%s" % check_result1['detail_err_msg'])

    log.info("3> 重命名A --> B")
    cmd = "cd %s; mv %s %s" % (QUOTA_TRUE_PATH, OLD_NAME, NEW_NAME)
    rc, stdout = common.run_command(quota_common.NOTE_IP_1, cmd)
    common.judge_rc(rc, 0, 'rename failed')

    log.info("4> 再次创建目录A后仍对A创建配额")
    cmd = "cd %s; mkdir %s" % (QUOTA_TRUE_PATH, OLD_NAME)
    rc, stdout = common.run_command(quota_common.NOTE_IP_1, cmd)
    common.judge_rc(rc, 0, 'mkdir failed')

    rc, check_result2 = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_path1)),
                                                      filenr_quota_cal_type='QUOTA_LIMIT',
                                                      filenr_hard_threshold=2000)
    common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    if check_result2['err_no'] != 0:
        common.except_exit(info="detail_err_msg:%s" % check_result2['detail_err_msg'])

    log.info("清除创建的配额")
    quota_path2 = os.path.join(QUOTA_CREATE_PATH, NEW_NAME)
    rc, check_result3 = quota_common.get_all_quota_info()
    common.judge_rc(rc, 0, "get quota failed")
    quota_id_lst = []
    for quota in check_result3['result']['quotas']:
        if quota['path'] == "%s:/%s" % (quota_common.VOLUME_NAME, quota_path1) or \
                        quota['path'] == "%s:/%s" % (quota_common.VOLUME_NAME, quota_path2):
            quota_id_lst.append(quota['id'])
    """删除配额"""
    for quota_id in quota_id_lst:
        quota_common.delete_single_quota_config(quota_id)
    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
