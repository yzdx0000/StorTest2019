# -*-coding:utf-8 -*
import os
import time

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
# date 2018-11-14
# @summary：
#    DAC跨平台（posix/nfs/smb）综合测试。
# @steps:
#    脚本运行前准备工作：a) 配置访问管理，包括AD认证服务器(u1属于g1,u2属于g2,u3属于g3,u4属于g1)、访问区、业务子网，并将相应信息写入配置文件
#                        b) posix客户端授权并手动挂载，并将相应信息写入配置文件
#                        c) nfs/posix客户端需要加入AD域
#
#    1、获取节点信息:posix客户端ip、nfs客户端ip、posix客户端挂载路径、nfs客户端挂载路径、ip池的ip；
#    2、将所需工具(创建文件并设置初始权限用)拷贝到posix客户端节点/tmp下；
#    3、创建测试目录并将权限修改为777；
#    4、创建nfs共享，配置客户端列表；创建smb共享，配置用户列表；
#    5、posix客户端创建文件并设置权限，挂载nfs客户端，而后在posix/nfs客户端进行权限验证；
#    6、挂载smb客户端，在smb客户端进行权限验证；
#    7、如权限验证成功，卸载nfs/smb客户端挂载目录，并删除nfs/smb授权；
#    8、测试成功，则删除测试目录中所有内容
#
# @changelog：
##########################################################################

#################### 全局变量 ####################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[
    0]                 # 本脚本名字
dac_set_path = "/cliparastor/tools/dac_setadvacl"   # posix客户端dac工具路径
multi_platform_dir = "multi_platform_dir"    # 权限测试目录名称
tools_location = "/tmp"    # posix客户端创建文件依赖的工具路径
export_name_nfs = 'nfs' + FILE_NAME   # nfs共享名称
export_name_smb = 'smb' + FILE_NAME  # smb共享名称
tools_dir = "/home/StorTest/test_cases/cases/test_case/P300/DAC/dac_multi_client"
# smb_disk_symbol_list = ['h:', 'i:', 'j:', 'k:']    # smb客户端，u1-u4四个用户挂载的盘符
# smb_client_ip = '10.2.41.250'    # smb客户端ip
# smb_client_port = '8270'    # smb端口号
# smb_scripts_location = r'Z:\StorTest\\test_cases\cases\\test_case\P300\DAC\dac_multi_client' # 测试脚本在smb客户端的路径



