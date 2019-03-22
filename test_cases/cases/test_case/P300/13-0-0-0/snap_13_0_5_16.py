# -*-coding:utf-8 -*
import os
import time

import utils_path
import common
import snap_common
import log
import prepare_clean

####################################################################################
#
# Author: baorb
# date 2018-01-19
# @summary：
#    创建单个目录快照，修改目录和子文件的扩展属性，执行revert，文件内容回滚到之前的内容
# @steps:
#    1、部署3个客户端；
#    2、对目录/mnt/parastor/snap/和/mnt/parastor/snap/snap_dir1/添加扩展属性（setfattr），对目录/mnt/parastor/snap/创建快照a1；
#    3、修改目录/mnt/parastor/snap/和/mnt/parastor/snap/snap_dir1/的扩展属性（使用setfattr）；
#    4、到/mnt/parastor/.snapshot/下观察snap/和snap_dir1/的扩展属性（使用getfattr）；
#    5、对快照a1进行revert；
#    6、3个客户端观察目录/mnt/parastor/snap/和/mnt/parastor/snap/snap_dir1/的扩展属性；
#    7、删除快照；
#    8、3个客户端检查是否有快照路径入口；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              # /mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   # /snap/snap_13_0_0_0


def case():
    # 2> 创建目录
    dir_path_1 = os.path.join(SNAP_TRUE_PATH, 'test_dir_1')
    cmd = 'mkdir %s' % dir_path_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 修改参数
    common.update_param(section='oApp', name='xattr_enable', current=1)

    # 添加扩展属性
    snap_common.setfattr_file(snap_common.CLIENT_IP_1, SNAP_TRUE_PATH, 'user.abc', '123')
    snap_common.setfattr_file(snap_common.CLIENT_IP_1, dir_path_1, 'user.def', '456')

    # 创建快照
    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name, path)
    common.judge_rc(rc, 0, 'create_snapshot %s failed!!!' % snap_name)

    # 3> 修改扩展属性
    snap_common.setfattr_file(snap_common.CLIENT_IP_1, SNAP_TRUE_PATH, 'user.abc', '321')
    snap_common.setfattr_file(snap_common.CLIENT_IP_1, SNAP_TRUE_PATH, 'user.cba', '321')
    snap_common.setfattr_file(snap_common.CLIENT_IP_1, dir_path_1, 'user.def', '654')
    snap_common.setfattr_file(snap_common.CLIENT_IP_1, dir_path_1, 'user.fed', '654')

    # 5> 对快照进行revert
    snap_info = snap_common.get_snapshot_by_name(snap_name)
    snap_id = snap_info['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id)
    common.judge_rc(rc, 0, "revert snapshot %s failed!!!" % snap_name)
    snap_common.check_revert_finished(snap_id)

    time.sleep(3)

    # 6> 检查文件的扩展属性
    rc, stdout = snap_common.getfattr_file(snap_common.CLIENT_IP_2, SNAP_TRUE_PATH, 'user.abc')
    common.judge_rc(stdout, '123', '%s Extended attributes is not right!!!' % SNAP_TRUE_PATH)
    rc, stdout = snap_common.getfattr_file(snap_common.CLIENT_IP_2, SNAP_TRUE_PATH, 'user.cba')
    common.judge_rc_unequal(rc, 0, '%s Extended attributes is not right!!!' % SNAP_TRUE_PATH)
    rc, stdout = snap_common.getfattr_file(snap_common.CLIENT_IP_2, dir_path_1, 'user.def')
    common.judge_rc(stdout, '456', '%s Extended attributes is not right!!!' % dir_path_1)
    rc, stdout = snap_common.getfattr_file(snap_common.CLIENT_IP_2, dir_path_1, 'user.fed')
    common.judge_rc_unequal(rc, 0, '%s Extended attributes is not right!!!' % dir_path_1)

    # 7> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_path(path)
    common.judge_rc(rc, 0, '%s delete snapshot failed!!!' % (path))

    time.sleep(10)

    # 修改参数
    common.update_param(section='oApp', name='xattr_enable', current=0)

    # 8> 3个客户端检查快照路径入口是否存在
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name)
    snap_common.check_snap_entry(snap_path)
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)