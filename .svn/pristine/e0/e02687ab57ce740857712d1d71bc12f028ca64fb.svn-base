#-*-coding:utf-8 -*
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
date 2018-08-01
@summary：
     缺陷自动化：配置LDAP认证服务到访问区,在nas_enable下查看中文用户信息。
@steps:
    1、添加ldap认证服务器到访问区1
    2、确定测试中文用户
    3、在nas_disable下获取中文用户信息
    4、在nas_enable下获取中文用户信息
    5、返回结果
@changelog：
    最后修改时间：2018-08-06
    修改内容：添加访问区的添加、删除操作；
        
        todo_不支持ad切换ldap
"""
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
MAX_WAIT_TIME = 600


def nas_state_change(case_ip, flag=False):
    """
    author：LiangXiaoyu
    function:改变访问区中的nas，根据参数开启或关闭nas
    :param case_ip:访问区所在节点ip；
    :param flag:开启（True）或关闭（False）nas
    :return:
    @changelog：
    """
    class_action = "disable"
    if flag is True:
        class_action = "enable"
    log.info("change nas status,flag:%s---%s" % (flag, class_action))
    msg_get_az = nas_common.get_access_zones(None)

    if flag is True:
        msg_nas = nas_common.enable_nas(msg_get_az["result"]["access_zones"][0]["id"])
    else:
        msg_nas = nas_common.disable_nas(msg_get_az["result"]["access_zones"][0]["id"])
    action_nas_rst = msg_nas["detail_err_msg"]
    if "" != action_nas_rst:
        log.error("%s nas action failed and exit:\n%s" % (class_action, action_nas_rst))
        raise Exception("case failed!!!")
    else:
        time_count = 0
        while True:
            msg_get_az = nas_common.get_access_zones(None)
            nas_status_active = msg_get_az["result"]["access_zones"][0]["nas_service_enabled"]
            cmp_nas_status_active = cmp(flag, nas_status_active)

            if 0 != int(cmp_nas_status_active):

                if MAX_WAIT_TIME < time_count:
                    log.error("wait for nas %s active too long:%d s" % (class_action, time_count))
                    raise Exception("case failed!!!")
                log.info("%s  nas not active yet,waiting:" % class_action)
                time.sleep(20)
                time_count += 20
                log.info("%d s" % time_count)
            else:
                log.info("%s nas done" % class_action)
                break
    return


def get_add_one_ldap(case_ip, ldap_info_add):
    """
    author：LiangXiaoyu
    function:检查集群中的LDAP数量，若存在，取第一个；若不存在，添加一个nas_common
    :param case_ip集群内ip； ldap_info_add:添加的ad认证服务器信息列表
    :return: Ldap认证服务器的id
    @changelog：
    """
    '''get,获取ldap和az状态'''
    msd_get_ldap = nas_common.get_auth_providers_ldap(None)
    ldap_total_sys_org = msd_get_ldap["result"]["total"]

    '''没有ldap就添加ldap'''
    if 0 == int(ldap_total_sys_org):

        msg_add_ldap = nas_common.add_auth_provider_ldap(ldap_info_add[0], ldap_info_add[1], ldap_info_add[2])
        # msg_set_ntp = nas_common.set_ntp("true", ldap_info_add[2], 5)
        add_ldap_result = msg_add_ldap["err_no"]
        # set_ntp_rst = msg_set_ntp["err_no"]
        set_ntp_rst = 0
        add_ldap_final = set_ntp_rst + add_ldap_result
        if 0 == int(add_ldap_final):
            msd_get_ldap = nas_common.get_auth_providers_ldap(None)
            log.info("add ldap sever success")
        else:
            log.error("add ldap failed:%s\nunix range is right?%s)" %
                      (msg_add_ldap, ldap_info_add))
            raise Exception("case failed!!!add ldap failed")

    '''不止一个ldap,只取第一个'''
    sys_ldap_id_org = msd_get_ldap["result"]["auth_providers"][0]["id"]
    log.info("ldap add:%d OK" % sys_ldap_id_org)
    return sys_ldap_id_org


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
    '''非代码节点'''
    ob_node = common.Node()
    case_node_id = random.choice(ob_node.get_nodes_id())
    case_ip = ob_node.get_node_ip_by_id(case_node_id)

    az_info_add = [case_node_id, FILE_NAME+"az"]
    ldap_info_add = [FILE_NAME+"ldap", nas_common.LDAP_BASE_DN, nas_common.LDAP_IP_ADDRESSES]
    ldap_group_user_test = nas_common.LDAP_USER_3_NAME
    # ["用户1"]
    rst_disable_nas = False
    rst_enable_nas = False
    '''
    添加az
    '''
    msg_add_az = nas_common.create_access_zone(az_info_add[0], az_info_add[1])
    az_id = msg_add_az["result"]
    add_az_result = msg_add_az["detail_err_msg"]
    if "" == add_az_result:
        msg_get_az = nas_common.get_access_zones(None)
        log.info("add access_zone success,id:%d" %
                 msg_get_az["result"]["access_zones"][0]["id"])
    else:
        log.error("add access_zone failed in node :%d" % case_node_id)
        raise Exception("case failed!!!")

    '''
    确定nas状态,disable
    '''
    nas_state_change(case_ip, False)
    """添加ldap认证服务器，获取用户ldap认证服务器"""

    id_ldap = get_add_one_ldap(case_ip, ldap_info_add)
    ldap_to_az = nas_common.update_access_zone(access_zone_id=az_id, node_ids=case_node_id,
                                               auth_provider_id=id_ldap)
    if "" != ldap_to_az["detail_err_msg"]:
        log.error("update LDAP online cmd failed")
        raise Exception("case failed!!!")
    rc, msg_get_users_ldap = nas_common.get_auth_users(id_ldap)
    msg_get_nephew = msg_get_users_ldap["result"]["auth_users"]
    log.info("test user:\'%s\'" % ldap_group_user_test)
    for name in msg_get_nephew:
        enter_cmp = cmp(ldap_group_user_test, str(name["name"]))
        if 0 == enter_cmp:
            log.info("Found Chinese user：%s" % name)
            rst_disable_nas = True

    nas_state_change(case_ip, True)
    msg_check_provider = nas_common.check_auth_provider(id_ldap)
    if "" != msg_check_provider["detail_err_msg"]:
        raise Exception("case failed!!!check_auth_provider failed:%d" % id_ldap)
    rc, msg_get_users_ldap = nas_common.get_auth_users(id_ldap)
    msg_get_nephew = msg_get_users_ldap["result"]["auth_users"]

    for name in msg_get_nephew:
        enter_cmp = cmp(ldap_group_user_test, str(name["name"]))
        if 0 == enter_cmp:
            log.info("Found Chinese user：%s" % name)
            rst_enable_nas = True
    if rst_disable_nas is True and rst_enable_nas is True:
        log.info("disenable/enable nas Found \'%s\,\ncase succeed!'" % ldap_group_user_test)
    else:
        log.info("enable_nas:%s,disable_nas:%s" % (rst_disable_nas, rst_enable_nas))
        common.except_exit("case failed!", -1)


    return


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    prepare_clean.nas_test_clean()
    case()
    prepare_clean.nas_test_clean()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
