# -*-coding:utf-8 -*
#######################################################
# author zhangchengyu
# date 2018-11-26
# @summary：
# x-x-x-x     用户/用户组，添加认证服务器，被enable的访问分区引用（访问区修改节点）
# @steps:
# 1.创建ad，ldap，ldap-pdc，nis认证，查看对应认证服务器下的部分用户（NAS配置文件中存在的用户）是否存在，存在则认为通过；
#   获取用户/用户组
# 2.随机引用认证服务创建访问分区，使用 FTP + SMB/NFS enable_nas，
#   ① 获取用户/用户组并与步骤1中获取结果作对比；
#   ② 并再次验证部分用户（NAS配置文件中存在的用户）是否存在，存在则认为通过
# 3.修改访问分区中的节点个数，
#   ① 验证FTP的功能；
#   ② 获取用户/用户组并与步骤2中获取用户/用户组的结果作对比
# @changelog：
#
#######################################################
import os
import time
import random

import utils_path
import common
import nas_common
import log
import get_config
import prepare_clean

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)  # /mnt/volume1/snap/snap_16_0_4_104
SYSTEM_IP = get_config.get_parastor_ip()
node_ip = SYSTEM_IP


def executing_case1():
    run_times = 2    # 跑多少遍的控制
    for i in range(1, run_times + 1):
        log.info("\t[this is %s/%s time]" % (i, run_times))
        if i > 1:
            """清理环境"""
            """删除所有NAS的配置文件"""
            nas_common.delete_all_nas_config()
            """删除所有的NAS目录"""
            common.rm_exe(prepare_clean.NAS_RANDOM_NODE_IP, nas_common.NAS_PATH)
            nas_common.mkdir_nas_path()

        """1 创建认证"""
        auth_provider_id_list = []
        """a.创建ad认证"""
        log.info("\t[1 add_auth_provider_ad]")
        ad_name = "ad_auth_provider"
        msg2 = nas_common.add_auth_provider_ad(name=ad_name,
                                               domain_name=nas_common.AD_DOMAIN_NAME,
                                               dns_addresses=nas_common.AD_DNS_ADDRESSES,
                                               username=nas_common.AD_USER_NAME,
                                               password=nas_common.AD_PASSWORD,
                                               services_for_unix="NONE")

        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            common.except_exit("add_auth_provider_ad failed")
        ad_auth_provider_id = msg2["result"]
        auth_provider_id_list.append(ad_auth_provider_id)
        get_ad_user_group(auth_provider_id=ad_auth_provider_id)
        get_ad_user_list = get_auth_users_list(ad_auth_provider_id)
        get_ad_group_list = get_auth_groups_list(ad_auth_provider_id)

        """b.创建ldap认证"""
        log.info("\t[1 add_auth_provider_ldap]")
        ldap_name = "ldap_auth_provider"
        msg2 = nas_common.add_auth_provider_ldap(name=ldap_name, base_dn=nas_common.LDAP_BASE_DN,
                                                 ip_addresses=nas_common.LDAP_IP_ADDRESSES, port=389)
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            common.except_exit("add_auth_provider_ldap failed")
        ldap_auth_provider_id = msg2["result"]
        auth_provider_id_list.append(ldap_auth_provider_id)
        get_ldap_user_group(auth_provider_id=ldap_auth_provider_id)
        get_ldap_user_list = get_auth_users_list(ldap_auth_provider_id)
        get_ldap_group_list = get_auth_groups_list(ldap_auth_provider_id)

        """c.创建ldap_pdc认证"""
        log.info("\t[1 add_auth_provider_ldap_pdc]")
        ldap_name = "ldap_pdc_auth_provider"
        msg2 = nas_common.add_auth_provider_ldap(name=ldap_name, base_dn=nas_common.LDAP_2_BASE_DN,
                                                 ip_addresses=nas_common.LDAP_2_IP_ADDRESSES, port=389,
                                                 bind_dn=nas_common.LDAP_2_BIND_DN,
                                                 bind_password=nas_common.LDAP_2_BIND_PASSWORD,
                                                 domain_password=nas_common.LDAP_2_DOMAIN_PASSWORD,
                                                 user_search_path=nas_common.LDAP_2_USER_SEARCH_PATH,
                                                 group_search_path=nas_common.LDAP_2_GROUP_SEARCH_PATH
                                                 )
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            common.except_exit("add_auth_provider_ldap_pdc failed")
        ldap_pdc_auth_provider_id = msg2["result"]
        auth_provider_id_list.append(ldap_pdc_auth_provider_id)
        get_ldap_pdc_user_group(auth_provider_id=ldap_pdc_auth_provider_id)
        get_ldap_pdc_user_list = get_auth_users_list(ldap_pdc_auth_provider_id)
        get_ldap_pdc_group_list = get_auth_groups_list(ldap_pdc_auth_provider_id)

        """d.创建nis认证"""
        log.info("\t[1 add_auth_provider_nis]")
        nis_name = "nis_auth_provider"
        msg2 = nas_common.add_auth_provider_nis(name=nis_name,
                                                domain_name=nas_common.NIS_DOMAIN_NAME,
                                                ip_addresses=nas_common.NIS_IP_ADDRESSES)

        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            common.except_exit("add_auth_provider_nis failed")
        nis_auth_provider_id = msg2["result"]
        auth_provider_id_list.append(nis_auth_provider_id)
        get_nis_user_group(auth_provider_id=nis_auth_provider_id)
        get_nis_user_list = get_auth_users_list(nis_auth_provider_id)
        get_nis_group_list = get_auth_groups_list(nis_auth_provider_id)

        """2.创建访问分区"""
        log.info("\t[2 create_access_zone ]")
        node = common.Node()
        ids = node.get_nodes_id()
        num = len(ids)
        access_zone_name = "access_zone_first"
        az_auth_provider_id = random.choice(auth_provider_id_list)  # 随机选一种认证服务
        a = []
        for d in range(1, num + 1):
            a.append(d)
        node_id_num = random.choice(a)
        node_id_a = random.sample(ids, int(node_id_num))
        node_id = [str(p) for p in node_id_a]
        access_zone_node_ids = ','.join(node_id)  # 随机选取节点
        msg1 = nas_common.create_access_zone(node_ids=access_zone_node_ids, name=access_zone_name,
                                             auth_provider_id=az_auth_provider_id)
        if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
            common.except_exit('create_access_zone failed!!!')
        access_zone_id = msg1["result"]

        log.info("\t[2 enable_nas ]")
        protocol_types_list = ["NFS", "SMB"]
        protocol_types = ",".join(random.sample(protocol_types_list,
                                                random.choice(range(1, len(protocol_types_list) + 1)))) + ",FTP"
        msg2 = nas_common.enable_nas(access_zone_id=access_zone_id, protocol_types=protocol_types)
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            common.except_exit('enable_nas failed!!!')
        time.sleep(10)

        """获取用户/用户组"""
        log.info("\t[2 创建访问分区后获取用户/用户组 ]")
        first_auth_user_list = get_auth_users_list(az_auth_provider_id)
        first_auth_group_list = get_auth_groups_list(az_auth_provider_id)

        """初步验证用户/用户组"""
        log.info("\t[2 初步验证用户/用户组 ]")
        if ad_auth_provider_id == az_auth_provider_id:
            get_ad_user_group(auth_provider_id=ad_auth_provider_id)
            if first_auth_user_list != get_ad_user_list:
                log.error("first_auth_user_list=%s, get_ad_user_list=%s"
                          % (first_auth_user_list, get_ad_user_list))
                common.except_exit("After create access zones, users have been changed ")
            if first_auth_group_list != get_ad_group_list:
                log.error("first_auth_group_list=%s, get_ad_group_list=%s"
                          % (first_auth_group_list, get_ad_group_list))
                common.except_exit("After create access zones, groups have been changed ")
        elif ldap_auth_provider_id == az_auth_provider_id:
            get_ldap_user_group(auth_provider_id=ldap_auth_provider_id)
            if first_auth_user_list != get_ldap_user_list:
                log.error("first_auth_user_list=%s, get_ldap_user_list=%s"
                          % (first_auth_user_list, get_ldap_user_list))
                common.except_exit("After create access zones, users have been changed ")
            if first_auth_group_list != get_ldap_group_list:
                log.error("first_auth_group_list=%s, get_ldap_group_list=%s"
                          % (first_auth_group_list, get_ldap_group_list))
                common.except_exit("After create access zones, groups have been changed ")
        elif ldap_pdc_auth_provider_id == az_auth_provider_id:
            get_ldap_pdc_user_group(auth_provider_id=ldap_pdc_auth_provider_id)
            if first_auth_user_list != get_ldap_pdc_user_list:
                log.error("first_auth_user_list=%s, get_ldap_pdc_user_list=%s"
                          % (first_auth_user_list, get_ldap_pdc_user_list))
                common.except_exit("After create access zones, users have been changed ")
            if first_auth_group_list != get_ldap_pdc_group_list:
                log.error("first_auth_group_list=%s, get_ldap_pdc_group_list=%s"
                          % (first_auth_group_list, get_ldap_pdc_group_list))
                common.except_exit("After create access zones, groups have been changed ")
        elif nis_auth_provider_id == az_auth_provider_id:
            get_nis_user_group(auth_provider_id=nis_auth_provider_id)
            if first_auth_user_list != get_nis_user_list:
                log.error("first_auth_user_list=%s, get_nis_user_list=%s"
                          % (first_auth_user_list, get_nis_user_list))
                common.except_exit("After create access zones, users have been changed ")
            if first_auth_group_list != get_nis_group_list:
                log.error("first_auth_group_list=%s, get_nis_group_list=%s"
                          % (first_auth_group_list, get_nis_group_list))
                common.except_exit("After create access zones, groups have been changed ")

        """3.修改访问分区"""
        log.info("\t[3 update_access_zone ]")
        node = common.Node()
        ids = node.get_nodes_id()
        num = len(ids)
        access_zone_name = "access_zone_update"
        a = []
        for d in range(1, num + 1):
            a.append(d)
        node_id_num = random.choice(a)
        node_id_a = random.sample(ids, int(node_id_num))
        node_id = [str(p) for p in node_id_a]
        access_zone_node_ids = ','.join(node_id)  # 随机选取节点
        msg1 = nas_common.update_access_zone(access_zone_id=access_zone_id, node_ids=access_zone_node_ids,
                                             name=access_zone_name)
        if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
            common.except_exit('update_access_zone failed!!!')
        time.sleep(10)

        """验证FTP的功能"""
        ftp_id = random.choice(node_id)
        node = common.Node()
        ftp_ip = node.get_node_ip_by_id(node_id=ftp_id)
        ftp_export(access_zone_id, node_ip=ftp_ip, d=i)

        """获取用户/用户组"""
        """初步验证用户/用户组"""
        log.info("\t[3 初步验证用户/用户组 ]")
        if ad_auth_provider_id == az_auth_provider_id:
            get_ad_user_group(auth_provider_id=ad_auth_provider_id)
        elif ldap_auth_provider_id == az_auth_provider_id:
            get_ldap_user_group(auth_provider_id=ldap_auth_provider_id)
        elif ldap_pdc_auth_provider_id == az_auth_provider_id:
            get_ldap_pdc_user_group(auth_provider_id=ldap_pdc_auth_provider_id)
        elif nis_auth_provider_id == az_auth_provider_id:
            get_nis_user_group(auth_provider_id=nis_auth_provider_id)

        log.info("\t[3 更新访问分区后获取用户/用户组 ]")
        update_auth_user_list = get_auth_users_list(az_auth_provider_id)
        update_auth_group_list = get_auth_groups_list(az_auth_provider_id)
        if update_auth_user_list != first_auth_user_list:
            log.error("update_auth_user_list=%s, first_auth_user_list=%s"
                      % (update_auth_user_list, first_auth_user_list))
            common.except_exit("After update access zones, users have been changed ")
        if update_auth_group_list != first_auth_group_list:
            log.error("update_auth_group_list=%s, first_auth_group_list=%s"
                      % (update_auth_group_list, first_auth_group_list))
            common.except_exit("After update access zones, groups have been changed ")

    return


