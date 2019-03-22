# -*-coding:utf-8 -*
#######################################################
# author zhangchengyu
# date 2018-11-30
# @summary：
# x-x-x-x     用户/用户组，本地认证服务器，修改用户/用户组
# @steps:
# 准备：创建本次认证，启动NAS
# 1.未被使用时，修改用户/用户组的参数：
# ① 修改用户的密码
# ② 修改用户的主组，[primary_group_id, None]中随机选取一个
# ③ 修改用户的副组，[1,2,3, ……]中随机选取n个，或者[1,2,3,None]中随机选取1个
# ④ 创建FTP导出，验证FTP功能
# 2.被使用时，修改用户/用户组的参数：在步骤1创建了FTP导出后，对同一用户进行如下操作
# ① 修改用户的密码
# ② 修改用户的主组，[primary_group_id, None]中随机选取一个
# ③ 修改用户的副组，[1,2,3, ……]中随机选取n个，或者[1,2,3,None]中随机选取1个
# ④ 删除原来的FTP导出，创建新FTP导出，验证FTP功能
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
    run_times = 2           # 跑多少遍的控制
    n = 2  # 修改附属组时，创建附属组的个数
    for p in range(1, run_times + 1):
        log.info("\t[########################## case begin #################################]")
        log.info("\t[this is %s/%s time]" % (p, run_times))
        if p > 1:
            """清理环境"""
            """删除所有NAS的配置文件"""
            nas_common.delete_all_nas_config()
            """删除所有的NAS目录"""
            common.rm_exe(prepare_clean.NAS_RANDOM_NODE_IP, nas_common.NAS_PATH)
            nas_common.mkdir_nas_path()

        """创建访问分区"""
        access_zone_id, az_node_id = create_access_zone(auth_provider_id_list=[None])
        """启动NAS"""
        enable_nas(access_zone_id=access_zone_id)
        """1.未被使用时，修改用户/用户组的参数"""
        log.info("\t[ 1 未被使用时，修改用户/用户组的参数 ]")
        """创建用户"""
        user_id_list, user_name_list = create_auth_user(m=1, n=1)
        user_id = random.choice(user_id_list)
        """修改用户"""
        """修改密码"""
        log.info("\t[ 1 update_auth_user_password ]")
        new_passwd = 222222
        msg1 = nas_common.update_auth_user(user_id=user_id, password=new_passwd)
        if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
            common.except_exit('update_auth_user_password failed!!!')

        """修改primary_group_id"""
        log.info("\t[ 1 update_auth_user_primary_group_id ]")
        msg2 = nas_common.get_auth_providers_local()
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            common.except_exit("get_auth_providers_local")
        auth_providers_local = msg2["result"]["auth_providers"][0]["id"]
        group_name = "update_primary_group"
        group_id_list = create_auth_group(auth_provider_id=auth_providers_local, m=1, group_name=group_name)
        group_id_list = group_id_list + [None]
        group_id = random.choice(group_id_list)
        msg1 = nas_common.update_auth_user(user_id=user_id, primary_group_id=group_id)
        if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
            common.except_exit('update_auth_user_primary_group_id failed!!!')

        """修改secondary_group_ids"""
        log.info("\t[ 1 update_auth_user_secondary_group_ids ]")
        msg2 = nas_common.get_auth_providers_local()
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            common.except_exit("get_auth_providers_local")
        auth_providers_local = msg2["result"]["auth_providers"][0]["id"]
        group_id_list = []
        for i in range(1, n + 1):
            group_name = "update_secondary_group_%s" % i
            group_id_list_a = create_auth_group(auth_provider_id=auth_providers_local, m=1, group_name=group_name)
            group_id_list = group_id_list + group_id_list_a
        log.info("group_id_list = %s" % group_id_list)
        a = [1, 2]
        b = random.choice(a)
        if b == 1:
            group_id_a = random.sample(group_id_list, random.choice(range(1, len(group_id_list) + 1)))
            group_id = ",".join([str(p) for p in group_id_a])
        elif b == 2:
            group_id_list = group_id_list + [None]
            group_id = random.choice(group_id_list)
        msg1 = nas_common.update_auth_user(user_id=user_id, secondary_group_ids=group_id)
        if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
            common.except_exit('update_auth_user_secondary_group_ids failed!!!')

        """验证FTP的功能"""
        ftp_id = random.choice(az_node_id)
        node = common.Node()
        ftp_ip = node.get_node_ip_by_id(node_id=ftp_id)
        local_user = random.choice(user_name_list)
        ftp_export(access_zone_id=access_zone_id, node_ip=ftp_ip, local_user=local_user, password=new_passwd)

        """2.被使用时，修改用户/用户组的参数"""
        log.info("\t[ 2 被使用时，修改用户/用户组的参数 ]")
        """修改用户"""
        """修改密码"""
        log.info("\t[ 1 update_auth_user_password ]")
        new_passwd_b = 333333
        msg1 = nas_common.update_auth_user(user_id=user_id, password=new_passwd_b)
        if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
            common.except_exit('update_auth_user_password failed!!!')

        """修改primary_group_id"""
        log.info("\t[ 1 update_auth_user_primary_group_id ]")
        msg2 = nas_common.get_auth_providers_local()
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            common.except_exit("get_auth_providers_local")
        auth_providers_local = msg2["result"]["auth_providers"][0]["id"]
        group_name = "enable_update_primary_group"
        group_id_list = create_auth_group(auth_provider_id=auth_providers_local, m=1, group_name=group_name)
        group_id_list = group_id_list + [None]
        group_id = random.choice(group_id_list)
        msg1 = nas_common.update_auth_user(user_id=user_id, primary_group_id=group_id)
        if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
            common.except_exit('update_auth_user_primary_group_id failed!!!')

        """修改secondary_group_ids"""
        log.info("\t[ 1 update_auth_user_secondary_group_ids ]")
        msg2 = nas_common.get_auth_providers_local()
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            common.except_exit("get_auth_providers_local")
        auth_providers_local = msg2["result"]["auth_providers"][0]["id"]
        group_id_list = []
        for i in range(1, n + 1):
            group_name = "enable_update_secondary_group_%s" % i
            group_id_list_a = create_auth_group(auth_provider_id=auth_providers_local, m=1, group_name=group_name)
            group_id_list = group_id_list + group_id_list_a
        log.info("group_id_list = %s" % group_id_list)
        a = [1, 2]
        b = random.choice(a)
        if b == 1:
            group_id_a = random.sample(group_id_list, random.choice(range(1, len(group_id_list) + 1)))
            group_id = ",".join([str(p) for p in group_id_a])
        elif b == 2:
            group_id_list = group_id_list + [None]
            group_id = random.choice(group_id_list)
        msg1 = nas_common.update_auth_user(user_id=user_id, secondary_group_ids=group_id)
        if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
            common.except_exit('update_auth_user_secondary_group_ids failed!!!')

        """删除FTP导出"""
        log.info("\t[ delete_ftp_exports ]")
        ftp_ids = nas_common.get_ftp_exports_id_list()
        if ftp_ids != "":
            check_result = nas_common.delete_ftp_exports(ids=ftp_ids)
            if check_result["detail_err_msg"] != "":
                log.error("delete_ftp_exports Failed")
                common.except_exit('delete_ftp_export failed!!!')

        log.info("\t[ FTP server clean environment ]")
        cmd = "cd %s && rm -rf *" % get_config.get_one_nas_test_path()
        rc, stdout = common.run_command(node_ip, cmd)
        common.judge_rc(rc, 0, 'FTP server %s delete file failed !!!' % node_ip)

        """验证FTP的功能"""
        ftp_id = random.choice(az_node_id)
        node = common.Node()
        ftp_ip = node.get_node_ip_by_id(node_id=ftp_id)
        local_user = random.choice(user_name_list)
        ftp_export(access_zone_id=access_zone_id, node_ip=ftp_ip, local_user=local_user, password=new_passwd_b)

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


