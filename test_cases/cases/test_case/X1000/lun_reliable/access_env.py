#!usr/bin/env python
# -*- coding:utf-8 _*-
"""
@author: Liu he
@file: access_env.py
@time: 2018/10/15
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
deploy_ips = get_config.get_env_ip_info(conf_file)


def init_access_env():
    """
    :Description:初始化access测试环境
    :return:
    """
    print "Reinstall access test environment"
    deploy_conf_file = '/home/deploy/deploy_config.xml'
    if not os.path.exists(conf_file):
        print('File {} does not exist.'.format(conf_file))
        exit(1)

    for ip in deploy_ips:
        cmd = ("ssh root@%s 'reboot'" % (ip,))
        log.info("Begin to shutdown %s." % (ip,))
        res, output = commands.getstatusoutput(cmd)
    time.sleep(100)

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
    # 获取客户端IP
    client_ips = get_config.get_allclient_ip()

    # 获取节点副本数和条带宽度
    config_info = xml.dom.minidom.parse(conf_file)
    replica = config_info.getElementsByTagName('replica')[0].firstChild.nodeValue
    strip_width = config_info.getElementsByTagName('stripwidth')[0].firstChild.nodeValue
    node_parity = int(replica) - 1

    def run_cmd(cmds):
        ress, outputs = commands.getstatusoutput(cmds)
        if ress != 0:
            print outputs
            log.error("Execute ####  %s  ####failed." % (cmds,))
            exit(1)

    def jnl_time():
        current_time = datetime.datetime.now()
        return current_time.strftime('%y-%m-%d %H:%M:%S')

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
    cmd = ("ssh root@%s '/home/parastor/cli/pscli --command=create_storage_pool --name=stor1 "
           "--type=BLOCK --node_pool_ids=1'" % (deploy_ips[0]))
    run_cmd(cmd)
    log.debug("Crteate storage pool: Success.")
    log.info("init access test environment finished")


def get_svip(s_ip=None):
    '''
    date    :   2018-07-06
    Description :   获取SVIP
    param   :   s_ip : iscsi服务端IP;
    return  :   SVIP
    '''
    vip_list = []
    if None == s_ip:
        log.error("Got wrong server_ip: %s" % (s_ip))
        os._exit(1)
    else:
        cmd = ("ssh %s \"pscli --command=get_subnets\"" % (s_ip))
        (res, final) = commands.getstatusoutput(cmd)
        log.info(cmd)
        if res != 0:
            log.error("Get_subnets cmd:%s error info:%s" % (cmd, final))
            os._exit(1)
        else:
            log.info("Get_subnets success.")
        final = json.loads(final)
        svip_list_info = final['result']["subnets"]
        if svip_list_info:
            finals = final['result']['subnets']
            for vip in finals:
                vip_list.append(vip['svip'])
            return vip_list
        else:
            log.info("get svip is none")
            return


def get_vip_address_pools(s_ip=None):
    '''
    date    :   2018-05-15
    Description :   获取VIP
    param   :   s_ip : iscsi服务端IP;n_id : 节点ID
    return  :   VIP
    '''
    vip_list = []
    if None == s_ip:
        log.error("Got wrong server_ip: %s" % (s_ip))
        os._exit(1)
    else:
        cmd = ("ssh %s \" pscli --command=get_vip_address_pools\"" % (s_ip))
        (res, final) = commands.getstatusoutput(cmd)
        log.info(cmd)
        if res != 0:
            log.error("Get_vip_address_pools error.info:%s" % (final))
            os._exit(1)
        else:
            log.info("Get_vip_address_pools success.")
            final = json.loads(final)
            vip_list_info = final["result"]["ip_address_pools"]
            if vip_list_info:
                finals = final['result']['ip_address_pools']
                for vip in finals:
                    vip_list.append(vip['vip_addresses'])
                return vip_list
            else:
                log.info("get vip is none")
                return


def clean_env():
    """
    :description: 先检查sasn是否被激活，如果激活选择（diskable或重装），如果未激活或被disable则进行vip和access检查
    :return:
    """
    lun_map_ids = osan.get_lun_maps(deploy_ips[0])
    if lun_map_ids:
        log.info("The system have lun maping ,will clean up")
        for lun_map_id in lun_map_ids:
            osan.delete_lun_map(s_ip=deploy_ips[0], map_id=lun_map_id)
    else:
        log.info("The system have not lun maping")
    log.info("will check lun ,if found it, clean up")
    lun_ids = osan.get_lun(s_ip=deploy_ips[0])
    if lun_ids:
        log.info("The system have lun, will clean")
        for lun_id in lun_ids:
            osan.delete_lun(s_ip=deploy_ips[0], lun_id=lun_id)
    else:
        log.info("The system have not lun ")
    ini_ids = osan.get_initiators(s_ip=deploy_ips[0])
    if ini_ids:
        log.info("The system have initiator: %s, will clean" % (ini_ids))
        for ini_id in ini_ids:
            osan.remove_initiator(s_ip=deploy_ips[0], ini_id=ini_id)
    host_ids = osan.get_hosts(s_ip=deploy_ips[0])
    if host_ids:
        log.info("The system have host: %s, will clean" % (host_ids))
        for host_id in host_ids:
            env_manage.osan.remove_hosts(deploy_ips[0], host_id)
    hostgroup_ids = osan.get_host_groups(s_ip=deploy_ips[0])
    if hostgroup_ids:
        log.info("The system have host group: %s, will clean" % (hostgroup_ids))
        for hostgroup_id in hostgroup_ids:
            env_manage.osan.delete_host_groups(deploy_ips[0], hostgroup_id)
    log.info("check san status")
    san_status = env_manage.com_lh.get_san_state(deploy_ips[0])
    if san_status is None:
        log.info("check san status is inactive")
    elif True in san_status:
        log.info("check san status is True. will reinstall")
        # log.info("checking host and host group and initiator, if found it, will clean")
        # env_manage.check_san_enable_env()
        # env_manage.disable_san()
        init_access_env()
        return
    else:
        log.info("check san status is unnormal.status: %s" % (san_status))
    log.info("check svip and vip ,if found it, will clean")
    vip_ips = get_vip_address_pools(deploy_ips[0])
    if vip_ips:
        log.info("check have vip:%s,will clean" % (vip_ips))
        env_manage.clean_vip_address_pool()
        svip_ips = get_svip(deploy_ips[0])
        if svip_ips:
            log.info("check have svip:%s,will clean" % (svip_ips))
            env_manage.clean_subnet()
    else:
        log.info("check have not vip,will pass")
    log.info("check access, if get it, will clean")
    access_ids = env_manage.com2_osan.get_access_zone_id(deploy_ips[0])
    if access_ids:
        env_manage.clean_access_zone(deploy_ips[0])
    else:
        log.info("The envireonment have not access")


def check_env():
    log.info("check and clean environment of test ")
    clean_env()
    log.info("check device :1.Chenck Node Network device")
    env_manage.check_eth()  # 检查存储端网卡
    log.info("2.Check Node Disk Device")
    env_manage.check_disk()  # 检查各个节点硬盘，不设置预期值将不进行对比


def main():
    init_access_env()


if __name__ == "__main__":
    setup()
    main()
