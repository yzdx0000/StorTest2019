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
Author:liangxy
date 2018-08-07
@summary：
     缺陷自动化——创建子网与VIP池后，enable nas——disable nas成功，再次enable nas报错
@steps:
    1、创建访问区FILE_NAME
    2、创建子网和VIP池
    3、enable nas
    4、disable nas
    5、返回结果，清理环境
@changelog：
    最后修改时间：
    修改内容：
"""

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
MAX_WAIT_TIME = 300


def nas_state_change(azid, flag=False):
    """
    author：LiangXiaoyu
    function:改变访问区中的nas，根据参数开启或关闭nas
    :param azid:访问区id；
    :param flag:开启（True）或关闭（False）nas
    :return:
    @changelog：修改raise方式（2018-08-06）
    """
    class_action = "disable"
    if flag is True:
        class_action = "enable"
    log.info("change nas status,flag:%s---%s" % (flag, class_action))
    if flag is True:
        msg_nas = nas_common.enable_nas(azid)
    else:
        msg_nas = nas_common.disable_nas(azid)
    action_nas_rst = msg_nas["detail_err_msg"]
    if "" != action_nas_rst:
        crt_err = "%s nas action failed and exit:\n%s" % (class_action, action_nas_rst)
        common.judge_rc(-1, 0, crt_err)
    else:
        """执行成功不代表真正生效（现有的缺陷），须通过get_access_zones来检查nas状态"""
        time_count = 0
        while True:
            msg_get_az = nas_common.get_access_zones(ids=azid)
            """返回bool型的nas状态，同设定的flag进行比较"""
            nas_status_active = msg_get_az["result"]["access_zones"][0]["nas_service_enabled"]
            cmp_nas_status_active = cmp(flag, nas_status_active)

            if 0 != int(cmp_nas_status_active):

                if MAX_WAIT_TIME < time_count:
                    crt_err = "wait for nas %s active too long:%d s" % (class_action, time_count)
                    common.judge_rc(-1, 0, crt_err)
                log.info("%s  nas not active yet,waiting:" % class_action)
                time.sleep(20)
                time_count += 20
                log.info("%d s" % time_count)
            else:
                log.info("%s nas done" % class_action)
                break
    return


def case():
    log.info("case begin")
    """节点列表和客户端IP列表"""
    ob_node = common.Node()
    client_ip_lsts = ob_node.get_client_ips()
    case_node_id_lst = ob_node.get_nodes_id()

    """handle->节点id、客户端ip；添加后要删除的访问区"""
    case_id = random.choice(case_node_id_lst)

    case_ip = ob_node.get_node_ip_by_id(case_id)
    imp_info_lst = []
    '''
    在选定节点添加上访问分区
    '''
    # add_list = []
    # for i in case_node_id_lst:
    #     add_list.append(str(i).split())
    case_choose_id_lst = case_node_id_lst
    if 3 < len(case_node_id_lst):
        case_choose_id_lst = random.sample(case_node_id_lst, 3)
    id_str = ','.join(str(p) for p in case_choose_id_lst)
    # if add_list:
    #     id_str = ",".join(add_list)
    # else:
    #     log.info("id_str is null")
    msg_add_az = nas_common.create_access_zone(id_str, FILE_NAME + "az")
    if "" != msg_add_az["detail_err_msg"]:
        add_az_err = "create subnet in node %d failed" % case_id
        common.judge_rc(-1, 0, add_az_err)
    id_az = msg_add_az["result"]
    imp_info_lst.append(id_az)
    log.info("az id created is %d" % id_az)
    """enable nas"""
    nas_state_change(id_az, True)
    """创建子网"""
    msg_crt_subnet = nas_common.create_subnet(id_az, FILE_NAME + "snet", "IPv4", nas_common.SUBNET_SVIP,
                                              nas_common.SUBNET_MASK,
                                              nas_common.SUBNET_NETWORK_INTERFACES,nas_common.SUBNET_GATEWAY,
                                              nas_common.SUBNET_MTU)
    if "" != msg_crt_subnet["detail_err_msg"]:
        crt_err = "create subnet in node %d failed;info:%s" % (case_id, imp_info_lst)
        common.judge_rc(-1, 0, crt_err)
    id_subnet = msg_crt_subnet["result"]
    imp_info_lst.append(id_subnet)
    """增加VIP池"""
    info_add_vip = [id_subnet,  nas_common.VIP_DOMAIN_NAME, nas_common.VIP_ADDRESSES, "NAS", "DYNAMIC"]
    mst_add_vip = nas_common.add_vip_address_pool(info_add_vip[0], info_add_vip[1], info_add_vip[2],
                                                  info_add_vip[3], info_add_vip[4])
    if "" != mst_add_vip["detail_err_msg"]:
        add_vip_err = "add VIP in node %d failed;info: %s" % (case_id, imp_info_lst)
        common.judge_rc(-1, 0, add_vip_err)
    id_vip = mst_add_vip["result"]
    imp_info_lst.append(id_vip)
    """多次验证:缺陷本身只做了一次就err了，此处拓展为多次"""
    # todo:需求不合理，现在需要删除vip后才可disable nas（jira id：P300-2883）
    # "detail_err_msg": "Can not disable all nas services, please remove the nas
    # protocol type's ip address pools firstly in the access zone id
    # :30",
    random_times = random.choice([2, 10])
    log.info("%d times disable-enable will to do!" % random_times)
    for times in range(1, random_times):
        log.info("No.%d disable-enable nas begin!" % times)
        """disable nas"""
        nas_state_change(id_az, False)
        """再次enable nas"""
        nas_state_change(id_az, True)
    log.info("%d disable-enable nas done!" % random_times)
    """删除本脚本创建的"""
    vip_dele = nas_common.delete_vip_address_pool(id_vip)
    # todo：no json object could be decoded
    if "" != vip_dele["detail_err_msg"]:
        dele_vip_err = "dele VIP in node %d failed;info: %s" % (case_id, imp_info_lst)
        common.judge_rc(-1, 0, dele_vip_err)
    nas_state_change(id_az, False)
    subnet_dele = nas_common.delete_subnet(id_subnet)
    if "" != subnet_dele["detail_err_msg"]:
        dele_sub_err = "dele subnet in node %d failed;info: %s" % (case_id, imp_info_lst)
        common.judge_rc(-1, 0, dele_sub_err)
    az_dele = nas_common.delete_access_zone(id_az)
    if "" != az_dele["detail_err_msg"]:
        dele_az_err = "dele az in node %d failed;info: %s" % (case_id, imp_info_lst)
        common.judge_rc(-1, 0, dele_az_err)
    log.info("case succeed!")
    return


def main():
    # prepare_clean.defect_test_prepare(FILE_NAME)
    prepare_clean.nas_test_prepare(FILE_NAME)
    case()
    prepare_clean.nas_test_clean()
    # prepare_clean.defect_test_clean(FILE_NAME)
    # oCnas服务比较特殊，不用检查


if __name__ == '__main__':
    common.case_main(main)
