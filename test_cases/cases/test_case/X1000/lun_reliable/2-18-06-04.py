# -*- coding:utf-8 -*-
# Author:Liu he
# Date  :2018-8-9

'''
测试内容:SVIP和VIP在同一节点上能被扫描LUN
测试步骤：
1、创建节点池和存储池
2、创建访问分区
3、启动i该访问分区SCSI
4、创建该访问区对应的子网，VIP地址池
5、创建对应该访问区的LUN和LUN映射
6、主机登录LUN，并下发大小快混合的读写业务
7、在业务继续，停止该访问分区iSCSI过程中，oPmgr主所在节点掉电
8、内部数据一致
检查项：
7、访问区iSCSI服务停止成功，业务中断
8、内部数据一致

'''

# testlink case: 1000-34196
import os
import time
import random
import xml
import commands
import threading
import utils_path
import log
import common
import ReliableTest
import prepare_x1000
import env_manage
import access_env
import get_config
import decorator_func
 

'''初始化'''
file_name = os.path.basename(__file__)
file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
current_path = os.path.dirname(os.path.abspath(__file__))


def setup():
    '''获取业务节点IP和非业务节点IP'''
    global node_ip1
    global node_ip2
    global client_ip1
    node_ip1 = env_manage.deploy_ips[0]  # 业务节点IP
    node_ip2 = env_manage.deploy_ips[1]  # 非业务节点IP
    client_ip1 = env_manage.client_ips[0]


def pro_test():
    orole_master_ip = env_manage.com_lh.get_master_oRole(s_ip=node_ip1)
    env_manage.com_lh.kill_thread(s_ip=orole_master_ip, p_name="oRole", t_name="pmgr")
    log.info("kill opmgr finished")
    return


def create_iscsi_login(ips, cli_ips, svip):
    env_manage.osan.discover_scsi_list(client_ip=cli_ips, svip=svip)  # 进行一下discovery，真正的tag从xstor中拿
    target_list = env_manage.osan.get_map_target(ips)
    log.info("Get Info:\nSvip list:%s \nTarget list:%s" % (svip, target_list))
    for tag in target_list:
        log.info("主机发现存储target：%s,主机 %s 将进行SCSI登录" % (tag, cli_ips))
        env_manage.osan.iscsi_login(client_ip=cli_ips, iqn=tag)


def run_vdb(client_ip, vdb_xml, jn_jro=None, output=None, time=1200, execute="Y", whether_change_xml="Y",
            need_judge=None):
    """
    执行vdbench
    :param client_ip:主机端IP
    :param vdb_xml:
    :param jn_jro:
    :param output:
    :param time:   执行时间
    :param execute: 是否执行vdbench，N 为不执行，非N就会执行
    :param whether_change_xml：是否执行change_xml，默认执行
    :return:
    """
    if execute == "N":
        log.info("Will not run  vdbench 。。。")
    else:
        if vdb_xml == None:
            log.error("Please input vdb xml.")
            os._exit(1)
        vdb_xml1 = "/home/vdbench/vdb_xml"
        vdb_path = get_config.get_vdbench_path()  # vdbench工具所在路径
        cmd = ("ssh %s 'mkdir -p /root/output/;mkdir -p /root/vdbench/journal/%s'" % (client_ip, str(output)))
        log.info(cmd)
        commands.getstatusoutput(cmd)
        if time != None:
            cmd1 = ("ssh %s '%s/vdbench -f %s -jn -e %s -o /root/output/%s_jn'" % (
                client_ip, vdb_path, vdb_xml1, str(time), str(output)))
            cmd2 = ("ssh %s '%s/vdbench -f %s -jro -e %s -o /root/output/%s_jro'" % (
                client_ip, vdb_path, vdb_xml1, str(time), str(output)))
        else:
            cmd1 = (
            "ssh %s '%s/vdbench -f %s -jn  -o /root/output/%s_jn'" % (client_ip, vdb_path, vdb_xml1, str(output)))
            cmd2 = (
                "ssh %s '%s/vdbench -f %s -jro -o /root/output/%s_jro'" % (client_ip, vdb_path, vdb_xml1, str(output)))
        if None == jn_jro or jn_jro == "no":
            env_manage.com2_osan.change_xml(vdb_xml=vdb_xml, whether_change=whether_change_xml)
            cmd = ("scp %s root@%s:/home/vdbench/vdb_xml" % (vdb_xml, client_ip,))
            log.info(cmd)
            res, final = commands.getstatusoutput(cmd)
            if res != 0:
                print final
                os._exit(1)
            cmd = ("ssh %s '%s/vdbench -f %s -e %s -o /root/output/%s_nor'" % (
                client_ip, vdb_path, vdb_xml1, str(time), str(output)))
            log.info(cmd)
            res, out = commands.getstatusoutput(cmd)
            if res != 0:
                log.error("Error! Run vdbench without data check error.")
            else:
                pass
        else:
            ch_cmd = ("sed -r -i 's/,offset=[0-9]+//g' %s" % (vdb_xml))
            commands.getstatusoutput(ch_cmd)
            ch_cmd = ("sed -r -i 's/,align=[0-9]+//g' %s" % (vdb_xml))
            commands.getstatusoutput(ch_cmd)
            env_manage.com2_osan.change_xml(jn_on="yes", vdb_xml=vdb_xml, whether_change=whether_change_xml)
            cmd = ("scp %s root@%s:/home/vdbench/vdb_xml" % (vdb_xml, client_ip,))
            log.info(cmd)
            res, final = commands.getstatusoutput(cmd)
            if res != 0:
                print final
                os._exit(1)
            res, out = commands.getstatusoutput(cmd1)
            log.info(cmd1)
            if res != 0:
                log.error(
                    "Error! Run vdbench with journal verify error.Vdbench log path is /root/output/%s." % (str(output)))
                os._exit(1)
            else:
                log.info("Vdbench log path is /root/output.")
                log.info(cmd2)
                res, out = commands.getstatusoutput(cmd2)
                if res != 0:
                    log.error("Error! Vdbench check data error,journal path is /root/vdbench/journal.")
                    os._exit(1)
                else:
                    pass


