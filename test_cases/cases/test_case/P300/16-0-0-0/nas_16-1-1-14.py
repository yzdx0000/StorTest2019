# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import re
import utils_path
import common
import nas_common
import log
import get_config
import json
import random
import prepare_clean
import make_fault
import tool_use

####################################################################################
#
# Author: liyao
# date 2018-08-27
# @summary：
#    数据网中断对业务的影响（未绑定VIP）
# @steps:
#    1、创建ad访问分区，创建访问分区，启动NAS，配置vip地址池分配方式为动态
#    2、创建共享目录，导出并授权某个用户的导出权限（mount时，server端输入配置vip池的域名;需要提前进入/etc/resolv.conf添加nameserver:[svip对应的虚ip]）
#    3、通过pscli --command=get_subnets命令查看业务子网信息
#    4、添加vip池，输入正确的vip地址、掩码等参数
#    5、客户端进行域名解析，并添加主机路由表，检查vip池的域名是否可以ping通
#    6、创建共享目录并授权某个用户的导出权限
#    7、NFS客户端成功挂载到某机头节点并使用vdbench进行读写业务，断掉客户端的部分数据网
#    8、查看读写是否正常，恢复客户端数据网；断掉机头节点的全部数据网，查看业务读写是否正常
#    9、删除读写数据
#    10、将域名解析文件恢复原状
#    11、删除nfs_export_auth_clients, nfs_exports, 访问分区及ad认证服务器，清理环境
#
# @changelog：
####################################################################################
VOLUME_NAME = get_config.get_one_volume_name()
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0].replace('-', '_')                 # 本脚本名字
NAS_PATH = get_config.get_one_nas_test_path()                            # /mnt/volume/nas_test_dir
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)             # /mnt/volume/nas_test_dir/nas_16_1_1_11
BASE_NAS_PATH = os.path.dirname(NAS_PATH)                                # /mnt/volume
NAS_PATH_BASENAME = os.path.basename(NAS_PATH)                           # nas_test_dir
SYSTEM_IP_0 = get_config.get_parastor_ip(0)
SYSTEM_IP_1 = get_config.get_parastor_ip(1)
SYSTEM_IP_2 = get_config.get_parastor_ip(2)


def umount(auth_name_ip, local_path):
    cmd = 'umount -l %s' % local_path
    rc, stdout = common.run_command(auth_name_ip, cmd)
    return rc


def judge_vdb_result(anchor_path, journal_path, exe_ip):
    obj_vdb = tool_use.Vdbenchrun(size="(64k,30,128k,35,256k,30,1m,5)", elapsed=60)
    rc = obj_vdb.run_create(anchor_path, journal_path, exe_ip)
    if rc != 0:
        print ('***** %s ******' % rc)
        common.except_exit('vdbench create failed !!!')
    else:
        print ('***** %s *****' % rc)
        return 0


def get_client_eth(node_ip, subnet_mask):
    '''获取客户端网卡信息'''
    mask_filter_mark = '/' + subnet_mask
    tmp_client_ip = '.'.join(nas_common.SUBNET_SVIP.split('.')[:-1]) + '.' + nas_common.CLIENT_IP_3.split('.')[-1]
    cmd = 'ip addr |grep inet |grep %s |grep -v %s |grep -v %s' % (mask_filter_mark, nas_common.CLIENT_IP_3, tmp_client_ip)
    rc, stdout = common.run_command(node_ip, cmd)
    eth_lines = stdout.splitlines()
    total_eth = []
    for line in eth_lines:
        total_eth.append(line.split()[-1])
    return total_eth


def get_mount_eth(mount_vip, nodes_ip_list):
    '''获取nfs客户端挂载对应的网卡'''
    for node_ip in nodes_ip_list:
        cmd = 'ip addr |grep %s' % mount_vip
        rc, stdout = common.run_command(node_ip, cmd)
        if 0 == rc:
            mount_eth = stdout.strip().split()[-1]
            return mount_eth, node_ip
    else:
        return -1, -2


def check_eth_svip(svip_judge, eth_judge, stdout, node_ip):
    split_line_list = stdout.splitlines()
    for line in split_line_list:
        if svip_judge in line:
            for mem in eth_judge:
                if mem in line:
                    log.info('svip is on %s' % node_ip)
                    return True, mem, node_ip   # 寻找并记录svip飘到的网卡及节点
                else:
                    common.except_exit("svip in %s, not in %s" % (line.split()[-1], eth_judge))
    return False, -1, -2


