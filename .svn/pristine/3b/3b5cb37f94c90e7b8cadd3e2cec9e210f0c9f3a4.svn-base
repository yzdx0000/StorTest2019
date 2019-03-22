# -*-coding:utf-8 -*
import os
import time
import datetime

import utils_path
import common
import get_config
import log
import prepare_clean
import remote
import nas_common

##########################################################################
#
# Author: zhanghan
# date 2018-12-01
# @summary：
#    DAC smb客户端自动化脚本集合，原P200开发写的最小用例集。
# @steps:
#    脚本运行前准备工作：a) 配置访问管理，包括AD认证服务器(du1属于dg1,du2属于dg1,du3属于dg3,du4属于sugon,du5属于dg5)、访问区、业务子网，并将相应信息写入配置文件
#                        d) 修改全局变量smb_client_ip、scripts_location_win、current_ip
#
#    1、获取节点信息:集群节点ip、集群节点客户端挂载路径、ip池的域名；
#    2、测试前准备，创建smb共享，并添加用户/用户组列表；
#    3、smb客户端自动化脚本集合测试主体部分；
#        3-1、挂载smb客户端
#        3-2、将测试脚本拷贝到本地C盘
#        3-3、smb客户端权限验证
#        3-4、将生成的日志拷贝到linux节点记录日志位置并判断脚本执行成功与否
#        3-5、删除创建到环境中的测试目录
#        3-6、C盘中删除测试脚本
#    4、权限验证成功，卸载smb客户端挂载目录，并删除授权；
#
# @changelog：
##########################################################################

#################### 全局变量 ####################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[
    0]                 # 本脚本名字
smb_file_dir = "smb_file_dir"    # 权限测试目录名称
disk_symbol = 'h:'
export_name_smb = 'smb_' + FILE_NAME  # smb共享名称
smb_client_ip = '10.2.43.204'    # smb客户端ip
smb_client_port = '8270'    # smb端口号
current_ip = "10.2.42.80"  # 当前节点，即脚本执行所在节点的ip
scripts_location_win = r'Z:\StorTest\\test_cases\cases\\test_case\P300\DAC\smb_scripts\smbd_ps'  # 测试脚本在smb客户端的路径


