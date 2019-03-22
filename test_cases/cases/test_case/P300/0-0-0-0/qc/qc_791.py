# -*-coding:utf-8 -*
import os
import time

import utils_path
import common
import snap_common
import log
import quota_common
import get_config
import prepare_clean
import json

####################################################################################
#
# Author: liyao
# date 2018-07-12
# @summary：
#    配额硬阈值存在限制不住的情况
# @steps:
#    1、部署3节点集群；
#    2、对目录/mnt/volume1/defect_case/qc_791/test创建硬阈值为100的文件数配额；
#    3、写入105个文件验证配额限制是否成功；
#    4、删除上述目录；
#    5、创建同样的目录，并在此目录下写入105个文件（预期写入成功）；
#    6、删除配额
#    7、创建配额，硬阈值文件数100
#    8、在/mnt/volume1/defect_case/qc_791/test目录下创建一个文件（预期创建失败）
#    9、清理环境，删除配额
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]        # 本脚本名字
DEFECT_PATH = get_config.get_one_defect_test_path()                # "/mnt/volume1/defect_case"
DEFECT_TRUE_PATH = os.path.join(DEFECT_PATH, FILE_NAME)            # "/mnt/volume1/defect_case/qc_791"
BASE_DEFECT_PATH = os.path.dirname(DEFECT_PATH)                    # "/mnt/volume1"
DEFECT_PATH_BASENAME = os.path.basename(DEFECT_PATH)               # "/defect_case"
DEFECT_PATH_ABSPATH = os.path.abspath(DEFECT_PATH)                 # "/mnt/volume1/defect_case"
SNAPSHOT_PAHT = os.path.join(BASE_DEFECT_PATH, '.snapshot')      # "/mnt/volume1/.snapshot"
CREATE_SNAP_PATH = os.path.join(DEFECT_PATH_BASENAME, FILE_NAME)   # "/defect_case/qc_791"


def case():
    # 2> 对目录/mnt/volume1/defect_case/qc_791/test/创建文件数硬阈值为100的配额
    # 创建目录/test/
    test_dir = os.path.join(DEFECT_TRUE_PATH, 'test')
    common.mkdir_path(snap_common.CLIENT_IP_1, test_dir)

    # 创建配额
    quota_path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH + '/test'
    rc, check_result = quota_common.create_one_quota(path=quota_path,
                                                     filenr_quota_cal_type='QUOTA_LIMIT',
                                                     filenr_hard_threshold=100)
    common.judge_rc(rc, 0, "create quota failed")

    # 检查配额是否生效
    rc, quota_id = quota_common.get_one_quota_id(path=quota_path,
                                                 u_or_g_type=quota_common.TYPE_CATALOG)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    # 3> 在目录../test下首先创建100个文件，再创始创建第101个文件
    for i in range(100):
        test_file = os.path.join(test_dir, 'test_file_%d' % i)
        cmd = 'echo 111111 > %s' % test_file
        rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
        if rc != 0:
            log.error('file creating failed !!!')
            raise Exception('file creating failed !!!')
    test_file = os.path.join(test_dir, 'test_file_101')
    cmd = 'echo 111111 > %s' % test_file
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if rc == 0:
        log.error('quota did not work well !!!')
        raise Exception('quota did not work well !!!')

    # 4> 删除配额对应的目录
    common.rm_exe(common.SYSTEM_IP, test_dir)
    log.info('waiting for 10s')
    time.sleep(10)

    # 5> 创建同样的目录，并在此目录下写入105个文件（预期写入成功）
    cmd = 'mkdir %s' % test_dir
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if rc != 0:
        log.error('%s creating failed !!!' % test_dir)
        raise Exception('%s creating failed !!!' % test_dir)

    for i in range(105):
        test_file = os.path.join(test_dir, 'test_file_again_%d' % i)
        cmd = 'echo 222222 > %s' % test_file
        rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
        if rc != 0:
            log.error('quota did not work well !!!')
            raise Exception('quota did not work well !!!')

    # 6> 删除配额
    rc, stdout = quota_common.delete_one_quota(quota_id)
    common.judge_rc(rc, 0, "delete quota failed")
    log.info('waiting for 10s')
    time.sleep(10)

    # 7> 相同路径下创建硬阈值文件数为100的配额
    rc, check_result = quota_common.create_one_quota(path=quota_path,
                                                     filenr_quota_cal_type='QUOTA_LIMIT',
                                                     filenr_hard_threshold=100)
    common.judge_rc(rc, 0, "create quota failed")

    # 检查配额是否生效
    rc, quota_id = quota_common.get_one_quota_id(path=quota_path,
                                                 u_or_g_type=quota_common.TYPE_CATALOG)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    log.info('waiting for 10s')
    time.sleep(10)

    # 8> 配额目录下尝试创建文件（预期失败）
    test_file = os.path.join(test_dir, 'test_try')
    cmd = 'touch %s' % test_file
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if rc == 0:
        log.error('quota did not work well !!!')
        raise Exception('quota did not work well !!!')

    # 9> 清理环境，删除配额
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