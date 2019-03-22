# -*-coding:utf-8 -*
import os
import time
import json

import utils_path
import common
import snap_common
import log
import shell
import get_config
import prepare_clean

####################################################################################
#
# Author: chenjy1
# Date 2018-08-06
# @summary：
#    因临时快照占用快照名额导致快照达到上限后无法回滚
# @steps:
#    1、对一个目录不间断的创建快照，直到1000个
#    2、执行回滚操作可以正常回滚
#    3、批量删除快照
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                     # 本脚本名字
SNAP_TRUE_PATH = os.path.join(prepare_clean.DEFECT_PATH, FILE_NAME)             # /mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(os.path.basename(prepare_clean.DEFECT_PATH), FILE_NAME)
NUM = 1000


def case():
    log.info("case begin")

    snap_true_path = os.path.join(snap_common.SNAP_PATH, FILE_NAME)  # /mnt/liyao/snap/snap_13_0_1_1
    snap_common.cleaning_environment(FILE_NAME, snap_true_path, False)

    log.info("1> 对一个目录不间断的创建快照，直到1000个")
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    name = ''
    for i in range(NUM):
        name = FILE_NAME + '_snapshot_%d' % i
        rc, stdout = snap_common.create_snapshot(name, path)
        if i == 999:
            cmd = ("cd %s ;echo 111 > %s") % (SNAP_TRUE_PATH, FILE_NAME)
            rc, stdout = common.run_command(snap_common.SYSTEM_IP, cmd)
        if 0 != rc:
            common.except_exit(info='create_snapshot %s failed!!!' % name)

    log.info('wait 10s')
    time.sleep(10)

    log.info("2> 回滚快照")
    snap_info = snap_common.get_snapshot_by_name(name)
    snap_id = snap_info['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id)
    common.judge_rc(rc, 0, "revert snapshot %s failed!!!" % name)
    snap_common.check_revert_finished(snap_id)

    stdout = snap_common.get_all_snapshot(param_name='name', param_value=FILE_NAME)
    common.judge_rc(stdout['result']['total'], NUM, "snapshot num is not 1000, is %d" % stdout['result']['total'])

    log.info("3> 批量删除快照")
    rc, stdout = snap_common.delete_snapshot_by_name(FILE_NAME)
    common.judge_rc(rc, 0, 'delete_snapshot %s failed!!!' % FILE_NAME)
    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)