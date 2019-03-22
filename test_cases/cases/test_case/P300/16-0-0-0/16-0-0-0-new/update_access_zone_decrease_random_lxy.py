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
 date 2018-11-17
 @summary：
    修改访问分区，使其分解为节点数目不同的新访问区
 @steps:
    1、清除环境
    2、创建访问区，要求使用集群所有节点，启动smb/nfs/ftp服务，并检查
    3、确定分解节点组合，使用update_access_zone命令将节点踢出访问区；
       踢出访问区的节点建立新的访问区，启动smb/nfs/ftp服务
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
                        log.info("节点长度选择历史{}, 剩下待分解的节点是{}, 长度为{}， 本次选择的节点数是{}".format(lenth_history_lst, nodes_update, lenth_now, num_choose))

                        num_choose = lenth_now
                    # 一旦历史中有2，并且成为(2,3)互选，则选3，停止分解
                        loop_flag = False

                else:
                    num_choose = random.choice(range(2, lenth_now))

                while_loop_time += 1
        lenth_history_lst.append(num_choose)
        nodes_to_create = random.sample(nodes_update, num_choose)
        # 普通情况，减去拿掉的节点就是更新后的节点列表
        nodes_update = list(set(nodes_update) - set(nodes_to_create))
        node_id_update_param = ",".join(nodes_update)
    else:
        nodes_to_create = nodes_update
        nodes_update = []
        node_id_update_param = nodes_update
        num_choose = len(nodes_to_create)
        lenth_history_lst.append(num_choose)
        loop_flag = False

    log.info("count: {} node(s) choosen, {} to create new access zone".format(num_choose, node_id_update_param))

    return nodes_to_create, nodes_update, node_id_update_param, lenth_history_lst, loop_flag