def get_auth_users_list(auth_provider_id):
    rc, msg2 = nas_common.get_auth_users(auth_provider_id=auth_provider_id, print_flag=False)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("get_auth_users failed")
    auth_users = msg2["result"]["auth_users"]
    first_auth_user_list = []
    for auth_user in auth_users:
        first_auth_user_list.append(auth_user["name"])
    return first_auth_user_list


def get_auth_groups_list(auth_provider_id):
    msg2 = nas_common.get_auth_groups(auth_provider_id=auth_provider_id, print_flag=False)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("get_auth_groups failed")
    auth_groups = msg2["result"]["auth_groups"]
    first_auth_group_list = []
    for auth_group in auth_groups:
        first_auth_group_list.append(auth_group["name"])
    return first_auth_group_list


def get_ad_user_group(auth_provider_id):
    """获取用户"""
    ad_auth_user_list = get_auth_users_list(auth_provider_id=auth_provider_id)
    if nas_common.AD_USER_1 not in ad_auth_user_list:
        common.except_exit("get_auth_users %s failed" % nas_common.AD_USER_1)
    if nas_common.AD_USER_2 not in ad_auth_user_list:
        common.except_exit("get_auth_users %s failed" % nas_common.AD_USER_2)
    if nas_common.AD_USER_3 not in ad_auth_user_list:
        common.except_exit("get_auth_users %s failed" % nas_common.AD_USER_3)
    """获取用户组"""
    ad_auth_group_list = get_auth_groups_list(auth_provider_id=auth_provider_id)
    if nas_common.AD_GROUP not in ad_auth_group_list:
        common.except_exit("get_auth_groups %s failed" % nas_common.AD_GROUP)
    return


