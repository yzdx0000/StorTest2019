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
import make_fault

####################################################################################
#
# Author: baorb
# date 2018-04-12
# @summary：
#    快照revert过程中，断掉主lmos节点的数据网
# @steps:
#    1、部署3节点集群，配比4 2 1；
#    2、在目录/mnt/parastor/snap/下运行vdbench 00.init脚本（vdbench写入数据）；
#    3、对目录/mnt/parastor/snap/创建快照a1；
#    4、在目录/mnt/parastor/snap/下使用vdbench修改数据；
#    5、对快照a1进行revert，revert过程中断开主lmos的数据网；
#    6、在目录/mnt/parastor/snap/下使用vdbench进行数据校验；
#    7、删除快照；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              #/mnt/volume1/snap/snap_13_0_0_0
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   #/snap/snap_13_0_0_0


def case():
    '''2> 运行00vdbench脚本创建数据'''
    tool_use.vdbench_run(SNAP_TRUE_PATH, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, run_create=True)

    #cmd1 = 'scp -r /tmp/vdb_control.file root@%s:/tmp' % snap_common.CLIENT_IP_2
    #cmd2 = 'scp -r /tmp/vdb_control.file root@%s:/tmp' % snap_common.CLIENT_IP_3
    #common.run_command(snap_common.CLIENT_IP_1, cmd1)
    #common.run_command(snap_common.CLIENT_IP_1, cmd2)

    '''3> 创建快照'''
    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name)
        raise Exception('create_snapshot %s failed!!!' % snap_name)

    '''4> 运行01vdbench脚本修改数据'''
    tool_use.vdbench_run(SNAP_TRUE_PATH, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, run_write=True)

    '''5> 对快照进行revert，同时断开主lmos的数据网'''
    fault_node_id = snap_common.get_lmos_node_id()
    node_obj = common.Node()
    sys_node_id_lst = node_obj.get_nodes_id()
    ext_node_id = None
    for node_id in sys_node_id_lst:
        if node_id != int(fault_node_id):
            ext_node_id = node_id
            break

    fault_node_ip = node_obj.get_node_ip_by_id(fault_node_id)
    eth_list, data_ip_list, ip_mask_lst = node_obj.get_node_eth(fault_node_id)
    ext_node_ip = node_obj.get_node_ip_by_id(ext_node_id)

    '''down掉数据网'''
    make_fault.down_eth(fault_node_ip, eth_list)
    log.info('waiting for 180s')
    time.sleep(180)
    wait_time = 180

    '''执行revert'''
    snap_info = snap_common.get_snapshot_by_name(snap_name, fault_node_ip=fault_node_ip)
    snap_id = snap_info['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id, fault_node_ip=fault_node_ip)
    while 0 != rc:
        if wait_time > 300:
            log.error('find master time too long !!!')
            raise Exception('find master time too long !!!')
        log.info('waiting for 20s')
        time.sleep(20)
        wait_time = wait_time + 20
        rc, stdout = snap_common.revert_snapshot_by_id(snap_id, fault_node_ip=fault_node_ip)

    # if rc != 0:
    #    log.error("revert snapshot %s failed!!!" % snap_name)
    #    raise Exception("revert snapshot %s failed!!!" % snap_name)
    snap_common.check_revert_finished(snap_id, fault_node_ip=fault_node_ip)

    '''6> 运行02vdbench脚本进行数据校验'''
    tool_use.vdbench_run(SNAP_TRUE_PATH, snap_common.CLIENT_IP_1, snap_common.CLIENT_IP_2, run_check=True)
    start_time = time.time()
    while True:
        time.sleep(20)
        if common.check_ping(fault_node_ip):
            break
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        log.info('node %s cannot ping pass %dh:%dm:%ds' % (fault_node_ip, h, m, s))
    log.info('wait 20s')
    time.sleep(20)
    '''up数据网'''
    make_fault.up_eth(fault_node_ip, eth_list, ip_mask_lst)

    '''检查数据是否完全修复'''
    log.info('waiting for 120s')
    time.sleep(120)
    count = 0
    while True:
        count += 1
        log.info("the %d times check badjobnr" % count)
        log.info("wait 60 seconds")
        time.sleep(60)
        if common.check_badjobnr():
            break

    '''7> 删除快照'''
    rc, stdout = snap_common.delete_snapshot_by_name(FILE_NAME)
    if 0 != rc:
        log.error('%s delete snapshot failed!!!' % (FILE_NAME))
        raise Exception('%s delete snapshot failed!!!' % (FILE_NAME))
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)