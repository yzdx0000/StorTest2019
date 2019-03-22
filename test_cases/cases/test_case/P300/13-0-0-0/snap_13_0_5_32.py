#-*-coding:utf-8 -*
#!/usr/bin/python

import os

import utils_path
import common
import snap_common
import log
import prepare_clean

#=================================================================================
#  latest update:2018-05-14                                                     =
#  author:wangguanglin                                                           =
#=================================================================================
# 2018-05-14:
# 修改者：wangguanglin
#@summary：
#   创建多个目录快照（同一目录），按照快照创建顺序revert，
#   每次目录内容是正确的（每个快照之间分别对目录进行修改内容、修改属性、修改名字、移动位置、删除目录）
#@steps:
#   1、部署3个客户端；
#   2、对目录/mnt/wangguanglin/snap/snap_13_0_5_32/snap_parent/snap_child/
#   创建软连接/mnt/wangguanglin/snap/snap_13_0_5_32/snap_parent/snap_child_so；
#   3、对软连接/mnt/wangguanglin/snap/snap_13_0_5_32/snap_parent/snap_child_so创建快照a1；
#   4、修改/mnt/wangguanglin/snap/snap_13_0_5_32/snap_parent/snap_child_so
#   和修改/mnt/wangguanglin/snap/snap_13_0_5_32/snap_parent/snap_child/的内容；
#   5、对快照a1进行revert，3个客户端观察/mnt/wangguanglin/snap/snap_13_0_5_32/snap_parent/下的内容；
#   6、删除快照；
#   7、3个客户端检查是否有快照入口路径；
#
#changelog:
######################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             #/mnt/wangguanglin/snap/snap_13_0_5_32
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  #/snap/snap_13_0_5_32


def case():
    """创建子目录/mnt/wangguanglin/snap/snap_13_0_5_32/snap_parent/snap_child"""
    test_dir=os.path.join(SNAP_TRUE_PATH,'snap_parent')
    cmd='mkdir %s'% test_dir
    common.run_command(snap_common.CLIENT_IP_1, cmd)
    test_dir00 = os.path.join(test_dir, 'snap_child')
    cmd='mkdir %s'% test_dir00
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    """
    对目录/mnt/wangguanglin/snap/snap_13_0_5_32/snap_parent/snap_child/
    创建软连接/mnt/wangguanglin/snap/snap_13_0_5_32/snap_parent/snap_child_so
    """
    test_dir10 = os.path.join(test_dir, 'snap_child_so')
    cmd='ln -s %s %s'% (test_dir00,test_dir10)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    """
    对目录/mnt/wangguanglin/snap/snap_13_0_5_32/snap_parent/snap_child_so创建快照1
    在设计预期中是不支持对软连接做快照的
    """
    snap_name1 = FILE_NAME + '_snapshot1'
    path1 = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'snap_parent')+'/snap_child_so'
    rc, stdout = snap_common.create_snapshot(snap_name1, path1)
    stdout = common.json_loads(stdout)
    if 14003 != stdout["err_no"]:
        log.error('create_snapshot %s failed!!!' % snap_name1)
        raise Exception('create_snapshot %s failed!!!' % snap_name1)

    """ 删除快照"""
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
