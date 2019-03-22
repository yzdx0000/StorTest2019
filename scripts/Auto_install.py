#!/usr/bin/python
# -*- coding:utf-8 -*-
# ===================================
# latest update: 2018-12-10
# author: diws
# updater: wuyq,2018-12-10
# ===================================
import random
import datetime
import time
import xml
from optparse import OptionParser
import os
import commands
import copy
import re
import utils_path
import log
import get_config
import common2
import ReliableTest
import breakdown
import Lun_managerTest
import env_manage_lun_manage

# 参数初始化
osan = common2.oSan()
lun_osan = Lun_managerTest.oSan()
break_down = breakdown.disk()
com_bk_os = breakdown.Os_Reliable()
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
log.init(log_file_path, True)  # 初始化日志文件
mkpkg_flag = 0
parser = OptionParser()
parser.add_option("--mkpkg", "-m",
                  action="store_true",
                  dest="mkpkg",
                  help="When you want to refresh the code and mkpkg, set this parameter to -m or --mkpkg. default: "
                       "%default, do not refresh code and mkpkg")
options, args = parser.parse_args()
if options.mkpkg is True:
    mkpkg_flag = 1

# 读取配置文件
# 获取路径：/home/StorTest/src_code/ofs/code/test/mgr/it/script/san.py/scripts
current_path_1 = os.path.dirname(os.path.abspath(__file__))
# 获取路径：/home/StorTest/src_code/ofs/code/test/mgr/it/script/san.py
current_path = os.path.dirname(current_path_1)
# 获取路径：/home/StorTest/src_code/ofs/code/test/mgr/it/script/san.py/conf
conf_path = os.path.join(current_path, 'conf')
new_feature_file = 'x1000_new_feature.xml'
new_feature_path = os.path.join(conf_path, new_feature_file)
conf_file = get_config.CONFIG_FILE
deploy_conf_file = '/home/deploy/deploy_config.xml'

# 判断x1000_test_config.xml配置文件是否存在
if not os.path.exists(conf_file):
    log.error('error!file %s is not exists.' % conf_file)
    os._exit(1)

# 获取节点IP列表
deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()

# 重启节点
for ip in deploy_ips:
    cmd = ("timeout 15 ssh root@%s ' echo b > /proc/sysrq-trigger &'" % ip)
    log.info("Begin to reboot node %s..." % ip)
    res, output = commands.getstatusoutput(cmd)
time.sleep(120)


def check_host(ip):
    cmd = ("ssh %s 'hostname'" % ip)
    rc = os.system(cmd)
    if rc != 0:
        return False
    else:
        return True


# 检查节点是否重启成功
for ip in deploy_ips:
    count = 0
    while False is check_host(ip):
        log.info("wait node %s up..." % ip)
        if count == 600:
            log.error("the node %s is not boot in 10min." % ip)
            os._exit(1)
        time.sleep(10)
        count += 10

# 获取节点副本数和条带宽度
config_info = xml.dom.minidom.parse(conf_file)
replica = config_info.getElementsByTagName('replica')[0].firstChild.nodeValue
strip_width = config_info.getElementsByTagName('stripwidth')[0].firstChild.nodeValue
cmd = ("ssh %s \" dmidecode -s system-product-name\"" % (deploy_ips[0]))
rc, mac_stdout = commands.getstatusoutput(cmd)

node_parity = int(replica) - 1


def run_cmd(cmds):
    res, outputs = commands.getstatusoutput(cmds)
    if res != 0:
        log.error(outputs)
        log.error("Command execute ####  %s  #### failed." % cmds)
        os._exit(1)


def jnl_time():
    current_time = datetime.datetime.now()
    return current_time.strftime('%y-%m-%d %H:%M:%S')


# 检查环境，检查部署用的配置文件是否存在
log.info('##### Step1:Check the environment and the configuration file. #####')
cmd = ("ssh root@%s '[ -e %s ]'" % (deploy_ips[0], deploy_conf_file))
res, stdout = commands.getstatusoutput(cmd)
if res != 0:
    log.error("Error,I don't know what to say, I beg you to check if %s "
              "is exists on %s" % (deploy_ips[0], deploy_conf_file))
    os._exit(1)
log.debug("Check the cluster has /home/deploy and %s : Success." % deploy_conf_file)

