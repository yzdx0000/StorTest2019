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

######################################################
#Author: liyao
#date 2018-4-10
# @summary:创建快照，通过硬链接修改源文件内容，
#@steps:
# 1. 对/mnt/liyao/snap/test_file1创建硬链接/mnt/liyao/snap/test_file1_hd
# 2. 对/mnt/liyao/snap/创建快照a1
# 3. 通过/mnt/liyao/snap/test_file1_hd修改文件内容
# 4. 进入/mnt/liyao/.snapshot目录浏览快照a1数据
# 5. 删除快照
# 6. 查看是否有快照入口路径
#
#changelog:
######################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             #/mnt/liyao/snap/snap_13_0_2_24
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  #/snap/snap_13_0_2_24

def case():
    # 创建文件/mnt/liyao/snap/test_file1
    test_file1=os.path.join(SNAP_TRUE_PATH,'test_file1')
    
    cmd="echo 'hello, world!'> %s"% test_file1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 创建硬链接
    test_file1_hd=os.path.join(SNAP_TRUE_PATH,'test_file1_hd')
    cmd='ln %s %s'%(test_file1,test_file1_hd)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 创建快照
    snap_name1 = FILE_NAME + '_snapshot1'
    path1 = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name1, path1)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name1)
        raise Exception('create_snapshot %s failed!!!' % snap_name1)

    # 通过硬链接/mnt/liyao/snap/test_file1_hd 修改源文件内容
    cmd="echo 'nice to meet you'>> %s"% test_file1_hd
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 浏览快照内容
    snap_path1 = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name1)
    cmd = 'cat %s' % os.path.join(snap_path1, 'test_file1')
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if 'hello, world!' != stdout.strip():
        log.error('%s is not right!!!' % snap_name1)
        raise Exception('%s is not right!!!' % snap_name1)

    # 删除快照
    rc, stdout = snap_common.delete_snapshot_by_name(FILE_NAME)
    if 0 != rc:
        log.error('%s delete failed!!!' % (FILE_NAME))
        raise Exception('%s delete failed!!!' % (FILE_NAME))

    log.info('waiting for 10s')
    time.sleep(10)
    judge_mark = True
    while judge_mark:
        delete_check = snap_common.get_snapshot_by_name(snap_name1)
        if delete_check != -1:
            log.info('waiting for 10s')
            time.sleep(10)
        else:
            judge_mark = False

    # 检查快照路径入口是否存在
    snap_common.check_snap_entry(snap_path1)
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)