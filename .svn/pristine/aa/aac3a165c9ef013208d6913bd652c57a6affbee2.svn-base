# -*-coding:utf-8 -*
import os
import time

import utils_path
import common
import snap_common
import log
import shell
import get_config
import prepare_clean

####################################################################################
#
# Author: baorb
# date 2018-01-19
# @summary：
#    修改快照的过期时间。
# @steps:
#    1、对/mnt/parastor/snap/路径创建快照(使用命令pscli --command=create_snapshot  expire_time为0)；
#    2、修改快照的过期时间和描述信息(pscli --command=update_snapshot  expire_time为具体值)；
#    3、查询快照的信息(使用pscli --command=get_snapshot)；
#    4、到过期时间时查询快照是否删除(使用pscli --command=get_snapshot)；
#
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]               # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)


def case():
    # 1> 对目录创建快照
    name1 = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(name1, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % name1)
        raise Exception('create_snapshot %s failed!!!' % name1)

    # 获取当前快照的信息
    snapshot1_info = snap_common.get_snapshot_by_name(name1)
    if -1 == snapshot1_info:
        log.error('snap %s is not exist!!!' % name1)
        raise Exception('snap %s is not exist!!!' % name1)
    elif 0 != snapshot1_info['expire_time']:
        log.error("snap %s's expire_time is not 0" % name1)
        raise Exception("snap %s's expire_time is not 0" % name1)
    elif '' != snapshot1_info['description']:
        log.error("snap %s's description is not right" % name1)
        raise Exception("snap %s's description is not right" % name1)

    # 获取当前时间
    rc, current_time = snap_common.get_current_time()
    expect_expire_time = int(current_time) + 20

    # 2> 修改快照的过期时间和描述信息
    expect_description = '"I am a snap, welcome_to_P300!!!"'
    rc = snap_common.update_snapshot(snapshot1_info['id'], expect_expire_time, expect_description)
    if 0 != rc:
        log.error('update snapshot %s failed !!!' % name1)
        raise Exception('update snapshot %s failed !!!' % name1)

    # 3> 查询快照超时时间信息
    snapshot1_info = snap_common.get_snapshot_by_name(name1)
    if -1 == snapshot1_info:
        log.error('snap %s is not exist!!!' % name1)
        raise Exception('snap %s is not exist!!!' % name1)
    elif expect_expire_time != snapshot1_info['expire_time']:
        log.error("snap %s's expire_time is not %d" % (name1, expect_expire_time))
        raise Exception("snap %s's expire_time is not %d" % (name1, expect_expire_time))
    elif "I am a snap, welcome_to_P300!!!" != snapshot1_info['description']:
        log.error("snap %s's description is not %s" % (name1, expect_description))
        raise Exception("snap %s's description is not %s" % (name1, expect_description))

    # 4> 超过时间后检查快照是否删除
    log.info('wait 30s')
    time.sleep(30)
    snapshot1_info = snap_common.get_snapshot_by_name(name1)
    if -1 != snapshot1_info:
        rc1, stdout = snap_common.get_current_time()
        log.error('expire_time is %s, current time is %s, snap %s not delete!!!' %
                  (snapshot1_info['expire_time'], stdout, name1))
        raise Exception('expire_time is %s, current time is %s, snap %s not delete!!!' %
                        (snapshot1_info['expire_time'], stdout, name1))
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)