# 检查主机端是否有/home/vdbench目录
log.info('##### Step2:Check the host vdbench test tool. #####')
for ip in client_ips:
    cmd = ("ssh root@%s '[ -e /home/vdbench ]'" % ip)
    res, stdout = commands.getstatusoutput(cmd)
    if res != 0:
        log.error(
            "Error, I don't know what to say, I beg you to check if /home/vdbench is exists on %s" % (ip,))
        exit(1)
log.debug("Check the clients has vdbench: Success.")

# 卸载所有lun
log.info('##### Step3:Logout all luns from clients #####')
for ip in client_ips:
    cmd1 = ("ssh root@%s 'iscsiadm -m node -u'" % ip)
    cmd2 = ("ssh root@%s 'iscsiadm -m node -o delete'" % ip)
    os.system(cmd1)
    os.system(cmd2)
log.info("Logout all luns on clients: Success.")

# 获取quickmk.sh路径,并且判断是否需要打包
src_path = current_path + "/src_code/ofs/"
if mkpkg_flag == 1:
    git_pull_cmd = "cd %s;git pull" % (src_path,)
    run_cmd(git_pull_cmd)
    log.debug("Refresh code: Success.")
    quick_mk_cmd = "cd %s;sh quickmk.sh rebuild mkpkg" % (src_path,)
    run_cmd(quick_mk_cmd)
    log.debug("Make package: Success.")

# 获取新包路径,并且取出最近时间点的包
log.info("##### Step4:Copy the new pkg to the node. #####")
new_pkg_path = src_path + 'code/bin/'
new_pkg_tar = None
cmd = ('ls -t %s' % new_pkg_path)
result = commands.getoutput(cmd)
lists = result.split('\n')
for file_name in lists:
    if 'parastor-3.0.0-centos' in file_name:
        log.info("New Pkg: %s" % file_name)
        new_pkg_tar = file_name
        break
if new_pkg_tar is None:
    log.error("Sorry,I can not find the new package.")
    os._exit(1)
cmd = ("ssh %s '[ -f /home/deploy/%s ]'" % (deploy_ips[0], new_pkg_tar))
rc = os.system(cmd)
if rc != 0:
    log.info("Delete all old pkgs in the node.")
    cmd = ("ssh %s 'rm -rf /home/deploy/parastor-3.0.0-centos*'" % deploy_ips[0])
    run_cmd(cmd)
    log.info("Copy the new package to the node.")
    cmd = ("scp %s/%s root@%s:/home/deploy/" % (new_pkg_path, new_pkg_tar, deploy_ips[0]))
    run_cmd(cmd)
    log.info("Copy the new package to %s: Success." % (deploy_ips[0]))
else:
    log.info("the new package is exist in node:%s." % (deploy_ips[0]))

log.info("##### Step5:Check if unpack the new pkg. #####")
log.info("Check the new package on %s:/home/deploy" % (deploy_ips[0]))
new_pkg_name = new_pkg_tar.split('.tar')[0]
tar_tag = 1
cmd = ("ssh %s 'ls /home/deploy'" % deploy_ips[0])
rc, stdout = commands.getstatusoutput(cmd)
dir_list = stdout.split('\n')
for tfile in dir_list:
    if tfile == new_pkg_name:
        tar_tag = 0
        log.info("the dirname of the new pkg is exist")
        break
if tar_tag == 1:
    log.info("Begin to unpack the new pkg.")
    cmd = ("ssh root@%s 'cd /home/deploy; tar -xvf %s'" % (deploy_ips[0], new_pkg_tar))
    run_cmd(cmd)
    log.info("Chnage default_disk_speed_category.xml.")
    cmd = ("ssh root@%s \"sed -i 's/LOW/MID/g' /home/deploy/%s/server/conf/default_disk_speed_category.xml\""
           % (deploy_ips[0], new_pkg_name,))
    run_cmd(cmd)
    log.info("Rm the package.")
    cmd = ("ssh root@%s 'rm -rf /home/deploy/%s'" % (deploy_ips[0], new_pkg_tar))
    run_cmd(cmd)
    log.info("Generate the tar package.")
    cmd = ("ssh root@%s 'cd /home/deploy;tar -cvf %s.tar %s'" % (deploy_ips[0], new_pkg_name, new_pkg_name))
    run_cmd(cmd)
    log.info("Generate the tar.xz package.")
    cmd = ("ssh root@%s 'cd /home/deploy;xz -z -0 %s.tar'" % (deploy_ips[0], new_pkg_name))
    run_cmd(cmd)

