#-*-coding:utf-8 -*
#!/usr/bin/python

import os
import time
import commands

import utils_path
import common
import snap_common
import log
import prepare_clean

#=================================================================================
#  latest update:2018-04-23                                                      =
#  author:wangguanglin                                                           =
#=================================================================================
# 2018-04-23:
# 修改者：wangguanglin
#summary:
#    顺序删除快照后,校验数据正确
#@steps:
#    1、对目录/mnt/wangguanglin/snap创建10个快照，每个快照之间修改目录下的内容
#    2、顺序删除第二个到第九个快照，检查第一个和第十个快照内容是否正确
#
#changelog:
######################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             #/mnt/wangguanglin/snap/snap_13_0_2_37
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  #/snap/snap_13_0_2_37


def case():

    """创建子目录/mnt/wangguanglin/snap/snap_13_0_2_37/test_dir"""
    test_dir=os.path.join(SNAP_TRUE_PATH,'test_dir')
    cmd='mkdir %s'% test_dir
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    """                                                                                                                                                                                                               
    创建文件/mnt/wangguanglin/snap/snap_13_0_2_37/test_dir/test_file1
    对目录 /mnt/wangguanglin/snap创建个快照，每个快照之间修改目录下的内容
    """
    test_file1 = os.path.join(test_dir, 'test_file1')
    for num in range(1,11):
        cmd = "echo '%d'>> %s"% (num, test_file1)
        common.run_command(snap_common.CLIENT_IP_1, cmd)
        """创建快照"""
        snap_name1 = FILE_NAME + '_snapshot%d'% num
        path1 = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_dir')
        rc, stdout = snap_common.create_snapshot(snap_name1, path1)
        if 0 != rc:
           log.error('create_snapshot %s failed!!!' % snap_name1)
           raise Exception('create_snapshot %s failed!!!' % snap_name1)

    """顺序删除第二个到第九个快照"""
    for num1 in range(2,10):
        snap_name2 = FILE_NAME + '_snapshot%d' % num1
        """删除指定的快照"""
        rc, stdout = snap_common.delete_snapshot_by_name(snap_name2)
        if 0 != rc:
            log.error('%s delete failed!!!' % (snap_name2))
            raise Exception('%s delete failed!!!' % (snap_name2))

    """检查第一个快照的正确性"""
    snap_name3 = FILE_NAME + '_snapshot1'
    snap_path2 = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name3)
    cmd = 'cat %s' % os.path.join(snap_path2, 'test_file1')
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if '1' != stdout.strip():
        log.error('%s is not right!!!' % snap_name3)
        raise Exception('%s is not right!!!' % snap_name3)

    """检查第十个快照内容的正确性"""
    snap_name4 = FILE_NAME + '_snapshot10'
    snap_path3 = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name4)
    cmd = 'cat %s' % os.path.join(snap_path3, 'test_file1')
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if '1\n2\n3\n4\n5\n6\n7\n8\n9\n10' != stdout.strip():
        log.error('%s is not right!!!' % snap_name4)
        raise Exception('%s is not right!!!' % snap_name4)

    time.sleep(10)
    """ 删除快照1和10"""
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