def get_ldap_user_group(auth_provider_id):
    """获取用户"""
    ldap_auth_user_list = get_auth_users_list(auth_provider_id=auth_provider_id)
    if nas_common.LDAP_USER_1_NAME not in ldap_auth_user_list:
        common.except_exit("get_auth_users %s failed" % nas_common.LDAP_USER_1_NAME)
    if nas_common.LDAP_USER_2_NAME not in ldap_auth_user_list:
        common.except_exit("get_auth_users %s failed" % nas_common.LDAP_USER_2_NAME)
    if nas_common.LDAP_USER_3_NAME not in ldap_auth_user_list:
        common.except_exit("get_auth_users %s failed" % nas_common.LDAP_USER_3_NAME)
    """获取用户组"""
    ldap_auth_group_list = get_auth_groups_list(auth_provider_id=auth_provider_id)
    if nas_common.LDAP_GROUP_1_NAME not in ldap_auth_group_list:
        common.except_exit("get_auth_groups %s failed" % nas_common.LDAP_GROUP_1_NAME)
    if nas_common.LDAP_GROUP_2_NAME not in ldap_auth_group_list:
        common.except_exit("get_auth_groups %s failed" % nas_common.LDAP_GROUP_2_NAME)
    if nas_common.LDAP_GROUP_3_NAME not in ldap_auth_group_list:
        common.except_exit("get_auth_groups %s failed" % nas_common.LDAP_GROUP_3_NAME)
    return


