#!usr/bin/env python  
# -*- coding:utf-8 -*-  
""" 
:author: Liu he
:Description:
@file: install_man.py 
@time: 2018/11/21 
"""
import io
import datetime
import json
import sys
import time
import xml
from optparse import OptionParser
import os
import commands
import re
import utils_path
import Lun_managerTest
import env_manage
import common
import log
import get_config
import common2
import ReliableTest
import breakdown


def setup():
    file_name = os.path.basename(__file__)
    file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
    log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
    log.init(log_file_path, True)  # 初始化日志文件


mkpkg_flag = 0
parser = OptionParser()
parser.add_option("--mkpkg", "-m", action="store_true", dest="mkpkg",
                  help="When you want to refresh the code and mkpkg, set this parameter to -m or --mkpkg. default: "
                       "%default, do not refresh code and mkpkg")
options, args = parser.parse_args()
if options.mkpkg is True:
    mkpkg_flag = 1
osan = common2.oSan()
break_down = breakdown.disk()
# 读取配置文件
conf_file = get_config.CONFIG_FILE  # 配置文件路径
# 获取路径：/home/StorTest/src_code/ofs/code/test/mgr/it/script/san.py/scripts
current_path_1 = os.path.dirname(os.path.abspath(__file__))
# 获取路径：/home/StorTest/src_code/ofs/code/test/mgr/it/script/san.py
current_path = os.path.dirname("/home/StorTest/")
# print current_path
# 获取路径：/home/StorTest/src_code/ofs/code/test/mgr/it/script/san.py/conf
# conf_path = os.path.join(current_path, 'conf')
# print conf_path
# conf_file = conf_path + '/' + 'x1000_test_config.xml'
# print conf_file
# 获取IP列表
deploy_ips = get_config.get_env_ip_info(conf_file)


def storage_pool():
    node_ids_list = osan.get_nodes(deploy_ips[0])
    node_ids = ",".join('%s' % id for id in node_ids_list)
    data_unuse_disks = []
    for i in node_ids_list:
        j = break_down.get_assign_data_disk_id(s_ip=deploy_ips[0], node_id=i)
        data_unuse_disks.append(j)
    lists = [[] for i in range(3)]
    for m in range(3):
        new_list = []
        for list in data_unuse_disks:
            new_list.append(list[m])
        lists[m].append(new_list)
    return lists


def run_cmd(cmds):
    ress, outputs = commands.getstatusoutput(cmds)
    if ress != 0:
        print outputs
        log.error("Execute ####  %s  ####failed." % (cmds,))
        exit(1)


def jnl_time():
    current_time = datetime.datetime.now()
    return current_time.strftime('%y-%m-%d %H:%M:%S')


