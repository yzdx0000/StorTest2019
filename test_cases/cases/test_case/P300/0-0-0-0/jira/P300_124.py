#-*-coding:utf-8 -*
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
# author 刘俊鑫
# date 2018-07-11
#@summary：
#   revert快照到达128个以后报错
#@steps:
#   step1:创建200个快照
#   step2：对这200个快照做revert
#   step3:revert成功后，删除快照清理环境
#
#@changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]               #本脚本名字
DEFECT_PATH=get_config.get_one_defect_test_path()                         #DEFECT_PATH = "/mnt/volume1/defect_case
DEFECT_TRUE_PATH = os.path.join(DEFECT_PATH, FILE_NAME)                   #/mnt/volume1/defect_case/P300-124
DEFECT_PATH_BASENAME=os.path.basename(DEFECT_PATH)                        #defect_case
DEFECT_TRUE_PATH_BASENAME=os.path.basename(DEFECT_TRUE_PATH)              #P300-124

def case():
    log.info("----------case----------")
    #step1:创建200个快照'''
    path = snap_common.VOLUME_NAME + ':/' + DEFECT_PATH_BASENAME + '/' + DEFECT_TRUE_PATH_BASENAME
    for i in range(1,201):
        (rc, stdout) = snap_common.create_snapshot("snap_%s" %i, path)
        if rc != 0:
            raise Exception("snap_%s create failed" %i)

    #step2:对这200个快照做revert
    for i in range(1,201):
        snap_name = "snap_%s" %i
        snap_info = snap_common.get_snapshot_by_name(snap_name)
        snap_id = snap_info['id']
        rc, stdout = snap_common.revert_snapshot_by_id(snap_id)
        if 0 != rc:
            raise Exception('revert_snapshot %s failed!!!' % snap_name)
        snap_common.check_revert_finished(snap_id)

    #step3:revert成功后，删除快照清理环境
    for i in range(1,201):
        snap_name = "snap_%s" %i
        snap_info = snap_common.get_snapshot_by_name(snap_name)
        snap_id = snap_info['id']
        rc, stdout = snap_common.delete_snapshot_by_ids(snap_id)
        if 0 != rc:
            raise Exception('delete_snapshot %s failed!!!' % snap_name)
        snap_common.wait_snap_del_by_name(snap_name)


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)