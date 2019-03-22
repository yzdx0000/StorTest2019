# -*- encoding=utf8 -*-
# ===================================================
# latest date :2018-07-31
# author: wangxiang
# ===================================================
# 2018-08-07:
# 修改者:wangxiang
# 1.修改安装和卸载在主机端发起；修改共享盘个数为2，为用例做准备
# 2018-07-31:
# 修改者:wangxiang
# 1.创建 env_manage_repair_test

"""
Xstor的安装和各种清理工作
"""

import os, sys
import time
import commands
import utils_path
import Lun_managerTest
import common
import common2
import breakdown
import log
import ReliableTest
import get_config
from get_config import config_parser as cp
import decorator_func
import error

conf_file = get_config.CONFIG_FILE  # 配置文件路径
deploy_ips = get_config.get_env_ip_info(conf_file)  # 获取集群IP列表
log.info(deploy_ips)
node_ip1 = deploy_ips[0]  # 集群节点1
client_ips = get_config.get_allclient_ip()  # 获取主机端IP
log.info(client_ips)
client_ip1 = client_ips[0]  # 主机端1
client_ip2 = client_ips[1]  # 主机端2
Esxi_ips = cp('esxi', 'Esxi_ips')

Lun_osan = Lun_managerTest.oSan()
co2_osan = common2.oSan()
Reliable_osan = breakdown.Os_Reliable()
com_disk = common.Disk()
com_node = common.Node()
assert_ins = decorator_func.assert_cls()
nodeids = Lun_osan.get_nodes(node_ip1)


def rel_check_before_run(filename):
    """执行用例前环境检测"""
    error.rel_check_before_run(file_name=filename, jnl_rep=int(cp("env", "jnl_rep")),
                               free_jnl_num=int(cp("env", "free_jnl_num")),
                               node_num=int(cp("env", "node_num")))


def setup():
    file_name = os.path.basename(__file__)
    file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
    log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
    log.init(log_file_path, True)  # 初始化日志文件


def xstor_init():
    decorator_func.timer(15)
    Lun_osan.uninstall_Xstor(node_ip1)
    tgt_res = 0
    for ip in deploy_ips:
        cmd = ("ssh root@%s 'lsmod |grep -w tgt'" % (ip,))
        res, output = commands.getstatusoutput(cmd)
        if res == 0:
            log.error("Sorry, I detect that there is tgt module on %s" % (ip,))
            tgt_res = 1
    if tgt_res == 1:
        log.error("Begin to restart these nodes.")
        for ip in deploy_ips:
            cmd = ("ssh root@%s 'reboot'" % (ip))
            log.info(cmd)
            res, output = commands.getstatusoutput(cmd)
            Reliable_osan.get_os_status(ip)

    Lun_osan.install_Xstor(node_ip1)
    node_pool_id = Lun_osan.create_node_pool(s_ip=node_ip1, node_ids=cp('create_node_pool', 'node_ids'),
                                             replica_num=cp("create_node_pool", "replica_num"),
                                             stripe_width=cp('create_node_pool', 'stripe_width'),
                                             disk_parity_num=cp("create_node_pool", "disk_parity_num"),
                                             node_parity_num=cp("create_node_pool", "node_parity_num"),
                                             name="nodepool1")
    Lun_osan.startup(s_ip=node_ip1)
    stor_id1 = Lun_osan.create_storage_pool(s_ip=node_ip1, node_pool_ids=node_pool_id, name='pool1')
    assert_ins.assertIN('pool1',
                        Lun_osan.get_option(s_ip=node_ip1, command='get_storage_pools', indexname='storage_pools',
                                            argv='name'), suc_msg='pool1 create success')
    Lun_osan.update_param(s_ip=node_ip1, section='MGR', name='mgcd_auto_mount_flag', current='0')  # 解除自动挂载
    az_id = Lun_osan.create_access_zone(s_ip=node_ip1, node_id='1,2,3', name='accesszone1')
    sub_id = Lun_osan.create_subnet(s_ip=node_ip1, access_zone_id=az_id, name='subnet1',
                                    sv_ip=cp("create_subnet", "sv_ip"),
                                    mask=cp("create_subnet", "mask"),
                                    vv_ip=cp("create_subnet", "vv_ip"),
                                    gate_way=cp("create_subnet", "gate_way"),
                                    network_interface=cp("create_subnet", "network_interface"))
    Lun_osan.add_vip_address_pool(s_ip=node_ip1, subnet_id=sub_id,
                                  domain_name=cp("add_vip_address_pool", "domain_name"),
                                  vip=cp("add_vip_address_pool", "vips"))
    Reliable_osan.init_otrace()  # 开启otrace
    Lun_osan.enable_san(s_ip=node_ip1, access_zone_id=az_id)
    hg_id1 = Lun_osan.create_host_group(s_ip=node_ip1, hg_name="hg_1")
    hg_id2 = Lun_osan.create_host_group(s_ip=node_ip1, hg_name="hg_2")
    h_id1 = Lun_osan.add_host(s_ip=node_ip1, h_name="h_1", hg_id=hg_id1)
    h_id2 = Lun_osan.add_host(s_ip=node_ip1, h_name="h_2", hg_id=hg_id2)
    ini_id1 = Lun_osan.add_initiator(s_ip=node_ip1, h_id=h_id1, iqn=cp('add_initiator', 'iqn'),
                                     alias=cp('add_initiator', 'alias'))
    Lun_osan.update_iscsid_conf(cli_ip=client_ip1, CHAPTYPE='None', s_ip=client_ip1)
    ini_id2 = Lun_osan.add_initiator(s_ip=node_ip1, h_id=h_id2, iqn=cp('add_initiator', 'iqn1'),
                                     alias=cp('add_initiator', 'alias1'))
    for i in range(1, 13):
        lun_id = Lun_osan.create_lun(s_ip=deploy_ips[0], lun_type="THIN",
                                     lun_name='LUN{}'.format(i),
                                     stor_pool_id=stor_id1, acc_zone_id=az_id, stripe_width=3)
        log.info(lun_id)
        decorator_func.judge_target(
            Lun_osan.get_option_single(s_ip=deploy_ips[0], command="get_luns", indexname="luns"
                                       , argv2="name", ids="ids", argv1=lun_id),
            'LUN{}'.format(i))

    lun = Lun_osan.get_lun(s_ip=node_ip1)
    for i in lun:
        if i % 2 == 0:
            Lun_osan.map_lun(s_ip=node_ip1, lun_ids=i, hg_id=hg_id1)
        else:
            Lun_osan.map_lun(s_ip=node_ip1, lun_ids=i, hg_id=hg_id2)