def init_xstor():
    """
    :Description:初始化access测试环境
    :return:
    """
    print "Reinstall access test environment"
    deploy_conf_file = '/home/deploy/deploy_config_sample.xml'
    if not os.path.exists(conf_file):
        print('File {} does not exist.'.format(conf_file))
        exit(1)

    for ip in deploy_ips:
        cmd = ("ssh root@%s 'reboot'" % (ip,))
        log.info("Begin to shutdown %s." % (ip,))
        res, output = commands.getstatusoutput(cmd)
    time.sleep(100)
    for ip in deploy_ips:
        while False is ReliableTest.check_ping(ip):
            time.sleep(5)
    time.sleep(200)
    # 获取客户端IP
    client_ips = get_config.get_allclient_ip()

    # 获取节点副本数和条带宽度
    config_info = xml.dom.minidom.parse(conf_file)
    replica = config_info.getElementsByTagName('replica')[0].firstChild.nodeValue
    strip_width = config_info.getElementsByTagName('stripwidth')[0].firstChild.nodeValue
    node_parity = int(replica) - 1
    # ####################################################Step 1##############
    # 检查环境，检查部署用的配置文件是否存在
    cmd = ("ssh root@%s '[ -e %s ]'" % (deploy_ips[0], deploy_conf_file))
    res, output = commands.getstatusoutput(cmd)
    if res != 0:
        log.error("Ai, I don't know what to say, I beg you to check if %s "
                  "is exists on %s" % (deploy_ips[0], deploy_conf_file))
        exit(1)
    log.debug("Check if the test cluster has /home/deploy and %s : Success." % (deploy_conf_file,))
    # 检查主机端是否有/home/vdbench目录
    for ip in client_ips:
        cmd = ("ssh root@%s '[ -e /home/vdbench ]'" % (ip,))
        res, output = commands.getstatusoutput(cmd)
        if res != 0:
            log.error("Ai, I don't know what to say, I beg you to check if /home/vdbench is exists on %s" % (ip,))
            exit(1)
    log.debug("Check if the clients has vdbench: Success.")
    # 卸载所有lun
    for ip in client_ips:
        # cmd = ("ssh root@%s 'iscsiadm -m node --logoutall=all'" % (ip))
        cmd = ("ssh root@%s 'iscsiadm -m node -u'" % (ip,))
        res, output = commands.getstatusoutput(cmd)
    # print output
    log.debug("Umount luns on clients: Success.")
    # ####################################################Step 2##############
    # 获取quickmk.sh路径
    src_path = current_path + "/src_code/ofs/"
    if mkpkg_flag == 1:
        git_pull_cmd = "cd %s;git pull" % (src_path,)
        run_cmd(git_pull_cmd)
        log.debug("Refresh code: Success.")
        quick_mk_cmd = "cd %s;sh quickmk.sh rebuild mkpkg" % (src_path,)
        run_cmd(quick_mk_cmd)
        log.debug("Make package: Success.")
    # 新包路径
    new_pkg_path = src_path + '/code/bin/'
    # 获取安装包的名字
    new_pkg_tar = None
    lists = os.listdir(new_pkg_path)
    for i in lists:
        if 'parastor-3.0.0-centos' in i:
            new_pkg_tar = i
    if new_pkg_tar is None:
        log.error("Sorry,I can not find the new package.")
        exit(1)
    cmd = ("ssh root@%s 'rm -rf /home/deploy/parastor*'" % (deploy_ips[0]))
    commands.getstatusoutput(cmd)
    log.debug("Delete the old package on  %s:/home/deploy: Success." % (deploy_ips[0]))
    cmd = ("scp %s/parastor-3.0.0-centos* root@%s:/home/deploy/" % (new_pkg_path, deploy_ips[0]))
    run_cmd(cmd)
    log.debug("Copy the new package to %s: Success." % (deploy_ips[0]))
    # ####################################################Step 3##############
    log.debug("################# Begin install #################")
    log.info("Unzip the new package on %s:/home/deploy" % (deploy_ips[0]))
    cmd = ("ssh root@%s 'cd /home/deploy;tar -xvf %s'" % (deploy_ips[0], new_pkg_tar))
    run_cmd(cmd)
    cmd = ("ssh root@%s \"sed -r -i 's/\/home\/deploy\/.*<\/package_path>/"
           "\/home\/deploy\/%s<\/package_path>/g' %s\"" % (deploy_ips[0], new_pkg_tar, deploy_conf_file))
    run_cmd(cmd)
    log.debug("Begin to clean the cluster.")
    new_pkg_name = new_pkg_tar.split('.tar')[0]
    clean_cmd = ("ssh root@%s '/home/deploy/%s/server/tools/deployment/clean.py --deploy_config=%s > /dev/null'" % (
        deploy_ips[0], new_pkg_name, deploy_conf_file))
    res, output = commands.getstatusoutput(clean_cmd)
    log.info(output)
    log.debug("Check if the tgt module is clean.")
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
            cmd = ("ssh root@%s 'reboot'" % (ip,))
            log.info("Begin to shutdown %s." % (ip,))
            res, output = commands.getstatusoutput(cmd)
        time.sleep(100)
        for ip in deploy_ips:
            while False is ReliableTest.check_ping(ip):
                time.sleep(5)
        time.sleep(200)
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
    log.info("Install script check the install environment.")
    cmd = ("ssh root@%s '/home/deploy/%s/server/tools/env_check/env_check.py "
           "--ip=%s --config=%s'" % (deploy_ips[0], new_pkg_name, deploy_ips[0], deploy_conf_file))
    commands.getstatusoutput(cmd)
    cmd = ("ssh root@%s '/home/deploy/%s/server/tools/deployment/deploy.py --deploy_config=%s --type=BLOCK'" % (
        deploy_ips[0], new_pkg_name, deploy_conf_file))
    run_cmd(cmd)
    log.debug("Execute deploy.py: Success.")
    cmd = ("ssh root@%s '/home/parastor/cli/pscli --command=update_param --section=MGR "
           "--name=min_meta_replica --current=%s'" % (deploy_ips[0], str(replica)))
    run_cmd(cmd)
    log.debug("Get disk ids and change the disk speed.")
    share_disk_ids = re.sub(r'\[|\]| ', '', str(break_down.get_all_shared_disk_id()))
    data_disk_ids = re.sub(r'\[|\]| ', '', str(break_down.get_all_data_disk_id()))
    cmd = (
        "ssh root@%s '/home/parastor/cli/pscli --command=change_disk_speed_level --disk_ids=%s --speed_level=HIGH'" % (
            deploy_ips[0], share_disk_ids))
    run_cmd(cmd)
    cmd = (
        "ssh root@%s '/home/parastor/cli/pscli --command=change_disk_speed_level --disk_ids=%s --speed_level=MID'" % (
            deploy_ips[0], data_disk_ids))
    run_cmd(cmd)
    log.debug("Chage the min meata replica number to 3: Success.")
    node_ids = []
    for i in range(1, len(deploy_ips) + 1):
        node_ids.append(i)
    node_ids = re.sub(r' |\[|\]', '', str(node_ids))
    cmd = ("ssh root@%s '/home/parastor/cli/pscli --command=create_node_pool --node_ids=%s "
           "--replica_num=%s --stripe_width=%s --disk_parity_num=0 --node_parity_num=%s --name=firstpool'" % (
               deploy_ips[0], node_ids, str(replica), str(strip_width), str(node_parity)))
    run_cmd(cmd)
    log.debug("Create node_pool，replica：%s, stripwidth：%s: Success." % (str(replica), str(strip_width)))
    cmd = ("ssh root@%s '/home/parastor/cli/pscli --command=startup'" % (deploy_ips[0]))
    run_cmd(cmd)
    log.debug("Start service: Success.")
    stor_pools = storage_pool()
    for i in range(3):
        log.info("will create storage :%s" % (i))
        pool_id = ",".join('%s' % id for id in stor_pools[i][0])
        cmd = (
            "ssh root@%s '/home/parastor/cli/pscli --command=create_storage_pool --name=stor1 --type=BLOCK --node_pool_ids=1 --disk_ids=%s '" % (
                deploy_ips[0], pool_id))
    run_cmd(cmd)
    log.debug("Crteate storage pool: Success.")
    # ####################################################配置vip#####################################################
    svip = get_config.get_svip(conf_file)
    log.debug("svip is :" + str(svip))
    vip = get_config.get_vip(conf_file)
    log.debug("vips:" + str(vip))
    storid = osan.get_storage_id(s_ip=deploy_ips[0])
    nodeid = osan.get_nodes(s_ip=deploy_ips[0])
    acc_zone_ids = osan.create_access_zone(s_ip=deploy_ips[0], node_id=str(nodeid).strip("[|]| ").replace(" ", ""),
                                           name="acc_0")
    log.debug("Create access zone: Success.")
    osan.create_subnet(s_ip=deploy_ips[0], sv_ip=svip[0], access_zone_id=acc_zone_ids, name="subnet1")
    log.debug("Create subnet: Success.")
    sub_id = osan.get_subnet_id(s_ip=deploy_ips[0])
    osan.add_vip_address_pool(s_ip=deploy_ips[0], subnet_id=sub_id[0], domain_name="vip1.com", vip=vip[0])
    log.debug("Add vip_address_pool: Success.")
    # for sip in deploy_ips:
    #     cmd = ("ssh root@%s \"/home/parastor/tools/otraced -d\"" % (sip, ))
    #     run_cmd(cmd)
    #     log.debug("Open otrace on %s : Success." % (sip, ))
    osan.enable_san(s_ip=deploy_ips[0], access_zone_id=acc_zone_ids)
    log.debug("Enable san: Success.")


def main():
    setup()
    init_xstor()


if __name__ == "__main__":
    main()