log.info("##### Step6:Uninstall the old system. #####")
cmd = ("ssh root@%s \"sed -r -i 's/\/home\/deploy\/.*<\/package_path>/"
       "\/home\/deploy\/%s<\/package_path>/g' %s\"" % (deploy_ips[0], new_pkg_tar, deploy_conf_file))
run_cmd(cmd)
log.debug("Begin to clean the cluster.")
for dip in deploy_ips:
    clean_cmd = ("ssh root@%s 'python /home/parastor/tools/deployment/uninstall_local_software.py --reserve_log=0'" % (
        dip,))
    clean_cmd2 = ("ssh root@%s 'rm -rf /home/parastor/*'" % (dip,))
    res, output = commands.getstatusoutput(clean_cmd)
    res, output = commands.getstatusoutput(clean_cmd2)

log.info("Check if the tgt module is clean.")
tgt_res = 0
for ip in deploy_ips:
    cmd = ("ssh root@%s 'lsmod |grep -w tgt'" % ip)
    res, output = commands.getstatusoutput(cmd)
    if res == 0:
        log.error("Sorry, I detect that there is tgt module on %s" % (ip,))
        tgt_res = 1
if tgt_res == 1:
    log.error("Begin to restart these nodes.")
    for ip in deploy_ips:
        cmd = ("timeout 15 ssh root@%s ' echo b > /proc/sysrq-trigger &'" % (ip,))
        log.info("Begin to reboot %s." % (ip,))
        res, output = commands.getstatusoutput(cmd)
    time.sleep(100)
    for ip in deploy_ips:
        count = 0
        while False is ReliableTest.check_ping(ip):
            log.info("wait node %s up..." % ip)
            if count == 600:
                log.error("the node %s is not boot in 10min." % ip)
                os._exit(1)
            time.sleep(10)
            count += 10
    time.sleep(30)
    clean_cmd = ("ssh root@%s '/home/deploy/%s/server/tools/deployment/clean.py --deploy_config=%s > /dev/null'"
                 % (deploy_ips[0], new_pkg_name, deploy_conf_file))
    res, output = commands.getstatusoutput(clean_cmd)
    log.debug("Check if the tgt module is clean, again.")
    tgt_res = 0
    for ip in deploy_ips:
        cmd = ("ssh root@%s 'lsmod |grep -w tgt'" % (ip,))
        res, output = commands.getstatusoutput(cmd)
        if res == 0:
            log.error("Sorry, I detect that there is tgt module on %s, again." % (ip,))
            tgt_res = 1
    if tgt_res == 1:
        log.error("Sorry, but I already do what I can, please restart these nodes yourself.")
        exit(1)

log.info("##### Step7:Install script check the install environment. #####")
log.info("Check the environment.")
cmd = ("ssh root@%s '/home/deploy/%s/server/tools/env_check/env_check.py "
       "--ip=%s --config=%s'" % (deploy_ips[0], new_pkg_name, deploy_ips[0], deploy_conf_file))
commands.getstatusoutput(cmd)
log.info("Begin to install the system.")
cmd = ("ssh root@%s '/home/deploy/%s/server/tools/deployment/deploy.py --deploy_config=%s --type=BLOCK'"
       % (deploy_ips[0], new_pkg_name, deploy_conf_file))
run_cmd(cmd)
log.debug("Congratulations.the system install Success.")
cmd = ("ssh root@%s '/home/parastor/cli/pscli --command=update_param --section=MGR "
       "--name=min_meta_replica --current=%s'" % (deploy_ips[0], str(replica)))
run_cmd(cmd)
log.debug("Change the min data replica number to 3: Success.")

# 获取节点ID列表
node_ids = []
for i in range(1, len(deploy_ips) + 1):
    node_ids.append(str(i))
acc_zone_node_ids = node_ids[:]
node_ids = ','.join(node_ids)
acc_zone_node_ids = ','.join(acc_zone_node_ids)

log.info("##### Step8:Create node pool and startup system. #####")
cmd = ("ssh root@%s '/home/parastor/cli/pscli --command=create_node_pool --node_ids=%s "
       "--replica_num=%s --stripe_width=%s --disk_parity_num=0 --node_parity_num=%s --name=firstpool'"
       % (deploy_ips[0], node_ids, str(replica), str(strip_width), str(node_parity)))
