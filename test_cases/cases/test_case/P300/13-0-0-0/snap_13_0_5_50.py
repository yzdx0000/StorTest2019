# -*-coding:utf-8 -*
import os
import time
import json

import utils_path
import common
import snap_common
import log
import prepare_clean
import tool_use

####################################################################################
#
# Author: liyao
# date 2018-05-21
# @summary：
#    对目录创建快照，修改文件，执行revert过程中删除回滚
# @steps:
#    1、部署3个客户端；
#    2、在目录/mnt/parastor/snap/下执行vdbench00脚本创建数据；
#    3、对目录/mnt/parastor/snap/创建快照a1；
#    4、在目录/mnt/parastor/snap/下执行vdbench01脚本修改数据；
#    5、对快照a1执行revert，回滚过程中执行delete_revert_snapshot删除回滚；
#    6、在目录/mnt/parastor/snap/下执行vdbench02脚本校验数据
#    7、删除快照；
#    8、3个客户端查看是否有快照入口路径；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             # /mnt/volume1/snap/snap_13_0_5_50
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  # /snap/snap_13_0_5_50


def revert_with_delete(snapshot_id):
    snap_common.revert_snapshot_by_id(snapshot_id)
    while True:
        rc, stdout = snap_common.get_revert_snapshot()
        common.judge_rc(rc, 0, 'get_revert_snapshot failed!!!')
        revertsnapshots = stdout['result']['revertSnapshots']
        for revertsnapshot in revertsnapshots:
            if revertsnapshot['snapshot_id'] == snapshot_id:
                revert_id = revertsnapshot['revert_id']
                if revertsnapshot['state'] == 'EXECUTE' or revertsnapshot['state'] == 'FINISHED':
                    snap_common.delete_revert_snapshot_by_id(revert_id)
                    return


def case():
    # 2> 运行00脚本
    obj_vdb = tool_use.Vdbenchrun(size="(64k,30,128k,35,256k,30,1m,5)", elapsed=60)
    obj_vdb.run_create(SNAP_TRUE_PATH, SNAP_TRUE_PATH, snap_common.CLIENT_IP_1)
    # tool_use.vdbench_run(SNAP_TRUE_PATH, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, run_create=True)

    # 3> 对目录创建快照
    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name, path)
    common.judge_rc(rc, 0, 'create_snapshot %s failed!!!' % snap_name)

    # 4> 运行01脚本修改数据
    obj_vdb.run_write(SNAP_TRUE_PATH, snap_common.CLIENT_IP_2)
    # tool_use.vdbench_run(SNAP_TRUE_PATH, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, run_write=True)

    # 5> 对快照执行revert，回滚过程中执行delete_revert_snapshot
    snapshot = snap_common.get_snapshot_by_name(snap_name)
    snapshot_id = snapshot['id']
    revert_with_delete(snapshot_id)

    # 6> 运行02脚本
    snap_common.check_revert_finished(snapshot_id)
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name)
    obj_vdb.run_check(SNAP_TRUE_PATH, SNAP_TRUE_PATH, snap_common.CLIENT_IP_3)
    # tool_use.vdbench_run(SNAP_TRUE_PATH, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, run_check=True)

    # 7> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_path(path)
    common.judge_rc(rc, 0, '%s delete snapshot failed!!!' % (path))

    time.sleep(10)

    # 7> 3个客户端检查快照路径入口是否存在
    snap_common.check_snap_entry(snap_path)
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
