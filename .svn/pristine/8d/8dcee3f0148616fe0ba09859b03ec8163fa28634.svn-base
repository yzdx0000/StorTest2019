# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random
import math
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
 date 2018-11-19
 @summary：
    修改访问分区，使其包含的节点依次增加，直至访问区内包括所有节点
 @steps:
    1、清除环境
    2、创建访问区，随机选取一个节点，启动smb/nfs/ftp服务
    3、按照节点列表，按照不同步长分解剩余节点，使用update_access_zone命令将节点添加至访问区，启动smb/nfs/ftp服务
    4、检查所有访问区的服务状态是否正常

 @changelog：
"""
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0].replace('-', '_')                 # 本脚本名字
NAS_PATH = get_config.get_one_nas_test_path()                            # /mnt/volume/nas_test_dir
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)             # /mnt/volume/nas_test_dir/nas_16_6_0_16
BASE_NAS_PATH = os.path.dirname(NAS_PATH)                                # /mnt/volume
NAS_PATH_BASENAME = os.path.basename(NAS_PATH)                           # nas_test_dir


def create_all_kind_of_provider():
    """1 创建认证"""
    auth_provider_id_list = []
    ad_name = "ad_auth_provider"
    msg2 = nas_common.add_auth_provider_ad(name=ad_name,
                                           domain_name=nas_common.AD_DOMAIN_NAME,
                                           dns_addresses=nas_common.AD_DNS_ADDRESSES,
                                           username=nas_common.AD_USER_NAME,
                                           password=nas_common.AD_PASSWORD,
                                           services_for_unix="NONE")

    common.judge_rc(msg2["err_no"], 0, "add_auth_provider_ad failed")
    ad_auth_provider_id = msg2["result"]
    auth_provider_id_list.append(ad_auth_provider_id)
    log.info("ad认证：{}".format(ad_auth_provider_id))

    ldap_name = "ldap_auth_provider"
    msg2 = nas_common.add_auth_provider_ldap(name=ldap_name, base_dn=nas_common.LDAP_BASE_DN,
                                             ip_addresses=nas_common.LDAP_IP_ADDRESSES, port=389)
    common.judge_rc(msg2["err_no"], 0, "ldap_auth_provider failed")

    ldap_auth_provider_id = msg2["result"]
    auth_provider_id_list.append(ldap_auth_provider_id)
    log.info("ldap认证：{}".format(ldap_auth_provider_id))

    ldap_name = "ldap_pdc_auth_provider"
    msg2 = nas_common.add_auth_provider_ldap(name=ldap_name, base_dn=nas_common.LDAP_2_BASE_DN,
                                             ip_addresses=nas_common.LDAP_2_IP_ADDRESSES, port=389,
                                             bind_dn=nas_common.LDAP_2_BIND_DN,
                                             bind_password=nas_common.LDAP_2_BIND_PASSWORD,
                                             domain_password=nas_common.LDAP_2_DOMAIN_PASSWORD)
    common.judge_rc(msg2["err_no"], 0, "ldap_pdc_auth_provider failed")

    ldap_pdc_auth_provider_id = msg2["result"]
    auth_provider_id_list.append(ldap_pdc_auth_provider_id)
    log.info("ldap_pdc认证：{}".format(ldap_pdc_auth_provider_id))

    nis_name = "nis_auth_provider"
    msg2 = nas_common.add_auth_provider_nis(name=nis_name,
                                            domain_name=nas_common.NIS_DOMAIN_NAME,
                                            ip_addresses=nas_common.NIS_IP_ADDRESSES)

    common.judge_rc(msg2["err_no"], 0, "nis_auth_provider failed")
    nis_auth_provider_id = msg2["result"]
    auth_provider_id_list.append(nis_auth_provider_id)
    log.info("nis认证：{}".format(nis_auth_provider_id))
    return auth_provider_id_list


def decompose_az_with_different_num(nodes_lst, lenth_history_lst, loop_flag, loop_time):
    """
    author:JiangXiaoguang, LiangXiaoyu
    summit:对n个节点的列表分解为长度不同的子列表：
            1、每次选择的子列表长度为开区间(1,n)的一个随机数；
            2、当满足：剩余节点数为1或者2，分解结束
    :param nodes_lst: 输入的节点列表信息，随更新而改变
    :param lenth_history_lst: 曾经选择的节点数(节点数长度历史)
    :param loop_flag: 循环是否继续
    :return: 选完新节点之后的剩余节点列表，剩余节点与“留守节点”的全集以更新访问区，步长历史，循环停止标志位
    """

    nodes_update = nodes_lst
    nodes_to_create = []
    lenth_now = len(nodes_update)
    num_choose = 0
    while_loop_time = 0
    log.info("input:nodes_lst {},lenth_history_lst {},loop_flag {}".format(nodes_lst, lenth_history_lst, loop_flag))
    if lenth_now > 2:

        if not lenth_history_lst:
            num_choose = random.choice(range(2, lenth_now))
            log.info("choose {} node(s) for new az from (2, {})".format(num_choose, lenth_now))
        else:
            num_choose = random.choice(range(2, lenth_now))
            while num_choose in lenth_history_lst:
                log.info("number {} node(s) in lenth_history_lst {}, left {} nodes".format(num_choose, lenth_history_lst, lenth_now))
                if while_loop_time > (lenth_now + 80):
                    common.except_exit("while, bug!")
                # 当所选步长为历史步长，重新选，不是死循环，因为lenth_now大于2控制了条件
                """
                但是历史步长中有2，且本次num_choose == 2,lenth_now == 3的时候，
                成为死循环，比如6=1+5,5=2+3,3成为lenth_now
                """
                if num_choose == 2 and lenth_now == 3:
                        log.info("节点长度选择历史{}, 剩下待分解的节点是{}, 长度为{}".format(lenth_history_lst, nodes_update, lenth_now))

                        num_choose = lenth_now
                    # 一旦历史中有2，并且成为(2,3)互选，则选3，停止分解
                        loop_flag = False

                else:
                    num_choose = random.choice(range(2, lenth_now))
                log.info("本次选择的节点数是{}".format(num_choose))

                while_loop_time += 1
        lenth_history_lst.append(num_choose)
        nodes_to_create = random.sample(nodes_update, num_choose)
        # 普通情况，减去拿掉的节点就是更新后的节点列表
        nodes_update = list(set(nodes_update) - set(nodes_to_create))
        node_id_update_param = ",".join(nodes_to_create)
    else:
        nodes_to_create = nodes_update
        nodes_update = []
        node_id_update_param = ",".join(nodes_to_create)
        num_choose = len(nodes_to_create)
        lenth_history_lst.append(num_choose)
        loop_flag = False

    log.info("count: {} node(s) choosen, {} to create new access zone".format(num_choose, node_id_update_param))

    return nodes_to_create, nodes_update, node_id_update_param, lenth_history_lst, loop_flag


def case():

    """函数主体"""
    log.info("1> 清理环境完成，访问区节点个数不同步长增加")
    log.info("2> 创建访问区，随机选取一个节点，启动smb/nfs/ftp服务")
    node_obj = common.Node()
    node_list_all = node_obj.get_nodes_id()
    node_list_string = []
    info_record = ""
    info_record_lst = []
    loop_flag = True

    random_times = 1
    lenth_for_loop_random_time = math.ceil(len(node_list_all) / 2)
    lenth_for_loop_random_time += 1
    for node_id_int in node_list_all:
        node_list_string.append(str(node_id_int))
    log.info("lenth_for_loop_random_time is {}".format(int(lenth_for_loop_random_time)))
    for random_times in range(1, int(lenth_for_loop_random_time)):
        # 默认环境完整，有四种provider
        provider_flag = False
        provider_lst = []
        provider_id = None
        """provider_flag为True，进行认证服务器切换"""
        if provider_flag:
            provider_lst = create_all_kind_of_provider()
        log.info("=================================={} BEGIN==================================".format(random_times))
        if random_times > 1 and loop_flag is False:
            # 清理条件：本次循环已经结束，此时的loop_falg 应该为False，应再次置为True
            prepare_clean.nas_test_clean()
            loop_flag = True
            provider_lst = []
        init_nodes_id_param = random.choice(node_list_string)
        all_nodes_az_name = "az_" + str(time.localtime().tm_hour) + str(time.localtime().tm_min) + str(time.localtime().tm_sec)
        msg_crt_az_all = nas_common.create_access_zone(node_ids=init_nodes_id_param, name=all_nodes_az_name)
        common.judge_rc(msg_crt_az_all["err_no"], 0, "created az include all nodes")
        id_az_all_nodes = msg_crt_az_all["result"]
        msg_enabel_nas_all = nas_common.enable_nas(id_az_all_nodes, "NFS,SMB,FTP")
        common.judge_rc(msg_enabel_nas_all["err_no"], 0, "created az include all nodes")

        log.info("3> 按照节点列表，按照不同步长分解剩余节点，使用update_access_zone命令将节点添加至访问区，启动smb/nfs/ftp服务")
        nodes_update = node_list_string[:]
        nodes_update.remove(init_nodes_id_param)
        loop_time = 0
        lenth_history_lst = []
        lenth_nodes_up = len(nodes_update)
        if not lenth_nodes_up:
            loop_flag = False
            log.info("这是一个单节点集群，不适用于本用例")

        while loop_flag:
            log.info("------------------lenth_history_lst {}------------------".format(lenth_history_lst))
            nodes_update_record = init_nodes_id_param
            (nodes_chosen, nodes_update, node_id_chosen_param, lenth_history_lst, loop_flag) = \
                decompose_az_with_different_num(nodes_update, lenth_history_lst, loop_flag, loop_time)
            # init节点需要更新，否则变成(1;3,4,5,6)：1->1,3,4->1,5,6

            init_nodes_id_param = init_nodes_id_param + "," + node_id_chosen_param
            if provider_flag:
                log.info("默认参数完整，更新时一并更新访问区的鉴权服务器")
                provider_id = random.choice(provider_lst)
                msg_update = nas_common.update_access_zone(access_zone_id=id_az_all_nodes, node_ids=init_nodes_id_param, auth_provider_id=provider_id)

            else:
                msg_update = nas_common.update_access_zone(access_zone_id=id_az_all_nodes, node_ids=init_nodes_id_param)
            common.judge_rc(msg_update["err_no"], 0, "update az,add nodes:{},left id:{}".format(init_nodes_id_param, nodes_update))
            loop_time += 1
            info_record = "3-{}-{}> 访问区节点从{}至 {},步长历史列表为{}".format(random_times, loop_time, nodes_update_record, init_nodes_id_param, lenth_history_lst)
            log.info(info_record)
            info_record_lst.append(info_record)

            log.info("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        log.info("4> 检查所有节点{}的访问区服务状态是否正常".format(node_list_all))

        nas_check = nas_common.check_nas_status()
        common.judge_rc(nas_check, 0, "nas status of node is wrong")

        log.info("lenth_history_lst is {}".format(lenth_history_lst))
    log.info("case passed:")
    log.info(info_record_lst)
    return


def nas_main():
    log_file_path = log.get_log_path(FILE_NAME)
    log.init(log_file_path, True)
    prepare_clean.nas_test_clean()
    case()

    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    nas_main()