run_cmd(cmd)
log.info("Create node_pool，replica：%s, stripwidth：%s: Success." % (str(replica), str(strip_width)))
cmd = ("ssh root@%s '/home/parastor/cli/pscli --command=startup'" % (deploy_ips[0]))
run_cmd(cmd)
log.info("System start up: Success.")
disk_info = break_down.get_disk_ids_by_node_id()
disk_num = []
for nid in disk_info.keys():
    disk_num.append(len(disk_info[nid]))
# 检查系统节点类型，如果测试环境为虚拟机，就创建一个数据存储池，如果物理机，则创建多个

if "VMware" in mac_stdout:
    log.info("the running environment is:%s, will create only one storage pool" % (stdout,))
    storagepool_num = 1
else:
    storagepool_num = min(disk_num) / 3
stor_disks = {}
tmp_i = 0
for stor in range(storagepool_num):
    disks = []
    for nid in disk_info.keys():
        if stor + 1 == storagepool_num:
            disks = disks + disk_info[nid][tmp_i:]
        else:
            disks = disks + disk_info[nid][tmp_i:tmp_i + 3]
    tmp_i += 3
    stor_disks[stor] = re.sub('\[|\]| ', '', str(disks))
for stor_disk in stor_disks.keys():
    log.info("##### Step9:Create storage pool. #####")
    cmd = ("ssh root@%s '/home/parastor/cli/pscli --command=create_storage_pool --name=stor%d "
           "--type=BLOCK --node_pool_ids=1 --disk_ids=%s'" % (deploy_ips[0], stor_disk, stor_disks[stor_disk]))
    run_cmd(cmd)
    log.info("Crteate storage pool: Success.")

log.info("##### Step10:Create oSan access zone. #####")
svip = get_config.get_svip(conf_file)
vip = get_config.get_vip(conf_file)
log.info("svip is %s, vips is %s" % (svip, vip))
storid = osan.get_storage_id(s_ip=deploy_ips[0])
nodeid = osan.get_nodes(s_ip=deploy_ips[0])
acc_zone_ids = osan.create_access_zone(s_ip=deploy_ips[0], node_id=acc_zone_node_ids, name="access_zone1")
log.info("Create access zone: Success.")

log.info("##### Step11:Create subnet. #####")
osan.create_subnet(s_ip=deploy_ips[0], sv_ip=svip[0], access_zone_id=acc_zone_ids, name="subnet1")
log.info("Create subnet: Success.")

log.info("##### Step12:Create vip address pool. #####")
sub_id = osan.get_subnet_id(s_ip=deploy_ips[0])
osan.add_vip_address_pool(s_ip=deploy_ips[0],rebalance_policy='RB_AUTOMATIC', subnet_id=sub_id[0], domain_name="sugon2018.com", vip_addresses=vip[0])
log.info("Add vip_address_pool: Success.")

log.info("##### Step13:Enable oSan. #####")
osan.enable_san(s_ip=deploy_ips[0], access_zone_id=acc_zone_ids)
lun_osan.xstor_pre_config(s_ip=deploy_ips[0], osan_space_check=0, is_display_raw_capacity=0)
log.info("Enable san: Success.")

log.info("##### Step14:Create host groups and hosts. #####")
hg_id1 = osan.create_host_group(s_ip=deploy_ips[0], hg_name="hg_1")
hg_id2 = osan.create_host_group(s_ip=deploy_ips[0], hg_name="hg_2")
h_id1 = osan.add_host(s_ip=deploy_ips[0], h_name="h_1", hg_id=hg_id1[0])
h_id2 = osan.add_host(s_ip=deploy_ips[0], h_name="h_2", hg_id=hg_id2[0])

log.info("##### Step15:Add initiators. #####")
osan.add_initiator(s_ip=deploy_ips[0], h_id=h_id1[0], iqn="iqn.1990-21.com.sugon", alias="sugon1990.initiator")
log.info("Add initiator:iqn='iqn.1990-21.com.sugon' : Success.")
osan.add_initiator(s_ip=deploy_ips[0], h_id=h_id2[0], iqn="iqn.1991-21.com.sugon", alias="sugon1991.initiator")
log.info("Add initiator:iqn='iqn.1991-21.com.sugon' : Success.")

log.info("##### Step16:Update the initiator config in hosts. #####")
iqn = osan.get_iqn(s_ip=deploy_ips[0])
osan.write_iqn(cli_ip=client_ips[0], iqn=iqn[0])
osan.write_iqn(cli_ip=client_ips[1], iqn=iqn[1])