def case():
    log.info("1> 获取节点信息")

    client_ip = get_config.get_client_ip()
    log.info("posix client ip is: %s" % client_ip)

    nfs_ip = get_config.get_nfs_client_ip()[0]
    log.info("nfs client ip is: %s" % nfs_ip)

    # posix客户端需要预先手动挂载，且挂载目录需要与卷名称相同
    posix_mount_path = get_config.get_one_mount_path()
    log.info("posix_mount_path is: %s" % posix_mount_path)

    nfs_mount_path = get_config.get_nfs_mount_path()[0]
    log.info("nfs_mount_path is: %s" % nfs_mount_path)

    vip_domain_name = get_config.get_vip_domain_name()[0]
    log.info("vip_domain_name is: %s" % vip_domain_name)

    posix_file_location = os.path.join(posix_mount_path, multi_platform_dir)
    log.info("posix_file_location is: %s" % posix_file_location)

    nfs_file_location = os.path.join(nfs_mount_path, multi_platform_dir)
    log.info("nfs_file_location is: %s" % nfs_file_location)

    # the next is added by zhanghan 20190129
    dac_smb_info_dict = get_config.get_dac_smb_info()

    smb_client_ip = dac_smb_info_dict["smb_client_ip"]
    log.info("smb_client_ip is: %s" % smb_client_ip)

    smb_client_port = dac_smb_info_dict["smb_client_port"]
    log.info("smb_client_port is: %s" % smb_client_port)

    smb_scripts_location = dac_smb_info_dict["smb_scripts_location"]
    log.info("smb_scripts_location is: %s" % smb_scripts_location)

    smb_disk_symbol = dac_smb_info_dict["smb_disk_symbol_list"]
    smb_disk_symbol_list = []
    for item in smb_disk_symbol.split(','):
        smb_disk_symbol_list.append(item)
    log.info("smb_disk_symbol_list is: %s" % smb_disk_symbol_list)

    log.info("2> 将所需工具拷贝到posix客户端节点")
    rc = common.command("scp -r %s/tools %s:%s" % (tools_dir, client_ip, tools_location))
    common.judge_rc(rc, 0, "scp tools failed")

    log.info("3> 创建测试目录")
    rc = common.command(
        "ssh %s \"mkdir %s\"" %
        (client_ip, posix_file_location))
    common.judge_rc(rc, 0, "mkdir testdir failed")
    rc = common.command(
        "ssh %s \"chmod %s %s\"" %
        (client_ip, "777", posix_file_location))
    common.judge_rc(rc, 0, "chmod testdir failed")

    log.info(r"4> 测试前准备，创建nfs\smb共享")
    log.info("4-1> 创建nfs共享，并配置客户端列表")
    # 获取访问区id
    access_zone_name = get_config.get_access_zone_name()[0]
    access_zone_info = nas_common.get_access_zones()
    access_zone_info = access_zone_info["result"]["access_zones"]
    access_zone_id = ''
    for access_zone_tmp in access_zone_info:
        if access_zone_name in access_zone_tmp["name"]:
            access_zone_id = access_zone_tmp["id"]
    if  '' == access_zone_id:
        common.judge_rc(1, 0, "get access_zone_id failed")
    else:
        pass

    export_path = posix_mount_path.split('/')[-1] + ':/'
    nas_common.create_nfs_export(access_zone_id, export_name_nfs, export_path)

    nfs_export_msg = nas_common.get_nfs_exports()
    nfs_export_msg = nfs_export_msg["result"]["exports"]
    nfs_export_id = ""
    for nfs_info in nfs_export_msg:
        if export_name_nfs in nfs_info["export_name"]:
            nfs_export_id = nfs_info["id"]
    if nfs_export_id == "":
        common.judge_rc(1, 0, "get nfs_export_id failed")
    nas_common.add_nfs_export_auth_clients(nfs_export_id, '*', 'rw')

    log.info("4-2> 创建smb共享,并添加用户用户组列表")
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
    ad_users_list = ad_users_list[6:]
    for i in range(len(ad_users_list)):
        nas_common.add_smb_export_auth_clients(
            smb_export_id,
            ad_users_list[i],
            'USER',
            'false',
            'full_control')

    log.info("5> 跨平台权限测试主体,posix/nfs部分")
    log.info("5-1> 挂载nfs客户端")
    rc = common.command(
        "ssh %s \"mount -t nfs %s:%s %s\"" %
        (nfs_ip, vip_domain_name, posix_mount_path, nfs_mount_path))
    common.judge_rc(rc, 0, "mount nfs client failed")

    log.info("5-2> posix/nfs客户端权限验证")
    is_init_ok = 1
    rc = common.command(
        "perl acl.pl %s %s %s %s %s %s %d" %
        (client_ip,
         nfs_ip,
         tools_location,
         posix_file_location,
         nfs_file_location,
         dac_set_path,
         is_init_ok))
    common.judge_rc(rc, 0, "posix/nfs acl test failed")

    log.info("6> 跨平台权限测试主体,smb部分")
    a = remote.Remote('%s:%s' % (smb_client_ip, smb_client_port))

    log.info("6-1> 挂载smb客户端")
    vip_addresses = get_config.get_vip_addresses()[2]
    vip_addresses_list = vip_addresses.split(',')
    log.info("vip_true_address_list is: %s" % str(vip_addresses_list))

    passwd = get_config.get_ad_user_pw_dac()[0]
    ad_domain_name = get_config.get_ad_domain_name_dac()[0]
    mount_path_list = []

    for num in range(len(vip_addresses_list)):
        mount_path_tmp = '\\\\' + \
            vip_addresses_list[num] + '\\' + export_name_smb
        mount_path_list.append(mount_path_tmp)
        user_tmp = ad_domain_name + '\\' + ad_users_list[num]
        rc = a.run_keyword('smb_mount',
                           [smb_disk_symbol_list[num],
                            mount_path_tmp,
                            passwd,
                            user_tmp])
        common.judge_rc(rc[0], 0, "mount smb failed")

    log.info("6-2> smb客户端权限验证")
    win_test_dir = multi_platform_dir
    rc = a.run_keyword('excute_perl_script',
                       [smb_scripts_location,
                        mount_path_list[0],
                           mount_path_list[1],
                           mount_path_list[2],
                           mount_path_list[3],
                           win_test_dir])
    common.judge_rc(rc[0], 0, "win perl excute failed")

    log.info("7> 权限验证成功，卸载nfs/smb客户端挂载目录，并删除授权")
    log.info("7-1> 卸载nfs客户端挂载目录")
    rc = common.command(
        "ssh %s \"umount -l %s\"" %
        (nfs_ip, nfs_mount_path))
    common.judge_rc(rc, 0, "umount nfs client failed")

    log.info("7-2> 删除nfs授权")
    nas_common.delete_nfs_exports(nfs_export_id)

    log.info("7-3> 卸载smb客户端挂载目录")
    for i in range(len(smb_disk_symbol_list)):
        (rc, output) = a.run_keyword('smb_umount', [smb_disk_symbol_list[i]])
        common.judge_rc(rc, 0, "umount smb client failed")

    log.info("7-4> 删除smb授权")
    nas_common.delete_smb_exports(smb_export_id)

    log.info("8> 全部测试成功，则删除测试目录中所有内容")
    rc = common.command(
        "ssh %s \"rm -fr %s\"" %
        (client_ip, posix_file_location))
    common.judge_rc(rc, 0, "rm testdir")

    return


def main():
    prepare_clean.test_prepare(FILE_NAME)
    case()
    prepare_clean.test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
