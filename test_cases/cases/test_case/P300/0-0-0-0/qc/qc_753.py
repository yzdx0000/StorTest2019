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
#    2、在目录/mnt/volume1/defect_case/qc_753/test/下创建10个、总容量为100M的文件；
#    3、对上述目录创建文件数软阈值为5、逻辑空间软阈值为50M，grace_time均为60s（此场景中，配额生成时文件数与容量即超过软阈值）；
#    4、执行get_quota，分别获取filenr_soft_threshold和logical_soft_threshold对应的over_time；
#    5、等待60s后在同一系统节点获取当前时间，与上述over_time进行比较（预期为over_time小于系统当前时间）；
#    6、删除配额
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
    # 2> 在目录/mnt/volume1/defect_case/qc_753/test/下创建10个、总容量为100M的文件
    # 创建目录../test/
    test_dir = os.path.join(DEFECT_TRUE_PATH, 'test')
    common.mkdir_path(snap_common.CLIENT_IP_1, test_dir)

    # 创建10个，共100M文件
    for i in range(10):
        test_file = os.path.join(test_dir, 'test_file_%d' % i)
        cmd = 'dd if=%s of=%s bs=1M count=10' % (snap_common.get_system_disk(snap_common.CLIENT_IP_1), test_file)
        common.run_command(snap_common.CLIENT_IP_1, cmd)
        log.info('waiting for 5s')
        time.sleep(5)

    # 3> 对上述目录创建文件数、逻辑空间软阈值，grace_time均为60s
    quota_path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH + '/test'
    rc, check_result = quota_common.create_one_quota(path=quota_path,
                                                     logical_quota_cal_type='QUOTA_LIMIT',
                                                     logical_soft_threshold=52428800,
                                                     logical_grace_time=60,
                                                     filenr_quota_cal_type='QUOTA_LIMIT',
                                                     filenr_soft_threshold=5,
                                                     filenr_grace_time=60)
    common.judge_rc(rc, 0, "create quota failed")

    # 检查配额是否生效
    rc, stdout = common.get_quota('path', quota_path)
    stdout = json.loads(stdout)
    quota_state = stdout['result']['quotas'][0]['state']

    while quota_state != 'QUOTA_WORK':
        log.info('waiting for 10s')
        time.sleep(10)
        rc, stdout = common.get_quota('path', quota_path)
        stdout = json.loads(stdout)
        quota_state = stdout['result']['quotas'][0]['state']

    # 4> 执行get_quota，分别获取filenr_soft_threshold和logical_soft_threshold对应的over_time

    rc, stdout = common.get_quota('path', quota_path)
    stdout = json.loads(stdout)
    filenr_over_time = stdout['result']['quotas'][0]['filenr_soft_threshold_over_time'].split(':')[1]
    print(filenr_over_time)
    logical_over_time = stdout['result']['quotas'][0]['logical_soft_threshold_over_time'].split(':')[1]
    print(logical_over_time)

    # 5> 等待60s后在同一系统节点获取当前时间，与上述over_time进行比较
    log.info('waiting for 60s')
    time.sleep(60)

    cmd = 'date'
    rc, stdout = common.run_command(common.SYSTEM_IP, cmd)
    sys_time = stdout.split(':')[1]

    # 系统（同一节点）当前时间与over_time相比较
    if (filenr_over_time < sys_time) and (logical_over_time < sys_time):
        log.info('over_time is filled correctly.')
    else:
        log.error('over_time is filled wrong !!!')
        raise Exception('over_time is filled wrong !!!')

    # 6> 清理环境，删除配额
    rc, stdout = common.get_quota('path', quota_path)
    stdout = json.loads(stdout)
    quota_id = stdout['result']['quotas'][0]['id']
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