def clean_lun_map():
    lun_map_ids = Lun_osan.get_lun_maps(node_ip1)
    log.info(lun_map_ids)

    [Lun_osan.delete_lun_map(s_ip=node_ip1, map_id=lun_map_id) for lun_map_id in lun_map_ids]


def clean_node_pools():
    node_pool_ids = Lun_osan.get_option(s_ip=node_ip1, command="get_node_pools", indexname="node_pools", argv="id")
    log.info(node_pool_ids)
    for node_pool_id in node_pool_ids:
        Lun_osan.delete_node_pools(s_ip=node_ip1, node_pool_id=node_pool_id)


def clean_lun():
    lun_ids = Lun_osan.get_lun(s_ip=node_ip1)
    log.info(lun_ids)
    for lun_id in lun_ids:
        Lun_osan.delete_lun(s_ip=node_ip1, lun_id=lun_id)


def clean_initiator():
    ini_ids = Lun_osan.get_initiators(s_ip=node_ip1)
    log.info(ini_ids)
    for ini_id in ini_ids:
        Lun_osan.remove_initiator(s_ip=node_ip1, ini_id=ini_id)


def clean_host():
    host_ids = Lun_osan.get_hosts(s_ip=node_ip1)
    log.info(host_ids)
    for host_id in host_ids:
        Lun_osan.remove_hosts(s_ip=node_ip1, id=host_id)


def clean_hostgroup():
    hostgroup_ids = Lun_osan.get_host_groups(s_ip=node_ip1)
    log.info(hostgroup_ids)
    for hostgroup_id in hostgroup_ids:
        Lun_osan.delete_host_groups(s_ip=node_ip1, id=hostgroup_id)


def clean_vip_address_pool():
    vip_pool_ids = Lun_osan.get_option(s_ip=node_ip1, command="get_vip_address_pools", indexname="ip_address_pools",
                                       argv="id")
    for vip_pool_id in vip_pool_ids:
        Lun_osan.delete_vip_address_pool(s_ip=node_ip1, id=vip_pool_id)


def clean_subnet():
    subnet_ids = Lun_osan.get_subnet_id(s_ip=node_ip1)
    log.info(subnet_ids)
    for subnet_id in subnet_ids:
        Lun_osan.delete_subnet(s_ip=node_ip1, id=subnet_id)


def clean_access_zone(azs=None):
    azs = Lun_osan.get_access_zone_id(s_ip=node_ip1)
    log.info(azs)
    for az in azs:
        Lun_osan.delete_access_zone(s_ip=node_ip1, id=az)


def clean_storage_pool():
    sto_pool_ids = Lun_osan.get_storage_id(s_ip=node_ip1)
    log.info(sto_pool_ids)
    for sto_pool_id in sto_pool_ids:
        Lun_osan.delete_storage_pool(s_ip=node_ip1, id=sto_pool_id)