def get_ldap_pdc_user_group(auth_provider_id):
    """获取用户"""
    ldap_pdc_auth_user_list = get_auth_users_list(auth_provider_id=auth_provider_id)
    if nas_common.LDAP_USER_1_NAME not in ldap_pdc_auth_user_list:
        common.except_exit("get_auth_users %s failed" % nas_common.LDAP_USER_1_NAME)
    if nas_common.LDAP_2_USER_1_NAME not in ldap_pdc_auth_user_list:
        common.except_exit("get_auth_users %s failed" % nas_common.LDAP_2_USER_1_NAME)
    """获取用户组"""
    ldap_pdc_auth_group_list = get_auth_groups_list(auth_provider_id=auth_provider_id)
    if nas_common.LDAP_2_GROUP_1_NAME not in ldap_pdc_auth_group_list:
        common.except_exit("get_auth_groups %s failed" % nas_common.LDAP_2_GROUP_1_NAME)
    return


def get_nis_user_group(auth_provider_id):
    """获取用户"""
    nis_auth_user_list = get_auth_users_list(auth_provider_id=auth_provider_id)
    if nas_common.NIS_USER_1 not in nis_auth_user_list:
        common.except_exit("get_auth_users %s failed" % nas_common.NIS_USER_1)
    if nas_common.NIS_USER_2 not in nis_auth_user_list:
        common.except_exit("get_auth_users %s failed" % nas_common.NIS_USER_2)
    """获取用户组"""
    nis_auth_group_list = get_auth_groups_list(auth_provider_id=auth_provider_id)
    if nas_common.NIS_GROUP_1 not in nis_auth_group_list:
        common.except_exit("get_auth_groups %s failed" % nas_common.NIS_GROUP_1)
    if nas_common.NIS_GROUP_2 not in nis_auth_group_list:
        common.except_exit("get_auth_groups %s failed" % nas_common.NIS_GROUP_2)
    return


