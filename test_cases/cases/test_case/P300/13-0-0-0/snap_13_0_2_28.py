#-*-coding:utf-8 -*
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
#@summary：
#    各种命令浏览快照内容。
#@steps:
#    1、对目录/mnt/parastor/snap/创建快照a1，(使用命令pscli --command=create_snapshot)；
#    2、在/mnt/parastor/.snapshot/下使用mkdir创建文件夹，touch、vim、重定向(echo >)等创建文件；
#    3、使用cp、mv等复制文件到/mnt/parastor/.snapshot/；
#    4、在/mnt/parastor/.snapshot/使用pwd显示路径；
#    5、在/mnt/parastor/.snapshot/下分别执行cd、ls、df、du等命令；
#    6、在/mnt/parastor/.snapshot/下分别用cat、tail、less、more、vim等命令查看文件；
#    7、在/mnt/parastor/.snapshot/下对快照文件进行vim、>、>>、truncate、rm、mv等操作；
#    8、删除快照；
#    9、查看是否有快照入口路径；
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  #/snap/snap_13_0_0_0

def case():
    # 创建文件
    test_file = os.path.join(SNAP_TRUE_PATH, 'test_file')
    cmd = 'echo 111 > %s' % test_file
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 1> 创建快照
    snap_name = FILE_NAME + '_snapshot1'
    path1 = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name, path1)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name)
        raise Exception('create_snapshot %s failed!!!' % snap_name)

    # 2> 快照路径下创建文件夹、文件
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name)
    dir_test_1 = os.path.join(snap_path, 'dir_test_1')
    cmd = 'mkdir %s' % dir_test_1
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if rc == 0:
        log.error('%s succeed!!!' % cmd)
        raise Exception('%s succeed!!!' % cmd)

    file_test_1 = os.path.join(snap_path, 'file_test_1')
    cmd = 'touch %s' % file_test_1
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if rc == 0:
        log.error('%s succeed!!!' % cmd)
        raise Exception('%s succeed!!!' % cmd)

    cmd = 'echo 111 > %s' % file_test_1
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if rc == 0:
        log.error('%s succeed!!!' % cmd)
        raise Exception('%s succeed!!!' % cmd)

    # 3> 复制文件到快照目录
    tmp_file = '/tmp/file_test_1'
    cmd = 'touch %s' % tmp_file
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    cmd = 'cp %s %s' %(tmp_file, snap_path)
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if rc == 0:
        log.error('%s succeed!!!' % cmd)
        raise Exception('%s succeed!!!' % cmd)

    cmd = 'mv %s %s' %(tmp_file, snap_path)
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if rc == 0:
        log.error('%s succeed!!!' % cmd)
        raise Exception('%s succeed!!!' % cmd)

    # 4> 路径查询
    cmd = 'cd %s; pwd' % snap_path
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if stdout.strip() != snap_path:
        log.error('%s error!!!' % cmd)
        raise Exception('%s error!!!' % cmd)

    # 5> 执行ls等命令
    cmd = 'ls %s' % snap_path
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if rc != 0:
        log.error('%s failed!!!' % cmd)
        raise Exception('%s failed!!!' % cmd)

    cmd = 'cd %s;df' % snap_path
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if rc != 0:
        log.error('%s failed!!!' % cmd)
        raise Exception('%s failed!!!' % cmd)

    cmd = 'cd %s;du -sh *' % snap_path
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if rc != 0:
        log.error('%s failed!!!' % cmd)
        raise Exception('%s failed!!!' % cmd)

    # 6> 查看文件内容
    snap_test_file = os.path.join(snap_path, 'test_file')
    cmd = 'cat %s' % snap_test_file
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if stdout.strip() != '111':
        log.error('%s is not right!!!' % snap_test_file)
        raise Exception('%s is not right!!!' % snap_test_file)

    cmd = 'tail %s' % snap_test_file
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if stdout.strip() != '111':
        log.error('%s is not right!!!' % snap_test_file)
        raise Exception('%s is not right!!!' % snap_test_file)

    # 7> 修改快照文件内容
    cmd = 'echo 222 > %s' % snap_test_file
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if rc == 0:
        log.error('%s failed!!!' % cmd)
        raise Exception('%s failed!!!' % cmd)

    cmd = 'echo 222 >> %s' % snap_test_file
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if rc == 0:
        log.error('%s failed!!!' % cmd)
        raise Exception('%s failed!!!' % cmd)

    cmd = 'truncate %s -s 1M' % snap_test_file
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if rc == 0:
        log.error('%s failed!!!' % cmd)
        raise Exception('%s failed!!!' % cmd)

    common.rm_exe(snap_common.CLIENT_IP_1,snap_test_file)

    cmd = 'mv %s /tmp' % snap_test_file
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if rc == 0:
        log.error('%s failed!!!' % cmd)
        raise Exception('%s failed!!!' % cmd)

    # 8> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_name(snap_name)
    if 0 != rc:
        log.error('%s delete failed!!!' % (snap_name))
        raise Exception('%s delete failed!!!' % (snap_name))

    log.info('waiting for 10s')
    time.sleep(10)
    judge_mark = True
    while judge_mark:
        delete_check = snap_common.get_snapshot_by_name(snap_name)
        if delete_check != -1:
            log.info('waiting for 10s')
            time.sleep(10)
        else:
            judge_mark = False

    # 9> 3个客户端检查快照路径入口是否存在
    snap_common.check_snap_entry(snap_path)

    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)