def vdb_test():
    lun_name = env_manage.osan.ls_scsi_dev(client_ip=client_ip1)
    if len(lun_name) > 10:
        lun_name = lun_name[:10]
    vdb_file = env_manage.com2_osan.gen_vdb_xml(lun=lun_name, xfersize="4k", rdpct="50")
    log.info("vdbench 进行读写业务")
    run_vdb(client_ip=client_ip1, vdb_xml=vdb_file, output=node_ip1, time=600)


def run_vdb_case(az_id1):
    threads = []
    threads.append(threading.Thread(target=vdb_test))
    threads.append(threading.Thread(target=os_down_osan, args=(az_id1,)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def os_down_osan(access_id):
    time.sleep(30)
    log.info("will disable san and kill process ")
    threads = []
    threads.append(threading.Thread(target=env_manage.osan.disable_san, args=(node_ip1, access_id)))
    threads.append(threading.Thread(target=pro_test))
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    log.info("disable san and kill process finished")


def case():
    svip1 = env_manage.svip[0]
    vip1 = env_manage.vips[0]
    log.info("step:1.创建访问区")
    az_id1 = env_manage.create_access(ips=node_ip1, node_ids="1,2,3", access_name="accesszone1")
    sub_id1 = env_manage.create_subnet(s_ip=node_ip1, svip=svip1, a_z_id=az_id1, access_name="sub1")
    env_manage.create_vip(s_ip=node_ip1, subnet_id=sub_id1, vip_name="vip1.com", vip_pool=vip1)
    log.info("step:2.启动scsi")
    env_manage.enable_san()
    env_manage.create_host_group()
    env_manage.create_host()
    env_manage.create_add_initiator()
    env_manage.create_lun(ips=node_ip1, name="LUN1", access_id=az_id1)
    env_manage.create_lun_map(node_ip1)
    create_iscsi_login(ips=node_ip1, cli_ips=client_ip1, svip=svip1)
    log.info("step:3.停止scsi过程中，主oPmgr线程异常")
    rc = run_vdb_case(az_id1)
    if rc == 0:
        log.error("The vdbench not stop")
        os._exit(1)
    log.info("检查san 协议是否开启成功")
    san_status = env_manage.com_lh.get_san_state(node_ip1)
    if all(san_status) is True:
        log.info("check all san is active, all san status:%s" % (san_status))
        os._exit(1)
    else:
        log.info("check san status is :%s" % (san_status))
    log.info("step:5.检查节点运行状态，检查服务恢复情况。")
    env_manage.com_lh.get_os_status(node_ip2)
    # env_manage.com_lh.multi_check_part_lun_uniform_by_ip()  # 比较数据一致性


def main():
    access_env.check_env()
    setup()
    case()
    log.info("step:6.检查清理测试环境")
    access_env.check_env()
    log.info("The case finished!!!")


if __name__ == '__main__':
    env_manage.rel_check_before_run(file_name, free_jnl_num=0, node_num=3)
    common.case_main(main)
