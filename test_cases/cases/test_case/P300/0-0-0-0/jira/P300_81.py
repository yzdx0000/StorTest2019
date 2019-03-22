# -*-coding:utf-8 -*
import os
import random

import utils_path
import log
import common
import snap_common
import prepare_clean

####################################################################################
#
# Author: baorb
# Date: 2018-08-08
# @summary：
#      删除不存在的快照
# @steps:
#     1、查询快照；
#     2、删除不存在的快照；
#
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字


def case():
    log.info("获取所有快照的id")
    snaps_info = snap_common.get_all_snapshot()
    snaps_info_lst = snaps_info['result']['snapshots']
    snapshot_id_lst = []
    for snap_info in snaps_info_lst:
        if snap_info['state'] != 'SNAPSHOT_DELETING':
            snapshot_id_lst.append(snap_info['id'])

    log.info("找一个非快照id的数字")
    while True:
        num = random.randint(1, 5000)
        if num not in snapshot_id_lst:
            del_snap_id = num
            break

    rc, stdout = snap_common.delete_snapshot_by_ids(del_snap_id)
    common.judge_rc_unequal(rc, 0, 'not del snapshot')
    stdout = common.json_loads(stdout)
    if stdout['detail_err_msg'] != 'Item is not exist':
        raise Exception('delete snapshot succeed')


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)