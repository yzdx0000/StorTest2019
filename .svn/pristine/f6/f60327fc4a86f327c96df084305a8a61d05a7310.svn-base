# -*-coding:utf-8 -*
#######################################################
# author zhangchengyu
# date 2018-11-30
# @summary：
# x-x-x-x     用户/用户组，本地认证服务器，添加用户/用户组
# @steps:
# 1.创建认证服务器，启动NAS
# 2.创建用户组n个，用户m个，其中用户的主组从n个中随机抽取，副组从n+[None]中随机抽取
# 3.随机选取步骤2中的用户验证FTP功能和SMB功能
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
import remote

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)  # /mnt/volume1/snap/snap_16_0_4_104
SYSTEM_IP = get_config.get_parastor_ip()
node_ip = SYSTEM_IP
WIN_HOST = get_config.get_win_client_ips()[0]
DISK_SYMBOL = get_config.get_win_disk_symbols()[0]


def executing_case1():
    group_num = 2   # 创建用户组的个数
    user_num = 5    # 创建用户的个数
    """创建访问分区"""
    access_zone_id, az_node_id = create_access_zone(auth_provider_id_list=[None])
    """启动NAS"""
    enable_nas(access_zone_id=access_zone_id)
    """创建用户"""
    user_id_list, user_name_list = create_auth_user(m=user_num, n=group_num)
    """验证FTP的功能"""
    ftp_id = random.choice(az_node_id)
    node = common.Node()
    ftp_ip = node.get_node_ip_by_id(node_id=ftp_id)
    local_user = random.choice(user_name_list)
    ftp_export(access_zone_id=access_zone_id, node_ip=ftp_ip, local_user=local_user)
    """验证SMB功能"""
    smb_id = random.choice(az_node_id)
    node = common.Node()
    smb_ip = node.get_node_ip_by_id(node_id=smb_id)
    smb_export(access_zone_id=access_zone_id, node_ip=smb_ip, user_name_list=user_name_list, d=0)
    # user_name_list = [a, b, c]
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
    # protocol_types_list = ["NFS", "SMB"]
    # protocol_types = ",".join(random.sample(protocol_types_list,
    #                                         random.choice(range(1, len(protocol_types_list) + 1)))) + ",FTP"
    protocol_types = "SMB,NFS,FTP"
    msg2 = nas_common.enable_nas(access_zone_id=access_zone_id, protocol_types=protocol_types)
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit('enable_nas failed!!!')
    time.sleep(10)
    return


def create_auth_group(auth_provider_id, m=1):   # m 为创建用户组的个数
    group_id_list = []
    for i in range(1, m+1):
        log.info("\t[ create_auth_group %s/%s ]" % (i, m))
        group_name = "group_%s" % i
        msg2 = nas_common.create_auth_group(auth_provider_id=auth_provider_id, name=group_name)
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            common.except_exit("get_auth_providers_local")
        group_id = msg2["result"]
        group_id_list.append(group_id)
    return group_id_list       # 返回列表


def create_auth_user(m=1, n=1):   # m 为创建用户的个数
    msg2 = nas_common.get_auth_providers_local()
    if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
        common.except_exit("get_auth_providers_local")
    auth_providers_local = msg2["result"]["auth_providers"][0]["id"]
    group_id_list = create_auth_group(auth_provider_id=auth_providers_local, m=n)
    user_id_list = []
    user_name_list = []
    for i in range(1, m+1):
        """创建用户"""
        primary_group_id = random.choice(group_id_list)
        secondary_group_ids_a = group_id_list + [None]
        secondary_group_ids = random.choice(secondary_group_ids_a)
        log.info("\t[ create_auth_user %s/%s ]" % (i, m))
        user_name = "user_%s" % i
        user_password = "111111"
        msg2 = nas_common.create_auth_user(auth_provider_id=auth_providers_local, name=user_name, password=user_password,
                                           primary_group_id=primary_group_id, secondary_group_ids=secondary_group_ids)
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            common.except_exit("get_auth_providers_local")
        user_id = msg2["result"]
        user_id_list.append(user_id)
        user_name_list.append(user_name)
    return user_id_list, user_name_list       # 返回列表


def ftp_export(access_zone_id, node_ip, local_user=None, d=0):
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
    ftp_export_id = msg1["result"]

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

    """删除FTP导出"""
    log.info("\t[ delete_ftp_exports ]")
    msg1 = nas_common.delete_ftp_exports(ids=ftp_export_id)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('delete_ftp_export failed!!!')
    return