def case():
    '''函数执行主体'''
    """创建访问分区"""
    obj_node = common.Node()
    nodes_id_list = obj_node.get_nodes_id()
    nodes_id_str = ','.join(str(p) for p in nodes_id_list)
    access_zone_name = 'az_' + FILE_NAME
    exe_info = nas_common.create_access_zone(nodes_id_str, access_zone_name)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('create access zone %s failed !!!' % access_zone_name)
        raise Exception('create access zone %s failed !!!' % access_zone_name)
    access_zone_id = exe_info['result']

    """启动nas服务"""
    exe_info = nas_common.enable_nas(access_zone_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('enable nas failed !!!')
        raise Exception('enable nas failed !!!')

    '''2> 在az1上创建业务子网，配置正确的az1 ID、svip、掩码、网关，与接口信息'''
    subnet_name = 'subnet_' + FILE_NAME
    ip_family = 'IPv4'
    subnet_mask_info = nas_common.SUBNET_MASK
    exe_info = nas_common.create_subnet(access_zone_id=access_zone_id, name=subnet_name, ip_family=ip_family,
                                        svip=nas_common.SUBNET_SVIP, subnet_mask=subnet_mask_info,
                                        subnet_gateway=nas_common.SUBNET_GATEWAY,
                                        network_interfaces=nas_common.SUBNET_NETWORK_INTERFACES)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('create subnet %s failed !!!' % subnet_name)
        raise Exception('create subnet %s failed !!!' % subnet_name)
    subnet_id = exe_info['result']

    """通过命令行ip addr观察SVIP绑定到哪个节点ethx上"""
    obj_node = common.Node()
    nodes_ip_list = obj_node.get_nodes_ip()
    svip_judge = nas_common.SUBNET_SVIP + '/' + nas_common.SUBNET_MASK
    eth_judge_str = nas_common.SUBNET_NETWORK_INTERFACES
    eth_judge_lst = eth_judge_str.split(',')
    for node_ip in nodes_ip_list:
        cmd = 'ip addr'
        rc, stdout = common.run_command(node_ip, cmd)
        rc, svip_eth_1, first_node_ip = check_eth_svip(svip_judge, eth_judge_lst, stdout, node_ip)
        if rc:
            break
    else:
        common.except_exit('svip is not on any system node !!!')

    '''3> 通过pscli --command=get_subnets命令查看业务子网信息'''
    exe_info = nas_common.get_subnets(subnet_id)
    subnet = exe_info['result']['subnets'][0]
    if subnet['id'] == subnet_id and subnet['name'] == subnet_name and subnet['svip'] == nas_common.SUBNET_SVIP and \
            subnet['subnet_mask'] == int(nas_common.SUBNET_MASK) and subnet[
        'subnet_gateway'] == nas_common.SUBNET_GATEWAY \
            and subnet['network_interfaces'][0] == nas_common.SUBNET_NETWORK_INTERFACES:
        log.info('subnet params are correct !')
    else:
        log.error('subnet params are wrong !!! ')
        raise Exception('subnet params are wrong !!!')

    '''4> 添加vip池，输入正确的vip地址、掩码等参数'''
    allocation_method_list = ['DYNAMIC']
    used_protocol = 'NAS'
    used_method = random.choice(allocation_method_list)
    exe_info = nas_common.add_vip_address_pool(subnet_id, nas_common.VIP_DOMAIN_NAME, nas_common.VIP_ADDRESSES,
                                               used_protocol, used_method)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('add vip address pool failed !!!')
        raise Exception('add vip address pool failed !!!')
    vip_pool_id = exe_info['result']

    '''5> 客户端进行域名解析，并添加主机路由表，检查vip池的域名是否可以ping通'''
    """域名解析"""
    nameserver_conf_ip = nas_common.CLIENT_IP_3
    add_nameserver_path = '/etc/resolv.conf'
    resolv_file_bak = '/etc/resolv.conf.bak'
    cmd = 'cp %s %s' % (add_nameserver_path, resolv_file_bak)   # 备份域名解析文件
    rc, stdout = common.run_command(nameserver_conf_ip, cmd)
    common.judge_rc(rc, 0, 'resolve file backup failed !!!')

    cmd = 'echo "nameserver %s" > %s' % (nas_common.SUBNET_SVIP, add_nameserver_path)
    rc, stdout = common.run_command(nameserver_conf_ip, cmd)
    common.judge_rc(rc, 0, 'resolve domain name failed !!!')

    """客户端添加主机路由表"""
    vip_ip_parts = re.split('[.-]', nas_common.VIP_ADDRESSES)
    vip_start_part = vip_ip_parts[3]
    vip_end_part = vip_ip_parts[4]
    diff_num = int(vip_end_part) - int(vip_start_part)  # vip地址之间的差距，用于后续路由表的循环添加
    typical_vip_ip = []
    #typical_eth = nas_common.SUBNET_NETWORK_INTERFACES.split(',')[0]
    ob_client = common.Client()
    tmp_client_ip = '.'.join(nas_common.SUBNET_SVIP.split('.')[:-1]) + '.' + nameserver_conf_ip.split('.')[-1]
    rc, typical_eth = ob_client.get_client_eth_by_ip(clientip=nameserver_conf_ip, ip_for_eth=tmp_client_ip)
    common.judge_rc(rc, 0, 'failed')
    for i in range(0, diff_num + 1):
        tmp_vip_ip = vip_ip_parts[0] + '.' + vip_ip_parts[1] + '.' + vip_ip_parts[2] + '.' + str(
            int(vip_ip_parts[3]) + i)
        typical_vip_ip.append(tmp_vip_ip)
        cmd = 'route add -host %s dev %s' % (tmp_vip_ip, typical_eth)
        common.run_command(nameserver_conf_ip, cmd)

    """检查vip池的域名是否可以被客户端ping通"""
    log.info('waiting for 10s')
    time.sleep(10)
    rc = make_fault.check_ping(nas_common.VIP_DOMAIN_NAME, nameserver_conf_ip)
    if rc is not True:
        common.except_exit('client %s can not connect to %s !!!' % (nameserver_conf_ip, nas_common.VIP_DOMAIN_NAME))

    '''6> 创建共享目录并授权某个用户的导出权限'''
    """检查NAS_PATH是否存在"""
    cmd = 'ls %s' % NAS_PATH
    rc, stdout = common.run_command(SYSTEM_IP_1, cmd)
    if rc != 0:
        cmd = 'mkdir -p %s' % NAS_TRUE_PATH
        common.run_command(SYSTEM_IP_1, cmd)
    else:
        cmd = 'mkdir %s' % NAS_TRUE_PATH
        common.run_command(SYSTEM_IP_1, cmd)

    """在存储卷里创建目录并导出共享目录"""
    log.info('waiting for 15s')
    time.sleep(15)

    export_name = 'nfs_exp_test'
    create_export_path = VOLUME_NAME + ':/' + os.path.join(NAS_PATH_BASENAME, FILE_NAME)
    export_sys_ip = SYSTEM_IP_2
    exe_info = nas_common.create_nfs_export(access_zone_id, export_name, create_export_path)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('create nfs export failed !!!')

    exe_info = nas_common.get_nfs_exports()
    nfs_info = exe_info['result']['exports']
    for mem in nfs_info:
        if mem['export_name'] == export_name:
            export_id = mem['id']
            break
    else:
        common.except_exit('nfs export information is wrong !!!')

    """授权某个用户的导出权限"""
    permission_level = 'rw'
    cmd = 'ip addr | grep %s | grep inet' % tmp_client_ip
    rc, stdout = common.run_command(nameserver_conf_ip, cmd)
    common.judge_rc(rc, 0, 'ip addr execution failed !!!')

    auth_name_ip = stdout.split()[1].split('/')[0]
    exe_info = nas_common.add_nfs_export_auth_clients(export_id, auth_name_ip, permission_level)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('add nfs export auth clients failed !!!')
    export_auth_id = exe_info['result'][0]
    log.info('waiting for 15s')
    time.sleep(15)

    """nfs客户端挂载"""
    mount_path = nas_common.VIP_DOMAIN_NAME + ':/' + NAS_TRUE_PATH
    local_path = os.path.join('/home/local', FILE_NAME)
    cmd = 'mkdir -p %s' % local_path
    common.run_command(nameserver_conf_ip, cmd)

    rc = umount(nameserver_conf_ip, local_path)   # 检查本地路径是否已经mount
    if rc != 0:
        log.info('local path did not mount')

    cmd = 'mount -t nfs %s %s' % (mount_path, local_path)
    rc, stdout = common.run_command(nameserver_conf_ip, cmd)
    common.judge_rc(rc, 0, 'mount nfs failed !!!')

    log.info('waiting for 10s')
    time.sleep(10)

    exe_info = nas_common.get_nfs_export_auth_clients(export_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('mount nfs failed !!!')

    """查询nfs客户端挂载的vip，并获取对应网卡及mount对应的vip"""
    cmd = 'mount |grep %s' % nas_common.VIP_DOMAIN_NAME
    rc, stdout = common.run_command(nameserver_conf_ip, cmd)
    common.judge_rc(rc, 0, 'mount execution failed !!!')
    target_line = stdout.strip()
    mount_vip = re.split('[=)]', target_line)[-2]
    mount_eth, exe_node_ip = get_mount_eth(mount_vip, nodes_ip_list)
    if mount_eth == -1:
        common.except_exit('get mount eth failed !!!')

    '''7> NFS客户端成功挂载到某机头节点并使用vdbench进行读写业务，断掉客户端的部分数据网'''
    p1 = Process(target=judge_vdb_result, args=(local_path, local_path, nameserver_conf_ip))
    p1.start()

    client_eth_list = get_client_eth(nameserver_conf_ip, subnet_mask_info)
    client_fault_eth = client_eth_list[-2:]
    rc = make_fault.down_eth(nameserver_conf_ip, client_fault_eth)
    common.judge_rc(rc, 0, 'down data eth failed !!!')

    p1.join()

    if p1.exitcode != 0:
        common.except_exit('vdbench create data failed !!!')

    '''8> 查看读写是否正常，恢复客户端数据网；断掉机头节点的全部数据网，查看业务读写是否正常'''
    log.info('waiting for 10s')
    time.sleep(10)

    rc = make_fault.up_eth(nameserver_conf_ip, client_fault_eth)
    common.judge_rc(rc, 0, 'up client data eth failed !!!')

    """断掉机头节点的全部数据网，查看业务读写是否正常"""
    p2 = Process(target=judge_vdb_result, args=(local_path, local_path, nameserver_conf_ip))
    p2.daemon = True
    p2.start()

    sys_node_id = obj_node.get_node_id_by_ip(exe_node_ip)
    sys_node_eth, data_ip_list, ip_mask_lst = obj_node.get_node_eth(sys_node_id)
    sys_fault_eth = sys_node_eth   # 断掉机头节点的全部数据网
    print ('*********')
    print sys_fault_eth
    print ('*********')
    rc = make_fault.down_eth(exe_node_ip, sys_fault_eth)
    common.judge_rc(rc, 0, 'down sys_node eth failed !!!')

    time_limitation = 120
    time_used = 0
    while p2.is_alive() is True:
        log.info('waiting for 10s')
        time.sleep(10)
        time_used = time_used + 10
        if time_used > time_limitation:
            common.except_exit('vdbench is timeout !!!')

    start_time = time.time()
    while True:
        time.sleep(20)
        if common.check_ping(exe_node_ip):
            break
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        log.info('node %s cannot ping pass %dh:%dm:%ds' % (exe_node_ip, h, m, s))
    log.info('wait 20s')
    time.sleep(20)

    '''9> 恢复节点数据网，删除vdbench创建的数据'''
    rc = make_fault.up_eth(exe_node_ip, sys_node_eth, ip_mask_lst)
    common.judge_rc(rc, 0, 'up sys_node eth failed !!!')

    rc = umount(nameserver_conf_ip, local_path)
    common.judge_rc(rc, 0, 'umount %s failed !!!' % local_path)

    deleted_file_path = os.path.dirname(local_path)
    deleted_file_path = os.path.join(deleted_file_path, '*')
    common.rm_exe(nameserver_conf_ip, deleted_file_path)

    '''10> 将域名解析文件恢复原状'''
    cmd = 'mv %s %s' % (resolv_file_bak, add_nameserver_path)
    rc, stdout = common.run_command(nameserver_conf_ip, cmd)
    common.judge_rc(rc, 0, 'resolv file recovery failed !!!')

    """从客户端删除已经添加的路由表"""
    for i in range(0, diff_num + 1):
        cmd = 'route delete -host %s dev %s' % (typical_vip_ip[i], typical_eth)
        common.run_command(nameserver_conf_ip, cmd)

    '''11> 清理环境'''
    delete_sys_path = os.path.join(NAS_PATH, '*')
    common.rm_exe(export_sys_ip, delete_sys_path)

    return


def nas_main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    # nas_common.cleaning_environment()
    case()
    prepare_clean.nas_test_clean()
    log.info('%s succeed!' % FILE_NAME)

    return


if __name__ == '__main__':
    nas_main()