def iscsi_logout():
    for cli in client_ips:
        Lun_osan.iscsi_logout_all(cli)


def get_os_type(s_ip):
    cmd = ("ssh %s \" dmidecode -s system-product-name\"" % (s_ip))
    rc, stdout = commands.getstatusoutput(cmd)
    if rc != 0:
        log.info("get  %s system type failed" % (s_ip))
        os._exit(1)
    else:
        if "VMware" in stdout:
            log.info("check the system is %s " % (stdout))
            return "VM"
        else:
            log.info("phy")
            return "phy"


def down_node(node_ip, type_info, cmd=None):
    """

    :param node_ip: 节点IP
    :param type_info: 节点类型，由get_os_type函数导入
    :param cmd: 是否使用命令关机，
    :return: 虚拟机返回虚拟机ID号，物理机返回IPMI地址
    """
    if type_info == "phy":
        if cmd is None:
            ipmi_ip = ReliableTest.get_ipmi_ip(node_ip)
            log.info("The pyh node will IPMI to down os")
            if False == ReliableTest.run_down_node(ipmi_ip):
                print ("node %s down failed!!!" % node_ip)
                exit(1)
            else:
                return ipmi_ip
        else:
            ipmi_ip = ReliableTest.get_ipmi_ip(node_ip)
            Reliable_osan.poweroff_os(node_ip, cmd)
            return ipmi_ip

    else:
        (esxi_ip, esxi_un, esxi_pw) = get_config.get_esxi(conf_file)
        if cmd is None:
            log.info("the VMware node will power cut ")
            vm_id = ReliableTest.run_down_vir_node(esxi_ip=esxi_ip[0], u_name=esxi_un[0], pw=esxi_pw[0],
                                                   node_ip=node_ip)
            log.info("Down VM ID : %s " % (vm_id))
            return vm_id
        else:
            log.info("The node %s will down make cmd :%s" % (node_ip, cmd))
            vm_id = Reliable_osan.vm_id(esxi_ip=esxi_ip[0], u_name=esxi_un[0], pw=esxi_pw[0], node_ip=node_ip)
            Reliable_osan.poweroff_os(node_ip, cmd)
            while True:
                vm_status = Reliable_osan.get_vm_status(esxi_ip=esxi_ip[0], vm_name=esxi_un[0], pw=esxi_pw[0],
                                                        vm_id=vm_id).strip()
                log.info("now,get the node status is %s " % (vm_status))
                if vm_status == "Powered off" and cmd == "init 0":
                    log.info("The vm system power off success \nVM ID is : %s" % (vm_id))
                    time.sleep(1)
                    return vm_id
                elif cmd == "init 6":
                    log.info("Node %s system will reboot" % (vm_id))
                    time.sleep(1)
                    return vm_id
                time.sleep(1)


def up_node(node_info=None, type_info=None):
    """

    :param node_info: down_node的返回值
    :param type_info: 节点类型类型，由get_os_type返回值
    :return:
    """
    if type_info == "phy":
        if False == ReliableTest.run_up_node(node_info):
            print ("node up failed!!!")
            os._exit(1)
    else:
        (esxi_ip, esxi_un, esxi_pw) = get_config.get_esxi(conf_file)
        os_up(nums=node_info, esxi_ip=esxi_ip[0], u_name=esxi_un[0], pw=esxi_pw[0])


def os_up(nums, esxi_ip, u_name, pw):
    for i in range(600):
        vm_status = Reliable_osan.get_vm_status(esxi_ip, u_name, pw, nums).strip()
        if vm_status == "Powered off":
            log.info("will send power on to vm")
            ReliableTest.run_up_vir_node(esxi_ip=esxi_ip, u_name=u_name, pw=pw, vm_id=nums)
            time.sleep(20)
        elif vm_status == "Powered on":
            log.info("waiting  the os up finish")
            return
        elif i == 599:
            log.info("The vm lost when waiting 600s, you need check vm os")
            os._exit(1)
        else:
            time.sleep(1)


def clean():
    log.info("执行环境清理和还原工作...")
    # iscsi_logout()
    log.info("还原磁盘和节点修复的超时时间")
    Reliable_osan.run_down_disk_wait(s_ip=node_ip1,
                                     timeout='3600000')
    Reliable_osan.run_down_node_wait(s_ip=node_ip1,
                                     timeout='86400000')


def main():
    setup()
    iscsi_logout()
    Lun_osan.write_iqn(cli_ip=client_ip1, iqn=cp('add_initiator', 'iqn'))
    Lun_osan.write_iqn(cli_ip=client_ip2, iqn=cp('add_initiator', 'iqn1'))
    xstor_init()
    common.ckeck_system()


if __name__ == '__main__':
    main()