def smb_export(access_zone_id, node_ip, user_name_list=None, d=0):  # user_name_list = [a, b, c]
    """创建smb导出并对授权IP不做限制"""
    """创建目录"""
    log.info("\t[ create_file_list ]")
    m = access_zone_id + d
    smb_path = nas_common.ROOT_DIR + "smb_dir_%s" % m
    nas_smb_path = get_config.get_one_nas_test_path() + "/smb_dir_%s" % m
    msg6 = nas_common.create_file(path=smb_path, posix_permission="rwxr-xr-x")
    if msg6["err_msg"] != "" or msg6["detail_err_msg"] != "":
        common.except_exit('create_file failed!!!')

    """ 检查file是否创建成功"""
    log.info("\t[ get_file_list ]")
    msg7 = nas_common.get_file_list(path=smb_path)
    if msg7["err_msg"] != "" or msg7["detail_err_msg"] != "":
        common.except_exit('get_file_list failed!!!')

    """创建smb导出"""
    log.info("\t[ create_smb_export ]")
    export_name = 'smb_export_%s' % m
    exe_info = nas_common.create_smb_export(access_zone_id=access_zone_id, export_name=export_name,
                                            export_path=smb_path)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('create smb export failed !!!')
    export_id = exe_info['result']

    """创建smb授权客户端"""
    log.info("\t[ add_smb_export_auth_clients ]")
    auth_clients_list = []
    for user_name in user_name_list:
        a = [1, 2]
        b = random.choice(a)
        if b == 1:
            exe_info = nas_common.add_smb_export_auth_clients(export_id=export_id, name=user_name, user_type='USER',
                                                              run_as_root="true")
            if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                log.error('add_smb_export_auth_clients failed !!!')
        elif b == 2:
            exe_info = nas_common.add_smb_export_auth_clients(export_id=export_id, name=user_name, user_type='USER',
                                                              run_as_root="false", permission_level="full_control")
            if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
                log.error('add_smb_export_auth_clients failed !!!')
        auth_clients_list.append(exe_info['result'][0])

    """windows客户端挂载验证"""
    log.info("\t[ windows_mount_smb_path ]")
    mount_export_name = export_name
    mount_user = random.choice(user_name_list)
    mount_vip = node_ip
    mount_passwd = '111111'
    rc = smb_mount_create(mount_vip, mount_export_name, mount_passwd, mount_user)  # windows端执行挂载、创建文件
    dir_lst = rc[0]
    file_lst = rc[1]
    client_total_num = int(len(dir_lst) + len(file_lst))
    print ('**********%s %s**************' % (len(dir_lst), len(file_lst)))

    '''linux端导出目录下检查文件是否正确'''
    log.info("\t[ linux_check_smb_file ]")
    cmd = "cd %s; ls -lR |grep '^-'|wc -l" % nas_smb_path
    rc, check_file_num = common.run_command(node_ip, cmd)
    common.judge_rc(rc, 0, 'get files failed !!!')
    cmd = "cd %s; ls -lR |grep '^d'|wc -l" % nas_smb_path
    rc, check_dir_num = common.run_command(node_ip, cmd)
    common.judge_rc(rc, 0, 'get directories failed !!!')
    check_total_num = int(check_file_num) + int(check_dir_num)  # 导出目录下文件及目录数检查
    if check_total_num != client_total_num:
        common.except_exit('server file&dir check failed !!!')

    '''windows客户端删除文件并umount'''
    log.info("\t[ waiting for 30s ]")
    time.sleep(30)
    smb_clean_umount(dir_lst, file_lst)

    """SMB server删除文件"""
    log.info("\t[ SMB server delete file ]")
    cmd = "cd %s && rm -rf *" % nas_smb_path
    rc, stdout = common.run_command(node_ip, cmd)
    common.judge_rc(rc, 0, 'SMB server %s delete file failed !!!' % node_ip)

    """删除SMB导出"""
    log.info("\t[ delete_smb_exports ]")
    msg1 = nas_common.delete_smb_exports(ids=export_id)
    if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
        common.except_exit('delete_smb_exports failed!!!')
    return


def smb_mount_create(mount_vip, mount_export_name, mount_passwd, mount_user):
    rs = remote.Remote(uri='%s:8270' % WIN_HOST)
    rc, stdout = rs.run_keyword(name='smb_mount', args=(DISK_SYMBOL, '\\\\%s\%s' % (mount_vip, mount_export_name),
                                                        mount_passwd, mount_user))
    log.info(rc)
    log.info(stdout.decode("gb2312"))
    log.info('waiting for 5s')
    time.sleep(5)
    rc = rs.run_keyword(name='create_dir_file', args=(DISK_SYMBOL, ))
    return rc


def smb_clean_umount(dir_lst, file_lst):
    rs = remote.Remote(uri='%s:8270' % WIN_HOST)
    log.info(rs.run_keyword(name='delete_dir_file', args=(dir_lst, file_lst)))

    log.info('waiting for 5s')
    time.sleep(5)
    rs.run_keyword(name='smb_umount', args=(DISK_SYMBOL,))
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