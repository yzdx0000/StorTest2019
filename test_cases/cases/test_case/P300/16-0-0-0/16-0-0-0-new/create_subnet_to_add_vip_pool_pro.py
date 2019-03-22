# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random
import re

import utils_path
import common
import log
import prepare_clean
import get_config
import nas_common
import make_fault
import snap_common
import tool_use

"""
 Author: liangxy
 date 2018-12-3
 @summary：
    创建业务子网，添加vip池，参数为参数全集，覆盖客户端挂载
 @steps:
    1、根据是否继承的标志位决定是否清除环境
    2、生成参数字典
    3、为访问区创建业务子网、添加vip池
    4、检查所有访问区的服务状态/子网状态是否正常
    5、客户端以域名挂载
    6、根据遗传标志位决定是或否清除环境

 @changelog：
 
"""
# todo:负载均衡及ip故障转移未交付
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0].replace('-', '_')                 # 本脚本名字
NAS_PATH = get_config.get_one_nas_test_path()                            # /mnt/volume/nas_test_dir
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)             # /mnt/volume/nas_test_dir/nas_16_6_0_16
BASE_NAS_PATH = os.path.dirname(NAS_PATH)                                # /mnt/volume
NAS_PATH_BASENAME = os.path.basename(NAS_PATH)                           # nas_test_dir


def generate_params_subnet(node_num=None):
    params_dict = {}
    params_dict_lst = []

    # expect_rst为True的话就是期望通过，commom.judge_rc的判断flag也是Ture,才会验证功能
    expect_rst = True
    """
    create_subnet(access_zone_id, name, ip_family, svip, subnet_mask, subnet_gateway, network_interfaces, mtu=None,
                  description=None, print_flag=True, fault_node_ip=None)
    """
    ip_family_lst = ["IPv4", "IPv4"]
    svip_lst = [nas_common.SUBNET_SVIP]
    subnet_mask_lst = ["0", "16", "22", "24"]
    subnet_gateway_lst = [nas_common.SUBNET_GATEWAY]
    network_interfaces_lst = [nas_common.SUBNET_NETWORK_INTERFACES, nas_common.SUBNET_2_NETWORK_INTERFACES]

    mtu_lst = [None, "576", "1500", "9000"]
    description_lst = [None, "aaaaa0", "_bbbbbbbbbbbbbbbbb1", "c", "d_", "_e"]

    # p_lst_p = [ip_family_lst, svip_lst, subnet_mask_lst, subnet_gateway_lst, network_interfaces_lst, mtu_lst,]
    for ip_family in ip_family_lst:
        params_dict = {}
        params_dict = {'ip_family': ip_family}

        for svip in svip_lst:
            params_dict.update({'svip': svip})
            for subnet_mask in subnet_mask_lst:
                params_dict.update({'subnet_mask': subnet_mask})
                for subnet_gateway in subnet_gateway_lst:
                    params_dict.update({'subnet_gateway': subnet_gateway})
                    for network_interfaces in network_interfaces_lst:
                        params_dict.update({'network_interfaces': network_interfaces})
                        for mtu in mtu_lst:
                            params_dict.update({'mtu': mtu})
                            for description in description_lst:
                                params_dict.update({'description': description})
                                # log.info("OK@{}".format(params_dict))
                                params_dict_lst.append(params_dict)

    return params_dict_lst


