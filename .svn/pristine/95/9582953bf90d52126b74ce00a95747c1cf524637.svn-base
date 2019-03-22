#-*-coding:utf-8 -*
import os
import time

import utils_path
import common
import snap_common
import log
import get_config
import prepare_clean
from multiprocessing import Process
import tool_use

####################################################################################
#
# Author: liyao
# date 2018-05-08
#@summary：
#    vdbench数据校验的情况下不断创建、删除快照
#@steps:
#    1、vdbench数据校验的情况下不断创建、删除快照；
#
#@changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             #/mnt/volume1/snap/snap_13_0_5_39
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  #/snap/snap_13_0_5_39

def create_snap_constant():    # 快照不断创建与删除
    for i in range(25920):   # 3天
        snap_name = FILE_NAME + '_snapshot_%s'% str(i)
        path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
        rc, stdout = snap_common.create_snapshot(snap_name, path)
        if 0 != rc:
            log.error('create_snapshot %s failed!!!' % snap_name)
            raise Exception('create_snapshot %s failed!!!' % snap_name)

        log.info('waiting for 10s')
        time.sleep(10)

        rc, stdout = snap_common.delete_snapshot_by_name(FILE_NAME)
        if 0 != rc:
            log.error('%s delete failed!!!' % (FILE_NAME))
            raise Exception('%s delete failed!!!' % (FILE_NAME))
    return

def vdbench_large_data(SNAP_VDB_TOOL, vdbench_tool_path, exe_ip, SNAP_TRUE_PATH):
    cmd = 'cd %s;sh 03.largedata.sh %s %s %s' % (
        SNAP_VDB_TOOL, vdbench_tool_path, exe_ip, SNAP_TRUE_PATH)
    rc = common.command(cmd)
    if rc != 0:
        raise Exception("03.largedata.sh is failed!!!!!!")
    return

def case():
    test_file = os.path.join(SNAP_TRUE_PATH, 'test_file')        # 目录下创建文件
    cmd = 'dd if=%s of=%s bs=1k count=8' % (snap_common.get_system_disk(snap_common.CLIENT_IP_1), test_file)
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    '''获取vdbench工具'''
    obj_vdbench = tool_use.Vdbenchrun(files=1000, size='(500m,50,600m,50)', elapsed=30000)
    # 并行运行vdbench与快照创建、删除
    p1 = Process(target=create_snap_constant)
    p2 = Process(target=obj_vdbench.run_stress_no_jnl,
                 args=(SNAP_TRUE_PATH, snap_common.CLIENT_IP_1))

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