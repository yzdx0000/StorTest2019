# -*-coding:utf-8 -*
import os
import time

import utils_path
import common
import snap_common
import log
import prepare_clean
import make_fault
import tool_use
####################################################################################
#
# Author: liyao
# date 2018-04-20
# @summary：
#    快照revert过程中，断掉一个客户端的数据网，恢复数据网后，观察快照数据
# @steps:
#    1、部署3节点集群，配比4 2 1，部署三个客户端；
#    2、客户端1在目录/mnt/parastor/snap/下执行vdbench创建文件；
#    3、对目录/mnt/parastor/snap/创建快照；
#    4、客户端1在目录/mnt/parastor/snap/下执行vdbench修改文件；
#    5、断开客户端2的数据网，对快照进行revert；
#    6、revert完成后，恢复客户端2的数据网，客户端2在/mnt/parastor/snap/下执行vdbench进行数据校验；
#    7、删除快照；
#    8、检查是否有快照路径入口；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              # /mnt/liyao/snap/snap_13_1_3_13
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   # /snap/snap_13_1_3_13


def vdbench_run(anchor_path, node1_ip, run_create=False, run_write=False, run_check=False):
    obj_vdbench = tool_use.Vdbenchrun()
    if run_create is True:
        rc = obj_vdbench.run_create(anchor_path, '/tmp', node1_ip)
        if rc != 0:
            log.error('rc = %d' % rc)
            raise Exception("vdbench create failed!!!!!!")
    if run_write is True:
        rc = obj_vdbench.run_write(anchor_path, node1_ip)
        if rc != 0:
            raise Exception("vdbench write failed!!!!!!")
    if run_check is True:
        rc = obj_vdbench.run_check(anchor_path, '/tmp', node1_ip)
        if rc != 0:
            raise Exception("vdbench check failed!!!!!!")


def grab_client_global(client_ip):
    '''获取私有客户端数据网'''
    node_obj = common.Node()
    sys_node_id_lst = node_obj.get_nodes_id()
    eth_list, data_ip_list, ip_mask_lst = node_obj.get_node_eth(sys_node_id_lst[0])

    cmd = 'ssh %s ip addr | grep global | grep inet' % client_ip
    rc, stdout = common.run_command(client_ip, cmd)
    line_lst = stdout.splitlines()
    data_ips_part = []

    '''获取集群节点数据网IP的前两部分'''
    for ip in data_ip_list:
        ip_part_dist1 = ip.split('.')[0]
        ip_part_dist2 = ip.split('.')[1]
        ip_part = [ip_part_dist1, ip_part_dist2]
        ip_specific = '.'.join(ip_part)
        data_ips_part.append(ip_specific)

    eth_name_lst = []
    ip_mask_lst = []
    for line in line_lst:
        external_client_ip = line.split()[1].split('/')[0]
        eth_name = line.split()[-1]
        ip_mask = line.split()[1]
        ip_part_dist1 = external_client_ip.split('.')[0]
        ip_part_dist2 = external_client_ip.split('.')[1]
        ip_part = [ip_part_dist1, ip_part_dist2]
        client_ip_part = '.'.join(ip_part)
        if client_ip_part in data_ips_part:
            eth_name_lst.append(eth_name)
            ip_mask_lst.append(ip_mask)
    return eth_name_lst, ip_mask_lst


def case():
    '''2> 运行00vdbench脚本'''
    vdbench_run(SNAP_TRUE_PATH, snap_common.CLIENT_IP_1, run_create=True)

    cmd1 = 'scp -r /tmp/*fsd* root@%s:/tmp' % snap_common.CLIENT_IP_2
    # cmd2 = 'scp -r /tmp/vdb_control.file root@%s:/tmp' % snap_common.CLIENT_IP_3
    common.run_command(snap_common.CLIENT_IP_1, cmd1)
    # common.run_command(snap_common.CLIENT_IP_1, cmd2)

    '''3> 创建快照'''
    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH
    rc, stdout = snap_common.create_snapshot(snap_name, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name)
        raise Exception('create_snapshot %s failed!!!' % snap_name)

    '''4> 运行01vdbench脚本'''
    vdbench_run(SNAP_TRUE_PATH, snap_common.CLIENT_IP_1, run_write=True)

    '''5> 断开客户端2的数据网，对快照进行revert'''
    eth_name_list, ip_mask_lst = grab_client_global(snap_common.CLIENT_IP_2)
    make_fault.down_eth(snap_common.CLIENT_IP_2, eth_name_list)
    log.info('waiting for 180s')

    snap_info = snap_common.get_snapshot_by_name(snap_name)
    snap_id = snap_info['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id)
    if rc != 0:
        log.error("revert snapshot %s failed!!!" % snap_name)
        raise Exception("revert snapshot %s failed!!!" % snap_name)
    snap_common.check_revert_finished(snap_id)

    time.sleep(10)

    '''5> 恢复客户端2的数据网，客户端2对数据进行校验'''
    '''恢复网络'''
    make_fault.up_eth(snap_common.CLIENT_IP_2, eth_name_list, ip_mask_lst)

    '''数据校验'''
    vdbench_run(SNAP_TRUE_PATH, snap_common.CLIENT_IP_2, run_check=True)

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

    '''6> 删除快照'''
    rc, stdout = snap_common.delete_snapshot_by_name(FILE_NAME)
    if 0 != rc:
        log.error('%s delete snapshot failed!!!' % (FILE_NAME))
        raise Exception('%s delete snapshot failed!!!' % (FILE_NAME))

    time.sleep(15)

    '''7>3个客户端检查快照路径入口是否存在'''
    snap_path = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name)
    snap_common.check_snap_entry(snap_path)
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)