def generate_params_vip(node_num, vip_add):
    params_dict = {}
    params_dict_lst = []

    # expect_rst为True的话就是期望通过，commom.judge_rc的判断flag也是Ture,才会验证功能
    expect_rst = True
    """
    add_vip_address_pool(subnet_id, domain_name, vip_addresses, supported_protocol, allocation_method,
                         load_balance_policy=None, ip_failover_policy=None, rebalance_policy=None, print_flag=True,
                         fault_node_ip=None)
    """
    domain_name_lst = [nas_common.VIP_DOMAIN_NAME]
    vip_choose = ""
    vip_add_string = ",".join(vip_add)
    if node_num < 3:
        vip_choose = vip_add_string
    else:
        first_ip = str(vip_add[0])
        end_ip = vip_add[-1]
        end_ex = str(end_ip).split(".")
        end_ex_str = str(end_ex[-1])
        vip_choose = first_ip + "-" + end_ex_str
        log.info("vip fusion:".format(vip_choose))
    vip_addresses_lst = [vip_add_string, vip_choose]
    supported_protocol_lst = [nas_common.NAS]
    allocation_method_lst = [nas_common.DYNAMIC, nas_common.STATIC]

    load_balance_policy_lst = [None, nas_common.BALANCE_LB_ROUND_ROBIN, nas_common.BALANCE_LB_CONNECTION_COUNT, nas_common.BALANCE_LB_CPU_USAGE, nas_common.BALANCE_LB_THROUGHPUT]
    # load_balance_policy_lst = [None, nas_common.BALANCE_LB_ROUND_ROBIN, nas_common.BALANCE_LB_CONNECTION_COUNT]
    # ip_failover_policy_lst = [None, nas_common.IP_IF_ROUND_ROBIN, nas_common.IP_IF_CONNECTION_COUNT, nas_common.IP_IF_CPU_USAGE, nas_common.IP_IF_THROUGHPUT]
    ip_failover_policy_lst = [None, nas_common.IP_IF_ROUND_ROBIN, nas_common.IP_IF_CONNECTION_COUNT]
    rebalance_policy_lst = [None, nas_common.IP_RB_AUTOMATIC, nas_common.IP_RB_DISABLED]
    for domain_name in domain_name_lst:
        params_dict = []
        params_dict = {'domain_name': domain_name}
        for vip_addresses in vip_addresses_lst:
            params_dict.update({'vip_addresses': vip_addresses})
            for supported_protocol in supported_protocol_lst:
                params_dict.update({'supported_protocol': supported_protocol})
                for allocation_method in allocation_method_lst:
                    params_dict.update({'allocation_method': allocation_method})
                    for load_balance_policy in load_balance_policy_lst:
                        params_dict.update({'load_balance_policy': load_balance_policy})
                        for ip_failover_policy in ip_failover_policy_lst:
                            params_dict.update({'ip_failover_policy': ip_failover_policy})
                            for rebalance_policy in rebalance_policy_lst:
                                params_dict.update({'rebalance_policy': rebalance_policy})
                                # log.info("OK@{}".format(params_dict))
                                params_dict_lst.append(params_dict)

    return params_dict_lst