storid.remove(1)
storid_bak = copy.deepcopy(storid)
time.sleep(60)
log.info("##### Step17:Create 12 luns. #####")
lun_info = {}
for sid in storid:
    max_strip_width = 24 / int(replica)
    strip_width = random.randint(1, max_strip_width)
    lun_info[sid] = strip_width
set_lun_readhead_ids = []
for i in range(0, 20):
    if len(storid) == 0:
        storid = copy.deepcopy(storid_bak)
    s_id = random.choice(storid)
    storid.remove(s_id)
    j = random.randint(0, i)
    if j % 2 == 0:
        lun_id = osan.create_lun(s_ip=deploy_ips[0], lun_name="lun_" + str(i), stor_pool_id=s_id,
                                 acc_zone_id=acc_zone_ids, replica_num=replica, node_parity_num=node_parity,
                                 stripe_width=lun_info[s_id], lun_type="THIN", total_bytes="99999999999",
                                 max_throughput="9000", max_iops="2000", disk_parity_num="0")

    else:
        lun_id = osan.create_lun(s_ip=deploy_ips[0], lun_name="lun_" + str(i), stor_pool_id=s_id,
                                 acc_zone_id=acc_zone_ids, replica_num=replica, node_parity_num=node_parity,
                                 stripe_width=lun_info[s_id], lun_type="THIN", total_bytes="9999999999",
                                 max_throughput="9000", max_iops="2000", disk_parity_num="0")
    set_lun_readhead_ids.append(lun_id)
log.info("Create 12 luns: Success.")

log.info("##### Step18:Map all luns to host groups. #####")
lun = osan.get_lun(s_ip=deploy_ips[0])
for i in lun:
    if i % 2 == 0:
        osan.map_lun(s_ip=deploy_ips[0], lun_ids=i, hg_id=hg_id1[0])
    else:
        osan.map_lun(s_ip=deploy_ips[1], lun_ids=i, hg_id=hg_id2[0])
log.info("Map the 12 luns to the host groups: Success.")
log.info("Congratulations on your successful installation!")

if common2.windows_tag == 0:
    hg_id3 = osan.create_host_group(s_ip=deploy_ips[0], hg_name="hg_3")
    h_id3 = osan.add_host(s_ip=deploy_ips[0], h_name="h_3", hg_id=hg_id3[0])
    osan.add_initiator(s_ip=deploy_ips[0], h_id=h_id2[0], iqn="iqn.windows.com.sugon", alias="sugon.windows.initiator")
    log.info("Add initiator:iqn='iqn.windows.com.sugon' : Success.")
    for i in range(12, 18):
        osan.create_lun(s_ip=deploy_ips[0], lun_name="lun_" + str(i), stor_pool_id=storid_bak[0],
                        acc_zone_id=acc_zone_ids, replica_num=replica, node_parity_num=node_parity,
                        stripe_width=strip_width, lun_type="THIN", total_bytes="99999999999",
                        max_throughput="9000", max_iops="2000", disk_parity_num="0")
    for i in range(13, 19):
        osan.map_lun(s_ip=deploy_ips[0], lun_ids=i, hg_id=hg_id3[0])
log.info("还原测试环境")
env_manage_lun_manage.revert_env()
for c_ip in client_ips:
    target_list = lun_osan.discover_scsi_list(client_ip=c_ip, svip=svip[0])  # 从主机端拿到iqn
    log.info("Get Info:\nSvip list:%s \nTarget list:%s" % (svip[0], target_list))
    for tag in target_list:
        log.info("主机发现存储target：%s,主机 %s 将进行SCSI登录" % (tag, c_ip))
        osan.iscsi_login(client_ip=c_ip, iqn=tag)
read_ahead_status = get_config.get_read_ahead_switch(new_feature_path)
if read_ahead_status == "on":
    log.info("will set lun read ahead:%s" % (set_lun_readhead_ids,))
    for set_id in set_lun_readhead_ids:
        log.info("will set lun id:%s" % (set_id,))
        com_bk_os.set_cache(id=set_id[0], mode=1, s_ip=deploy_ips[0])
    log.info("set lun read ahead finished!!!")
else:
    log.info("pass the set read ahead")

log.info("##### Step19:Check all vips for balance . #####")
rc = osan.check_vip_balance()
# if rc == False:
#     log.info("vips is not balanced in nodes.Please check.")
#     os._exit(1)
