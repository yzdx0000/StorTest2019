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
# date 2018-07-26
# @summary：
#    更新配额成功（等待get_events接口完成）
# @steps:
#   1、部署3节点集群环境
#   2、对/mnt/volume1/snap/data_dir创建配额（参数输入正确，预期创建成功）
#   3、执行update_quota命令，输入正确参数（预期更新成功）
#   4、执行get_events查看配额更新结果显示
#   5、删除配额，清理环境
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
    '''函数主体'''
    '''获取当前时间'''
    cmd = 'date +%s'
    rc, stdout = common.run_command(SYSTEM_IP_1, cmd)
    start_time = int(stdout)   # 获取操作事件信息的起始时间

    '''2> 对/mnt/volume1/snap/data_dir创建配额（参数输入正确，预期创建成功）'''
    test_file = os.path.join(EVENT_TRUE_PATH, 'test_file')
    quota_common.creating_dir(SYSTEM_IP_0, EVENT_TRUE_PATH)
    cmd = 'dd if=/dev/zero of=%s bs=1M count=100' % test_file
    rc, stdout = common.run_command(SYSTEM_IP_0, cmd)
    if rc != 0:
        log.error('data directory create failed !!!')
        raise Exception('data directory create failed !!!')

    ''' 创建文件数配额'''
    quota_path = snap_common.VOLUME_NAME + ':/' + CREATE_EVENT_PATH
    rc, check_result = quota_common.create_one_quota(path=quota_path,
                                                     filenr_quota_cal_type='QUOTA_LIMIT',
                                                     filenr_hard_threshold=10)
    common.judge_rc(rc, 0, "create quota failed")

    log.info('waiting for 30s')
    time.sleep(30)

    ''' 3> 执行update_quota命令，输入正确参数（预期更新成功）'''
    rc, quota_id = quota_common.get_one_quota_id(path=quota_path,
                                                 u_or_g_type=quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get quota info failed")

    rc, stdout = quota_common.update_one_quota(id=quota_id,
                                               logical_quota_cal_type='QUOTA_LIMIT',
                                               logical_hard_threshold=1073741824)
    common.judge_rc(rc, 0, "update quota failed", exit_flag=False)
    if rc != 0:
        log.error('update quota failed !!!')
        raise Exception('update quota failed !!!')

    ''' 4> 执行get_events查看配额更新结果显示'''
    delay_time = event_common.DELAY_TIME
    log.info('waiting for %s' % delay_time)
    time.sleep(delay_time)

    code = '0x02060033'
    description = 'updating quota'
    event_common.check_events_result(start_time, code, description)

    ''' 5> 删除配额，清理环境'''
    rc, stdout = quota_common.delete_one_quota(quota_id)
    common.judge_rc(rc, 0, "delete quota failed")
    return


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=True)
    case()
    prepare_clean.test_clean()
    common.rm_exe(SYSTEM_IP_0, os.path.join(quota_common.BASE_QUOTA_PATH, 'event'))
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)