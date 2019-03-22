# -*-coding:utf-8 -*
import os
import time

import utils_path
import common
import snap_common
import log
import get_config
import prepare_clean
import quota_common

####################################################################################
#
# Author: liyao
# date 2018-07-13
# @summary：
#    测试配额文件数硬阈值设置与实际获取值是否相符
# @steps:
#    1、部署3节点集群；
#    2、对目录/mnt/volume1/defect_case/qc_729/test/创建文件数硬阈值为0的配额；
#    3、执行get_quota获取配额信息,并比较配额创建时的硬阈值与获取的硬阈值数值是否对应；
#    4、删除配额；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]        # 本脚本名字
DEFECT_PATH = get_config.get_one_defect_test_path()                # "/mnt/volume1/defect_case"
DEFECT_TRUE_PATH = os.path.join(DEFECT_PATH, FILE_NAME)            # "/mnt/volume1/defect_case/qc_690"
BASE_DEFECT_PATH = os.path.dirname(DEFECT_PATH)                    # "/mnt/volume1"
DEFECT_PATH_BASENAME = os.path.basename(DEFECT_PATH)               # "defect"
DEFECT_PATH_ABSPATH = os.path.abspath(DEFECT_PATH)                 # "/mnt/volume1/defect"
SNAPSHOT_PAHT = os.path.join(BASE_DEFECT_PATH, '.snapshot')      # "/mnt/volume1/.snapshot"
CREATE_SNAP_PATH = os.path.join(DEFECT_PATH_BASENAME, FILE_NAME)   # "/defect/qc_690"


def case():
    # 2> 对特定目录创建文件数硬阈值为0的配额
    test_dir = os.path.join(DEFECT_TRUE_PATH, 'test')
    common.mkdir_path(snap_common.CLIENT_IP_1, test_dir)

    # 创建文件数硬阈值为100的配额
    filenr_count = 0
    quota_path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH + '/test'
    rc, check_result = quota_common.create_one_quota(path=quota_path,
                                                     filenr_quota_cal_type='QUOTA_LIMIT',
                                                     filenr_hard_threshold=filenr_count)
    common.judge_rc(rc, 0, "create quota failed")

    # 检查配额是否生效
    rc, quota_id = quota_common.get_one_quota_id(path=quota_path,
                                                 u_or_g_type=quota_common.TYPE_CATALOG)
    rc = quota_common.wait_quota_work(quota_id)
    common.judge_rc(rc, 0, "get quota info failed")

    # 3> 执行get_quota获取配额信息
    rc, stdout = quota_common.get_one_quota_info(quota_id)
    actual_count = stdout['result']['quotas'][0]['filenr_hard_threshold']
    if filenr_count != actual_count:
        log.error('quota did not work well !!!')
        raise Exception('quota did not work well !!!')

    # 4> 删除../test/下的所有文件
    file_delete = os.path.join(test_dir, 'file_*')
    common.rm_exe(snap_common.CLIENT_IP_1, file_delete)

    log.info('waiting for 10s')
    time.sleep(10)
    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)