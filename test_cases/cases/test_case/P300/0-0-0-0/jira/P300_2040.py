# -*-coding:utf-8 -*
import os
import time

import utils_path
import common
import snap_common
import log
import shell
import get_config
import prepare_clean
import random
import nas_common
import json
"""
author 梁晓昱
date 2018-07-24
@summary：
     缺陷自动化：disable_nas后update访问分区的认证服务器，执行enable_nas
@steps:
    1、固定的访问区号1
    2、先disable_nas；确定状态
    3、更新访问区的认证服务器
    4、enable_nas，检查环境，返回结果

@changelog：todo_
           添加的访问区，在nas完全交付后删除；
           disable nas 后最少需要6分钟（经验值）才可完全生效
"""
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
MAX_WAIT_TIME = 6000


def get_add_one_ad(case_ip, ad_info_add):
    """
    author：LiangXiaoyu
    function:检查集群中的AD数量，若存在，取第一个；若不存在，添加一个nas_common里的251
    :param case_ip集群内ip； ad_info_add:添加的ad认证服务器信息列表，如ad_info_add = ["ad_test", nas_common.AD_DOMAIN_NAME, nas_common.AD_DNS_ADDRESSES,
                   nas_common.AD_USER_NAME, nas_common.AD_PASSWORD,
                   "NONE", "2000-3000"]
    :return: 配置好的AD认证服务器id
    @changelog：
    """
    '''get,获取ad和az状态'''
    msd_get_ad = nas_common.get_auth_providers_ad(None)
    ad_total_sys_org = msd_get_ad["result"]["total"]

    '''没有ad就添加ad'''
    if 0 == int(ad_total_sys_org):

        msg_add_ad = nas_common.add_auth_provider_ad(ad_info_add[0], ad_info_add[1], ad_info_add[2], ad_info_add[3],
                                                     ad_info_add[4], ad_info_add[5])
        msg_set_ntp = nas_common.set_ntp("true", ad_info_add[2], 5)
        add_ad_result = msg_add_ad["err_no"]
        set_ntp_rst = msg_set_ntp["err_no"]
        add_ad_final = set_ntp_rst + add_ad_result
        if 0 == int(add_ad_final):
            msd_get_ad = nas_common.get_auth_providers_ad(None)
            log.info("add ad sever success")
        else:
            log.error("add ad failed:%s\nunix range is right?%s,ntp:%s)" %
                      (msd_get_ad, ad_info_add, msg_set_ntp))
            raise Exception("case failed!!!")

    '''不止一个ad,只取第一个'''
    sys_ad_id_org = msd_get_ad["result"]["auth_providers"][0]["id"]
    log.info("ad_system OK")
    return sys_ad_id_org


def random_choose_node(ob_node):
    """
        name  :      delete_disk_random_beta
        parameter:   common库中的node类
        author:      LiangXiaoyu
        date  :      2018.07.13
        Description: 返回一个随机得到的node_id和IP
        @changelog：
    """
    nodeid_list = ob_node.get_nodes_id()
    '''随机选一个节点'''
    fault_node_id = random.choice(nodeid_list)
    return fault_node_id


def case():
    log.info("case begin")
    '''随机节点'''
    ob_node = common.Node()
    case_node_id = 1
    case_ip = ob_node.get_node_ip_by_id(case_node_id)

    az_info_add = [case_node_id, "az_test"]
    ad_info_add = ["ad_test", nas_common.AD_DOMAIN_NAME, nas_common.AD_DNS_ADDRESSES,
                   nas_common.AD_USER_NAME, nas_common.AD_PASSWORD,
                   "NONE", "2000-3000"]

    '''
    没有访问区就添加az
    '''
    msg_get_az = nas_common.get_access_zones(None)
    az_total_num_org = msg_get_az["result"]["total"]

    if 0 == int(az_total_num_org):

        msg_add_az = nas_common.create_access_zone(az_info_add[0], az_info_add[1])
        add_az_result = msg_add_az["err_no"]

        if 0 == int(add_az_result):

            msg_get_az = nas_common.get_access_zones(None)
            log.info("add access_zone success,id:%d" %
                     msg_get_az["result"]["access_zones"][0]["id"])
        else:

            log.error("add access_zone failed:\n%s" % msg_add_az)
            raise Exception("case failed!!!")

    '''确定nas状态,若是enable状态则先disable'''
    msg_get_az = nas_common.get_access_zones(None)
    msg_disable_nas = nas_common.disable_nas(msg_get_az["result"]["access_zones"][0]["id"])
    disable_nas_rst = msg_disable_nas["err_no"]
    if 0 != disable_nas_rst:
        log.error("disable_nas action failed and exit:\n%s" % disable_nas_rst)
        raise Exception("case failed!!!")
    else:
        time_count = 0
        while True:
            msg_get_az = nas_common.get_access_zones(None)
            nas_status_active = msg_get_az["result"]["access_zones"][0]["nas_service_enabled"]
            cmp_nas_status_active = cmp(False, nas_status_active)

            if 0 != int(cmp_nas_status_active):

                if MAX_WAIT_TIME < time_count:
                    log.error("wait for nas disable active too long:%d s" % time_count)
                    raise Exception("case failed!!!")
                log.info("disable nas not active yet,waiting:")
                time.sleep(20)
                time_count += 20
                log.info("%d s" % time_count)
            else:
                log.info("disable nas done")
                break
    '''确定访问区的认证服务器状态和集群可配置的认证服务器ad'''
    update_provider_id = get_add_one_ad(case_ip, ad_info_add)
    msg_get_az = nas_common.get_access_zones(None)
    org_provider_id = msg_get_az["result"]["access_zones"][0]["auth_provider_id"]
    log.info("old provider id is:%d" % org_provider_id)
    if org_provider_id == update_provider_id:
        update_provider_id = 4
    log.info("new provider id will be:%d" % update_provider_id)
    '''核心操作，update访问区认证服务器，enable_nas'''
    msg_get_az = nas_common.get_access_zones(None)
    id_az = msg_get_az["result"]["access_zones"][0]["id"]
    msg_up_provider = nas_common.update_access_zone(access_zone_id=id_az, auth_provider_id=update_provider_id)
    if 0 != msg_up_provider["err_no"]:
        log.error("update_access_zone failed ")
        raise Exception("case failed!!!")
    log.info("update access zone done!")
    msg_enable_rst = nas_common.enable_nas(msg_get_az["result"]["access_zones"][0]["id"])
    enable_final_rst = msg_enable_rst["err_no"]
    if 0 != int(enable_final_rst):

        log.error("enable nas failed failed and exit")
        raise Exception("case failed!!!")
    time_count = 0
    while True:

        msg_get_az = nas_common.get_access_zones(None)
        nas_status_enable = msg_get_az["result"]["access_zones"][0]["nas_service_enabled"]
        cmp_nas_status_en = cmp(True, nas_status_enable)
        if 0 != int(cmp_nas_status_en):
            if MAX_WAIT_TIME < time_count:
                log.error("wait for nas enable active too long:%d s" % time_count)
                raise Exception("case failed!!!")
            log.info("wait for enable_nas active:")
            time.sleep(20)
            time_count += 20
            log.info("%d s" % time_count)
        else:
            log.info("enable_nas succeed")
            break

    return


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    case()
    prepare_clean.nas_test_clean()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
