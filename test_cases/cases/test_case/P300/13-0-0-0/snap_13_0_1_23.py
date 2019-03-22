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
# Author: liyao
# date 2018-04-24
# @summary：
#    时间跳变到快照超时前
# @steps:
#    1、创建快照，设定快照超时时间；
#    2、快照还有一分钟超时，将主MGR系统时间向前修改，等一分钟后观察快照是否删除；
#    3、查询快照的信息(使用pscli --command=get_snapshot)；
#
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              # /mnt/liyao/snap/snap_13_0_1_23
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   # /snap/snap_13_0_1_23


def case():
    '''获取当前时间'''
    rc, current_time = snap_common.get_current_time()
    expire_time = int(current_time) + 60

    '''1> 对目录创建快照'''
    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = common.create_snapshot(name=snap_name, path=path, expire_time=str(expire_time))
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name)
        raise Exception('create_snapshot %s failed!!!' % snap_name)

    '''2>修改主MGR点的系统时间'''
    '''获取主MGR节点IP'''
    rc, stdout = common.get_master(print_flag=True)
    stdout = common.json_loads(stdout)
    node_obj = common.Node()
    master_id = stdout['result']['node_id']
    master_ip = node_obj.get_node_ip_by_id(master_id)
    '''修改系统时间'''
    cmd = 'date +%s'
    rc, stdout = common.run_command(master_ip, cmd)
    sys_time = int(stdout) - 30
    cmd = 'date -d @%s' % sys_time
    rc, stdout = common.run_command(master_ip, cmd)
    cmd = 'date -s "%s"' % stdout
    common.run_command(master_ip, cmd)

    time.sleep(60)
    '''3〉查询快照信息'''
    snapshot_info = snap_common.get_snapshot_by_name(snap_name)
    cmd = 'date +%s'
    rc, stdout = common.run_command(master_ip, cmd)
    if -1 != snapshot_info:
        log.info('expire_time is %s, current time is %s, snap %s not delete!!!' %
                 (snapshot_info['expire_time'], stdout, snap_name))
    cmd = 'date +%s'
    rc, stdout = common.run_command(master_ip, cmd)
    numerical_time = int(stdout) + 30
    sys_time = str(numerical_time)
    cmd = 'date -d @%s' % sys_time
    common.run_command(master_ip, cmd)
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)