def case():
    log.info("1> 获取节点信息")
    parastor_ip = get_config.get_parastor_ip()
    log.info("parastor_ip is: %s" % parastor_ip)

    parastor_mount_path = get_config.get_one_mount_path()
    log.info("parastor_mount_path is: %s" % parastor_mount_path)

    vip_domain_name = get_config.get_vip_domain_name()[0]
    log.info("vip_domain_name is: %s" % vip_domain_name)

    log.info("2> 测试前准备，创建smb共享，并添加用户/用户组列表")
    access_zone_name = get_config.get_access_zone_name()[0]
    access_zone_info = nas_common.get_access_zones()
    access_zone_info = access_zone_info["result"]["access_zones"]
    access_zone_id = ''
    for access_zone_tmp in access_zone_info:
        if access_zone_name in access_zone_tmp["name"]:
            access_zone_id = access_zone_tmp["id"]
    if '' == access_zone_id:
        common.judge_rc(1, 0, "get access_zone_id failed")
    else:
        pass
    export_path = parastor_mount_path.split('/')[-1] + ':/'
    nas_common.create_smb_export(access_zone_id, export_name_smb, export_path)
    smb_export_msg = nas_common.get_smb_exports()
    smb_export_msg = smb_export_msg["result"]["exports"]
    smb_export_id = ""
    for smb_info in smb_export_msg:
        if export_name_smb in smb_info["export_name"]:
            smb_export_id = smb_info["id"]
    if smb_export_id == "":
        common.judge_rc(1, 0, "get smb_export_id failed")
    ad_users_list = get_config.get_ad_users_dac()
    ad_users_list = ad_users_list[:6]
    for i in range(len(ad_users_list)):
        nas_common.add_smb_export_auth_clients(
            smb_export_id,
            ad_users_list[i],
            'USER',
            'false',
            'full_control')

    log.info("3> smb客户端自动化脚本集合测试主体部分")
    a = remote.Remote('%s:%s' % (smb_client_ip, smb_client_port))
    log.info("3-1> 挂载smb客户端")
    vip_addresses = get_config.get_vip_addresses()[2]
    vip_addresses_list = vip_addresses.split(',')
    log.info("vip_true_address_list is: %s" % str(vip_addresses_list))

    passwd = get_config.get_ad_user_pw_dac()[0]
    ad_domain_name = get_config.get_ad_domain_name_dac()[0]
    mount_path_tmp = '\\\\' + \
        vip_addresses_list[0] + '\\' + export_name_smb
    user_tmp = ad_domain_name + '\\' + ad_users_list[0]
    rc = a.run_keyword('smb_mount',
                       [disk_symbol,
                        mount_path_tmp,
                        passwd,
                        user_tmp])
    common.judge_rc(rc[0], 0, "mount smb failed")

    log.info("3-2> 将测试脚本拷贝到本地C盘")
    origin_path = scripts_location_win
    destination_path = "C:\\"
    rc = a.run_keyword('copy_file', [origin_path, destination_path])
    common.judge_rc(rc[0], 0, "cp test scripts failed")
    time.sleep(5)

    log.info("3-3> smb客户端权限验证")
    now_time = datetime.datetime.now()
    now_time = now_time.strftime('%Y-%m-%d-%H-%M-%S')
    file_dir = "C:\\smbd_ps"
    file_name = "smbd_st.bat"
    rc = a.run_keyword('excute_acl_bat', [file_dir, file_name])
    common.judge_rc(rc[0], 0, "win perl excute failed")
    log.info("3-4> 将生成的日志拷贝到linux节点记录日志位置并判断脚本执行成功与否")
    log.info("3-4-1> 将生成的日志拷贝到windows节点记录日志位置")
    log_origin = "C:\\smbd_ps\\st_smbd_test_result.txt"
    log_destination = scripts_location_win
    rc = a.run_keyword('copy_file', [log_origin, log_destination])
    common.judge_rc(rc[0], 0, "cp test scripts failed")
    log.info("3-4-2> 将生成的日志拷贝到linux节点记录日志位置")
    smbd_ps_dir = "/home/StorTest/test_cases/cases/test_case/P300/DAC/smb_scripts/smbd_ps"
    log_name = "st_smbd_test_result.txt"
    log_ori_linux = os.path.join(smbd_ps_dir, log_name)
    log_des_linux = "/home/StorTest/test_cases/log/case_log"
    cmd = "cp -rf %s %s" % (log_ori_linux, log_des_linux)
    rc = common.command(cmd)
    common.judge_rc(rc, 0, "cp logfile to log_dir %s" % log_des_linux)
    log.info("3-4-3> 使用dos2unix命令对日志文件进行转码")
    log_location = os.path.join(log_des_linux, log_name)
    cmd = "dos2unix %s" % log_location
    rc = common.command(cmd)
    common.judge_rc(rc, 0, "dos2unix log_file %s" % log_location)
    log.info("3-4-4> 修改日志文件名称，增加时间戳信息")
    log_name_with_time = now_time + '_' + log_name
    log_location_with_time = os.path.join(log_des_linux, log_name_with_time)
    cmd = "mv %s %s" % (log_location, log_location_with_time)
    rc = common.command(cmd)
    common.judge_rc(rc, 0, "rename log name with time info failed")
    log.info("3-4-5> 判断日志中是否记录有失败项，有失败项则报错退出")
    cmd = "cat %s | grep FAILED | cut -d ' ' -f2 | cut -d '.' -f1" % log_location_with_time
    (rc, output) = common.run_command(current_ip, cmd)
    output = output.strip()
    if str(output) != '0':
        exit_rc = 1
        log.info("the scripts is failed, please check")
        common.judge_rc(exit_rc, 0, "the scripts is failed, please check")
    else:
        pass
    log.info("3-5> 删除创建到环境中的测试目录")
    cmd = "ssh %s  \"cd %s;ls | grep DAC-STUC-SMBD | xargs rm -fr\"" % (
        parastor_ip, parastor_mount_path)
    rc = common.command(cmd)
    common.judge_rc(rc, 0, "rm -fr testdirfailed")
    log.info("3-6> C盘中删除测试脚本")
    rm_dir = r"C:\smbd_ps"
    rc = a.run_keyword('rm_win_file', [rm_dir])
    common.judge_rc(rc[0], 0, "rm test scripts failed")

    log.info("4> 权限验证成功，卸载smb客户端挂载目录，并删除授权")
    log.info("4-1> 卸载smb客户端挂载目录")
    (rc, output) = a.run_keyword('smb_umount', [disk_symbol])
    common.judge_rc(rc, 0, "umount smb client failed")
    log.info("4-2> 删除smb授权")
    nas_common.delete_smb_exports(smb_export_id)

    return


def main():
    prepare_clean.test_prepare(FILE_NAME)
    case()
    prepare_clean.test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
