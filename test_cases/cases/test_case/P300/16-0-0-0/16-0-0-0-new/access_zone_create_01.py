# -*-coding:utf-8 -*
#######################################################
# author zhangchengyu
# date 2018-11-16
# @summary：
# x-x-x-x     所有节点创建一个访问分区
# @steps:
# 1.创建ad，ldap，ldap-pdc，nis认证
# 2.随机选取一种认证服务器创建访问分区，启动NAS（NFS，FTP，SMB服务随机启动）
# 3.如果NAS服务中启动了NFS，通过NFS客户端挂载并创建文件，验证NFS的功能
# @changelog：
#       date: 2018-12-10
#       author:zhangchengyu
#       description: 增加创建访问分区跑vdbench的背景
#######################################################
from multiprocessing import Process
import os
import time
import random

import utils_path
import common
import nas_common
import log
import get_config
import prepare_clean
import tool_use

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)  # /mnt/volume1/snap/snap_16_0_4_104
SYSTEM_IP = get_config.get_parastor_ip()
node_ip = SYSTEM_IP
NAS_PATH = get_config.get_one_nas_test_path() + "/nfs_dir_01"


def case1():
    run_times = 2    # 跑多少遍的控制
    for i in range(1, run_times + 1):
        log.info("\t[this is %s time]" % i)
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

        """b.创建ldap认证"""
        log.info("\t[1 add_auth_provider_ldap]")
        ldap_name = "ldap_auth_provider"
        msg2 = nas_common.add_auth_provider_ldap(name=ldap_name, base_dn=nas_common.LDAP_BASE_DN,
                                                 ip_addresses=nas_common.LDAP_IP_ADDRESSES, port=389)
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            common.except_exit("add_auth_provider_ldap failed")
        ldap_auth_provider_id = msg2["result"]
        auth_provider_id_list.append(ldap_auth_provider_id)

        """c.创建ldap_pdc认证"""
        log.info("\t[1 add_auth_provider_ldap_pdc]")
        ldap_name = "ldap_pdc_auth_provider"
        msg2 = nas_common.add_auth_provider_ldap(name=ldap_name, base_dn=nas_common.LDAP_2_BASE_DN,
                                                 ip_addresses=nas_common.LDAP_2_IP_ADDRESSES, port=389,
                                                 bind_dn=nas_common.LDAP_2_BIND_DN,
                                                 bind_password=nas_common.LDAP_2_BIND_PASSWORD,
                                                 domain_password=nas_common.LDAP_2_DOMAIN_PASSWORD)
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            common.except_exit("add_auth_provider_ldap_pdc failed")
        ldap_pdc_auth_provider_id = msg2["result"]
        auth_provider_id_list.append(ldap_pdc_auth_provider_id)

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

        """2.创建访问分区"""
        log.info("\t[2 create_access_zone ]")
        access_zone_name = "access_zone"
        auth_provider_id = random.choice(auth_provider_id_list)
        # auth_provider_id_a = random.sample(auth_provider_id_list, 1)
        # auth_provider_id_b = [str(p) for p in auth_provider_id_a]
        # auth_provider_id = ''.join(auth_provider_id_b)
        node = common.Node()
        ids = node.get_nodes_id()
        access_zone_node_ids = ','.join(str(p) for p in ids)
        msg1 = nas_common.create_access_zone(node_ids=access_zone_node_ids, name=access_zone_name,
                                             auth_provider_id=auth_provider_id)
        if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
            common.except_exit('create_access_zone failed!!!')
        access_zone_id = msg1["result"]

        log.info("\t[2 enable_nas ]")
        protocol_types_list = ["NFS", "SMB", "FTP"]
        protocol_types = ",".join(random.sample(protocol_types_list,
                                                random.choice(range(1, len(protocol_types_list) + 1))))
        # protocol_types_number_list = ["1", "2", "3"]
        # protocol_types_number_a = random.sample(protocol_types_number_list, 1)
        # protocol_types_number = int("".join(protocol_types_number_a))
        # protocol_types_a = random.sample(protocol_types_list, protocol_types_number)
        # protocol_types = ",".join(str(p) for p in protocol_types_a)
        msg2 = nas_common.enable_nas(access_zone_id=access_zone_id, protocol_types=protocol_types)
        if msg2["err_msg"] != "" or msg2["detail_err_msg"] != "":
            common.except_exit('enable_nas failed!!!')

        if "NFS" in protocol_types:
            """3.创建NFS导出"""
            """创建目录"""
            log.info("\t[ 3 create_file ]")
            nfs_path = nas_common.ROOT_DIR + "nfs_dir_01"
            msg6 = nas_common.create_file(path=nfs_path, posix_permission="rwxr-xr-x")
            if msg6["err_msg"] != "" or msg6["detail_err_msg"] != "":
                common.except_exit('create_file failed!!!')

            """ 检查file是否创建成功"""
            log.info("\t[3 get_file_list ]")
            msg7 = nas_common.get_file_list(path=nfs_path)
            if msg7["err_msg"] != "" or msg7["detail_err_msg"] != "":
                common.except_exit('get_file_list failed!!!')

            """创建导出路径"""
            log.info("\t[3 create_nfs_export ]")
            nfs_export_name = "nfs_export"
            description_nfs = 'old_export_description'
            msg1 = nas_common.create_nfs_export(access_zone_id=access_zone_id, export_name=nfs_export_name,
                                                export_path=nfs_path, description=description_nfs)
            if msg1["err_msg"] != "" or msg1["detail_err_msg"] != "":
                common.except_exit('create_nfs_export failed!!!')
            nfs_export_id = msg1["result"]

            """添加NFS客户端"""
            log.info("\t[3 add_nfs_export_auth_clients ]")
            auth_clients_name = nas_common.NFS_1_CLIENT_IP
            auth_clients_permission_level = 'rw'
            msg = nas_common.add_nfs_export_auth_clients(export_id=nfs_export_id, name=auth_clients_name,
                                                         permission_level=auth_clients_permission_level)
            if msg["err_msg"] != "" or msg["detail_err_msg"] != "":
                common.except_exit('add_nfs_export_auth_clients failed!!!')

            """创建一个文件，并写入内容"""
            log.info("\t[ 3 create_file ]")
            cmd = "touch %s/test && echo 'test' > %s/test" % (NAS_PATH, NAS_PATH)
            rc, stdout = common.run_command(node_ip, cmd)
            if rc != 0:
                common.except_exit('%s create_file failed!!!' % node_ip)

            """客户端mount共享路径"""
            log.info("\t[ 3 客户端mount共享路径 ]")
            """2-1> 客户端创建mount路径"""
            log.info("\t[ 3 客户端创建mount路径 ]")
            auth_clients_path = "/mnt/nfs_dir_client"
            cmd = "ls %s" % auth_clients_path
            rc, stdout = common.run_command(auth_clients_name, cmd)
            if stdout == "":
                cmd = "umount -l %s" % auth_clients_path
                common.run_command(auth_clients_name, cmd)
                cmd = "rm -rf %s" % auth_clients_path
                rc, stdout = common.run_command(auth_clients_name, cmd)
                if rc != 0:
                    common.except_exit('%s rm -rf client file failed!!!' % auth_clients_name)
            cmd = "mkdir %s" % auth_clients_path
            rc, stdout = common.run_command(auth_clients_name, cmd)
            if rc != 0:
                common.except_exit('%s create_file failed!!!' % auth_clients_name)

            """2-2> 客户端mount共享路径"""
            log.info("\t[ 3 客户端mount共享路径 ]")
            begin_time = time.time()
            rc = 1
            while rc != 0:
                cmd1 = "mount -t nfs %s:%s %s" % (node_ip, NAS_PATH, auth_clients_path)
                rc, stdout = common.run_command(auth_clients_name, cmd1)
                print stdout
                last_time = time.time()
                during_time = last_time - begin_time
                if int(during_time) >= 15:
                    common.except_exit('%s mount file failed and timeout 15s!!!' % auth_clients_name)
                log.info('node_ip = %s, cmd = %s, check_result = %s' % (auth_clients_name, cmd1, stdout))
                time.sleep(5)

            """3> 测试r"""
            log.info("\t[ 3 test-r ]")
            cmd1 = "ls %s" % auth_clients_path
            rc, stdout = common.run_command(auth_clients_name, cmd1)
            print stdout
            if rc != 0 or stdout == "":
                common.except_exit('%s test-r failed!!!' % node_ip)

            """4> 测试w"""
            log.info("\t[ 3 test-w ]")
            cmd2 = "touch %s/test2" % auth_clients_path
            rc, stdout = common.run_command(auth_clients_name, cmd2)
            if rc != 0:
                common.except_exit('%s test-w failed!!!' % node_ip)

            """5> 删除test-w的文件"""
            log.info("\t[ 3 删除test-w的文件 ]")
            cmd1 = "rm -rf %s/test2" % auth_clients_path
            rc, stdout = common.run_command(auth_clients_name, cmd1)
            print stdout
            if rc != 0:
                common.except_exit('%s rm file failed!!!' % auth_clients_name)

            """6> 客户端umount共享路径"""
            log.info("\t[ 3 客户端umount共享路径 ]")
            cmd1 = "umount -fl %s" % auth_clients_path
            rc, stdout = common.run_command(auth_clients_name, cmd1)
            print stdout
            if rc != 0:
                common.except_exit('%s umount file failed!!!' % auth_clients_name)

            """7> 客户端删除mount路径"""
            log.info("\t[ 3 客户端删除mount路径 ]")
            cmd1 = "rm -rf %s " % auth_clients_path
            rc, stdout = common.run_command(auth_clients_name, cmd1)
            print stdout
            if rc != 0:
                common.except_exit('%s rm file failed!!!' % node_ip)

        time.sleep(5)

        """检查NAS服务是否正常"""
        log.info("\t[4. 检查NAS服务是否正常]")
        nas_common.check_nas_status()

        """检查ctdb状态"""
        log.info("\t[4. 查看ctdb状态]")
        cmd = 'ctdb status'
        rc, stdout = common.run_command(node_ip, cmd)
        log.info(stdout)
        if stdout.find("UNHEALTHY") != -1 or stdout.find("DISCONNECTED") != -1 or stdout.find("INACTIVE") != -1:
            common.except_exit("ctdb状态不正常，请检查节点状态")

    return


# 运行vdbench，先创建，再读写
def vdbench_run(anchor_path, journal_path, *args):
    vdb = tool_use.Vdbenchrun(elapsed=3000000)

    vdb.run_create(anchor_path, journal_path, *args)

    vdb.run_check_write(anchor_path, journal_path, *args)

    return


def executing_case1():
    vdbench_path = nas_common.BASE_NAS_PATH
    log.info("vdbench_path=%s" % vdbench_path)
    p1 = Process(target=vdbench_run, args=(vdbench_path, '/tmp', nas_common.CLIENT_IP_1))
    p2 = Process(target=case1)

    p1.start()
    p2.start()

    p2.join()
    p1.terminate()
    p1.join()
    return


#######################################################
# 函数功能：本用例入口函数
# 函数入参：无
# 函数返回值：无
#######################################################
def nas_main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    executing_case1()
    if nas_common.DEBUG != 'on':
        prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)