def case():

    """函数主体"""
    node_obj = common.Node()
    node_list_all = node_obj.get_nodes_id()
    node_list_string = []
    for node_id_int in node_list_all:
        node_list_string.append(str(node_id_int))

    lenth_nodes_up = len(node_list_string)
    """默认继承True，遗留（不删除）子网True"""
    flag_inherit = False
    flag_genetic = True
    log.info("1> 根据是否继承的标志位{}决定是(False)否(True)清除并创建新的nas环境".format(flag_inherit))
    access_zone_id = '0'
    access_zone_id_lst = []
    az_new_name = '_'
    all_nodes_string = ",".join(node_list_string)
    for_loop_time = 1

    if flag_inherit:
        log.info("inherit, would not delete")
        msg_get_az = nas_common.get_access_zones(print_flag=False)
        common.judge_rc(msg_get_az['err_no'], 0, "get access zone ")
        if len(msg_get_az['result']['access_zones']) < 1:
            log.info("There is no access zone to inherit:{}".format(msg_get_az['result']))
            flag_inherit = False
        else:

            for az in msg_get_az['result']['access_zones']:
                access_zone_id_lst.append(az['id'])
    if not flag_inherit:
        log.info("no access zone to inherit,create a new one")
        # clean 之后要出创建nas的起始目录
        prepare_clean.nas_test_clean()
        msg_crt_dir = nas_common.create_file(path=nas_common.ROOT_DIR, posix_permission="rwxr-xr-x")
        common.judge_rc(msg_crt_dir['err_no'], 0, "create dir {}".format(nas_common.ROOT_DIR))
        az_new_name = "az_" + str(time.localtime().tm_hour) + str(time.localtime().tm_min) + str(
            time.localtime().tm_sec)
        msg_crt_az = nas_common.create_access_zone(node_ids=all_nodes_string, name=az_new_name)
        common.judge_rc(msg_crt_az['err_no'], 0, "create new access zone")
        access_zone_id = msg_crt_az["result"]
        access_zone_id_lst.append(access_zone_id)

    for idd in access_zone_id_lst:
        msg_enable_nas = nas_common.enable_nas(access_zone_id=idd, print_flag=False)
        common.judge_rc(msg_enable_nas['err_no'], 0, "if it was enable?", False)
    access_zone_id = random.choice(access_zone_id_lst)
    log.info("aceess_zone_id list is {}, az id is {}".format(access_zone_id_lst, access_zone_id))
    log.info("2> 生成参数字典")

    crt_sub_param_lst = generate_params_subnet(len(access_zone_id_lst))
    # log.info("crt_sub_param_lst is {}".format(len(crt_sub_param_lst)))
    # msg_get_az 肯定会有
    msg_get_az = nas_common.get_access_zones(ids=access_zone_id, print_flag=False)
    common.judge_rc(msg_get_az['result']['access_zones'][0]['id'], access_zone_id, "get access zone ")
    node_id_lst_in_az = msg_get_az['result']['access_zones'][0]['node_ids']
    node_count = len(node_id_lst_in_az)
    vip_count = node_count * 4
    vip_org = str(nas_common.VIP_3_ADDRESSES)
    vip_org_lst = vip_org.split(",")
    if vip_count > len(vip_org_lst):
        common.except_exit(
            "conf file wrong;{} vips {} less than nodes*4 {}".format(len(vip_org_lst), vip_org_lst, vip_count))
    vip_add = random.sample(vip_org_lst, vip_count)


    crt_vip_param_lst = generate_params_vip(len(access_zone_id_lst), vip_add)
    log.info("crt_sub_param_lst long: {},{}; crt_vip_param_lst long: {},{}".format(
        len(crt_sub_param_lst), crt_sub_param_lst[0].keys(), len(crt_vip_param_lst), crt_vip_param_lst[0].keys()))

    log.info("3> 为访问区{}（节点：{}）创建业务子网、添加vip池".format(access_zone_id, node_id_lst_in_az))
    vip_pool_id = -1
    sub_net_id = -1
    for sub_net_para in crt_sub_param_lst:

        for vip_para in crt_vip_param_lst:
            log.info("clean ip pool {}".format(vip_pool_id))
            log.info("clean sub net {}".format(sub_net_id))

            if vip_pool_id != -1:
                msg_delete_vip = nas_common.delete_vip_address_pool(vip_address_pool_id=vip_pool_id, print_flag=False)
                common.judge_rc(msg_delete_vip['err_no'], 0, sub_net_id)
                if sub_net_id != -1:
                    msg_delete_subnet = nas_common.delete_subnet(subnet_id=sub_net_id, print_flag=False)
                    common.judge_rc(msg_delete_subnet['err_no'], 0, sub_net_id)

            # 循环的开头删除子网，以便跳出循环时保留了一个id
            log.info("3-{}-1> 为访问区{}创建业务子网".format(for_loop_time, access_zone_id))

            sub_net_name = "sub_" + str(time.localtime().tm_hour) + str(time.localtime().tm_min) + str(
                time.localtime().tm_sec)
            msg_crt_subnet = nas_common.create_subnet(access_zone_id=access_zone_id, name=sub_net_name,
                                                      ip_family=str(sub_net_para['ip_family']), svip=str(sub_net_para['svip']),
                                                      subnet_mask=str(sub_net_para['subnet_mask']),
                                                      subnet_gateway=str(sub_net_para['subnet_gateway']),
                                                      network_interfaces=str(sub_net_para['network_interfaces']),
                                                      mtu=str(sub_net_para['mtu']), description=str(sub_net_para['description']))
            common.judge_rc(msg_crt_subnet['err_no'], 0, "create subnet")
            sub_net_id = msg_crt_subnet['result']

            log.info("3-{}-2> 为业务子网{}添加vip池".format(for_loop_time, sub_net_id))

            msg_add_ip_pool = nas_common.add_vip_address_pool(subnet_id=sub_net_id, domain_name=str(vip_para['domain_name']),
                                                              vip_addresses=str(vip_para['vip_addresses']),
                                                              supported_protocol=str(vip_para['supported_protocol']),
                                                              allocation_method=str(vip_para['allocation_method']),
                                                              load_balance_policy=str(vip_para['load_balance_policy']),
                                                              ip_failover_policy=str(vip_para['ip_failover_policy']),
                                                              rebalance_policy=str(vip_para['rebalance_policy']))
            common.judge_rc(msg_add_ip_pool['err_no'], 0, "add vip pool")
            vip_pool_id = msg_add_ip_pool['result']

            log.info("4> 检查所有访问区{}的服务状态/子网状态是否正常".format(node_id_lst_in_az))
            node_id_lst_in_az_str = []
            for nid in node_id_lst_in_az:
                node_id_lst_in_az_str.append(str(nid))
            node_id_str = ",".join(node_id_lst_in_az_str)
            nas_service_check = nas_common.check_nas_status(get_node_id=node_id_str)
            common.judge_rc(nas_service_check, 0, "nas service check")
            vip_service_check = nas_common.check_svip_in_eth(sub_svip=str(sub_net_para['svip']),
                                                             sub_subnet_mask=str(sub_net_para['subnet_mask']),
                                                             sub_network_interfaces=str(sub_net_para['network_interfaces']))
            common.judge_rc(vip_service_check, 0, "vip service check", False)
            log.info("5> 客户端以域名挂载")
            file_test_flag = False
            if file_test_flag:
                #NAS_TRUE_PATH
                log.info("5-{}-1> 创建目录".format(for_loop_time))
                nfs_path_4crt = nas_common.ROOT_DIR + "nfs_dir_{}".format(for_loop_time)
                msg_crt_dir = nas_common.create_file(path=nfs_path_4crt, posix_permission="rwxr-xr-x")
                common.judge_rc(msg_crt_dir['err_no'], 0, "create dir {}".format(nfs_path_4crt))
                log.info("5-{}-2> 创建nfs导出".format(for_loop_time))
                nfs_export_name = "nfs_name_{}".format(for_loop_time)
                msg_exp_nfs = nas_common.create_nfs_export(access_zone_id=access_zone_id, export_name=nfs_export_name, export_path=nfs_path_4crt)
                common.judge_rc(msg_exp_nfs['err_no'], 0, "export nfs {}".format(nfs_export_name))
                nfs_ex_id = msg_exp_nfs['result']

                #auth_clients_name = nas_common.NFS_1_CLIENT_IP
                auth_clients_name = "*"
                log.info("5-{}-3> 添加NFS客户端{}".format(for_loop_time, nas_common.NFS_1_CLIENT_IP))
                msg_add_nfs_client = nas_common.add_nfs_export_auth_clients(export_id=nfs_ex_id, name=auth_clients_name,
                                                             permission_level='rw')
                common.judge_rc(msg_add_nfs_client['err_no'], 0, "add nfs client {}".format(auth_clients_name))
                log.info("5-{}-4> 创建一个文件，并写入内容".format(for_loop_time))
                case_id = random.choice(node_id_lst_in_az)
                case_ip = node_obj.get_node_ip_by_id(case_id)
                cmd = "echo 'test_{}' > {}/test".format(for_loop_time, NAS_PATH)
                rc, stdout = common.run_command(case_ip, cmd)
                common.judge_rc(rc, 0, '{} create_file failed:{}'.format(case_ip, stdout))
                log.info("5-{}-5> 客户端mount共享路径".format(for_loop_time))
                auth_clients_path = "/mnt/nfs_client_{}".format(for_loop_time)

                server_path = os.path.basename(nfs_path_4crt)
                # nfs_dir_{}
                server_path = os.path.join(nas_common.NAS_PATH, server_path)
                # /mnt/volume/nas1/nfs_dir_{}
                mount_rc = nas_common.mount(str(sub_net_para['svip']), server_path, nas_common.NFS_1_CLIENT_IP, auth_clients_path)
                common.judge_rc(mount_rc, 0, "mount nfs dir")
                log.info("5-{}-6> 测试读".format(for_loop_time))
                cmd_r = "ls %s" % auth_clients_path
                rc, stdout = common.run_command(nas_common.NFS_1_CLIENT_IP, cmd_r, False)
                common.judge_rc(rc, 0, stdout)
                log.info("5-{}-7> 测试写".format(for_loop_time))
                cmd_w = "touch %s/test2" % auth_clients_path
                rc, stdout = common.run_command(nas_common.NFS_1_CLIENT_IP, cmd_w, False)
                common.judge_rc(rc, 0, stdout)

                log.info("5-{}-8> 删除test-w的文件".format(for_loop_time))
                rc, stdout = common.rm_exe(nas_common.NFS_1_CLIENT_IP, os.path.join(auth_clients_path, "test2"))
                common.judge_rc(rc, 0, stdout)

                log.info("5-{}-9> 客户端umount共享路径".format(for_loop_time))
                umount_rc = nas_common.umount(nas_common.NFS_1_CLIENT_IP, auth_clients_path)
                common.judge_rc(rc, 0, stdout)

                log.info("5-{}-10> 客户端删除mount路径".format(for_loop_time))
                rc, stdout = common.rm_exe(nas_common.NFS_1_CLIENT_IP, auth_clients_path)
                common.judge_rc(rc, 0, stdout)
                log.info("5-{}-11> 删除nfs导出".format(for_loop_time))
                msg_dele_nfs = nas_common.delete_nfs_exports(ids=nfs_ex_id, print_flag=False)
                common.judge_rc(msg_dele_nfs['err_no'], 0, "delete nfs export: {}".format(nfs_ex_id))
            log.info("============================NO.{} FINISH===============================".format(for_loop_time))
            for_loop_time += 1

    log.info("6> 根据遗传标志位{}决定是(True)否(False)删除子网".format(flag_genetic))
    if not flag_genetic:
        dele_vip_info = "delete vip {}".format(vip_pool_id)
        dele_sub_info = "delete subnet {}".format(sub_net_id)
        log.info(dele_vip_info)
        msg_dele_vip = nas_common.delete_vip_address_pool(vip_address_pool_id=vip_pool_id, print_flag=False)
        common.judge_rc(msg_dele_vip['err_no'], 0, dele_vip_info)

        log.info(dele_sub_info)
        msg_dele_subnet = nas_common.delete_subnet(subnet_id=sub_net_id, print_flag=False)
        common.judge_rc(msg_dele_subnet['err_no'], 0, dele_sub_info)
    log.info("case passed!")
    return


def nas_main():
    log_file_path = log.get_log_path(FILE_NAME)
    log.init(log_file_path, True)
    case()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    nas_main()
