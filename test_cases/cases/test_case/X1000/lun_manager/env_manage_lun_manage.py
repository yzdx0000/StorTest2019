# -*- encoding=utf8 -*-
# @Time: 2018/7/3 13:53
# @Author: wangxiang

"""
Xstor的安装和各种清理工作
"""

import os, sys
import random
import time
import threading
import commands
import re
import xml
import utils_path
import Lun_managerTest
import common
import common2
import log
import breakdown
import ReliableTest
import error
import get_config
from get_config import config_parser as cp
import decorator_func


def setup():
    file_name = os.path.basename(__file__)
    file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
    log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
    log.init(log_file_path, True)  # 初始化日志文件
    log.info("'\033[44m##################该部署脚本用于部署执行卷管理用例的测试环境################ ...\033[0m'")


conf_file = get_config.CONFIG_FILE
# 配置文件路径
deploy_ips = get_config.get_env_ip_info(conf_file)  # 获取集群IP列表
log.info(deploy_ips)
node_ip = deploy_ips[0]
node_ip1 = deploy_ips[0]  # 集群节点1
node_ip2 = deploy_ips[1]
node_ip3 = deploy_ips[2]
client_ips = get_config.get_allclient_ip()  # 获取客户端IP
log.info(client_ips)
client_ip1 = client_ips[0]
client_ip2 = client_ips[1]

co2_osan = common2.oSan()
osan = Lun_managerTest.oSan()
Reliable_osan = breakdown.Os_Reliable()
break_down = breakdown.disk()
com_disk = common.Disk()
com_node = common.Node()
assert_ins = decorator_func.assert_cls()
Esxi_ips = cp('esxi', 'Esxi_ips')

father_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print father_path


def xstor_install():
    decorator_func.timer(15)
    config_info = xml.dom.minidom.parse(conf_file)
    replica = config_info.getElementsByTagName('replica')[0].firstChild.nodeValue
    strip_width = config_info.getElementsByTagName('stripwidth')[0].firstChild.nodeValue
    node_parity = int(replica) - 1
    # 1.检查节点上的存储软件包和配置文件是否存在
    new_pkg = ''
    cmd = ('ssh %s "ls /home/deploy/"' % deploy_ips[0])
    rc, result = commands.getstatusoutput(cmd)
    if 0 != rc:
        log.error("the directory deploy is not exists.")
        os._exit(1)
    else:
        if 'deploy_config.xml' in result:
            log.info("the x1000 install config is exists.")
        else:
            log.error("the x1000 install config is not exists.")
            os._exit(1)
        if 'parastor-3.0.0-centos' in result:
            log.info("the x1000 software package is exists.")
            cmd = ('ssh %s "ls -t /home/deploy/" | grep "parastor" | head -n 1' % deploy_ips[0])
            rc, stdout = commands.getstatusoutput(cmd)
            new_pkg = stdout
        else:
            log.info("the x1000 software package is not exists.")
            os._exit(1)
    # 2.开始卸载旧系统
    for ip in client_ips:
        cmd1 = ("ssh root@%s 'iscsiadm -m node -u'" % ip)
        cmd2 = ("ssh root@%s 'iscsiadm -m node -o delete'" % ip)
        os.system(cmd1)
        os.system(cmd2)
    log.info("Logout all luns on clients: Success.")
    cmd = ("ssh root@%s \"sed -r -i 's/\/home\/deploy\/.*<\/package_path>/"
           "\/home\/deploy\/%s<\/package_path>/g' /home/deploy/deploy_config.xml\"" % (deploy_ips[0], new_pkg))
    os.system(cmd)
    log.info("Unpack the new package on %s:/home/deploy" % (deploy_ips[0]))
    new_pkg_name = new_pkg.split('.tar')[0]
    cmd = ("ssh %s 'ls /home/deploy'" % deploy_ips[0])
    rc, stdout = commands.getstatusoutput(cmd)
    dir_list = stdout.split('\n')
    deploy_conf_file = '/home/deploy/deploy_config.xml'
    tar_tag = 1
    for file in dir_list:
        if file == new_pkg_name:
            tar_tag = 0
            break
    if tar_tag == 1:
        cmd = ("ssh root@%s 'cd /home/deploy;tar -xvf %s'" % (deploy_ips[0], new_pkg))
        os.system(cmd)
    log.info("Begin to clean the cluster.")
    clean_cmd = ('ssh %s "/home/deploy/%s/server/tools/deployment/clean.py --deploy_config=%s > /dev/null"'
                 % (deploy_ips[0], new_pkg_name, deploy_conf_file))
    rc = os.system(clean_cmd)
    if 0 == rc:
        log.info("uninstall x1000 successful!")
    for ip in deploy_ips:
        cmd = ("ssh root@%s 'lsmod | grep -w tgt'" % (ip,))
        res, output = commands.getstatusoutput(cmd)
        if res == 0:
            log.error("Sorry, I detect that there is tgt module on %s" % ip)
            for ip in deploy_ips:
                cmd = ("ssh %s 'reboot'" % ip)
                log.info("Begin to shutdown %s." % ip)
                os.system(cmd)
            time.sleep(100)
            for ip in deploy_ips:
                while False is ReliableTest.check_ping(ip):
                    time.sleep(5)
            rc = os.system(clean_cmd)
            if 0 == rc:
                log.info("uninstall x1000 successful!")

    # 3.开始部署新系统
    log.info("Install script check the install environment.")
    cmd = ("ssh root@%s '/home/deploy/%s/server/tools/env_check/env_check.py "
           "--ip=%s --config=%s'" % (deploy_ips[0], new_pkg_name, deploy_ips[0], deploy_conf_file))
    os.system(cmd)
    cmd = ("ssh root@%s '/home/deploy/%s/server/tools/deployment/deploy.py --deploy_config=%s --type=BLOCK'"
           % (deploy_ips[0], new_pkg_name, deploy_conf_file))
    rc = os.system(cmd)
    if 0 == rc:
        log.info("install x1000 system successful!")
    else:
        log.error("install x1000 failed!!!")
    cmd = ("ssh root@%s '/home/parastor/cli/pscli --command=update_param --section=MGR "
           "--name=min_meta_replica --current=%s' > /dev/null" % (deploy_ips[0], str(replica)))
    os.system(cmd)

    # 创建节点池
    log.info("step1: create node pool")
    count = 0
    node_ids = []
    for x in deploy_ips:
        count += 1
        node_ids.append(count)
    node_ids = ','.join(map(str, node_ids))
    cmd = ("ssh %s '/home/parastor/cli/pscli --command=create_node_pool --node_ids=%s --replica_num=%s "
           "--stripe_width=%s --disk_parity_num=0 --node_parity_num=%s --name=node_pool1'"
           % (deploy_ips[0], node_ids, str(replica), str(strip_width), str(node_parity)))
    rc, stdout = commands.getstatusoutput(cmd)
    if 0 != rc:
        log.error("create node pool failed! info:%s" % stdout)
        os._exit(1)
    else:
        log.info("create node pool successful.")

    # 启动xstor系统
    log.info("step2: startup xstor system")
    cmd = ("ssh root@%s '/home/parastor/cli/pscli --command=startup'" % (deploy_ips[0]))
    rc, stdout = commands.getstatusoutput(cmd)
    if 0 != rc:
        log.error("startup xstor system failed! info:%s" % stdout)
        os._exit(1)
    else:
        log.info("startup xstor system successful!")

    # 创建存储池
    log.info("step3: create storage pool")
    co2_osan.create_storage_pool(deploy_ips[0], 'storge_pool1', 1)

    # 创建访问区
    log.info("step4: create oSan access_zone")
    co2_osan.create_access_zone(deploy_ips[0], node_ids, 'access_zone1')

    svip = get_config.get_svip(conf_file)
    # 创建业务子网
    log.info("step5: create oSan subnet")
    co2_osan.create_subnet(deploy_ips[0], svip[0])


