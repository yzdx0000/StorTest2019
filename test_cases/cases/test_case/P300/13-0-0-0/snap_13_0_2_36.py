# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time

import utils_path
import common
import snap_common
import log
import tool_use
import prepare_clean

####################################################################################
#
# Author: liyao
# date 2018-04-24
# @summary：
#    时间跳变，检查数据正确性
# @steps:
#    1、在目录/mnt/volume1/snap下执行00 vdbench脚本创建；
#    2、对目录/mnt/volume1/snap创建快照a1；
#    3、在目录/mnt/volume1/snap下跑01vdbench脚本修改数据，同时修改主MGR点的系统时间；
#    4、在./snapshot/a1下跑02vdbench脚本校验数据；
#    5、删除快照；
#    6、检查是否有快照路径入口；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              # /mnt/volume1/snap/snap_13_0_2_36
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   # /snap/snap_13_0_2_36


def sys_time_revision():
    '''获取主MGR节点IP'''
    node_obj = common.Node()
    master_id = node_obj.get_master_mgr_id()
    master_ip = node_obj.get_node_ip_by_id(master_id)
    '''修改系统时间'''
    cmd = 'date +%s'
    rc, stdout = common.run_command(master_ip, cmd)
    sys_time = int(stdout) + 120
    cmd = 'date -d @%s' % sys_time
    rc, stdout = common.run_command(master_ip, cmd)
    cmd = 'date -s "%s"' % stdout
    common.run_command(master_ip, cmd)


def case():
    # 1> 运行00脚本
    tool_use.vdbench_run(SNAP_TRUE_PATH, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, run_create=True)

    # cmd1 = 'scp -r /tmp/vdb_control.file root@%s:/tmp' % snap_common.CLIENT_IP_2
    # cmd2 = 'scp -r /tmp/vdb_control.file root@%s:/tmp' % snap_common.CLIENT_IP_3
    # common.run_command(snap_common.CLIENT_IP_1, cmd1)
    # common.run_command(snap_common.CLIENT_IP_1, cmd2)

    # 2> 对目录创建快照
    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name, path)
    common.judge_rc(rc, 0, 'create_snapshot %s failed!!!' % snap_name)

    # 3> 并行修改文件，同时修改主MGR点的系统时间
    p1 = Process(target=tool_use.vdbench_run,
                 args=(SNAP_TRUE_PATH, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2),
                 kwargs={'run_write': True})
    p2 = Process(target=sys_time_revision)

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    common.judge_rc(p1.exitcode, 0, "vdbench is failed!!!!!!")

    # 4> 运行02脚本
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name)
    tool_use.vdbench_run(snap_path, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, run_check=True)

    # 5> 删除快照
    rc, stdout = snap_common.delete_snapshot_by_path(path)
    common.judge_rc(rc, 0, '%s delete snapshot failed!!!' % (path))

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

    # 6> 检查快照路径入口是否存在
    snap_common.check_snap_entry(snap_path)
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)