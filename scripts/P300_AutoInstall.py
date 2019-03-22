#!/usr/bin/python
# -*- coding:utf-8 -*-
#===================================
# latest update: 2019-01-20
# author: zff
#===================================

import os
import re
import sys
import time
import xml.etree.ElementTree as et

import utils_path
import log
import common
import get_config


class Parastor(object):
    def __init__(self):
        self.parastor_ip_lst = get_config.get_allparastor_ips()     # 集群节点ip
        client_ip_lst = get_config.get_allclient_ip()               # 私有客户端节点ip
        self.client_ip_lst = []
        for client_ip in client_ip_lst:
            if client_ip not in self.parastor_ip_lst:
                self.client_ip_lst.append(client_ip)
        self.pkg_path = get_config.get_client_install_path()        # 安装包目录

        """检查安装包和配置文件"""
        self.check_pkg_exist()
        self.check_config_file()

    def uninstall_system(self):
        """
        卸载环境
        """
        """卸载私有客户端"""
        self.uninstall_client()
        """卸载集群节点"""
        self.uninstall_parastor()

    def uninstall_parastor(self):
        """
        卸载集群
        """
        cmd = "/home/parastor/tools/deployment/uninstall --mode=AUTO_REBOOT"
        common.run_command(self.parastor_ip_lst[0], cmd, timeout=120)

        time.sleep(30)

        """不断检查节点是否可以ping通"""
        for node_ip in self.parastor_ip_lst:
            self.check_node_ping(node_ip)

        time.sleep(60)

    def uninstall_client(self):
        """
        卸载客户端
        """
        client_ip_lst = []
        """检查是否有客户端"""
        for client_ip in self.client_ip_lst:
            if common.check_file_exist(client_ip, '/cliparastor'):
                client_ip_lst.append(client_ip)

        """重启客户端"""
        cmd = "echo b > /proc/sysrq-trigger"
        for client_ip in client_ip_lst:
            common.run_command(client_ip, cmd, timeout=10)

        """不断检查节点是否可以ping通"""
        for client_ip in client_ip_lst:
            self.check_node_ping(client_ip)

        time.sleep(30)

        """卸载客户端"""
        cmd = "/cliparastor/uninstall.py"
        for client_ip in client_ip_lst:
            rc, stdout = common.run_command(client_ip, cmd)
            common.judge_rc(rc, 0, "node: %s, uninstall client failed!!!" % client_ip)

    def install_system(self, storpool_type='file'):
        """
        部署环境
        """
        self.install_parastor(storpool_type)
        self.install_client()

    def install_parastor(self, storpool_type):
        """
        部署集群
        """
        """安装集群"""
        node_ip = self.parastor_ip_lst[0]
        deploy_dir_path = os.path.join(self.pkg_path, self.sys_pkg_name).strip(".tar.xz")
        deploy_abs_path = os.path.join(deploy_dir_path, 'deploy')
        config_abs_path = os.path.join(self.pkg_path, 'deploy_config_p300.xml')
        cmd = 'ssh %s "python %s --deploy_config=%s"' % (node_ip, deploy_abs_path, config_abs_path)
        rc = common.command(cmd)
        common.judge_rc(rc, 0, "parastor install failed!!!")

        """配置节点池"""
        obj_node = common.Node()
        node_id_lst = obj_node.get_nodes_id()
        obj_node_pool = common.Nodepool()
        node_ids_str = ','.join([str(node_id) for node_id in node_id_lst])
        stripe_width = get_config.get_stripwidth()
        disk_parity_num = get_config.get_disk_parity_num()
        node_parity_num = get_config.get_node_parity_num()
        replica_num = get_config.get_replica()
        obj_node_pool.create_node_pool('node_pool_1', node_ids_str, stripe_width, disk_parity_num, node_parity_num,
                                       replica_num)
        """启动系统"""
        rc, stdout = common.startup()
        common.judge_rc(rc, 0, "startup failed!!! stdout: %s" % stdout)

        node_pool_id = obj_node_pool.get_node_pool_id_by_name('node_pool_1')

        """配置存储池"""
        '''
        all_disk_id_lst = []
        for node_id in node_id_lst:
            rc, stdout = common.get_disks(node_ids=node_id)
            common.judge_rc(rc, 0, "node_id: %s, get_disks failed!!!" % node_id)
            stdout = common.json_loads(stdout)
            disk_id_lst = []
            disk_info_lst = stdout['result']['disks']
            for disk_info in disk_info_lst:
                if disk_info['usage'] == 'DATA' and  disk_info['id'] != 0:
                    disk_id_lst.append(disk_info['id'])
            all_disk_id_lst.append(disk_id_lst)

        storage_pool_disk_id_str = ','.join([str(disk_id) for disk_id in all_disk_id_lst])
        '''
        if storpool_type == 'file':
            rc, stdout = common.create_storage_pool('file_stor', 'FILE', node_pool_ids=node_pool_id)
            common.judge_rc(rc, 0, "create_storage_pool file failed!!! stdout: %s" % stdout)
        else:
            rc, stdout = common.create_storage_pool('s3_stor', 'OBJECT', node_pool_ids=node_pool_id)
            common.judge_rc(rc, 0, "create_storage_pool s3 failed!!! stdout: %s" % stdout)

        """配置存储卷"""
        obj_storage_pool = common.Storagepool()
        rc, storage_pool_id = obj_storage_pool.get_storagepool_id('file_stor')
        common.judge_rc(rc, 0, "get_storagepool_id failed!!! stdout: %s" % storage_pool_id)

        volume_name_lst = get_config.get_volume_names()
        volume_id_lst = []
        obj_volume = common.Volume()
        for volume_name in volume_name_lst:
            rc, stdout = common.create_volume(volume_name, storage_pool_id, stripe_width, disk_parity_num,
                                              node_parity_num, replica_num)
            common.judge_rc(rc, 0, "create_volume %s failed, stdout: %s" % (volume_name, stdout))

            volume_id = obj_volume.get_volume_id(volume_name)
            volume_id_lst.append(volume_id)

        """创建授权"""
        volume_id_str = ','.join([str(volume_id) for volume_id in volume_id_lst])
        if self.client_ip_lst:
            client_ip_str = ','.join(self.client_ip_lst)
            rc, stdout = common.create_client_auth(client_ip_str, volume_id_str)
            common.judge_rc(rc, 0, "create_client_auth failed!!! stdout: %s" % stdout)

    def install_client(self):
        """
        安装客户端
        """
        client_deploy_abs_path = os.path.join(self.pkg_path, 'client', 'install.py')
        cmd_install_client = "python %s --ips=%s" % (client_deploy_abs_path, self.parastor_ip_lst[0])
        for client_ip in self.client_ip_lst:
            rc = 0
            stdout = ""
            for attempts in range(10):
                rc, stdout = common.run_command(client_ip, cmd_install_client)
                if 0 != rc:
                    """清空目的目录"""
                    common.rm_exe(client_ip, os.path.join(self.pkg_path, '*'))
                    common.mkdir_path(client_ip, self.pkg_path)

                    cmd = "scp -r %s root@%s:%s" % (self.client_pkg_abs_path, client_ip, self.pkg_path)
                    rc, stdout = common.run_command_shot_time(cmd)
                    common.judge_rc(rc, 0, "cmd: %s, stdout: %s" % (cmd, stdout))

                    time.sleep(10)
                    cmd = "echo 3 >/proc/sys/vm/drop_caches"
                    rc, stdout = common.run_command(client_ip, cmd, print_flag=True)
                    common.judge_rc(rc, 0, "cmd: %s, stdout: %s" % (cmd, stdout))
                    time.sleep(30)

                    client_path = os.path.join(self.pkg_path, 'client')
                    common.rm_exe(client_ip, client_path)

                    cmd = "tar -xf %s -C %s" % (os.path.join(self.pkg_path, self.client_pkg_name), self.pkg_path)
                    rc, stdout = common.run_command(client_ip, cmd, print_flag=True)
                    common.judge_rc(rc, 0, "cmd: %s, stdout: %s" % (cmd, stdout))

                    continue
                else:
                    break

            common.judge_rc(rc, 0, "node: %s, install client fialed!!! stdout: %s" % (client_ip, stdout))


        """不断检查卷是否挂载"""
        def _check_mount(volume_name_lst, client_ip_lst):
            cmd = "df"
            for client_ip in client_ip_lst:
                rc, stdout = common.run_command(client_ip, cmd, timeout=15)
                if rc != 0:
                    return False
                for volume_name in volume_name_lst:
                    if volume_name not in stdout:
                        return False
            return True

        volume_name_lst = get_config.get_volume_names()
        while True:
            time.sleep(5)
            if _check_mount(volume_name_lst, self.client_ip_lst):
                break

    def check_pkg_exist(self):
        """
        检查安装包
        """
        """检查本节点安装包"""
        scripts_path = os.path.dirname(os.path.abspath(__file__))
        stortest_path = os.path.dirname(scripts_path)
        dest_pkg_path = os.path.join(stortest_path, 'src_code', 'P300')

        pkg_lst = os.listdir(dest_pkg_path)
        pkg_base_name = ''
        pkg_time = ''
        for pkg_name in pkg_lst:
            if re.match('ParaStor-3\.0\.0-centos.*-.*feature_ofs3\.0_lastdebug.*_\w*_\d{8}_\d{6}.*\.tar', pkg_name):
                new_pkg_time = re.findall('\d{8}_\d{6}', pkg_name)[0]
                if not pkg_time or new_pkg_time > pkg_time:
                    pkg_base_name = pkg_name
        if not pkg_base_name:
            common.except_exit("%s do not have package" % dest_pkg_path)

        """解压缩安装包"""
        pkg_abs_path = os.path.join(dest_pkg_path, pkg_base_name)
        cmd = "tar -xf %s -C %s" % (pkg_abs_path, dest_pkg_path)
        rc, stdout = common.run_command_shot_time(cmd)
        if rc != 0:
            raise Exception('tar -xf failed')

        total_pkg_path = os.path.splitext(pkg_abs_path)[0]
        sys_pkg_path = ''
        client_pkg_path = ''
        for pkg in os.listdir(total_pkg_path):
            'parastor-3.0.0-centos7.5-feature_ofs3.0_lastdebug_ac1222f_20190119_192417-2-1.tar.xz'
            if re.match('parastor-3\.0\.0-centos.*-.*feature_ofs3\.0_lastdebug.*_\w*_\d{8}_\d{6}.*\.tar\.xz', pkg):
                sys_pkg_path = pkg
            elif re.match('parastor-3\.0\.0-client-centos.*-.*feature_ofs3\.0_lastdebug.*_\w*_\d{8}_\d{6}.*\.tar\.xz', pkg):
                client_pkg_path = pkg

        if not sys_pkg_path or not client_pkg_path:
            common.except_exit("pkg is not right")

        sys_pkg_abs_path = os.path.join(total_pkg_path, sys_pkg_path)
        client_pkg_abs_path = os.path.join(total_pkg_path, client_pkg_path)
        self.client_pkg_abs_path = client_pkg_abs_path  # add by zhanghan
        self.sys_pkg_name = sys_pkg_path
        self.client_pkg_name = client_pkg_path

        """拷贝系统包到第一个集群节点"""
        node_ip = self.parastor_ip_lst[0]
        """清空目的目录"""
        common.rm_exe(node_ip, os.path.join(self.pkg_path, '*'))
        common.mkdir_path(node_ip, self.pkg_path)

        cmd = "scp -r %s root@%s:%s" % (sys_pkg_abs_path, node_ip, self.pkg_path)
        rc, stdout = common.run_command_shot_time(cmd)
        common.judge_rc(rc, 0, "cmd: %s, stdout: %s" % (cmd, stdout))

        cmd = "tar -xf %s -C %s" % (os.path.join(self.pkg_path, self.sys_pkg_name), self.pkg_path)
        rc, stdout = common.run_command(node_ip, cmd, print_flag=False)
        common.judge_rc(rc, 0, "cmd: %s, stdout: %s" % (cmd, stdout))


        """拷贝客户端包到所有客户端节点"""
        for client_ip in self.client_ip_lst:
            """清空目的目录"""
            common.rm_exe(client_ip, os.path.join(self.pkg_path, '*'))
            common.mkdir_path(client_ip, self.pkg_path)

            cmd = "scp -r %s root@%s:%s" % (client_pkg_abs_path, client_ip, self.pkg_path)
            rc, stdout = common.run_command_shot_time(cmd)
            common.judge_rc(rc, 0 , "cmd: %s, stdout: %s" % (cmd, stdout))

            time.sleep(10)
            cmd = "echo 3 >/proc/sys/vm/drop_caches"
            rc, stdout = common.run_command(client_ip, cmd, print_flag=True)
            common.judge_rc(rc, 0, "cmd: %s, stdout: %s" % (cmd, stdout))
            time.sleep(30)

            client_path = os.path.join(self.pkg_path, 'client')
            common.rm_exe(client_ip, client_path)

            cmd = "tar -xf %s -C %s" % (os.path.join(self.pkg_path, self.client_pkg_name), self.pkg_path)
            rc, stdout = common.run_command(client_ip, cmd, print_flag=True)
            common.judge_rc(rc, 0, "cmd: %s, stdout: %s" % (cmd, stdout))

        time.sleep(10)


    def check_config_file(self):
        """
        检查配置文件
        """
        """检查配置文件"""
        scripts_path = os.path.dirname(os.path.abspath(__file__))
        stortest_path = os.path.dirname(scripts_path)
        config_abs_path = os.path.join(stortest_path, 'conf', 'deploy_config_p300.xml')
        if not os.path.exists(config_abs_path):
            common.except_exit("%s is not exist!!!" % config_abs_path)

        """修改配置文件"""
        tree = et.parse(config_abs_path)
        root = tree.getroot()

        root.find('package_path').text = os.path.join(self.pkg_path, self.sys_pkg_name)
        tree.write(config_abs_path)

        """拷贝到第一个集群节点"""
        node_ip = self.parastor_ip_lst[0]
        cmd = "scp -r %s root@%s:%s" % (config_abs_path, node_ip, self.pkg_path)
        rc, stdout = common.run_command_shot_time(cmd)
        common.judge_rc(rc, 0, "cmd: %s, stdout: %s, failed!!!" % (cmd, stdout))

    @staticmethod
    def check_node_ping(node_ip):
        """
        不断检查节点是否可以ping通
        """
        start_time = time.time()
        while True:
            time.sleep(10)
            if common.check_ping(node_ip):
                return
            exist_time = int(time.time() - start_time)
            m, s = divmod(exist_time, 60)
            h, m = divmod(m, 60)
            log.info('node: %s cannot ping pass %dh:%dm:%ds' % (node_ip, h, m, s))


if __name__ == '__main__':
    filename = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
    log_file_path = log.get_log_path(filename)
    log.init(log_file_path, True)
    obj_parastor = Parastor()
    obj_parastor.uninstall_system()
    if len(sys.argv) == 2 and sys.argv[-1] == 's3':
        obj_parastor.install_system('object')
    else:
        obj_parastor.install_system()