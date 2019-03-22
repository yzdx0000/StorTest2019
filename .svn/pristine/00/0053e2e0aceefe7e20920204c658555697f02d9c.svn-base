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
# date 2018-07-14
# @summary：
#    测试ls操作对文件数配额生效是否有影响
# @steps:
#    1、部署3节点集群；
#    2、对特定目录创建文件数硬阈值为100的配额；
#    3、在配额目录下尝试写入超过100个文件（预期超过部分不能写入）；
#    4、执行ls操作后，再次尝试在目录下创建文件；
#    5、删除配额
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]        # 本脚本名字
DEFECT_PATH = get_config.get_one_defect_test_path()                # "/mnt/volume1/defect_case"
DEFECT_TRUE_PATH = os.path.join(DEFECT_PATH, FILE_NAME)            # "/mnt/volume1/defect_case/qc_636"
BASE_DEFECT_PATH = os.path.dirname(DEFECT_PATH)                    # "/mnt/volume1"
DEFECT_PATH_BASENAME = os.path.basename(DEFECT_PATH)               # "defect"
DEFECT_PATH_ABSPATH = os.path.abspath(DEFECT_PATH)                 # "/mnt/volume1/defect"
SNAPSHOT_PAHT = os.path.join(BASE_DEFECT_PATH, '.snapshot')      # "/mnt/volume1/.snapshot"
CREATE_SNAP_PATH = os.path.join(DEFECT_PATH_BASENAME, FILE_NAME)   # "/defect/qc_636"


def case():
    # 2> 对特定目录创建文件数硬阈值为100的配额
    test_dir = os.path.join(DEFECT_TRUE_PATH, 'test')
    common.mkdir_path(snap_common.CLIENT_IP_3, test_dir)

    quota_path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH + '/test'
    filenr_threshold = 100
    rc, check_result = quota_common.create_one_quota(path=quota_path,
                                                     filenr_quota_cal_type='QUOTA_LIMIT',
                                                     filenr_hard_threshold=filenr_threshold)
    common.judge_rc(rc, 0, "create quota failed")

    # 检查配额是否生效
    rc, quota_id = quota_common.get_one_quota_id(path=quota_path,
                                                 u_or_g_type=quota_common.TYPE_CATALOG)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    # 3> 在配额目录下尝试写入超过100个文件（预期超过部分不能写入）
    for i in range(120):
        test_file = os.path.join(test_dir, 'file_%d' % i)
        cmd = 'echo 11111 > %s' % test_file
        rc, stdout = common.run_command(snap_common.CLIENT_IP_2, cmd)
        if rc != 0:
            log.info('quota limitation is reached !!!')
            break

    # 4> 执行ls操作后，再次尝试在目录下创建文件
    cmd = 'ls -l %s |grep "^-"|wc -l' % test_dir
    rc, stdout = common.run_command(snap_common.CLIENT_IP_3, cmd)
    total_filenr = int(stdout)
    if total_filenr != filenr_threshold:
        log.error('quota did not work well !!!')
        raise Exception('quota did not work well !!!')

    cmd = 'echo 22222 > %s' % test_dir
    rc, stdout = common.run_command(common.SYSTEM_IP, cmd)
    if rc == 0:
        log.error('quota did not work well !!!')
        raise Exception('quota did not work well !!!')

    # 5> 删除配额
    rc, stdout = quota_common.delete_one_quota(quota_id)
    common.judge_rc(rc, 0, "delete quota failed")
    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)