# -*-coding:utf-8 -*
import os
import time

import utils_path
import shell
import random
import json
import common
import snap_common
import log
import get_config
import prepare_clean
import nas_common

"""
Author:liangxy
date 2018-08-06
@summary：
     缺陷自动化——创建子网与VIP池后，无法ping通域名
@steps:
    1、创建访问区FILE_NAME
    2、创建子网和VIP池
    3、enable nas
    4、修改客户端的dns，ping子网地址、域名
    5、返回结果，清理环境
@changelog：
    最后修改时间：
    修改内容：
"""

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
MAX_WAIT_TIME = 300


def nas_state_change(case_ip, flag=False):
    """
    author：LiangXiaoyu
    function:改变访问区中的nas，根据参数开启或关闭nas
    :param case_ip:访问区所在节点ip；
    :param flag:开启（True）或关闭（False）nas
    :return:
    @changelog：修改raise方式（2018-08-06）
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
        crt_err = "%s nas action failed and exit:\n%s" % (class_action, action_nas_rst)
        common.judge_rc(-1, 0, crt_err)
    else:
        time_count = 0
        while True:
            msg_get_az = nas_common.get_access_zones(None)
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


def rewrite_client_dns(client_ip, dns):
    """
    author:LiangXiaoyu
    description：在客户端执行ping命令，检查子网或域名设置是否生效
    :param client_ip:执行命令的客户端ip
    :param dns:写入resolv.conf文件的dns
    :return:命令执行的返回值、标准输出、备份文件名
    """
    dns_path = "/etc/"
    dns_file = "resolv.conf"
    dns_file_bak = dns_file + "." + FILE_NAME
    cmd_ll = "cd %s && ll | grep %s | wc -l" % (dns_path, dns_file)
    rst_ll, stdout_ll = common.run_command(client_ip, cmd_ll)
    if rst_ll != 0:
        log.info("in %s can't find dns config file %s,touch it" % (client_ip, dns_file))
        cmd_touch = "cd %s && touch %s" % (dns_path, dns_file)
        rst_th, std_th = common.run_command(client_ip, cmd_touch)
    cmd_bak = "cd %s && cp %s %s" % (dns_path, dns_file, dns_file_bak)
    rst_bak, stdout_bak = common.run_command(client_ip, cmd_bak)
    context = "nameserver %s" % dns
    cmd_appent = "cd %s && echo %s > %s" % (dns_path, context, dns_file)
    rst, stdout = common.run_command(client_ip, cmd_appent)
    return rst, stdout, dns_file_bak


def ping_vip_client(client_ip, target_p):
    """
    author:LiangXiaoyu
    description：在客户端执行ping命令，检查子网或域名设置是否生效
    :param client_ip:客户端IP
    :param target_p:目标网段或域名
    :return:命令执行的返回值、标准输出
    """
    cmd = "ping -c 10 %s" % target_p
    rst, stdout = common.run_command(client_ip, cmd)
    return rst, stdout


def recover_client_dns_config(client_ip, dns_file_bak):
    """
    author:LiangXiaoyu
    description：在客户端执行ping命令，检查子网或域名设置是否生效
    :param client_ip:执行命令的客户端ip
    :param dns_file_bak:恢复的备份文件名
    :return:命令执行的返回值、标准输出
    """
    dns_path = "/etc/"
    dns_file = "resolv.conf"
    #todo如果中间有失败未删除的bak的情况，则cp会不会失败？先不返回判断cp的rc值
    cmd_rcv = "cd %s && mv -f %s %s" % (dns_path, dns_file_bak, dns_file)
    rst, stdout = common.run_command(client_ip, cmd_rcv)
    return rst, stdout


def case():
    log.info("case begin")
    """节点列表和客户端IP列表"""
    ob_node = common.Node()
    client_ip_lsts = get_config.get_allclient_ip()
    case_node_id_lst = ob_node.get_nodes_id()

    """handle->节点id、客户端ip；添加后要删除的访问区"""
    case_id = 2
    # todo:random.choice(case_node_id_lst)
    case_ip = ob_node.get_node_ip_by_id(case_id)
    client_ip = random.choice(client_ip_lsts)
    imp_info_lst = []
    '''
    在选定节点添加上访问分区
    '''
    node_ids = nas_common.get_node_ids()
    msg_add_az = nas_common.create_access_zone(node_ids, FILE_NAME + "az")
    if "" != msg_add_az["detail_err_msg"]:
        add_az_err = "create subnet in node %d" % node_ids
        common.judge_rc(-1, 0, add_az_err)
    id_az = msg_add_az["result"]
    imp_info_lst.append(id_az)
    log.info("az id created is %d" % id_az)
    """enable nas"""
    nas_state_change(case_ip, True)
    """创建子网"""
    msg_crt_subnet = nas_common.create_subnet(id_az, FILE_NAME + "snet", 'IPv4', nas_common.SUBNET_SVIP,
                                              nas_common.SUBNET_MASK,
                                              nas_common.SUBNET_NETWORK_INTERFACES, nas_common.SUBNET_GATEWAY,
                                              nas_common.SUBNET_MTU)
    if "" != msg_crt_subnet["detail_err_msg"]:
        crt_err = "create subnet in node %d failed;info:%s" % (node_ids, imp_info_lst)
        common.judge_rc(-1, 0, crt_err)
    id_subnet = msg_crt_subnet["result"]
    imp_info_lst.append(id_subnet)
    """增加VIP池"""
    mst_add_vip = nas_common.add_vip_address_pool(id_subnet, nas_common.VIP_DOMAIN_NAME,
                                                  nas_common.VIP_ADDRESSES, "NAS", "DYNAMIC")
    if "" != mst_add_vip["detail_err_msg"]:
        add_vip_err = "add VIP in node %d failed;info: %s" % (node_ids, imp_info_lst)
        common.judge_rc(-1, 0, add_vip_err)
    id_vip = mst_add_vip["result"]
    imp_info_lst.append(id_vip)
    """修改客户端dns为子网ip:nas_common.SUBNET_SVIP"""
    dns = nas_common.SUBNET_SVIP
    rc_w_dns, std_w_dns, bak_dns_file = rewrite_client_dns(client_ip, dns)
    """检查修改结果"""
    if 0 != rc_w_dns:
        crt_err = "rewrite dns in client %s failed;info: %s" % (client_ip, imp_info_lst)
        common.judge_rc(-1, 0, crt_err)
    """客户端ping域名/子网IP"""
    rc_ping_domin, std_ping_d = ping_vip_client(client_ip, nas_common.VIP_DOMAIN_NAME)
    rc_ping_dns,  std_ping_d = ping_vip_client(client_ip, nas_common.SUBNET_SVIP)
    """恢复客户端的dns"""
    rc_rcv, std_rcv = recover_client_dns_config(client_ip, bak_dns_file)
    if rc_rcv != 0:
        crt_err = "recover dns in client %s failed;info: %s" % (client_ip, imp_info_lst)
        common.judge_rc(-1, 0, crt_err)
    # """删除本脚本创建的"""
    # vip_dele = nas_common.delete_vip_address_pool(id_vip)
    # if "" != vip_dele["detail_err_msg"]:
    #     dele_vip_err = "dele VIP in node %d failed;info: %s" % (case_id, imp_info_lst)
    #     common.judge_rc(-1, 0, dele_vip_err)
    # nas_state_change(case_ip, False)
    # subnet_dele = nas_common.delete_subnet(id_subnet)
    # if "" != subnet_dele["detail_err_msg"]:
    #     dele_sub_err = "dele subnet in node %d failed;info: %s" % (case_id, imp_info_lst)
    #     common.judge_rc(-1, 0, dele_sub_err)
    # az_dele = nas_common.delete_access_zone(id_az)
    # if "" != az_dele["detail_err_msg"]:
    #     dele_az_err = "dele az in node %d failed;info: %s" % (case_id, imp_info_lst)
    #     common.judge_rc(-1, 0, dele_az_err)
    if rc_ping_domin != 0:
        ping_err = "info: %s;%s ping %s is " % (imp_info_lst, client_ip, nas_common.VIP_DOMAIN_NAME)
        common.judge_rc(rc_ping_domin, 0, ping_err)
    if rc_ping_dns != 0:
        ping_err = "info: %s;%s ping %s is " % (imp_info_lst, client_ip, nas_common.SUBNET_SVIP)
        common.judge_rc(rc_ping_dns, 0, ping_err)
    log.info("ping domin/subnet OK!\n(rc_domin:%d;rc_dns:%d)" % (rc_ping_domin, rc_ping_dns))
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