def ftp_export(access_zone_id, node_ip, d=None):
    # access_zone_id为访问分区的id，d为一个数字，为了区别路导出径名称
    log.info("\t[ 创建ftp导出 ]")
    """创建目录"""
    log.info("\t[ create_file ]")
    m = access_zone_id + d
    ftp_path = nas_common.ROOT_DIR + "ftp_dir_%s" % m
    nas_ftp_path = get_config.get_one_nas_test_path() + "/ftp_dir_%s" % m
    msg6 = nas_common.create_file(path=ftp_path, posix_permission="rwxr-xr-x")
    if msg6["err_msg"] != "" or msg6["detail_err_msg"] != "":
        common.except_exit('create_file failed!!!')

    """ 检查file是否创建成功"""
    log.info("\t[ get_file_list ]")
    msg7 = nas_common.get_file_list(path=ftp_path)
    if msg7["err_msg"] != "" or msg7["detail_err_msg"] != "":
        common.except_exit('get_file_list failed!!!')

    """创建导出路径"""
    log.info("\t[ create_ftp_export ]")
    msg = nas_common.get_access_zones(ids=access_zone_id)
    access_zone_type = msg["result"]["access_zones"][0]["auth_provider"]["type"]
    ftp_user_name = ""
    if access_zone_type == "LDAP":
        ftp_user_name = nas_common.LDAP_USER_1_NAME
    elif access_zone_type == "AD":
        ftp_user_name = nas_common.AD_USER_1
    elif access_zone_type == "NIS":
        ftp_user_name = nas_common.NIS_USER_1
    msg1 = nas_common.create_ftp_export(access_zone_id=access_zone_id, user_name=ftp_user_name, export_path=ftp_path,
                                        enable_upload="true")
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('create_ftp_export failed!!!')

    """客户端上传文件"""
    log.info("\t[ FTP client put file ]")
    ftp_sh_file = "/root/ftp.file.sh"
    ftp_client_ip = nas_common.FTP_1_CLIENT_IP
    cmd = "echo "" > %s &&" \
          "echo '#!/bin/bash' >> %s &&" \
          "echo 'ftp -nv << EOF' >> %s &&" \
          "echo 'open %s' >> %s &&" \
          "echo 'user %s 111111' >> %s &&" \
          "echo 'prompt off' >> %s &&" \
          "echo 'put %s /ftp' >> %s &&" \
          "echo 'close' >> %s &&" \
          "echo 'bye' >> %s &&" \
          "echo 'EOF' >> %s &&" \
          "echo 'sleep 2' >> %s " % (ftp_sh_file, ftp_sh_file, ftp_sh_file, node_ip, ftp_sh_file, ftp_user_name,
                                     ftp_sh_file, ftp_sh_file, ftp_sh_file, ftp_sh_file, ftp_sh_file, ftp_sh_file,
                                     ftp_sh_file, ftp_sh_file)
    rc, stdout = common.run_command(ftp_client_ip, cmd)
    log.info(stdout)
    common.judge_rc(rc, 0, 'FTP client create file failed !!!')
    time.sleep(5)

    cmd = "sh %s" % ftp_sh_file
    rc, stdout = common.run_command(ftp_client_ip, cmd)
    common.judge_rc(rc, 0, 'FTP client %s put file failed !!!' % ftp_client_ip)

    """验证ftp文件是否上传成功"""
    log.info("\t[ FTP server check file ]")
    cmd = "cd %s && ls" % nas_ftp_path
    rc, stdout = common.run_command(node_ip, cmd)
    common.judge_rc(rc, 0, 'FTP server %s check file failed !!!' % node_ip)
    if stdout == "":
        common.except_exit('FTP server %s can not find ftp file!!!' % node_ip)

    """FTP server删除文件"""
    log.info("\t[ FTP server delete file ]")
    cmd = "cd %s && rm -rf *" % nas_ftp_path
    rc, stdout = common.run_command(node_ip, cmd)
    common.judge_rc(rc, 0, 'FTP server %s delete file failed !!!' % node_ip)
    return


#######################################################
# 函数功能：本用例入口函数
# 函数入参：无
# 函数返回值：无
#######################################################
def nas_main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    executing_case1()
    prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)