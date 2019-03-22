# -*-coding:utf-8 -*
#######################################################
# author 张呈宇
# date 2018-11-17
# @summary：
# x-x-x-x     创建1<节点数<N的访问分区
# @steps:
# 1.创建ad，ldap，ldap-pdc，nis认证
# 2.随机选取一种认证服务器、随机选取N（1<N≤集群内节点总数）个节点（集群中除去这N个节点，剩下的节点进入下一轮循环），
# 创建访问分区，启动NAS（NFS，FTP，SMB服务随机启动）
# 3.如果NAS服务中启动了NFS，通过NFS客户端挂载并创建文件，验证NFS的功能
# 4.循环步骤1-3，直到集群内节点都被创建了访问分区
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
        node = common.Node()
        ids = node.get_nodes_id()
        num = len(ids)
        h = 1
        while num > 0:
            access_zone_name = "access_zone_%s" % h
            auth_provider_id = random.choice(auth_provider_id_list)       # 随机选一种认证服务
            # auth_provider_id_a = random.sample(auth_provider_id_list, 1)
            # auth_provider_id_b = [str(p) for p in auth_provider_id_a]
            # auth_provider_id = ''.join(auth_provider_id_b)                # 随机选一种认证服务
            a = []
            if num < 2:
                node_id_num = 1
            else:
                for d in range(2, num+1):
                    a.append(d)
                node_id_num = random.choice(a)
                # node_id_num_a = random.sample(a, 1)
                # node_id_num_b = [str(p) for p in node_id_num_a]
                # node_id_num = ''.join(node_id_num_b)
            node_id_a = random.sample(ids, int(node_id_num))
            node_id = [str(p) for p in node_id_a]
            access_zone_node_ids = ','.join(node_id)                    # 随机选取节点
            for m in node_id_a:
                ids.remove(m)
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
            num = len(ids)
            h += 1
            if "NFS" in protocol_types:
                """3.创建NFS导出"""
                """创建目录"""
                log.info("\t[ 3 create_file ]")
                nfs_path = nas_common.ROOT_DIR + "nfs_dir_random_%s" % access_zone_id
                nas_nfs_path = get_config.get_one_nas_test_path() + "/nfs_dir_random_%s" % access_zone_id
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
                nfs_export_name = "nfs_export_%s" % access_zone_id
                description_nfs = "'old_export_description_@#$#%^*&!{}[]|'"
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
                cmd = "touch %s/test && echo 'test' > %s/test" % (nas_nfs_path, nas_nfs_path)
                rc, stdout = common.run_command(node_ip, cmd)
                if rc != 0:
                    common.except_exit('%s create_file failed!!!' % node_ip)

                """客户端mount共享路径"""
                log.info("\t[ 3 客户端mount共享路径 ]")
                """2-1> 客户端创建mount路径"""
                log.info("\t[ 3 客户端创建mount路径 ]")
                auth_clients_path = "/mnt/nfs_dir_client_random_%s" % access_zone_id
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
                node_id_b = random.sample(node_id_a, 1)
                node_id_c = [str(p) for p in node_id_b]
                node_id_c = ','.join(node_id_c)
                nodes = common.Node()
                node_ip_access = nodes.get_node_ip_by_id(node_id_c)
                begin_time = time.time()
                rc = 1
                while rc != 0:
                    cmd1 = "mount -t nfs %s:%s %s" % (node_ip_access, nas_nfs_path, auth_clients_path)
                    rc, stdout = common.run_command(auth_clients_name, cmd1)
                    print stdout
                    last_time = time.time()
                    during_time = last_time - begin_time
                    if int(during_time) >= 31:
                        common.except_exit('%s mount file failed and timeout 31s!!!' % auth_clients_name)
                    log.info('node_ip = %s, cmd = %s, check_result = %s' % (auth_clients_name, cmd1, stdout))
                    time.sleep(10)

                """3> 测试r"""
                log.info("\t[ 3 test-r ]")
                cmd1 = "ls %s" % auth_clients_path
                rc, stdout = common.run_command(auth_clients_name, cmd1)
                print stdout
                if rc != 0 or stdout == "":
                    common.except_exit('%s test-r failed!!!' % auth_clients_name)

                """4> 测试w"""
                log.info("\t[ 3 test-w ]")
                cmd2 = "touch %s/test2" % auth_clients_path
                rc, stdout = common.run_command(auth_clients_name, cmd2)
                if rc != 0:
                    common.except_exit('%s test-w failed!!!' % auth_clients_name)

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
                    common.except_exit('%s rm file failed!!!' % auth_clients_name)

        time.sleep(5)

        """检查NAS服务是否正常"""
        log.info("\t[3. 检查NAS服务是否正常]")
        nas_common.check_nas_status()

        """检查ctdb状态"""
        log.info("\t[3. 查看ctdb状态]")
        cmd = 'ctdb status'
        rc, stdout = common.run_command(node_ip, cmd)
        log.info(stdout)
        if stdout.find("UNHEALTHY") != -1 or stdout.find("DISCONNECTED") != -1 or stdout.find("INACTIVE") != -1:
            common.except_exit("ctdb状态不正常，请检查节点状态")

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