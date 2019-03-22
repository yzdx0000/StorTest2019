# -*-coding:utf-8 -*
import os
import time

import utils_path
import common
import snap_common
import log
import prepare_clean
import get_config
import quota_common
import event_common

####################################################################################
#
# Author: liyao
# date 2018-08-03
# @summary：
#    逻辑空间阈值告警
# @steps:
#   1、部署3节点集群环境
#   2、对目录/mnt/volume1/snap/alarms_5_2_4_3/创建逻辑空间配额（硬阈值>软阈值），预期创建成功
#   3、在此目录下创建文件，容量超过软阈值
#   4、grace_time内继续创建文件，尝试超过硬阈值（预期创建失败）
#   5、执行get_events，查看告警信息显示是否正确
#   6、删除配额，清理环境
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
EVENT_TRUE_PATH = os.path.join(event_common.EVENT_TEST_PATH, FILE_NAME)
DATA_DIR = os.path.join(EVENT_TRUE_PATH, 'data_dir')                  # /mnt/volume1/event/events_5_3_1_11/data_dir/
CREATE_EVENT_PATH = os.path.join('event', FILE_NAME)                   # /event/events_5_3_6_21
SYSTEM_IP_0 = get_config.get_parastor_ip(0)
SYSTEM_IP_1 = get_config.get_parastor_ip(1)
SYSTEM_IP_2 = get_config.get_parastor_ip(2)


def case():
    '''函数执行主体'''
    '''获取当前时间'''
    cmd = 'date +%s'
    rc, stdout = common.run_command(SYSTEM_IP_1, cmd)
    start_time = int(stdout) - 30   # 获取操作事件信息的起始时间

    '''2> 对目录/mnt/volume1/snap/alarms_5_2_4_3/创建逻辑空间配额（硬阈值>软阈值），预期创建成功'''
    quota_path = snap_common.VOLUME_NAME + ':/' + CREATE_EVENT_PATH
    logical_hard_threshold = 1048576000
    logical_soft_threshold = 524288000
    rc, check_result = quota_common.create_one_quota(path=quota_path,
                                                     logical_quota_cal_type='QUOTA_LIMIT',
                                                     logical_hard_threshold=logical_hard_threshold,
                                                     logical_soft_threshold=logical_soft_threshold,
                                                     logical_grace_time=300)
    common.judge_rc(rc, 0, "create quota failed")

    '''3> 在此目录下创建文件，容量超过软阈值'''
    for i in range(10):
        test_file = os.path.join(EVENT_TRUE_PATH, 'test_file_%d' % i)
        cmd = 'dd if=/dev/zero of=%s bs=1M count=100' % test_file
        common.run_command(SYSTEM_IP_2, cmd)
        log.info('waiting for 5s')
        time.sleep(5)

    '''4> grace_time内继续创建文件，尝试超过硬阈值（预期创建失败）'''
    test_file_again = os.path.join(EVENT_TRUE_PATH, 'test_file_again')
    cmd = 'echo 11111 > %s' % test_file_again
    rc, stdout = common.run_command(SYSTEM_IP_2, cmd)
    if 0 == rc:
        log.error('quota did not work well !!!')
        raise Exception('quota did not work well !!!')

    code = '0x01050001'
    description = 'quota warning'
    event_common.check_alarms_result(code, description)

    '''6> 删除配额，清理环境'''
    rc, quota_id = quota_common.get_one_quota_id(path=quota_path,
                                                 u_or_g_type=quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get quota info failed")
    rc, stdout = quota_common.delete_one_quota(quota_id)
    common.judge_rc(rc, 0, "delete quota failed")
    log.info('waiting for 10s')
    time.sleep(10)
    return


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=True)
    quota_common.creating_dir(SYSTEM_IP_0, EVENT_TRUE_PATH)
    case()
    prepare_clean.test_clean()
    common.rm_exe(SYSTEM_IP_0, os.path.join(quota_common.BASE_QUOTA_PATH, 'event'))
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)