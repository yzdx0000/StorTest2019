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
# date 2018-07-12
# @summary：
#    删除配额目录下已写入额文件后再写入文件
# @steps:
#    1、部署3节点集群；
#    2、逻辑配额硬阈值100M；
#    3、客户端尝试写入200M（预期只能写入100M）；
#    4、删除所有文件；
#    5、再次尝试写入300M文件（预期只能写入100M）；
#    6、删除配额；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]        # 本脚本名字
DEFECT_PATH = get_config.get_one_defect_test_path()                # "/mnt/volume1/defect_case"
DEFECT_TRUE_PATH = os.path.join(DEFECT_PATH, FILE_NAME)            # "/mnt/volume1/defect_case/qc_795"
BASE_DEFECT_PATH = os.path.dirname(DEFECT_PATH)                    # "/mnt/volume1"
DEFECT_PATH_BASENAME = os.path.basename(DEFECT_PATH)               # "defect"
DEFECT_PATH_ABSPATH = os.path.abspath(DEFECT_PATH)                 # "/mnt/volume1/defect"
SNAPSHOT_PAHT = os.path.join(BASE_DEFECT_PATH, '.snapshot')      # "/mnt/volume1/.snapshot"
CREATE_SNAP_PATH = os.path.join(DEFECT_PATH_BASENAME, FILE_NAME)   # "/defect/qc_795"


def case():
    # 2> 对目录/mnt/volume1/defect_case/qc_795/test/创建配额
    # 创建上述目录
    test_dir = os.path.join(DEFECT_TRUE_PATH, 'test')
    common.mkdir_path(common.SYSTEM_IP, test_dir)

    # 创建逻辑硬阈值配额
    quota_path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH + '/test'
    rc, check_result = quota_common.create_one_quota(path=quota_path,
                                                     logical_quota_cal_type='QUOTA_LIMIT',
                                                     logical_hard_threshold=104857600)
    common.judge_rc(rc, 0, "create quota failed")

    # 检查配额是否生效
    rc, quota_id = quota_common.get_one_quota_id(path=quota_path,
                                                 u_or_g_type=quota_common.TYPE_CATALOG)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    # 3> 客户端尝试创建200M文件
    for i in range(5):
        test_file = os.path.join(test_dir, 'file_%d' % i)
        cmd = 'dd if=%s of=%s bs=1M count=20' % (snap_common.get_system_disk(common.SYSTEM_IP), test_file)
        common.run_command(snap_common.CLIENT_IP_1, cmd)
        log.info('waiting for 5s')
        time.sleep(5)

    i += 1
    test_file = os.path.join(test_dir, 'file_%d' % i)
    cmd = 'dd if=%s of=%s bs=1M count=20' % (snap_common.get_system_disk(common.SYSTEM_IP), test_file)
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if rc == 0:
        log.error('quota did not work well !!!')
        raise Exception('quota did not work well !!!')

    # 4> 删除../test/目录下的所有文件
    file_delete = test_dir + '/file_*'
    common.rm_exe(snap_common.CLIENT_IP_2, file_delete)
    log.info('waiting for 10s')
    time.sleep(10)

    # 5> 尝试写入超过100M的文件
    for i in range(5):
        test_file = os.path.join(test_dir, 'file_%d' % i)
        cmd = 'dd if=%s of=%s bs=1M count=20' % (snap_common.get_system_disk(common.SYSTEM_IP), test_file)
        common.run_command(snap_common.CLIENT_IP_1, cmd)
        log.info('waiting for 5s')
        time.sleep(5)

    i = i + 1
    test_file = os.path.join(test_dir, 'file_%d' % i)
    cmd = 'dd if=%s of=%s bs=1M count=20' % (snap_common.get_system_disk(common.SYSTEM_IP), test_file)
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if rc == 0:
        log.error('quota did not work well !!!')
        raise Exception('quota did not work well !!!')

    # 6> 删除配额
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