def create_access_zone(auth_provider_id_list):
    log.info("\t[create_access_zone ]")
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
    time.sleep(10)
    return access_zone_id, node_id


def enable_nas(access_zone_id):
    log.info("\t[ enable_nas ]")
    protocol_types_list = ["NFS", "SMB"]
    protocol_types = ",".join(random.sample(protocol_types_list,
                                            random.choice(range(1, len(protocol_types_list) + 1)))) + ",FTP"
    msg2 = nas_common.enable_nas(access_zone_id=access_zone_id, protocol_types=protocol_types)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('enable_nas failed!!!')
    time.sleep(10)
    return


def create_auth_group(auth_provider_id, m=1, group_name=None):   # m 为创建用户组的个数
    group_id_list = []
    for i in range(1, m+1):
        log.info("\t[ create_auth_group %s/%s ]" % (i, m))
        if group_name is None:
            group_name = "group_%s" % i
        msg2 = nas_common.create_auth_group(auth_provider_id=auth_provider_id, name=group_name)
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            common.except_exit("get_auth_providers_local")
        group_id = msg2["result"]
        group_id_list.append(group_id)
    return group_id_list       # 返回列表


def create_auth_user(m=1, n=1, user_name=None, group_name=None):   # m 为创建用户的个数
    msg2 = nas_common.get_auth_providers_local()
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("get_auth_providers_local")
    auth_providers_local = msg2["result"]["auth_providers"][0]["id"]
    group_id_list = create_auth_group(auth_provider_id=auth_providers_local, m=n, group_name=group_name)
    user_id_list = []
    user_name_list = []
    for i in range(1, m+1):
        """创建用户"""
        primary_group_id = random.choice(group_id_list)
        secondary_group_ids_a = group_id_list + [None]
        secondary_group_ids = random.choice(secondary_group_ids_a)
        log.info("\t[ create_auth_user %s/%s ]" % (i, m))
        if user_name is None:
            user_name = "group_%s" % i
        user_password = "111111"
        msg2 = nas_common.create_auth_user(auth_provider_id=auth_providers_local, name=user_name,
                                           password=user_password, primary_group_id=primary_group_id,
                                           secondary_group_ids=secondary_group_ids)
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            common.except_exit("get_auth_providers_local")
        user_id = msg2["result"]
        user_id_list.append(user_id)
        user_name_list.append(user_name)
    return user_id_list, user_name_list       # 返回列表


