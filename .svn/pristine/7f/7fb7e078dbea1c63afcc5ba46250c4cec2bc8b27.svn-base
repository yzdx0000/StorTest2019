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
#    2、对/mnt/volume1/defect_case/qc_663/test/目录创建1G的逻辑空间配额；
#    3、配额目录下写入1000M文件；
#    4、在目录下继续创建小文件（预期成功）；
#    5、删除配额
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


def case():
    # 2> 对/mnt/volume1/defect_case/qc_663/test/目录创建1G的逻辑空间配额
    test_dir = os.path.join(DEFECT_TRUE_PATH, 'test')
    common.mkdir_path(snap_common.CLIENT_IP_1, test_dir)

    quota_path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH + '/test'
    rc, check_result = quota_common.create_one_quota(path=quota_path,
                                                     logical_quota_cal_type='QUOTA_LIMIT',
                                                     logical_hard_threshold=1073741824)
    common.judge_rc(rc, 0, "create quota failed")

    # 检查配额是否生效
    rc, quota_id = quota_common.get_one_quota_id(path=quota_path,
                                                 u_or_g_type=quota_common.TYPE_CATALOG)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    # 3> 上述目录下创建1000M文件
    for i in range(10):
        test_file = os.path.join(test_dir, 'file_%d' % i)
        cmd = 'dd if=%s of=%s bs=1M count=100' % (snap_common.get_system_disk(snap_common.SYSTEM_IP), test_file)
        rc, stdou = common.run_command(snap_common.CLIENT_IP_2, cmd)
        if rc != 0:
            log.error('quota did not work well !!!')
            raise Exception('quota did not work well !!!')

    # 4> 在目录下继续创建小文件（预期成功）
    test_file_again = os.path.join(test_dir, 'file_again')
    cmd = 'echo 11111 > %s' % test_file_again
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if rc != 0:
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