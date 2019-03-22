# -*-coding:utf-8 -*
import os
from multiprocessing import Process

import utils_path
import common
import snap_common
import log
import prepare_clean

####################################################################################
#
# Author: liyao
# date 2018-05-08
# @summary：
#    同一时间进行多个revert
# @steps:同一时间进行多个revert
#    1、部署3个客户端；
#    2、对目录/mnt/parastor/snap/创建多个快照；
#    3、同时进行多个快照的revert；
#    4、删除快照；
#    5、3个客户端下观察是否有快照路径入口
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             # /mnt/volume1/snap/snap_13_0_5_37
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  # /snap/snap_13_0_5_37


def snap_revert(snap_id, exe_ip):
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id)
    common.judge_rc(rc, 0, 'revert_snapshot %s failed!!!')
    return


def case():
    # 在目录下创建文件
    test_file = os.path.join(SNAP_TRUE_PATH, 'test_file')
    cmd = 'dd if=%s of=%s bs=1k count=8' % (snap_common.get_system_disk(snap_common.CLIENT_IP_1),test_file)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 2>对目录创建多个快照，并保存快照信息
    snap_id_list = []
    for i in range(3):
        snapshot_name = FILE_NAME + '_snapshot_%s' % str(i)
        path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
        rc, stdout = snap_common.create_snapshot(snapshot_name, path)
        if 0 != rc:
            log.error('create_snapshot %s failed!!!' % snapshot_name)
            raise Exception('create_snapshot %s failed!!!' % snapshot_name)
        snap_info = snap_common.get_snapshot_by_name(snapshot_name)
        snap_id = str(snap_info['id'])
        snap_id_list.append(snap_id)

    # 3>同时进行多个快照的revert
    p1 = Process(target=snap_revert, args=(snap_common.SYSTEM_IP, snap_id_list[0]))
    p2 = Process(target=snap_revert, args=(snap_common.SYSTEM_IP, snap_id_list[1]))
    p3 = Process(target=snap_revert, args=(snap_common.SYSTEM_IP, snap_id_list[2]))

    p1.start()
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.join()

    # 4>删除快照
    rc, stdout = snap_common.delete_snapshot_by_name(FILE_NAME)
    if 0 != rc:
        log.error('%s delete failed!!!' % (FILE_NAME))
        raise Exception('%s delete failed!!!' % (FILE_NAME))
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)