def case():

    """函数主体"""
    log.info("1> 清理环境完成，访问区节点数不同步长减少")
    log.info("2> 创建访问区，要求使用集群所有节点，启动smb/nfs/ftp服务，并检查")
    node_obj = common.Node()
    nodes_lst = node_obj.get_nodes_id()
    node_list_string = []
    loop_flag = True
    loop_time = 0
    lenth_history_lst = []
    info_record_lst = []
    id_az_all_nodes = -1
    random_times = 0
    lenth_for_loop_random_time = math.ceil(len(nodes_lst) / 2)
    lenth_for_loop_random_time += 1
    log.info("test list is :{}".format(nodes_lst))
    for node_id_int in nodes_lst:
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
        loop_time = 0
        log.info("=================================={} BEGIN==================================".format(random_times))
        if random_times > 1 and loop_flag is False:
            #清理条件：本次循环已经结束，此时的loop_falg 应该为False，应再次置为True
            prepare_clean.nas_test_clean()
            loop_flag = True
            lenth_history_lst = []
        az_name = "az_" + str(loop_time) + "_" + str(time.localtime().tm_hour) + str(time.localtime().tm_min) + str(
                time.localtime().tm_sec)
        all_nodes_id_param = ",".join(node_list_string)
        msg_crt_az_all = nas_common.create_access_zone(node_ids=all_nodes_id_param, name=az_name)
        id_az_all_nodes = msg_crt_az_all["result"]

        msg_crt_az_all = nas_common.update_access_zone(access_zone_id=id_az_all_nodes, node_ids=all_nodes_id_param)
        common.judge_rc(msg_crt_az_all["err_no"], 0, "created/update az include all nodes")

        msg_enabel_nas_all = nas_common.enable_nas(id_az_all_nodes, "NFS,SMB,FTP")
        common.judge_rc(msg_enabel_nas_all["err_no"], 0, "created az include all nodes")

        log.info("3> 确定分解节点组合，使用update_access_zone命令将节点踢出访问区")
    #    right_value = (len(nodes_lst) + 1)
        node_watch_home_id = random.choice(node_list_string)
        log.info("node_watch_home is {}".format(node_watch_home_id))
        nodes_update = node_list_string[:]
        nodes_update.remove(node_watch_home_id)
        info_record = ""
        while loop_flag:
            log.info("----------------------------lenth_history_lst is {}---------------------------------".format(lenth_history_lst))
            (nodes_to_create, nodes_update, node_id_update_param, lenth_history_lst, loop_flag) = \
                decompose_az_with_different_num(nodes_update, lenth_history_lst, loop_flag, loop_time)
            nodes_update_p = nodes_update[:]
            nodes_update_p.append(str(node_watch_home_id))

            if len(nodes_update_p) > 1:
                node_id_update_param = ",".join(nodes_update_p)
            else:
                for p in nodes_update_p:
                    node_id_update_param = str(p)
            log.info("node_id_update_param should not be null:{}".format(node_id_update_param))
        # 将最终留下的节点id加入更新命令的参数，否则将会落下该节点;若没有节点则注意不要加冗余的逗号
            nodes_to_create_param = ",".join(nodes_to_create)
            loop_time += 1
            az_name = "az_" + str(loop_time) + "_" + str(time.localtime().tm_hour) + str(time.localtime().tm_min) + str(time.localtime().tm_sec)
            log.info("new access zone using param:{}".format(nodes_to_create_param))
        # log.info("left nodes_lst:{}, lenth_history_lst:{}, loop_flag:{}".format
        # (nodes_update, lenth_history_lst, loop_flag))
            info_record = "3-{}-{}> 从 {} 中踢出节点 {}，剩下的节点群是 {};".format(random_times, loop_time, nodes_lst, nodes_to_create, node_id_update_param)
            log.info(info_record)

            if provider_flag:
                log.info("默认参数完整，更新时一并更新访问区的鉴权服务器")

                provider_id = random.choice(provider_lst)
                msg_update = nas_common.update_access_zone(access_zone_id=id_az_all_nodes, node_ids=node_id_update_param, auth_provider_id=provider_id)

            else:
                msg_update = nas_common.update_access_zone(access_zone_id=id_az_all_nodes, node_ids=node_id_update_param)
            common.judge_rc(msg_update["err_no"], 0, "update az,delete nodes:{},left id:{}".format(nodes_to_create, node_id_update_param))
        # log.info("P300-5154")
            msg_crt_az = nas_common.create_access_zone(node_ids=nodes_to_create_param, name=az_name)
            id_az = msg_crt_az["result"]
            common.judge_rc(msg_crt_az["err_no"], 0, "created az use new nodes:{},id:{}".format(nodes_to_create, id_az))

            msg_enabel_nas = nas_common.enable_nas(id_az, "NFS,SMB,FTP")
            common.judge_rc(msg_enabel_nas["err_no"], 0, "enable nas on new az:".format(id_az))
            create_info = "使用节点{}创建的新访问区id 为 {}".format(nodes_to_create, id_az)

            log.info(create_info)
            info_record += create_info
            info_record_lst.append(info_record)
            log.info("^^^^^^^^^^^^^^^^^^^^^^^^^^^No.{} loop ended^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^".format(loop_time))

        log.info("4> 检查所有节点{}的访问区服务状态是否正常".format(nodes_lst))
    # for node in node_list_all:
    # log.info("check node {}".format(node))
        nas_check = nas_common.check_nas_status()
        common.judge_rc(nas_check, 0, "nas status of node is wrong")
        log.info("=================================={} GOT==================================".format(info_record))

    """
    for test_v in range(1, 4):
        nodes_lst.append(test_v)   
    """
    log.info("{} times , case passed!".format(len(info_record_lst)))
    for records in info_record_lst:
        log.info(records)

    return


def nas_main():
    log_file_path = log.get_log_path(FILE_NAME)
    log.init(log_file_path, True)
    prepare_clean.nas_test_clean()
    case()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    nas_main()
