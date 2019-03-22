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
#    创建单个文件快照，修改文件的扩展属性，执行revert，文件内容回滚到之前的内容
# @steps:
#    1、部署3个客户端；
#    2、对文件/test_file1添加扩展属性（setfattr）对文件/mnt/parastor/snap/test_file1创建快照a1；
#    3、修改文件/mnt/parastor/snap/test_file1的扩展属性（使用setfattr）；
#    4、到/mnt/parastor/.snapshot/下观察test_file1的扩展属性（使用getfattr）；
#    5、对快照a1执行revert;
#    6、3个客户端观察文件/mnt/parastor/snap/test_file1的扩展属性；
#    7、删除快照；
#    8、3个客户端查看是否有快照入口路径；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              # /mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   # /snap/snap_13_0_0_0


def case():
    # 修改参数
    common.update_param(section='oApp', name='xattr_enable', current=1)

    # 创建文件
    file_path = os.path.join(SNAP_TRUE_PATH, 'test_file1')
    test_str = '111111'
    cmd = 'echo %s > %s' % (test_str, file_path)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 对文件添加扩展属性
    snap_common.setfattr_file(snap_common.CLIENT_IP_1, file_path, 'user.bao', '123')

    # 2> 对文件创建快照
    snap_name1 = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_file1')
    rc, stdout = snap_common.create_snapshot(snap_name1, path)
    common.judge_rc(rc, 0, 'create_snapshot %s failed!!!' % snap_name1)

    # 3> 修改文件添加扩展属性
    snap_common.setfattr_file(snap_common.CLIENT_IP_2, file_path, 'user.bao', '456')

    log.info("wait 10s")
    time.sleep(10)

    # 4> 到快照路径下观察扩展属性
    snap_file_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name1)
    rc, stdout = snap_common.getfattr_file(snap_common.CLIENT_IP_1, snap_file_path, 'user.bao')
    common.judge_rc(stdout, '123', '%s Extended attributes is not right!!!' % snap_name1)

    # 5> 对文件执行revert
    snap_info = snap_common.get_snapshot_by_name(snap_name1)
    snap_id = snap_info['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id)
    common.judge_rc(rc, 0, "revert snapshot %s failed!!!" % snap_name1)
    snap_common.check_revert_finished(snap_id)

    log.info("wait 10s")
    time.sleep(10)

    # 6> 检查文件的扩展属性
    rc, stdout = snap_common.getfattr_file(snap_common.CLIENT_IP_1, file_path, 'user.bao')
    common.judge_rc(stdout, '123', '%s Extended attributes is not right!!!' % snap_name1)

    # 7> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_path(path)
    common.judge_rc(rc, 0, '%s delete snapshot failed!!!' % (path))

    time.sleep(10)

    # 修改参数
    common.update_param(section='oApp', name='xattr_enable', current=0)

    # 8> 3个客户端检查快照路径入口是否存在
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name1)
    snap_common.check_snap_entry(snap_path)
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)