def create_iscsi_login(ips=deploy_ips[0], cli_ips=client_ips[0]):
    svip = co2_osan.get_svip(ips)
    osan.discover_scsi_list(client_ip=cli_ips, svip=svip[0])  # 进行一下discovery，真正的tag从xstor中拿
    target_list = osan.get_map_target(ips)
    log.info("Get Info:\nSvip list:%s \nTarget list:%s" % (svip, target_list))
    for tag in target_list:
        log.info("主机发现存储target：%s,主机 %s 将进行SCSI登录" % (tag, cli_ips))
        osan.iscsi_login(client_ip=cli_ips, iqn=tag)


def clean_lun_map():
    iscsi_logout()  # 删除lun_map前先在所有主机端logout
    lun_map_ids = osan.get_lun_maps(node_ip)
    log.info(lun_map_ids)
    threads = []
    for i in lun_map_ids:
        threads.append(threading.Thread(target=osan.delete_lun_map, args=(node_ip1, i)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def clean_node_pools():
    node_pool_ids = osan.get_option(s_ip=node_ip, command="get_node_pools", indexname="node_pools", argv="id")
    log.info(node_pool_ids)
    if len(node_pool_ids) >= 2:
        node_pool_ids.remove(1)  # 列表删除共享节点池
        log.info(node_pool_ids)
        for node_pool_id in node_pool_ids:
            osan.shutdown(node_ip1)
            osan.delete_node_pools(s_ip=node_ip, node_pool_id=node_pool_id)


def clean_lun():
    lun_ids = osan.get_lun(s_ip=node_ip1)
    log.info(lun_ids)
    threads = []
    for i in lun_ids:
        threads.append(threading.Thread(target=osan.delete_lun, args=(node_ip1, i)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    while True:
        lun_ids = osan.get_lun(s_ip=node_ip1)

        if len(lun_ids) == 0:
            break
        log.info("Wait execute finish ...")
        time.sleep(20)

    osan.reserve_wait()


def clean_initiator():
    ini_ids = osan.get_initiators(s_ip=node_ip)
    log.info(ini_ids)
    threads = []
    for i in ini_ids:
        threads.append(threading.Thread(target=osan.remove_initiator, args=(node_ip1, i)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    while True:
        ini_ids = osan.get_initiators(s_ip=node_ip)

        if len(ini_ids) == 0:
            break
        log.info("Wait execute finish ...")
        time.sleep(20)


def lun_map_by_target():
    clean(target="lun_map")
    node_ids_list = osan.get_nodes(node_ip1)
    node_ids = ",".join('%s' % id for id in node_ids_list)

    exe_id = Reliable_osan.get_node_id_by_ip(node_ip2)

    targets = osan.gen_dict_mul(s_ip=node_ip2, command="get_targets", arg1="nodeId",
                                arg2="id",
                                arg3="targets", target=exe_id)

    node_id1 = Reliable_osan.get_node_id_by_ip(node_ip1)
    luns1 = osan.get_luns_by_node_id(node_id=node_id1)

    node_id2 = Reliable_osan.get_node_id_by_ip(node_ip2)
    luns2 = osan.get_luns_by_node_id(node_id=node_id2)
    hostgroup_ids = osan.get_host_groups(s_ip=node_ip1)
    ##节点1上面的lun只map一半到节点2的target上，剩下的留在节点1做默认的lun_map
    lun_index1 = int(len(luns1)) / 2
    lun_index2 = len(luns1)
    for lun in luns1[:lun_index1]:
        osan.lun_map_by_target(node_ip1, lun_ids=lun, target_id=random.choice(targets),
                               hp_id=hostgroup_ids[0])
    for lun in luns1[lun_index1:lun_index2]:
        osan.map_lun(s_ip=node_ip1, lun_ids=lun, hg_id=hostgroup_ids[0])

    for lun in luns2:
        osan.map_lun(s_ip=node_ip1, lun_ids=lun, hg_id=hostgroup_ids[1])


def clean_host():
    host_ids = osan.get_hosts(s_ip=node_ip)
    log.info(host_ids)
    threads = []
    for i in host_ids:
        threads.append(threading.Thread(target=osan.remove_hosts, args=(node_ip1, i)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    while True:
        host_ids = osan.get_hosts(s_ip=node_ip)

        if len(host_ids) == 0:
            break
        log.info("Wait execute finish ...")
        time.sleep(20)


def clean_hostgroup():
    hostgroup_ids = osan.get_host_groups(s_ip=node_ip)
    log.info(hostgroup_ids)
    threads = []
    for i in hostgroup_ids:
        threads.append(threading.Thread(target=osan.delete_host_groups, args=(node_ip1, i)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    while True:
        hostgroup_ids = osan.get_host_groups(s_ip=node_ip)
        if len(hostgroup_ids) == 0:
            break
        log.info("Wait execute finish ...")
        time.sleep(20)


def clean_vip_address_pool():
    # azs = osan.get_access_zone_id(s_ip=node_ip)
    # log.info(azs)
    # for az in azs:
    #     osan.disable_san(s_ip=node_ip1, access_zone_id=az)
    vip_pool_ids = osan.get_option(s_ip=node_ip, command="get_vip_address_pools", indexname="ip_address_pools",
                                   argv="id")
    for vip_pool_id in vip_pool_ids:
        osan.delete_vip_address_pool(s_ip=node_ip, id=vip_pool_id)


def clean_subnet():
    # azs = osan.get_access_zone_id(s_ip=node_ip)
    # log.info(azs)
    # for az in azs:
    #     osan.disable_san(s_ip=node_ip1, access_zone_id=az)
    subnet_ids = osan.get_subnet_id(s_ip=node_ip)
    log.info(subnet_ids)
    for subnet_id in subnet_ids:
        osan.delete_subnet(s_ip=node_ip, id=subnet_id)


def clean_access_zone(azs=None):
    azs = osan.get_access_zone_id(s_ip=node_ip)
    log.info(azs)
    for az in azs:
        osan.disable_san(s_ip=node_ip1, access_zone_id=az)
        osan.delete_access_zone(s_ip=node_ip, azid=az)


def clean_storage_pool():
    sto_pool_ids = osan.get_storage_id(s_ip=node_ip)
    if len(sto_pool_ids) >= 2:
        sto_pool_ids.remove(1)  # 列表删除共享池
        log.info(sto_pool_ids)
        for sto_pool_id in sto_pool_ids:
            osan.delete_storage_pool(s_ip=node_ip, id=sto_pool_id)


def iscsi_logout():
    for cli in client_ips:
        osan.iscsi_logout_all(cli)


def rel_check_before_run(filename):
    """执行用例前环境检测"""
    error.rel_check_before_run(file_name=filename, jnl_rep=int(cp("env", "jnl_rep")),
                               node_num=int(cp("env", "node_num")))


def init_env(target="enable_san", change_disk_speed=0, reboot_node=1, start_up=1, enable_san=1, osan_space_check=0,
             is_display_raw_capacity=1, set_rcvr=1, storage_pool_num=1, deploy_vip=1, deploy_svip=1):
    """
    初始化测试环境
    :param target: 指定创建到哪一步，默认创建到vip池
    :param change_disk_speed: 是否更改磁盘速率，0为不更改
    :param reboot_node:  是否安装xstor前重启节点，0为不重启
    :param start_up:  是否启动xstor系统，0为不启动，
    :param enable_san:是否激活san，0为不激活
    :param osan_space_check:  空间管理特性，0为打开,1为关闭
    :param is_display_raw_capacity:  显示存储池原始空间，1为显示，0为不显示
    :param set_rcvr :修复开关 ,1为关闭
    :param deploy_vip :是否取配置文件的vip；1为取；0为不取
    :return:
    """
    if target == "init":
        decorator_func.timer(15)
        if reboot_node:
            for ip in deploy_ips:
                cmd = ("ssh root@%s 'reboot'" % (ip))
                log.info(cmd)
                res, output = commands.getstatusoutput(cmd)
        for ip in deploy_ips:
            Reliable_osan.get_os_status_1(ip)
        osan.uninstall_Xstor(node_ip1)
        tgt_res = 0
        for ip in deploy_ips:
            cmd = ("ssh root@%s 'lsmod |grep -w tgt'" % (ip,))
            res, output = commands.getstatusoutput(cmd)
            if res == 0:
                log.error("Sorry, I detect that there is tgt module on %s" % (ip,))
                tgt_res = 1
            if tgt_res == 1:
                log.error("Begin to restart these nodes.")
                cmd = ("ssh root@%s 'reboot'" % (ip))
                log.info(cmd)
                res, output = commands.getstatusoutput(cmd)
                Reliable_osan.get_os_status_1(ip)
                osan.uninstall_Xstor(node_ip1)
        osan.install_Xstor(node_ip1)

    if target == "enable_san":
        decorator_func.timer(15)
        if reboot_node:
            for ip in deploy_ips:
                cmd = ("ssh root@%s 'reboot'" % (ip))
                log.info(cmd)
                res, output = commands.getstatusoutput(cmd)
        for ip in deploy_ips:
            Reliable_osan.get_os_status_1(ip)
        osan.uninstall_Xstor(node_ip1)
        tgt_res = 0
        for ip in deploy_ips:
            cmd = ("ssh root@%s 'lsmod |grep -w tgt'" % (ip,))
            res, output = commands.getstatusoutput(cmd)
            if res == 0:
                log.error("Sorry, I detect that there is tgt module on %s" % (ip,))
                tgt_res = 1
            if tgt_res == 1:
                log.error("Begin to restart these nodes.")
                cmd = ("ssh root@%s 'reboot'" % (ip))
                log.info(cmd)
                res, output = commands.getstatusoutput(cmd)
                Reliable_osan.get_os_status_1(ip)
                osan.uninstall_Xstor(node_ip1)
        osan.install_Xstor(node_ip1)
        # break_down.set_rcvr(set_rcvr)  # 关闭修复
        # break_down.seprate_ojmgs_orole()
        node_ids_list = osan.get_nodes(deploy_ips[0])
        node_ids = ",".join('%s' % id for id in node_ids_list)

        share_disk_ids_list = break_down.get_all_shared_disk_id()
        data_disk_ids_list = break_down.get_all_data_disk_id()
        share_disk_ids = re.sub('\[|\]| ', '', str(break_down.get_all_shared_disk_id()))
        data_disk_ids = re.sub('\[|\]| ', '', str(break_down.get_all_data_disk_id()))
        date_disk_ids_list = break_down.get_all_data_disk_id()
        log.info(data_disk_ids_list)
        log.info("数据盘数量 :{}".format(len(data_disk_ids_list)))
        if len(data_disk_ids_list) < 9:
            log.error("数据盘数量不够，3节点3副本创建3个存储池 至少需要9块盘(每节点至少3块)!")
            exit(1)
        if change_disk_speed:
            log.debug("更改共享盘速率为High、数据盘速率为MID")
            cmd = (
                    "ssh root@%s '/home/parastor/cli/pscli --command=change_disk_speed_level --disk_ids=%s --speed_level=HIGH'"
                    % (deploy_ips[0], share_disk_ids))
            commands.getstatusoutput(cmd)
            cmd = (
                    "ssh root@%s '/home/parastor/cli/pscli --command=change_disk_speed_level --disk_ids=%s --speed_level=MID'"
                    % (deploy_ips[0], data_disk_ids))
            commands.getstatusoutput(cmd)
        node_pool_id = osan.create_node_pool(s_ip=node_ip, node_ids=node_ids,
                                             replica_num=cp("create_node_pool", "replica_num"),
                                             stripe_width=cp('create_node_pool', 'stripe_width'),
                                             disk_parity_num=cp("create_node_pool", "disk_parity_num"),
                                             node_parity_num=cp("create_node_pool", "node_parity_num"),
                                             name="nodepool1")
        if start_up:
            osan.startup(s_ip=node_ip)
        data_unuse_disks = []
        for i in node_ids_list:
            j = break_down.get_assign_data_disk_id(s_ip=deploy_ips[0], node_id=i)
            data_unuse_disks.append(j)
        lists = [[] for a in range(3)]
        for m in range(3):
            new_list = []
            for h in data_unuse_disks:
                new_list.append(h[m])
            lists[m].append(new_list)

        log.info("集群中的所有未使用数据盘:{}".format(lists))
        if storage_pool_num == 3:
            for i in range(3):
                log.info("will create storage :%s" % i)
                pool_id = ",".join('%s' % id for id in lists[i][0])
                cmd = (
                        "ssh root@%s '/home/parastor/cli/pscli --command=create_storage_pool --name=stor%s --type=BLOCK --node_pool_ids=1 --disk_ids=%s '" % (
                    deploy_ips[0], i, pool_id))
                log.info(cmd)
                commands.getstatusoutput(cmd)
        elif storage_pool_num == 1:
            stor_id1 = osan.create_storage_pool(s_ip=node_ip1, node_pool_ids=node_pool_id, name='pool1')

        osan.update_param(s_ip=node_ip, section='MGR', name='mgcd_auto_mount_flag', current='0')  # 解除自动挂载
        az_id = osan.create_access_zone(s_ip=node_ip, node_id=node_ids, name='accesszone1')
        sub_id = osan.create_subnet(s_ip=node_ip, access_zone_id=az_id, name='subnet1',
                                    sv_ip=cp("create_subnet", "sv_ip"),
                                    mask=cp("create_subnet", "mask"), vv_ip=cp("create_subnet", "vv_ip"),
                                    gate_way=cp("create_subnet", "gate_way"),
                                    network_interface=cp("create_subnet", "network_interface"), deploy=deploy_svip)
        vip_id = osan.add_vip_address_pool(s_ip=node_ip, subnet_id=sub_id,
                                           domain_name=cp("add_vip_address_pool", "domain_name"),
                                           vip=cp("add_vip_address_pool", "vips"), deploy=deploy_vip)
        if enable_san:
            osan.enable_san(s_ip=node_ip, access_zone_id=az_id)

        osan.xstor_pre_config(s_ip=node_ip1, osan_space_check=osan_space_check,
                              is_display_raw_capacity=is_display_raw_capacity)

        # log.info("##### Step19:Check all vips for balance . #####")
        # rc = co2_osan.check_vip_balance()
        # if rc == False:
        #     log.info("vips is not balanced in nodes.Please check.")
        #     os._exit(1)

    elif target == "create_node_pool":
        decorator_func.timer(15)
        if reboot_node:
            for ip in deploy_ips:
                cmd = ("ssh root@%s 'reboot'" % (ip))
                log.info(cmd)
                res, output = commands.getstatusoutput(cmd)
            for ip in deploy_ips:
                Reliable_osan.get_os_status_1(ip)
        osan.uninstall_Xstor(node_ip1)
        tgt_res = 0
        for ip in deploy_ips:
            cmd = ("ssh root@%s 'lsmod |grep -w tgt'" % (ip,))
            res, output = commands.getstatusoutput(cmd)
            if res == 0:
                log.error("Sorry, I detect that there is tgt module on %s" % (ip,))
                tgt_res = 1
            if tgt_res == 1:
                log.error("Begin to restart these nodes.")
                cmd = ("ssh root@%s 'reboot'" % (ip))
                log.info(cmd)
                res, output = commands.getstatusoutput(cmd)
                Reliable_osan.get_os_status_1(ip)
                osan.uninstall_Xstor(node_ip1)
        osan.install_Xstor(node_ip1)
        node_ids_list = osan.get_nodes(deploy_ips[0])
        node_ids = ",".join('%s' % id for id in node_ids_list)

        share_disk_ids_list = break_down.get_all_shared_disk_id()
        data_disk_ids_list = break_down.get_all_data_disk_id()
        share_disk_ids = re.sub('\[|\]| ', '', str(break_down.get_all_shared_disk_id()))
        data_disk_ids = re.sub('\[|\]| ', '', str(break_down.get_all_data_disk_id()))
        if change_disk_speed:
            log.debug("更改共享盘速率为High、数据盘速率为MID")
            cmd = (
                    "ssh root@%s '/home/parastor/cli/pscli --command=change_disk_speed_level --disk_ids=%s --speed_level=HIGH'"
                    % (deploy_ips[0], share_disk_ids))
            commands.getstatusoutput(cmd)
            cmd = (
                    "ssh root@%s '/home/parastor/cli/pscli --command=change_disk_speed_level --disk_ids=%s --speed_level=MID'"
                    % (deploy_ips[0], data_disk_ids))
            commands.getstatusoutput(cmd)
        node_pool_id = osan.create_node_pool(s_ip=node_ip, node_ids=node_ids,
                                             replica_num=cp("create_node_pool", "replica_num"),
                                             stripe_width=cp('create_node_pool', 'stripe_width'),
                                             disk_parity_num=cp("create_node_pool", "disk_parity_num"),
                                             node_parity_num=cp("create_node_pool", "node_parity_num"),
                                             name="nodepool1")
        if start_up:
            osan.startup(s_ip=node_ip)

    elif target == "create_storage_pool":
        decorator_func.timer(15)
        if reboot_node:
            for ip in deploy_ips:
                cmd = ("ssh root@%s 'reboot'" % (ip))
                log.info(cmd)
                res, output = commands.getstatusoutput(cmd)
            for ip in deploy_ips:
                Reliable_osan.get_os_status_1(ip)
        osan.uninstall_Xstor(node_ip1)
        tgt_res = 0
        for ip in deploy_ips:
            cmd = ("ssh root@%s 'lsmod |grep -w tgt'" % (ip,))
            res, output = commands.getstatusoutput(cmd)
            if res == 0:
                log.error("Sorry, I detect that there is tgt module on %s" % (ip,))
                tgt_res = 1
            if tgt_res == 1:
                log.error("Begin to restart these nodes.")
                cmd = ("ssh root@%s 'reboot'" % (ip))
                log.info(cmd)
                res, output = commands.getstatusoutput(cmd)
                Reliable_osan.get_os_status_1(ip)
                osan.uninstall_Xstor(node_ip1)
        osan.install_Xstor(node_ip1)
        node_ids_list = osan.get_nodes(deploy_ips[0])
        node_ids = ",".join('%s' % id for id in node_ids_list)

        share_disk_ids_list = break_down.get_all_shared_disk_id()
        data_disk_ids_list = break_down.get_all_data_disk_id()
        share_disk_ids = re.sub('\[|\]| ', '', str(break_down.get_all_shared_disk_id()))
        data_disk_ids = re.sub('\[|\]| ', '', str(break_down.get_all_data_disk_id()))
        if change_disk_speed:
            log.debug("更改共享盘速率为High、数据盘速率为MID")
            cmd = (
                    "ssh root@%s '/home/parastor/cli/pscli --command=change_disk_speed_level --disk_ids=%s --speed_level=HIGH'"
                    % (deploy_ips[0], share_disk_ids))
            commands.getstatusoutput(cmd)
            cmd = (
                    "ssh root@%s '/home/parastor/cli/pscli --command=change_disk_speed_level --disk_ids=%s --speed_level=MID'"
                    % (deploy_ips[0], data_disk_ids))
            commands.getstatusoutput(cmd)
        node_pool_id = osan.create_node_pool(s_ip=node_ip, node_ids=node_ids,
                                             replica_num=cp("create_node_pool", "replica_num"),
                                             stripe_width=cp('create_node_pool', 'stripe_width'),
                                             disk_parity_num=cp("create_node_pool", "disk_parity_num"),
                                             node_parity_num=cp("create_node_pool", "node_parity_num"),
                                             name="nodepool1")
        if start_up:
            osan.startup(s_ip=node_ip)
        data_unuse_disks = []
        for i in node_ids_list:
            j = break_down.get_assign_data_disk_id(s_ip=deploy_ips[0], node_id=i)
            data_unuse_disks.append(j)
        lists = [[] for a in range(3)]
        for m in range(3):
            new_list = []
            for h in data_unuse_disks:
                new_list.append(h[m])
            lists[m].append(new_list)

        log.info("集群中的所有未使用数据盘:{}".format(lists))
        if storage_pool_num == 3:
            for i in range(3):
                log.info("will create storage :%s" % i)
                pool_id = ",".join('%s' % id for id in lists[i][0])
                cmd = (
                        "ssh root@%s '/home/parastor/cli/pscli --command=create_storage_pool --name=stor%s --type=BLOCK --node_pool_ids=1 --disk_ids=%s '" % (
                    deploy_ips[0], i, pool_id))
                log.info(cmd)
                commands.getstatusoutput(cmd)
        elif storage_pool_num == 1:
            stor_id1 = osan.create_storage_pool(s_ip=node_ip1, node_pool_ids=node_pool_id, name='pool1')

        osan.update_param(s_ip=node_ip, section='MGR', name='mgcd_auto_mount_flag', current='0')  # 解除自动挂载

    elif target == "create_access_zone":
        decorator_func.timer(15)
        if reboot_node:
            for ip in deploy_ips:
                cmd = ("ssh root@%s 'reboot'" % (ip))
                log.info(cmd)
                res, output = commands.getstatusoutput(cmd)
            for ip in deploy_ips:
                Reliable_osan.get_os_status_1(ip)
        osan.uninstall_Xstor(node_ip1)
        tgt_res = 0
        for ip in deploy_ips:
            cmd = ("ssh root@%s 'lsmod |grep -w tgt'" % (ip,))
            res, output = commands.getstatusoutput(cmd)
            if res == 0:
                log.error("Sorry, I detect that there is tgt module on %s" % (ip,))
                tgt_res = 1
            if tgt_res == 1:
                log.error("Begin to restart these nodes.")
                cmd = ("ssh root@%s 'reboot'" % (ip))
                log.info(cmd)
                res, output = commands.getstatusoutput(cmd)
                Reliable_osan.get_os_status_1(ip)
                osan.uninstall_Xstor(node_ip1)
        osan.install_Xstor(node_ip1)
        node_ids_list = osan.get_nodes(deploy_ips[0])
        node_ids = ",".join('%s' % id for id in node_ids_list)

        share_disk_ids_list = break_down.get_all_shared_disk_id()
        data_disk_ids_list = break_down.get_all_data_disk_id()
        share_disk_ids = re.sub('\[|\]| ', '', str(break_down.get_all_shared_disk_id()))
        data_disk_ids = re.sub('\[|\]| ', '', str(break_down.get_all_data_disk_id()))
        if change_disk_speed:
            log.debug("更改共享盘速率为High、数据盘速率为MID")
            cmd = (
                    "ssh root@%s '/home/parastor/cli/pscli --command=change_disk_speed_level --disk_ids=%s --speed_level=HIGH'"
                    % (deploy_ips[0], share_disk_ids))
            commands.getstatusoutput(cmd)
            cmd = (
                    "ssh root@%s '/home/parastor/cli/pscli --command=change_disk_speed_level --disk_ids=%s --speed_level=MID'"
                    % (deploy_ips[0], data_disk_ids))
            commands.getstatusoutput(cmd)
        node_pool_id = osan.create_node_pool(s_ip=node_ip, node_ids=node_ids,
                                             replica_num=cp("create_node_pool", "replica_num"),
                                             stripe_width=cp('create_node_pool', 'stripe_width'),
                                             disk_parity_num=cp("create_node_pool", "disk_parity_num"),
                                             node_parity_num=cp("create_node_pool", "node_parity_num"),
                                             name="nodepool1")
        if start_up:
            osan.startup(s_ip=node_ip)
        data_unuse_disks = []
        for i in node_ids_list:
            j = break_down.get_assign_data_disk_id(s_ip=deploy_ips[0], node_id=i)
            data_unuse_disks.append(j)
        lists = [[] for a in range(3)]
        for m in range(3):
            new_list = []
            for h in data_unuse_disks:
                new_list.append(h[m])
            lists[m].append(new_list)

        log.info("集群中的所有未使用数据盘:{}".format(lists))
        if storage_pool_num == 3:
            for i in range(3):
                log.info("will create storage :%s" % i)
                pool_id = ",".join('%s' % id for id in lists[i][0])
                cmd = (
                        "ssh root@%s '/home/parastor/cli/pscli --command=create_storage_pool --name=stor%s --type=BLOCK --node_pool_ids=1 --disk_ids=%s '" % (
                    deploy_ips[0], i, pool_id))
                log.info(cmd)
                commands.getstatusoutput(cmd)
        elif storage_pool_num == 1:
            stor_id1 = osan.create_storage_pool(s_ip=node_ip1, node_pool_ids=node_pool_id, name='pool1')

        osan.update_param(s_ip=node_ip, section='MGR', name='mgcd_auto_mount_flag', current='0')  # 解除自动挂载
        az_id = osan.create_access_zone(s_ip=node_ip, node_id=node_ids, name='accesszone1')

    elif target == "create_vip_address":
        decorator_func.timer(15)
        if reboot_node:
            for ip in deploy_ips:
                cmd = ("ssh root@%s 'reboot'" % (ip))
                log.info(cmd)
                res, output = commands.getstatusoutput(cmd)
            for ip in deploy_ips:
                Reliable_osan.get_os_status_1(ip)
        osan.uninstall_Xstor(node_ip1)
        tgt_res = 0
        for ip in deploy_ips:
            cmd = ("ssh root@%s 'lsmod |grep -w tgt'" % (ip,))
            res, output = commands.getstatusoutput(cmd)
            if res == 0:
                log.error("Sorry, I detect that there is tgt module on %s" % (ip,))
                tgt_res = 1
            if tgt_res == 1:
                log.error("Begin to restart these nodes.")
                cmd = ("ssh root@%s 'reboot'" % (ip))
                log.info(cmd)
                res, output = commands.getstatusoutput(cmd)
                Reliable_osan.get_os_status_1(ip)
                osan.uninstall_Xstor(node_ip1)
        osan.install_Xstor(node_ip1)
        node_ids_list = osan.get_nodes(deploy_ips[0])
        node_ids = ",".join('%s' % id for id in node_ids_list)

        share_disk_ids_list = break_down.get_all_shared_disk_id()
        data_disk_ids_list = break_down.get_all_data_disk_id()
        share_disk_ids = re.sub('\[|\]| ', '', str(break_down.get_all_shared_disk_id()))
        data_disk_ids = re.sub('\[|\]| ', '', str(break_down.get_all_data_disk_id()))
        if change_disk_speed:
            log.debug("更改共享盘速率为High、数据盘速率为MID")
            cmd = (
                    "ssh root@%s '/home/parastor/cli/pscli --command=change_disk_speed_level --disk_ids=%s --speed_level=HIGH'"
                    % (deploy_ips[0], share_disk_ids))
            commands.getstatusoutput(cmd)
            cmd = (
                    "ssh root@%s '/home/parastor/cli/pscli --command=change_disk_speed_level --disk_ids=%s --speed_level=MID'"
                    % (deploy_ips[0], data_disk_ids))
            commands.getstatusoutput(cmd)
        node_pool_id = osan.create_node_pool(s_ip=node_ip, node_ids=node_ids,
                                             replica_num=cp("create_node_pool", "replica_num"),
                                             stripe_width=cp('create_node_pool', 'stripe_width'),
                                             disk_parity_num=cp("create_node_pool", "disk_parity_num"),
                                             node_parity_num=cp("create_node_pool", "node_parity_num"),
                                             name="nodepool1")
        if start_up:
            osan.startup(s_ip=node_ip)
        data_unuse_disks = []
        for i in node_ids_list:
            j = break_down.get_assign_data_disk_id(s_ip=deploy_ips[0], node_id=i)
            data_unuse_disks.append(j)
        lists = [[] for a in range(3)]
        for m in range(3):
            new_list = []
            for h in data_unuse_disks:
                new_list.append(h[m])
            lists[m].append(new_list)

        log.info("集群中的所有未使用数据盘:{}".format(lists))
        if storage_pool_num == 3:
            for i in range(3):
                log.info("will create storage :%s" % i)
                pool_id = ",".join('%s' % id for id in lists[i][0])
                cmd = (
                        "ssh root@%s '/home/parastor/cli/pscli --command=create_storage_pool --name=stor%s --type=BLOCK --node_pool_ids=1 --disk_ids=%s '" % (
                    deploy_ips[0], i, pool_id))
                log.info(cmd)
                commands.getstatusoutput(cmd)
        elif storage_pool_num == 1:
            stor_id1 = osan.create_storage_pool(s_ip=node_ip1, node_pool_ids=node_pool_id, name='pool1')

        osan.update_param(s_ip=node_ip, section='MGR', name='mgcd_auto_mount_flag', current='0')  # 解除自动挂载
        az_id = osan.create_access_zone(s_ip=node_ip, node_id=node_ids, name='accesszone1')
        sub_id = osan.create_subnet(s_ip=node_ip, access_zone_id=az_id, name='subnet1',
                                    sv_ip=cp("create_subnet", "sv_ip"),
                                    mask=cp("create_subnet", "mask"), vv_ip=cp("create_subnet", "vv_ip"),
                                    gate_way=cp("create_subnet", "gate_way"),
                                    network_interface=cp("create_subnet", "network_interface"), deploy=deploy_svip)
        vip_id = osan.add_vip_address_pool(s_ip=node_ip, subnet_id=sub_id,
                                           domain_name=cp("add_vip_address_pool", "domain_name"),
                                           vip=cp("add_vip_address_pool", "vips"), deploy=deploy_vip)
        if enable_san:
            osan.enable_san(s_ip=node_ip, access_zone_id=az_id)

    elif target == "create_subnet":
        decorator_func.timer(15)
        if reboot_node:
            for ip in deploy_ips:
                cmd = ("ssh root@%s 'reboot'" % (ip))
                log.info(cmd)
                res, output = commands.getstatusoutput(cmd)
            for ip in deploy_ips:
                Reliable_osan.get_os_status_1(ip)
        osan.uninstall_Xstor(node_ip1)
        tgt_res = 0
        for ip in deploy_ips:
            cmd = ("ssh root@%s 'lsmod |grep -w tgt'" % (ip,))
            res, output = commands.getstatusoutput(cmd)
            if res == 0:
                log.error("Sorry, I detect that there is tgt module on %s" % (ip,))
                tgt_res = 1
            if tgt_res == 1:
                log.error("Begin to restart these nodes.")
                cmd = ("ssh root@%s 'reboot'" % (ip))
                log.info(cmd)
                res, output = commands.getstatusoutput(cmd)
                Reliable_osan.get_os_status_1(ip)
                osan.uninstall_Xstor(node_ip1)
        osan.install_Xstor(node_ip1)
        node_ids_list = osan.get_nodes(deploy_ips[0])
        node_ids = ",".join('%s' % id for id in node_ids_list)

        share_disk_ids_list = break_down.get_all_shared_disk_id()
        data_disk_ids_list = break_down.get_all_data_disk_id()
        share_disk_ids = re.sub('\[|\]| ', '', str(break_down.get_all_shared_disk_id()))
        data_disk_ids = re.sub('\[|\]| ', '', str(break_down.get_all_data_disk_id()))
        if change_disk_speed:
            log.debug("更改共享盘速率为High、数据盘速率为MID")
            cmd = (
                    "ssh root@%s '/home/parastor/cli/pscli --command=change_disk_speed_level --disk_ids=%s --speed_level=HIGH'"
                    % (deploy_ips[0], share_disk_ids))
            commands.getstatusoutput(cmd)
            cmd = (
                    "ssh root@%s '/home/parastor/cli/pscli --command=change_disk_speed_level --disk_ids=%s --speed_level=MID'"
                    % (deploy_ips[0], data_disk_ids))
            commands.getstatusoutput(cmd)
        node_pool_id = osan.create_node_pool(s_ip=node_ip, node_ids=node_ids,
                                             replica_num=cp("create_node_pool", "replica_num"),
                                             stripe_width=cp('create_node_pool', 'stripe_width'),
                                             disk_parity_num=cp("create_node_pool", "disk_parity_num"),
                                             node_parity_num=cp("create_node_pool", "node_parity_num"),
                                             name="nodepool1")
        if start_up:
            osan.startup(s_ip=node_ip)
        data_unuse_disks = []
        for i in node_ids_list:
            j = break_down.get_assign_data_disk_id(s_ip=deploy_ips[0], node_id=i)
            data_unuse_disks.append(j)
        lists = [[] for a in range(3)]
        for m in range(3):
            new_list = []
            for h in data_unuse_disks:
                new_list.append(h[m])
            lists[m].append(new_list)

        log.info("集群中的所有未使用数据盘:{}".format(lists))
        if storage_pool_num == 3:
            for i in range(3):
                log.info("will create storage :%s" % i)
                pool_id = ",".join('%s' % id for id in lists[i][0])
                cmd = (
                        "ssh root@%s '/home/parastor/cli/pscli --command=create_storage_pool --name=stor%s --type=BLOCK --node_pool_ids=1 --disk_ids=%s '" % (
                    deploy_ips[0], i, pool_id))
                log.info(cmd)
                commands.getstatusoutput(cmd)
        elif storage_pool_num == 1:
            stor_id1 = osan.create_storage_pool(s_ip=node_ip1, node_pool_ids=node_pool_id, name='pool1')

        osan.update_param(s_ip=node_ip, section='MGR', name='mgcd_auto_mount_flag', current='0')  # 解除自动挂载
        az_id = osan.create_access_zone(s_ip=node_ip, node_id=node_ids, name='accesszone1')
        sub_id = osan.create_subnet(s_ip=node_ip, access_zone_id=az_id, name='subnet1',
                                    sv_ip=cp("create_subnet", "sv_ip"),
                                    mask=cp("create_subnet", "mask"), vv_ip=cp("create_subnet", "vv_ip"),
                                    gate_way=cp("create_subnet", "gate_way"),
                                    network_interface=cp("create_subnet", "network_interface"), deploy=deploy_svip)


def clean(target="hostgroup"):
    if target == "lun_map":
        clean_lun_map()
    elif target == "lun":
        clean_lun_map()
        clean_lun()
    elif target == "initiator":
        clean_lun_map()
        clean_lun()
        clean_initiator()
    elif target == "host":
        clean_lun_map()
        clean_lun()
        clean_initiator()
        clean_host()
    elif target == "hostgroup":
        clean_lun_map()
        clean_lun()
        clean_initiator()
        clean_host()
        clean_hostgroup()
    elif target == "vip":
        clean_lun_map()
        clean_lun()
        clean_initiator()
        clean_host()
        clean_hostgroup()
        clean_vip_address_pool()
    elif target == "subnet":
        clean_lun_map()
        clean_lun()
        clean_initiator()
        clean_host()
        clean_hostgroup()
        clean_vip_address_pool()
        clean_subnet()
    elif target == "access_zone":
        clean_lun_map()
        clean_lun()
        clean_initiator()
        clean_host()
        clean_hostgroup()
        clean_vip_address_pool()
        clean_subnet()
        clean_access_zone()
    elif target == "storage_pool":
        clean_lun_map()
        clean_lun()
        clean_initiator()
        clean_host()
        clean_hostgroup()
        clean_vip_address_pool()
        clean_subnet()
        clean_access_zone()
        clean_storage_pool()
    elif target == "node_pool":
        clean_lun_map()
        clean_lun()
        clean_initiator()
        clean_host()
        clean_hostgroup()
        clean_vip_address_pool()
        clean_subnet()
        clean_access_zone()
        clean_storage_pool()
        clean_node_pools()


def create_iscsi_login(ips=deploy_ips[0], cli_ips=client_ips[0], subnet_id=None):
    # node_id = com_lh.get_node_id_by_ip(ips)
    if subnet_id:
        svip = co2_osan.get_svip(ips, subnet_id)
        osan.discover_scsi_list(client_ip=cli_ips, svip=svip[0])  # 进行一下discovery，真正的tag从xstor中拿
        target_list = osan.get_map_target(ips)
        log.info("Get Info:\nSvip list:%s \nTarget list:%s" % (svip, target_list))
        for tag in target_list:
            log.info("主机发现存储target：%s,主机 %s 将进行SCSI登录" % (tag, cli_ips))
            osan.iscsi_login(client_ip=cli_ips, iqn=tag)
    else:
        subnet_ids = osan.get_subnet_id(s_ip=node_ip)
        svip = co2_osan.get_svip(ips, subnet_ids[0])
        osan.discover_scsi_list(client_ip=cli_ips, svip=svip[0])  # 进行一下discovery，真正的tag从xstor中拿
        target_list = osan.get_map_target(ips)
        log.info("Get Info:\nSvip list:%s \nTarget list:%s" % (svip, target_list))
        for tag in target_list:
            log.info("主机发现存储target：%s,主机 %s 将进行SCSI登录" % (tag, cli_ips))
            osan.iscsi_login(client_ip=cli_ips, iqn=tag)


def revert_env():
    log.info("同步unistor_test_config.xml文件的ip配置到x1000.conf")
    svip = get_config.get_svip(conf_file)[0]
    vip = get_config.get_vip(conf_file)[0]
    (esxi_ip, esxi_un, esxi_pw) = get_config.get_esxi(conf_file)
    esxi_ip = esxi_ip[0]
    esxi_un = esxi_un[0]
    esxi_pw = esxi_pw[0]

    cmd_1 = (
        "sed -i 's/sv_ip=.*/sv_ip={}/' {}/lun_manager/x1000.conf".format(
            svip, father_path))
    log.info(cmd_1)
    cmd_2 = (
        "sed -i 's/vips=.*/vips={}/' {}/lun_manager/x1000.conf".format(
            vip, father_path))
    log.info(cmd_2)
    cmd_3 = (
        "sed -i 's/Esxi_ips=.*/Esxi_ips={}/' {}/lun_manager/x1000.conf".format(
            esxi_ip, father_path))
    log.info(cmd_3)

    cmd_4 = (
        "sed -i 's/esxi_user=.*/esxi_user={}/' {}/lun_manager/x1000.conf".format(
            esxi_un, father_path))
    log.info(cmd_4)
    cmd_5 = (
        "sed -i 's/esxi_passwd=.*/esxi_passwd={}/' {}/lun_manager/x1000.conf".format(
            esxi_pw, father_path))
    log.info(cmd_5)

    res1, final1 = commands.getstatusoutput(cmd_1)
    res2, final2 = commands.getstatusoutput(cmd_2)
    res3, final3 = commands.getstatusoutput(cmd_3)
    res4, final4 = commands.getstatusoutput(cmd_4)
    res5, final5 = commands.getstatusoutput(cmd_5)
    if any([res1, res2, res3, res4, res5]):
        log.error("替换x1000.conf  ip失败")
        exit(1)
    log.info("------------------- 还原主机端环境参数--------------- ...")
    total_ip = deploy_ips + client_ips
    for ip in total_ip:
        cmd = ("ssh {} \"cat /etc/security/limits.conf |grep '10240'\"".format(ip))
        res, stdout = commands.getstatusoutput(cmd)
        if stdout == '':
            log.info("解除OS线程数限制!")
            cmd = "ssh {} \"echo -e '* soft nofile 10240\n* hard nofile 10240' >>/etc/security/limits.conf\"".format(ip)
            log.info(cmd)
            commands.getstatusoutput(cmd)
    log.info("主机端logout ...")
    iscsi_logout()
    log.info("还原主机端iqn ...")
    osan.write_iqn(cli_ip=client_ip1, iqn=cp('add_initiator', 'iqn'))
    osan.write_iqn(cli_ip=client_ip2, iqn=cp('add_initiator', 'iqn1'))
    log.info("还原主机端CHAP的认证，默认为None ...")
    osan.update_iscsid_conf(cli_ip=client_ips[0], CHAPTYPE='None', s_ip=client_ips[0])
    osan.update_iscsid_conf(cli_ip=client_ips[0], CHAPTYPE='None', s_ip=client_ips[1])


def main():
    setup()
    revert_env()
    init_env()
    decorator_func.pass_flag(tip_type="deploy")


if __name__ == '__main__':
    common.case_main(main)