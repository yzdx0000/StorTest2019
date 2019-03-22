#-*-coding:utf-8 -*
import os
import time

import utils_path
import common
import snap_common
import log
import prepare_clean
from multiprocessing import Process

####################################################################################
#
# Author: liyao
# date 2018-05-08
#@summary：
#    压力下进行快照创建、删除和revert
#@steps:
#    1、跑iozone和mdtest的情况下，不断创建、删除快照、进行快照revert；
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             #/mnt/volume1/snap/snap_13_0_5_38
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  #/snap/snap_13_0_5_38

def create_snap_constant():    # 快照不断创建、删除与revert
    for i in range(5000):  # 3天
        snap_name = FILE_NAME + '_snapshot_%s'% str(i)
        path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
        # 创建快照
        rc, stdout = snap_common.create_snapshot(snap_name, path)
        if 0 != rc:
            log.error('create_snapshot %s failed!!!' % snap_name)
            raise Exception('create_snapshot %s failed!!!' % snap_name)

        log.info('waiting for 10s')
        time.sleep(10)

        # 删除快照
        rc, stdout = snap_common.delete_snapshot_by_name(FILE_NAME)
        if 0 != rc:
            log.error('%s delete failed!!!' % (FILE_NAME))
            raise Exception('%s delete failed!!!' % (FILE_NAME))
    return

def mdtest_large_data(machines_path, exe_ip):
    cmd = 'mpirun -hostfile %s -np 20 -allow-run-as-root mdtest -z 3 -b 10 -I 10 -i 3 -d %s'% (machines_path, SNAP_TRUE_PATH)
    rc, stdout = common.run_command(exe_ip, cmd)
    if rc != 0:
        raise Exception("mdtest execution is failed!!!!!!")
    return

def case():
    # 目录下创建文件
    test_file = os.path.join(SNAP_TRUE_PATH, 'test_file')
    cmd = 'dd if=%s of=%s bs=1k count=8' % (snap_common.get_system_disk(snap_common.CLIENT_IP_1), test_file)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    machines_path = '/tmp/machines'
    cmd = 'echo "%s slots=10\n%s slots=10" > %s'% (snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, machines_path)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 运行mdtest的同时不断创建、删除快照
    p1 = Process(target=create_snap_constant)
    p2 = Process(target=mdtest_large_data, args=(machines_path, snap_common.CLIENT_IP_1))

    p1.start()
    p2.start()

    p1.join()
    p2.terminate()
    p2.join()

    return

def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)