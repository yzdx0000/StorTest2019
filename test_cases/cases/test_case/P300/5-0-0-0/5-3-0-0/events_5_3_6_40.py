# -*-coding:utf-8 -*
import os
import time
import random

import utils_path
import common
import snap_common
import log
import prepare_clean
import get_config
import event_common
import quota_common

####################################################################################
#
# Author: liyao
# date 2018-07-27
# @summary：
#    回滚快照失败（等待get_events接口完成）
# @steps:
#   1、部署3节点集群环境
#   2、在/mnt/volume1/snap/snap_revert_success/目录下创建数据
#   3、对/mnt/volume1/snap/snap_revert_success/创建快照（参数输入正确，预期成功）
#   4、修改上述目录下的内容，执行revert_snapshot回滚快照，数据错误参数（预期回滚失败）
#   5、执行get_events查看回滚操作显示信息是否正确
#   6、删除快照，清理环境
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
    cmd = 'date +%s'
    rc, stdout = common.run_command(SYSTEM_IP_1, cmd)
    start_time = int(stdout)   # 获取操作事件信息的起始时间

    ''' 2> 在/mnt/volume1/snap/snap_create_success/目录下创建数据'''
    for i in range(10):
        test_file = os.path.join(EVENT_TRUE_PATH, 'test_file_%d' % i)
        cmd = 'dd if=/dev/zero of=%s bs=1M count=10' % test_file
        common.run_command(SYSTEM_IP_0, cmd)

    log.info('waiting for 10s')
    time.sleep(10)

    ''' 3> 对/mnt/volume1/snap/snap_create_success/创建快照（参数输入正确，预期成功）'''
    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_EVENT_PATH
    rc, stdout = snap_common.create_snapshot(snap_name, path)
    if rc != 0:
        log.error('snapshot %s create failed !!!' % snap_name)
        raise Exception('snapshot %s create failed !!!' % snap_name)
    log.info('waiting for 10s')
    time.sleep(10)

    ''' 4> 修改上述目录下的内容，执行revert_snapshot回滚快照，输入错误参数（预期回滚失败）'''
    file_change = os.path.join(EVENT_TRUE_PATH, 'file_change')
    cmd = 'echo 11111 > %s' % file_change
    common.run_command(SYSTEM_IP_1, cmd)

    rc, stdout = snap_common.revert_snapshot_by_id(0)
    if rc != 0:
        log.error('snapshot %s revert failed !!!' % snap_name)

    ''' 5> 执行get_events查看回滚操作显示信息是否正确'''
    delay_time = event_common.DELAY_TIME
    log.info('waiting for %s' % delay_time)
    time.sleep(delay_time)

    code = '0x02060048'
    description = 'reverting snapshot'
    event_common.check_events_result(start_time, code, description)

    ''' 6> 删除快照，清理环境'''
    rc, stdout = snap_common.delete_snapshot_by_name(FILE_NAME)
    if 0 != rc:
        log.error('%s delete failed!!!' % FILE_NAME)
        raise Exception('%s delete failed!!!' % FILE_NAME)

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