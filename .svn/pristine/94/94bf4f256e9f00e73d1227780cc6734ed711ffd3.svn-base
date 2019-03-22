# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time

import utils_path
import common
import snap_common
import log
import prepare_clean
import make_fault

####################################################################################
#
# Author: liyao
# date 2018-04-20
# @summary：
#    创建文件快照，一个客户端修改文件的过程中，断掉另一个客户端的数据网，恢复数据网后，观察快照数据
# @steps:
#    1、部署3节点集群，配比4 2 1；
#    2、在/mnt/parastor/snap/下创建文件snap_file（大小1g）；
#    3、客户端1对文件/mnt/parastor/snap/snap_file创建快照a1；
#    4、断开客户端2的数据网，客户端1对文件/mnt/parastor/snap/test_file1修改；
#    5、修改完成后，恢复客户端2的数据网，客户端2对数据进行校验；
#    6、删除快照；
#    7、检查是否有快照路径入口；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              # /mnt/liyao/snap/snap_13_1_3_11
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   # /snap/snap_13_1_3_11


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


def file_revision(client_ip, file):
    '''指定客户端对文件进行修改'''
    cmd = "ssh %s echo 'nice to meet you'>> %s" % (client_ip, file)
    common.run_command(client_ip, cmd)


def case():
    '''2> 创建1g文件'''
    file_test_1 = os.path.join(SNAP_TRUE_PATH, 'file_test_1')
    cmd = 'dd if=/dev/zero of=%s bs=1M count=1024' % file_test_1
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 获取md5值
    md5_file = snap_common.get_file_md5(snap_common.CLIENT_IP_1, file_test_1)

    '''3> 对文件创建快照'''
    snap_name = FILE_NAME + '_snapshot1'
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH + '/' + 'file_test_1'
    rc, stdout = snap_common.create_snapshot(snap_name, path)
    if 0 != rc:
        log.error('create_snapshot %s failed!!!' % snap_name)
        raise Exception('create_snapshot %s failed!!!' % snap_name)

    '''4> 断开客户端2的数据网，客户端1对文件修改'''
    eth_name_list, ip_mask_lst = grab_client_global(snap_common.CLIENT_IP_2)
    p1 = Process(target=file_revision, args=(snap_common.CLIENT_IP_1, file_test_1,))
    p2 = Process(target=make_fault.down_eth, args=(snap_common.CLIENT_IP_2, eth_name_list))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    if p1.exitcode != 0:
        raise Exception("file revision is failed!!!!!!")

    '''5> 恢复客户端2的数据网，客户端2对数据进行校验'''

    '''恢复网络'''
    make_fault.up_eth(snap_common.CLIENT_IP_2, eth_name_list, ip_mask_lst)

    '''获取md5值'''
    snap_file = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name)
    md5_snap = snap_common.get_file_md5(snap_common.CLIENT_IP_2, snap_file)

    ''' 数据校验'''
    if md5_snap != md5_file:
        log.error('md5 is not right!!!')
        raise Exception('md5 is not right!!!')

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
    rc, stdout = snap_common.delete_snapshot_by_path(path)
    if 0 != rc:
        log.error('%s delete snapshot failed!!!' % (path))
        raise Exception('%s delete snapshot failed!!!' % (path))

    time.sleep(15)

    '''7> 3个客户端检查快照路径入口是否存在'''
    snap_common.check_snap_entry(snap_file)

    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)