def ftp_export(access_zone_id, node_ip, local_user=None, password=111111, d=0):
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
    elif access_zone_type == "LOCAL":
        ftp_user_name = local_user
    msg1 = nas_common.create_ftp_export(access_zone_id=access_zone_id, user_name=ftp_user_name, export_path=ftp_path,
                                        enable_upload="true")
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('create_ftp_export failed!!!')
    # ftp_export_id = msg1["result"]

    """客户端上传文件"""
    log.info("\t[ FTP client put file ]")
    ftp_sh_file = "/root/ftp.file.sh"
    ftp_client_ip = nas_common.FTP_1_CLIENT_IP
    cmd = "echo "" > %s &&" \
          "echo '#!/bin/bash' >> %s &&" \
          "echo 'ftp -nv << EOF' >> %s &&" \
          "echo 'open %s' >> %s &&" \
          "echo 'user %s %s' >> %s &&" \
          "echo 'prompt off' >> %s &&" \
          "echo 'put %s /ftp' >> %s &&" \
          "echo 'close' >> %s &&" \
          "echo 'bye' >> %s &&" \
          "echo 'EOF' >> %s &&" \
          "echo 'sleep 2' >> %s " % (ftp_sh_file, ftp_sh_file, ftp_sh_file, node_ip, ftp_sh_file, ftp_user_name,
                                     password, ftp_sh_file, ftp_sh_file, ftp_sh_file, ftp_sh_file, ftp_sh_file,
                                     ftp_sh_file, ftp_sh_file, ftp_sh_file)
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