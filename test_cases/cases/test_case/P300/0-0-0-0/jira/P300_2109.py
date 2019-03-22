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
date 2018-07-13
@summary：P300-2109缺陷自动化：检查AD用户命令获取到的ad认证服务器id错误
@steps:
    0、可能的环境：没ad、没访问区；有ad、没访问区；有ad、有访问区，ad已经配置到访问区；
                ad、访问区都有，ad没配置到az；
    1、指定节点ip(可删除访问区后改为随机节点ip)
    2、获取ad认证服务器上的用户信息
      （命令pscli --command=get_auth_providers_ad)；
    3、检查2中命令返回的auth_provider_id是否为查询时指定的id；
    4、判定结果，检查环境，返回结果

@changelog：TODO
    因nas的访问分区删除未上线，回退不方便，且一个访问区只允许存在ntp冲突的一个鉴权服务器
"""

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]


def random_choose_node(ob_node):
    '''
        name  :      delete_disk_random_beta
        parameter:   common库中的node类
        author:      LiangXiaoyu
        date  :      2018.07.13
        Description: 返回一个随机得到的node_id和IP
        @changelog：
        '''
    nodeid_list = ob_node.get_nodes_id()
    '''随机选一个节点'''
    fault_node_id = random.choice(nodeid_list)
    return fault_node_id


def case():
    log.info("case begin")
    add_ad_sys_flag = 0
    '''
    现在访问区是删不掉的，但是以后可删除的时候:
    可根据 add_az_flag 恢复环境,case_node_id应随机选择
    '''
    add_az_flag = 0
    add_ad2za_flag = 0
    '''随机节点'''
    ob_node = common.Node()
    case_node_id = 1  # random_choose_node(ob_node)
    case_ip = ob_node.get_node_ip_by_id(case_node_id)  #
    ad_info_add = ["ad_test", nas_common.AD_DOMAIN_NAME, nas_common.AD_DNS_ADDRESSES,
                   nas_common.AD_USER_NAME, nas_common.AD_PASSWORD,
                   "NONE", "2000-3000"]
    az_info_add = [case_node_id, "az_test"]

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
            add_ad2za_flag = 1
            add_ad_sys_flag = 1  # 为删除做准备
        else:
            log.error("add ad failed:%s\nunix range is right?%s,ntp:%s)" %
                      (msd_get_ad, ad_info_add, msg_set_ntp))
            raise Exception("case failed!!!")

    '''不止一个ad,只取第一个'''
    sys_ad_id_org = msd_get_ad["result"]["auth_providers"][0]["id"]
    log.info("ad_system OK")

    '''
    没有访问区就添加az
    '''
    msg_get_az = nas_common.get_access_zones(None)
    az_total_num_org = msg_get_az["result"]["total"]  # 0?

    if 0 == int(az_total_num_org):
        msg_add_az = nas_common.create_access_zone(az_info_add[0], az_info_add[1])
        add_az_result = msg_add_az["err_no"]

        if 0 == int(add_az_result):
            msg_get_az = nas_common.get_access_zones(None)
            log.info("add access_zone success,id:%d" %
                     msg_get_az["result"]["access_zones"][0]["id"])
            add_ad2za_flag = 1
            add_az_flag = 1

        else:
            log.error("add access_zone failed:\n%s" % msg_add_az)
            raise Exception("case failed!!!")

    # az_zone_id4op = msg_get_az["result"]["access_zones"][0]["id"]
    '''应该最先get；若access_zone的认证服务器是ad，则ok；不是ad，一步步更新为ad'''
    cmp_ad2za_flag = 0  # 认为ad已经添加到az
    msg_get_az = nas_common.get_access_zones(None)
    access_zone_id = msg_get_az["result"]["access_zones"][0]["id"]
    msg_az_detail = msg_get_az["result"]["access_zones"][0]
    az_ad_id_org = msg_az_detail["auth_provider"]["id"]  # ?1?11最后还是要设置回来，恢复环境

    if 0 == int(add_ad2za_flag):
        type_provider_str = "AD"

        az_ad_type_org = msg_az_detail["auth_provider"]["type"]
        cmp_ad2za_flag = cmp(type_provider_str, str(az_ad_type_org))

    '''确定nas状态,若是enable状态则先disable'''
    nas_status_org = msg_get_az["result"]["access_zones"][0]["nas_service_enabled"]
    cmp_nas_status = cmp(False, nas_status_org)

    if 0 != cmp_nas_status:
        msg_get_az = nas_common.get_access_zones(None)
        msg_disable_nas = nas_common.disable_nas(msg_get_az["result"]["access_zones"][0]["id"])
        disable_nas_rst = msg_disable_nas["err_no"]
        log.info("wait 20s for disable_nas")
        time.sleep(20)
        if 0 != disable_nas_rst:
            log.error("disable_nas_rst failed and exit:\n%s" % disable_nas_rst)
            raise Exception("case failed!!!")
        else:
            log.info("disable_nas succeed ")
    '''
    如果前者没有添加新的ad或者az，则add_ad2za_flag为0，须判断az中的鉴权是否为ad
    若是，则cmp_ad2za_flag=0，add_ad2za_flag仍为0；
    若不是，则cmp_ad2za_flag=1，add_ad2za_flag置为1；
    '''
    if 0 != int(cmp_ad2za_flag):
        log.info("the user server in access zone:%s is %s,not AD.To add one:%s"
                 % (access_zone_id, msg_az_detail["auth_provider"]["type"], sys_ad_id_org))
        add_ad2za_flag = 1
    else:
        # 判断是不是同一个ad
        if int(sys_ad_id_org) != int(az_ad_id_org):
            log.info("not the same AD:\nNo.1 AD in system is %s,AD %s" \
                     % (sys_ad_id_org, az_ad_id_org))
            add_ad2za_flag = 1

    if 1 == add_ad2za_flag:
        msg_add_ad2az = nas_common.update_access_zone \
            (access_zone_id=access_zone_id, auth_provider_id=sys_ad_id_org)
        add_ad2az_rst = msg_add_ad2az["err_no"]
        if 0 == int(add_ad2az_rst):
            msg_get_az = nas_common.get_access_zones(None)
            log.info("add access_zone success,id:%d(is 251?)" % \
                     msg_get_az["result"]["access_zones"][0]["id"])
        else:
            log.error("add AD to access zone failed:\n%s" % msg_add_ad2az)
            raise Exception("case failed!!!")
    '''set ntp/ad_new->az/nas enable'''
    rc_get_ntp, stdout_get_ntp = common.get_ntp()
    msg_get_ntp = common.json_loads(stdout_get_ntp)
    msg_ntp_ip = msg_get_ntp["result"]["ntp_servers"][0]
    cmp_ntp_ip = cmp(str(msg_ntp_ip), ad_info_add[2])

    if 0 != int(cmp_ntp_ip):
        msg_reset_ntp = nas_common.set_ntp("true", ad_info_add[2], 5)
        add_ntp_rst = msg_reset_ntp["err_no"]
        if 0 == int(add_ntp_rst):
            log.info("set/reset ntp succeed,NTP:%s" % ad_info_add[2])
        else:
            log.error("set/reset ntp failed:\n%s" % msg_reset_ntp)
            raise Exception("case failed!!!")
    msg_get_az = nas_common.get_access_zones(None)
    msg_enable_nas = nas_common.enable_nas(msg_get_az["result"]["access_zones"][0]["id"])
    enable_nas_rst = msg_enable_nas["err_no"]
    if 0 != int(enable_nas_rst):
        log.error("enable_nas_rst failed and exit:\n%s" % enable_nas_rst)
        raise Exception("case failed!!!")
    else:
        time_count = 0
        while True:
            msg_get_az = nas_common.get_access_zones(None)
            nas_status_enable = msg_get_az["result"]["access_zones"][0]["nas_service_enabled"]
            cmp_nas_status_en = cmp(True, nas_status_enable)
            if 0 != int(cmp_nas_status_en):
                if 600 < time_count:
                    log.error("wait for nas enable active too long:%d s" % time_count)
                    raise Exception("case failed!!!")
                log.info("wait 20s for enable_nas active")
                time.sleep(20)
                time_count += 20
            else:
                log.info("enable_nas succeed:\n%s " % (msg_get_az["result"]["access_zones"][0]))
                break
    log.info("environment of access zone is OK")

    '''
    若配置到访问区里的AD服务器不是nas测试使用的251服务器，
    则需要在检查前更新access_zone里已配置的AD认证服务器的信息，再执行用例内容
    在指定的节点上（不应该是随机节点）遍历完访问区，初始有访问区的节点
    '''
    log.info("wait 7 min for pscli --command=get_auth_users")
    time.sleep(420)
    msg_get_az = nas_common.get_access_zones(None)
    id_para = msg_get_az["result"]["access_zones"][0]["auth_provider"]["id"]

    rc, msg_get_provider_users = nas_common.get_auth_users(id_para)
    id_get_user = msg_get_provider_users["result"]["auth_users"][0]["auth_provider_id"]

    if id_get_user == id_para:

        log.info("right!!!\nrelease:beta,node_id FIXED 1")
    else:
        log.error("wrong:!!!id_para:%d, cmd:%d\n" %(id_para, id_get_user))
        raise Exception("case failed!!!")
    return


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    case()
    prepare_clean.nas_test_clean()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
