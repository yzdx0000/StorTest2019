# -*-coding:utf-8 -*
from multiprocessing import Process, Value
import os
import time

import utils_path
import tool_use
import common
import quota_common
import log

##########################################
#
# Author: baorb
# date 2017-08-21
# @summary：
#    配额功能:目录读写业务中，配额策略创建删除
# @steps:
#    1、某个目录下通过vdbench循环读写操作；
#    2、给这个目录循环创建、修改、删除目录配额；
#
# @changelog：
##########################################

alive = Value('b', False)


def quota_operat(quota_path):
    while alive.value:
        time.sleep(10)
        rc, result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_path)),
                                                   filenr_quota_cal_type='QUOTA_LIMIT',
                                                   filenr_hard_threshold=10000,
                                                   logical_quota_cal_type='QUOTA_LIMIT',
                                                   logical_hard_threshold=2147483648)
        common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)
        if result['err_no'] != 0:
            log.error('create_quota failed!!!')
            raise Exception('create_quota failed!!!')

        time.sleep(10)
        rc, stdout = quota_common.get_all_quota_info()
        common.judge_rc(rc, 0, "get quota failed")
        quotas_info = stdout['result']['quotas']
        quota_id = None
        for quota_info in quotas_info:
            if quota_info['path'] == '%s:/%s' % (quota_common.VOLUME_NAME, quota_path):
                quota_id = quota_info['id']
                break

        rc, check_result = quota_common.update_one_quota(id=quota_id,
                                                         filenr_quota_cal_type='QUOTA_LIMIT',
                                                         filenr_hard_threshold=5000,
                                                         logical_quota_cal_type='QUOTA_LIMIT',
                                                         logical_hard_threshold=5368709120)
        common.judge_rc(rc, 0, "update quota failed", exit_flag=False)
        if check_result['err_no'] != 0:
            print check_result
            log.error('update_quota failed!!!')
            raise Exception('update_quota failed!!!')

        time.sleep(10)
        rc, pscli_info = quota_common.delete_one_quota(quota_id)
        common.judge_rc(rc, 0, "delete quota failed", exit_flag=False)


def case():
    '''打开配额功能'''
    quota_common.open_quota_global_switch()

    '''创建目录，设置配额规则'''
    quota_common.creating_dir(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH)
    quota_operat_dir = os.path.join(quota_common.BASE_QUOTA_PATH, 'vdbench1')
    quota_common.creating_dir(quota_common.CLIENT_IP_1, quota_operat_dir)

    '''起两个进程，一个跑vdbench，一个创建、修改、删除配额规则'''
    p1 = Process(target=tool_use.vdbench_run, args=(quota_common.QUOTA_PATH, quota_common.CLIENT_IP_1,
                                                    quota_common.CLIENT_IP_2),
                 kwargs={'run_create': True, 'run_check_write': True})
    p2 = Process(target=quota_operat, args=(quota_common.QUOTA_PATH_BASENAME,))

    alive.value = True

    p1.start()
    p2.start()

    p1.join()
    alive.value = False

    time.sleep(60)
    if p1.exitcode != 0:
        log.error("vdbench is failed!!!!!!")
        raise Exception("vdbench is failed!!!!!!")
    if p2.exitcode != 0:
        log.error("quota_operat is failed!!!!!!")
        raise Exception("quota_operat is failed!!!!!!")
    return


def main():
    file_name = os.path.basename(__file__)
    file_name = os.path.splitext(file_name)[0]
    log_file_path = log.get_log_path(file_name)
    stream = log.init(log_file_path, True)
    quota_common.cleaning_environment()
    case()
    quota_common.cleaning_environment()
    return


if __name__ == '__main__':
    common.case_main(main)