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
#      删除不存在的快照revert
# @steps:
#     1、查询快照revert；
#     2、删除不存在的快照revert；
#
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字


def case():
    log.info("获取所有快照revert的id")
    rc, snap_revert_id_lst = snap_common.get_revert_snapshot_ids()

    log.info("找一个非快照revert的id的数字")
    while True:
        num = random.randint(1, 5000)
        if num not in snap_revert_id_lst:
            del_snap_revert_id = num
            break

    rc, stdout = snap_common.delete_revert_snapshot_by_id(del_snap_revert_id)
    common.judge_rc_unequal(rc, 0, 'not del snap revert')
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