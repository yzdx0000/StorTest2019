#!/usr/bin/python
# -*- encoding=utf8 -*-
import os
import xml
import time
import commands
import threading
import ReliableTest

import log
import common
import common2
import breakdown
import get_config
import Lun_managerTest


config_path = get_config.CONFIG_FILE
deploy_ips = get_config.get_env_ip_info(config_path)
osan = common2.oSan()
test_log_path = get_config.get_testlog_path()
lun_osan = Lun_managerTest.oSan()
disk = breakdown.disk()

def get_err_log_ip():
    '''
    :Author:diws
    :Date:20180829
    :return: node ip 错误日志备份目标节点IP
    '''
    err_log_ip_info = xml.dom.minidom.parse(config_path)
    ip_info = err_log_ip_info.getElementsByTagName('err_log_ip')[0].firstChild.nodeValue
    return ip_info


def get_err_log_path():
    '''
    :Author:diws
    :Date:20180829
    :return: log path 错误日志备份目标节点的路径
    '''
    err_log_path_info = xml.dom.minidom.parse(config_path)
    path_info = err_log_path_info.getElementsByTagName('err_log_path')[0].firstChild.nodeValue
    return path_info

def get_mount_log_path_dic():
    ip_path_dic = {}
    root = xml.dom.minidom.parse(config_path)
    dom = root.documentElement
    for info in dom.getElementsByTagName('mount_log_path'):
        node_ip = info.getAttribute("ip")
        mount_path = info.firstChild.nodeValue
        ip_path_dic[node_ip] = mount_path
    return ip_path_dic

def collect_parastor(s_ip=None, dst=None):
    '''
    :Author:diws
    :Date:20180829
    :param s_ip:日志所在节点IP
    :return: None
    '''
    if s_ip is None or dst is None:
        print("Please input correct parameters.")
        os._exit(1)
    err_ip = get_err_log_ip()
    err_path = get_err_log_path()
    # 备份日志前，检查目标节点是否能正常登陆
    while False is ReliableTest.check_ping(s_ip):
        time.sleep(5)
    # 在日志目标节点，检查备份目录是否存在，不存在则创建
    dst_log_path = err_path + "/" + str(dst) + "/" + '/' + str(s_ip) + '_ser'
    cmd = ("ssh root@%s '[ -e %s]'" % (err_ip, dst_log_path))
    res, output = commands.getstatusoutput(cmd)
    if res != 0:
        cmd = ("ssh root@%s 'mkdir -p %s'" % (err_ip, dst_log_path))
        commands.getstatusoutput(cmd)
    zk_log = dst_log_path + '/zk_log'
    pro_log = dst_log_path + '/pro_log'
    bin_log = dst_log_path + '/bin'
    message_log = dst_log_path + '/message_log'
    pscli_log = dst_log_path + '/pscli_log'
    nwatch_log = dst_log_path + '/nwath_log'
    other_log = dst_log_path + '/other_log'
    cmd = (
            "ssh root@%s 'mkdir -p  %s %s %s %s %s %s %s %s/tmp*log %s/dev/shm/parastor %s/var/log'" % (
             err_ip, zk_log, bin_log, pro_log, message_log, pscli_log, nwatch_log, other_log, other_log, other_log,
             other_log))
    print cmd
    commands.getstatusoutput(cmd)
    # 拷贝/home/parastor/log目录下所有日志，拷贝完成后，将所有文件truncate到0
    cmd = ("ssh root@%s 'cd /home/parastor/log/;scp -r * %s:%s'" % (s_ip, err_ip, pro_log))
    print cmd
    commands.getstatusoutput(cmd)
    log_list = ["dbginfo_stub", "errinfo.sh", "gdb.dump", "gdb.dump.opmgr", "msginfo.sh", "potrc"]
    for i in log_list:
        cmd = ("ssh root@%s 'scp /home/parastor/tools/%s %s:%s'" % (s_ip, i, err_ip, other_log))
        commands.getstatusoutput(cmd)

    cmd = ("ssh root@%s 'scp -r /tmp/*log %s:%s/tmp*log'" % (s_ip, err_ip, other_log))
    print cmd
    commands.getstatusoutput(cmd)
    cmd = ("ssh root@%s 'scp -r /var/log/parastor*  %s:%s/var/log'" % (s_ip, err_ip, other_log))
    print cmd
    commands.getstatusoutput(cmd)

    cmd = ("ssh root@%s 'scp -r /var/log/imp_parastor.log_*  %s:%s/var/log'" % (s_ip, err_ip, other_log))
    print cmd
    commands.getstatusoutput(cmd)

    cmd = ("ssh root@%s 'scp -r /dev/shm/parastor* %s:%s/dev/shm/parastor'" % (s_ip, err_ip, other_log))
    print cmd
    commands.getstatusoutput(cmd)

    cmd = ("ssh root@%s 'ps -efH ' | ssh %s 'cat - > %s/ps_ef.log'" % (s_ip, err_ip, other_log))
    print cmd
    commands.getstatusoutput(cmd)
    cmd = (
            "ssh root@%s 'ps -ef|grep -i ojmgs|grep -v grep|awk '{print $2}' |xargs jstack -l' | ssh %s 'cat - > %s/ojmgs_jstack.log'" % (s_ip, err_ip, other_log))
    print cmd
    commands.getstatusoutput(cmd)

    cmd = ("timeout 20 ssh root@%s 'pstack `pidof oPara`' | ssh %s 'cat - > %s/opara.pstack'" % (s_ip, err_ip, pro_log))
    print cmd
    commands.getstatusoutput(cmd)
    cmd = ("ssh root@%s 'scp /home/parastor/bin/o* %s:%s'" % (s_ip, err_ip, bin_log))
    # cmd = ("ssh root@%s 'cd /home/parastor/log/;rm -rf core.*;find ./ -type f | xargs truncate -s 0'" % (s_ip, ))
    print cmd
    commands.getstatusoutput(cmd)
    cmd = ("ssh root@%s 'cd /;scp -r core* %s:%s'" % (s_ip, err_ip, pro_log))
    print cmd
    commands.getstatusoutput(cmd)
    cmd = ("ssh root@%s 'cd /;rm -rf core*'" % (s_ip,))
    print cmd
    commands.getstatusoutput(cmd)
    # 拷贝/root/zk/zookeeper.log和/tmp/mgcd_zookeeper.log
    cmd = ("ssh %s \"ls /root/zk/bin/zkCli.sh\"" % (s_ip,))
    rc, output = commands.getstatusoutput(cmd)
    if rc != 0:
        zk_dir = "/home/parastor/conf/zk"
    else:
        zk_dir = "/root/zk"
    cmd = ("ssh root@%s 'scp -r %s/ %s:%s'" % (s_ip, zk_dir, err_ip, zk_log))
    print cmd
    commands.getstatusoutput(cmd)
    cmd = ("ssh root@%s 'scp /tmp/mgcd_zookeeper.log %s:%s'" % (s_ip, err_ip, zk_log))
    print cmd
    commands.getstatusoutput(cmd)
    # 拷贝intiators/luns/lun_maps信息
    cmd = ("timeout 20 ssh root@%s 'pscli --command=get_initiators ' | ssh %s 'cat - > %s/initiators'" % (
        s_ip, err_ip, pscli_log))
    print cmd
    commands.getstatusoutput(cmd)
    cmd = ("timeout 20 ssh root@%s 'pscli   --command=get_perf_data ' | ssh %s 'cat - > %s/get_perf_data'" % (
        s_ip, err_ip, pscli_log))
    print cmd
    commands.getstatusoutput(cmd)
    cmd = ("timeout 20 ssh root@%s 'pscli   --command=get_all_jobs ' | ssh %s 'cat - > %s/get_all_jobs'" % (
        s_ip, err_ip, pscli_log))
    print cmd
    commands.getstatusoutput(cmd)
    cmd = ("timeout 20 ssh root@%s  'pscli --command=get_storage_pools ' | ssh %s 'cat - > %s/get_storage_pools'" % (
        s_ip, err_ip, pscli_log))
    print cmd
    commands.getstatusoutput(cmd)

    cmd = ("timeout 20 ssh root@%s 'pscli --command=get_luns ' | ssh %s 'cat - > %s/luns'" % (s_ip, err_ip, pscli_log))
    print cmd
    commands.getstatusoutput(cmd)
    cmd = (
            "timeout 20 ssh root@%s 'pscli --command=get_targets ' | ssh %s 'cat - > %s/targets'" % (s_ip, err_ip, pscli_log))
    print cmd
    commands.getstatusoutput(cmd)
    cmd = (
            "timeout 20 ssh root@%s 'pscli --command=get_lun_maps ' | ssh %s 'cat - > %s/lunmaps'" % (s_ip, err_ip, pscli_log))
    print cmd
    commands.getstatusoutput(cmd)
    cmd = ("timeout 20 ssh root@%s 'pscli --command=get_node_stat ' | ssh %s 'cat - > %s/node_stat'" % (s_ip, err_ip, pscli_log))
    print cmd
    commands.getstatusoutput(cmd)
    # 拷贝/var/log/messages
    cmd = ("ssh root@%s 'scp /var/log/message* %s:%s'" % (s_ip, err_ip, message_log))
    print cmd
    commands.getstatusoutput(cmd)
    cmd = ("ssh root@%s 'scp /tmp/part_disk* %s:%s'" % (s_ip, err_ip, message_log))
    print cmd
    commands.getstatusoutput(cmd)
    # 备份nWatch输出
    # 改xstor_io_dbg.sh，1. 注释掉145行之后拷贝/home/parastor/log的内容；2. 注释掉检查core存在则exit的行
    cmd = ("ssh root@%s \"sed -i '164,$ s/^/#/' /home/parastor/tools/xstor_io_dbg.sh\"" % (s_ip,))
    print cmd
    commands.getstatusoutput(cmd)
    cmd = ("ssh root@%s \"sed -i '/exit/s/^/#/g' /home/parastor/tools/xstor_io_dbg.sh\"" % (s_ip,))
    print cmd
    commands.getstatusoutput(cmd)
    # 注释掉fsinfo检查的行——打开会导致oRole进程core
    cmd = ("ssh root@%s \"sed -i '/fsinfo/s/^/#/g' /home/parastor/tools/xstor_io_dbg.sh\"" % (s_ip,))
    print cmd
    commands.getstatusoutput(cmd)
    # 根据节点IP获取该节点id
    node_id = disk.get_node_id_by_ip(n_ip=s_ip)
    # 执行nWatch收集工具，将其保存到该节点/home/xlog目录下
    cmd = ("timeout 600 ssh root@%s '/home/parastor/tools/xstor_io_dbg.sh xlog %s'" % (s_ip, str(node_id)))
    print cmd
    commands.getstatusoutput(cmd)
    
    node_nums = len(deploy_ips)
    for num in range(node_nums):
        cmd = ("ssh root@%s '/home/parastor/tools/nWatch -t oPara -i %s -a \"vmgrid=1 fout=0 fpath=/a/b/c\" -c oPara#vmgr_vset_dump >> /home/xlog/oPara.vmgr_vset_dump'"
               % (s_ip, str(num + 1)))
        os.system(cmd)
        cmd = ("ssh root@%s '/home/parastor/tools/nWatch -t oPara -i %s -a \"vmgrid=1\" -c oPara#vmgr_flattenrecord_dump >> /home/xlog/oPara.vmgr_flattenrecord_dump'"
               % (s_ip, str(num + 1)))
        os.system(cmd)
        cmd = ("ssh root@%s '/home/parastor/tools/nWatch -t oPara -i %s -a \"vmgrid=1\" -c oPara#vmgr_flattennr_dump >> /home/xlog/oPara.vmgr_flattennr_dump'"
               % (s_ip, str(num + 1)))
        os.system(cmd)
        cmd = ("ssh root@%s '/home/parastor/tools/nWatch -t oPara -i %s -a \"vmgrid=1\" -c oPara#vmgr_topo_dump >> /home/xlog/oPara.vmgr_topo_dump'"
               % (s_ip, str(num + 1)))
        os.system(cmd)

    # 收集完成后，将xstor_io_dbg.sh工具注释去掉
    cmd = ("ssh root@%s \"sed -i '164,$ s/^#//' /home/parastor/tools/xstor_io_dbg.sh\"" % (s_ip,))
    print cmd
    commands.getstatusoutput(cmd)
    # 将收集的信息备份到日志目标节点，并删除该节点收集的信息
    cmd = ("ssh root@%s 'scp -r /home/xlog %s:%s'" % (s_ip, err_ip, nwatch_log))
    print cmd
    commands.getstatusoutput(cmd)
    cmd = ("ssh root@%s 'rm -rf /home/xlog'" % (s_ip,))
    print cmd
    commands.getstatusoutput(cmd)
    # 收集lioc日志
    cmd = ("timeout 40 ssh root@%s '/home/parastor/tools/dlm_mml -t 5208 -p -s 1 -l 1' | ssh %s 'cat - > %s/dlm'"
           % (s_ip, err_ip, nwatch_log))
    print cmd
    commands.getstatusoutput(cmd)
    cmd = ("timeout 40 ssh root@%s '/home/parastor/tools/nWatch -t oRole -i %s -c oPmgr#pmgr_lunset_resv_dump' | "
           "ssh %s 'cat - > %s/pmgr_lunset_resv_dump'"
           % (s_ip, str(node_id), err_ip, nwatch_log))
    print cmd
    commands.getstatusoutput(cmd)
    cmd = ("timeout 40 ssh root@%s '/home/parastor/tools/nWatch -t MGCD -i %s -c NAL#mgcd_service_dump' | "
           "ssh %s 'cat - > %s/mgcd_service_dump'"
           % (s_ip, str(node_id), err_ip, nwatch_log))
    print cmd
    commands.getstatusoutput(cmd)


def collect_cli(s_ip=None, dst=None, ):
    '''
    :Author:diws
    :Date:20180829
    :param s_ip: 日志所在节点IP
    :param dst: 目标节点日志备份目录
    :return:
    '''
    if s_ip is None or dst is None:
        print("Please input correct parameters.")
        os._exit(1)
    err_ip = get_err_log_ip()
    err_path = get_err_log_path()
    # 备份日志前，检查目标节点是否能正常登陆
    while False is ReliableTest.check_ping(s_ip):
        time.sleep(5)
    dst_log_path = err_path + "/" + str(dst) + '/' + str(s_ip) + '_host'
    lun_log = dst_log_path + '/' + 'luns'
    message_log = dst_log_path + '/' + 'message'
    cmd = ("ssh root@%s '[ -e %s]'" % (err_ip, dst_log_path))
    res, output = commands.getstatusoutput(cmd)
    if res != 0:
        cmd = ("ssh root@%s 'mkdir -p %s %s %s'" % (err_ip, dst_log_path, lun_log, message_log))
        commands.getstatusoutput(cmd)
    # 拷贝/var/log/messages*
    cmd = ("ssh root@%s 'scp /var/log/message* %s:%s'" % (s_ip, err_ip, message_log))
    print cmd
    commands.getstatusoutput(cmd)
    # 拷贝lsscsi信息
    print cmd
    cmd = ("ssh root@%s 'lsscsi ' | ssh %s 'cat - > %s/lsscsi'" % (s_ip, err_ip, dst_log_path))
    print cmd
    commands.getstatusoutput(cmd)
    # 拷贝iscsiadm -m session -P 3信息
    cmd = ("ssh root@%s 'iscsiadm -m session -P 3 ' | ssh %s 'cat - > %s/iscsiadm'" % (s_ip, err_ip, dst_log_path))
    print cmd
    commands.getstatusoutput(cmd)
    # 拷贝/etc/iscsi/initiatorname.iscsi
    cmd = ("ssh root@%s 'scp /etc/iscsi/initiatorname.iscsi %s:%s'" % (s_ip, err_ip, dst_log_path))
    print cmd
    commands.getstatusoutput(cmd)
    #  拷贝/etc/iscsi/iscsid.conf
    cmd = ("ssh root@%s 'scp /etc/iscsi/iscsid.conf  %s:%s'" % (s_ip, err_ip, dst_log_path))
    print cmd
    commands.getstatusoutput(cmd)
    # 还原旧的iscsid.conf配置文件
    cmd = ("ssh root@%s \"sed -r -i 's/^node.session.auth/#node.session.auth/g' /etc/iscsi/iscsid.conf\"" % (s_ip,))
    print cmd
    commands.getstatusoutput(cmd)
    # 拷贝vdbench日志
    cmd = ("ssh root@%s 'scp -r /root/output %s:%s'" % (s_ip, err_ip, dst_log_path))
    print cmd
    commands.getstatusoutput(cmd)
    # 拷贝xstor_locate_lun.py信息
    cmd = ("ssh root@%s 'scp /home/parastor/tools/xstor_locate_lun.py %s:/root'" % (deploy_ips[0], s_ip))
    print cmd
    commands.getstatusoutput(cmd)
    luns = osan.ls_scsi_dev(s_ip)
    for lun in luns:
        cmd = ("timeout 10 ssh root@%s 'fdisk -l %s ' | ssh %s 'cat - >> %s/fdisk_info'" % (s_ip, lun, err_ip, lun_log))
        commands.getstatusoutput(cmd)
        lun = lun.split('/')[-1]
        cmd = ("timeout 15 ssh root@%s '/root/xstor_locate_lun.py %s ' | ssh %s 'cat - > %s/%s'"
               % (s_ip, lun, err_ip, lun_log, lun))
        print cmd
        commands.getstatusoutput(cmd)

def collect_win_cli(dst=None):
    if common2.windows_tag == 0:
        err_ip = get_err_log_ip()
        err_path = get_err_log_path()
        dst_log_path = err_path + "/" + str(dst) + '/' + 'windows_host'
        cmd = ('ssh root@%s "mkdir -p %s"' % (err_ip, dst_log_path))
        os.system(cmd)
        osan.upload_vdb_output(err_ip, dst_log_path)
    else:
        return None

def collect_parastors(s_ip=None, dst=None):
    col_threads = []
    for sip in s_ip:
        col_threads.append(threading.Thread(target=collect_parastor, args=(sip, dst)))
    for col_thread in col_threads:
        col_thread.setDaemon(True)
        col_thread.start()
    for col_thread in col_threads:
        col_thread.join()


def collect_clis(s_ip=None, dst=None):
    col_threads = []
    for sip in s_ip:
        col_threads.append(threading.Thread(target=collect_cli, args=(sip, dst)))
    for col_thread in col_threads:
        col_thread.setDaemon(True)
        col_thread.start()
    for col_thread in col_threads:
        col_thread.join()


def collect_script(dst=None):
    '''
    :Author:Diws
    :Date:20180901
    :Description:拷贝测试脚本日志
    :param dst: 脚本名
    :return:
    '''
    err_ip = get_err_log_ip()
    err_path = get_err_log_path()
    script_log_path = dst
    dst = dst.split('/')[0]
    cmd = ("cd %s;ls -lt |grep %s | sed -n 1p | awk '{print $NF}'" % (test_log_path, dst))
    res, fname = commands.getstatusoutput(cmd)
    dst_log_path = err_path + "/" + str(script_log_path) + '/'
    cmd = ("ssh root@%s '[ -e %s]'" % (err_ip, dst_log_path))
    res, output = commands.getstatusoutput(cmd)
    if res != 0:
        cmd = ("ssh root@%s 'mkdir -p %s'" % (err_ip, dst_log_path))
        commands.getstatusoutput(cmd)
    cmd = ("scp -r %s/%s root@%s:%s" % (test_log_path, fname, err_ip, dst_log_path))
    commands.getstatusoutput(cmd)


class Collect_log(object):
    """
    P300收集日志
    """
    parastor_bin = "/home/parastor/bin/"                # 集群bin文件
    parastor_oms = "/home/parastor/oms/"                # 集群oms bin文件
    parastor_oss = "/home/parastor/oss/"                # 集群oos bin文件
    parastor_log_path = "/home/parastor/log/"           # 集群log文件路径
    client_log_path = "/var/log/"                       # 客户端log文件路径
    zk_path = '/home/parastor/conf/zk'                  # zk路径
    client_property = '/proc/parastor'                  # iostat信息
    parastor_ko = '/home/parastor/tools/client/*.ko'    # 集群节点ko
    client_ko = '/cliparastor/tools/client/*.ko'        # 客户端ko
    gridview_path = '/opt/gridview/'                    # WebUI日志
    mysql_path = '/opt/gvmysql/data'                    # mysql路径
    TmpCollectLogPath = '/tmp/parastor_collect_logs'    # 脚本收集日志（包括数据校验错误信息）

    def __init__(self, node_ip_lst=None, client_ip_lst=None, crash_dic=None, log_name=None, test_log_lst=None):
        self.node_ip_lst = node_ip_lst
        self.client_ip_lst = client_ip_lst
        self.crash_dic = crash_dic
        self.dest_ip = get_err_log_ip()
        """获取当前时间"""
        current_time = self.get_current_time()
        if log_name:
            tem_name = '%s_%s' % (current_time, log_name)
        else:
            tem_name = current_time
        dest_path = get_err_log_path()
        dest_dir = os.path.join(dest_path, tem_name)
        common.mkdir_path(self.dest_ip, dest_dir)
        self.dest_path = dest_dir
        self.test_log_lst = test_log_lst
        self.all_log_dir = {}

    def begin_collect_log(self):
        """
        收集日志
        """
        log.info("******************** collect all log begin ********************")
        """获取crash日志"""
#        self.collect_crash_log()
#        """获取客户端日志"""
#        self.collect_client_log()
#        """获取集群日志"""
        self.collect_parastor_log()
#        """获取测试日志"""
#        self.collect_test_log()

        """拷贝文件"""
        self.scp_all_log()
        log.info("******************** collect all log finish ********************")

    def add_log_lst_to_dic(self, key, log_lst):
        """
        添加log列表到log字典中
        """
        if key in self.all_log_dir:
            self.all_log_dir[key] += log_lst
        else:
            self.all_log_dir[key] = log_lst

    def collect_parastor_log(self):
        """
        收集集群日志
        """
        for node_ip in self.node_ip_lst:
            parastor_log_lst = []
            """第一个节点获取pscli命令"""
            if node_ip == self.node_ip_lst[0]:
                pscli_top_job_log = "/tmp/pscli_top_job.log"
                pscli_perf_log = "/tmp/pscli_perf.log"
                pscli_executor_stat_log = "/tmp/pscli_executor_stat.log"
                pscli_all_jobs_log = "/tmp/pscli_all_jobs.log"
                pscli_resource_lock_log = "/tmp/pscli_resource_lock.log"
                cmd = "pscli --command=get_top_job_stat > %s" % pscli_top_job_log
                common.run_command_shot_time(cmd, node_ip, print_flag=False)
                cmd = "pscli --command=get_perf_data > %s" % pscli_perf_log
                common.run_command_shot_time(cmd, node_ip, print_flag=False)
                cmd = "pscli --command=get_executor_stat > %s" % pscli_executor_stat_log
                common.run_command_shot_time(cmd, node_ip, print_flag=False)
                cmd = "pscli --command=get_all_jobs > %s" % pscli_all_jobs_log
                common.run_command_shot_time(cmd, node_ip, print_flag=False)
                cmd = "pscli --command=get_resource_lock_info > %s" % pscli_resource_lock_log
                common.run_command_shot_time(cmd, node_ip, print_flag=False)
                """本节点获取性能统计"""
                #rc, lat_log_path = self.get_lat_log(node_ip)
                #if rc == 0:
                #    log_dic = {'log': lat_log_path, 'path': None}
                #    parastor_log_lst.append(log_dic)
                log_dic = {'log': pscli_top_job_log, 'path': 'mgr'}
                parastor_log_lst.append(log_dic)
                log_dic = {'log': pscli_perf_log, 'path': 'mgr'}
                parastor_log_lst.append(log_dic)
                log_dic = {'log': pscli_executor_stat_log, 'path': 'mgr'}
                parastor_log_lst.append(log_dic)
                log_dic = {'log': pscli_all_jobs_log, 'path': 'mgr'}
                parastor_log_lst.append(log_dic)
                log_dic = {'log': pscli_resource_lock_log, 'path': 'mgr'}
                parastor_log_lst.append(log_dic)

            """获取日志校验错误信息"""
            parastor_tools_path = self.get_BadFile_log(node_ip)
            log_dic = {'log': parastor_tools_path, 'path': "bad_file_sector"}
            parastor_log_lst.append(log_dic)

            """管理节点收集日志"""
            if common.check_file_exist(node_ip, self.zk_path):
                mgr_log_lst = self.get_mgr_log(node_ip)
                parastor_log_lst += mgr_log_lst

            """收集WebUI日志"""
            if common.check_file_exist(node_ip, self.gridview_path):
                log_dic = {'log': os.path.join(self.gridview_path, "GridviewLog"), 'path': 'opt_gridview'}
                parastor_log_lst.append(log_dic)
                log_dic = {'log': os.path.join(self.gridview_path, "conf"), 'path': 'opt_gridview'}
                parastor_log_lst.append(log_dic)

            """收集mysql日志"""
            if common.check_file_exist(node_ip, self.mysql_path):
                log_dic = {'log': os.path.join(self.mysql_path, 'mysql-bin.*'), 'path': 'opt_gvmysql_data'}
                parastor_log_lst.append(log_dic)
                log_dic = {'log': os.path.join(self.mysql_path, '*.err'), 'path': 'opt_gvmysql_data'}
                parastor_log_lst.append(log_dic)

            """收集客户端日志"""
            client_propert = self.get_client_iostat(node_ip)
            log_dic = {'log': client_propert, 'path': None}
            parastor_log_lst.append(log_dic)
            log_dic = {'log': os.path.join(self.client_log_path, 'parastor*'), 'path': 'var_log'}
            parastor_log_lst.append(log_dic)
            log_dic = {'log': os.path.join(self.client_log_path, 'imp_parastor*'), 'path': 'var_log'}
            parastor_log_lst.append(log_dic)
            log_dic = {'log': os.path.join(self.client_log_path, 'messages*'), 'path': 'var_log'}
            parastor_log_lst.append(log_dic)

            """收集集群日志"""
            log_dic = {'log': self.parastor_log_path, 'path': 'home_parastor_log'}
            parastor_log_lst.append(log_dic)

            """收集集群bin"""
            log_dic = {'log': self.parastor_bin, 'path': 'home_parastor_bin'}
            parastor_log_lst.append(log_dic)
            log_dic = {'log': self.parastor_oms, 'path': 'home_parastor_bin'}
            parastor_log_lst.append(log_dic)
            log_dic = {'log': self.parastor_oss, 'path': 'home_parastor_bin'}
            parastor_log_lst.append(log_dic)

            """收集root目录core文件"""
            core_lst = self.get_root_core(node_ip)
            parastor_log_lst += core_lst

            self.add_log_lst_to_dic(node_ip, parastor_log_lst)

    def collect_client_log(self):
        """
        获取客户端的日志
        """
        for node_ip in self.client_ip_lst:
            """获取客户端的性能统计"""
            client_log_lst = []
            client_propert = self.get_client_iostat(node_ip)
            log_dic = {'log': client_propert, 'path': None}
            client_log_lst.append(log_dic)
            """获取客户端的日志"""
            log_dic = {'log': os.path.join(self.client_log_path, 'parastor*'), 'path': 'var_log'}
            client_log_lst.append(log_dic)
            log_dic = {'log': os.path.join(self.client_log_path, 'imp_parastor*'), 'path': 'var_log'}
            client_log_lst.append(log_dic)
            log_dic = {'log': os.path.join(self.client_log_path, 'messages*'), 'path': 'var_log'}
            client_log_lst.append(log_dic)
            log_dic = {'log': self.parastor_log_path, 'path': 'home_parastor_log'}
            client_log_lst.append(log_dic)

            """收集root目录core文件"""
            core_lst = self.get_root_core(node_ip)
            client_log_lst += core_lst
            self.add_log_lst_to_dic(node_ip, client_log_lst)

    def collect_crash_log(self):
        """
        收集crash日志
        """
        if not self.crash_dic:
            return

        for node_ip in self.crash_dic:
            crash_log_lst = []
            """收集crash"""
            for crash_log in self.crash_dic[node_ip]:
                log_dic = {'log': crash_log, 'path': 'var_crash'}
                crash_log_lst.append(log_dic)
            """收集客户端log"""
            log_dic = {'log': os.path.join(self.client_log_path, 'parastor*'), 'path': 'var_log'}
            crash_log_lst.append(log_dic)
            log_dic = {'log': os.path.join(self.client_log_path, 'imp_parastor*'), 'path': 'var_log'}
            crash_log_lst.append(log_dic)
            log_dic = {'log': os.path.join(self.client_log_path, 'messages*'), 'path': 'var_log'}
            crash_log_lst.append(log_dic)

            if node_ip in self.node_ip_lst:
                """收集ko"""
                log_dic = {'log': self.parastor_ko, 'path': 'ko'}
                crash_log_lst.append(log_dic)
            else:
                """收集ko"""
                log_dic = {'log': self.client_ko, 'path': 'ko'}
                crash_log_lst.append(log_dic)
                """收集客户端log"""
                log_dic = {'log': self.parastor_log_path, 'path': 'home_parastor_log'}
                crash_log_lst.append(log_dic)
            self.add_log_lst_to_dic(node_ip, crash_log_lst)

    def collect_test_log(self):
        """
        收集测试日志
        """
        if self.test_log_lst:
            test_log_lst = []
            for test_log in self.test_log_lst:
                log_dic = {'log': test_log, 'path': None}
                test_log_lst.append(log_dic)
            self.add_log_lst_to_dic('test', test_log_lst)

    @staticmethod
    def get_lat_log(node_ip):
        """
        :author:      baoruobing
        :date  :      2018.07.28
        :description: 获取各模块的性能统计信息
        :return:
        """
        lat_path = '/tmp/lat_log_col_p300'
        if common.check_file_exist(node_ip, lat_path):
            cmd = 'rm -rf %s' % lat_path
            common.run_command_shot_time(cmd, node_ip, print_flag=False)
        common.mkdir_path(node_ip, lat_path)
        lat_file = os.path.join(lat_path, 'lat.log')
        log.info("get lat log begin, please wait for a while")
        cmd = 'sh /home/parastor/tools/print_lat.sh %s' % lat_file
        rc, stdout = common.run_command(node_ip, cmd, print_flag=False, timeout=900)
        if rc != 0:
            log.warn("print_lat.sh failed!!!")
            return rc, None
        log.info("print_lat.sh success!!!")
        return rc, lat_path

    def get_client_iostat(self, node_ip):
        """
        获取客户端性能文件
        """
        client_iostat_dir = '/tmp/client_property_p300'
        if common.check_file_exist(node_ip, client_iostat_dir):
            cmd = 'rm -rf %s' % client_iostat_dir
            common.run_command_shot_time(cmd, node_ip, print_flag=False)
        common.mkdir_path(node_ip, client_iostat_dir)

        cmd = 'ls -l %s |grep "^-"' % self.client_property
        rc, stdout = common.run_command_shot_time(cmd, node_ip, print_flag=False)
        for line in stdout.splitlines():
            file_name = line.split()[-1]
            dest_file = os.path.join(client_iostat_dir, file_name)
            source_file = os.path.join(self.client_property, file_name)
            cmd = "cat %s > %s" % (source_file, dest_file)
            common.run_command_shot_time(cmd, node_ip, print_flag=False)
        return client_iostat_dir

    def get_mgr_log(self, node_ip):
        """
        :author:        baoruobing
        :date  :        2018.07.28
        :description:   获取节点的管理日志
        :param node_ip: 节点ip
        :return:
        """
        mgr_log_lst = []
        """1> 收集/tmp/*.log日志"""
        log_dic = {'log': '/tmp/*.log', 'path': 'mgr'}
        mgr_log_lst.append(log_dic)

        """2> 收集dev/shm/parastor下所有日志"""
        log_dic = {'log': '/dev/shm/parastor', 'path': 'dev_shm_parastor'}
        mgr_log_lst.append(log_dic)

        """3> 收集zk日志"""
        """ zk在/home/parastor/conf中
        log_dic = {'log': self.zk_path, 'path': None}
        mgr_log_lst.append(log_dic)
        """

        """5> 收集oJmgs栈信息"""
        ojmgs_jstack_log = "/tmp/oJmgs_jstack_log"
        jcmd_native_memory_log = "/tmp/jcmd_native_memory.log"
        jmap_histo_log = "/tmp/jmap_histo.log"
        jmap_heap_log = "/tmp/jmap_heap.log"
        dump_bin_log = "/tmp/dump.bin"
        jstat_log = "/tmp/jstat.log"
        pid = self.get_process_pid(node_ip, "/home/parastor/bin/oJmgs")
        if pid:
            cmd = "jstack %s > %s" % (pid, ojmgs_jstack_log)
            common.run_command_shot_time(cmd, node_ip, print_flag=False)
            log_dic = {'log': ojmgs_jstack_log, 'path': 'mgr'}
            mgr_log_lst.append(log_dic)

            cmd = "jcmd %s VM.native_memory > %s" % (pid, jcmd_native_memory_log)
            common.run_command_shot_time(cmd, node_ip, print_flag=False)
            log_dic = {'log': jcmd_native_memory_log, 'path': 'mgr'}
            mgr_log_lst.append(log_dic)

            cmd = "jmap -histo %s > %s" % (pid, jmap_histo_log)
            common.run_command_shot_time(cmd, node_ip, print_flag=False)
            log_dic = {'log': jmap_histo_log, 'path': 'mgr'}
            mgr_log_lst.append(log_dic)

            cmd = "jmap -heap %s > %s" % (pid, jmap_heap_log)
            common.run_command_shot_time(cmd, node_ip, print_flag=False)
            log_dic = {'log': jmap_heap_log, 'path': 'mgr'}
            mgr_log_lst.append(log_dic)

            cmd = "jmap -dump:format=b,file=%s %s" % (dump_bin_log, pid)
            common.run_command_shot_time(cmd, node_ip, print_flag=False)
            log_dic = {'log': dump_bin_log, 'path': 'mgr'}
            mgr_log_lst.append(log_dic)

            cmd = "jstat -gcutil %s 1s 5 > %s" % (pid, jstat_log)
            common.run_command_shot_time(cmd, node_ip, print_flag=False)
            log_dic = {'log': jstat_log, 'path': 'mgr'}
            mgr_log_lst.append(log_dic)

        """6> 收集所有进程信息"""
        all_pro_log = "/tmp/all_pro_log"
        cmd = "ps -ef > %s" % all_pro_log
        common.run_command_shot_time(cmd, node_ip, print_flag=False)
        log_dic = {'log': all_pro_log, 'path': 'mgr'}
        mgr_log_lst.append(log_dic)

        """7> 收集配置文件"""
        conf_log_path = "/home/parastor/conf"
        log_dic = {'log': conf_log_path, 'path': 'home_parastor_conf'}
        mgr_log_lst.append(log_dic)
        return mgr_log_lst

    @staticmethod
    def get_root_core(node_ip):
        """
        获取根目录core
        """
        cmd = "ls /core*"
        rc, stdout = common.run_command_shot_time(cmd, node_ip, print_flag=False)
        if rc != 0:
            return []
        else:
            core_lst = []
            core_tmp_lst = stdout.split()
            for core_info in core_tmp_lst:
                log_dic = {'log': core_info, 'path': 'root_core'}
                core_lst.append(log_dic)
            return core_lst

    @staticmethod
    def get_process_pid(node_ip, process):
        """
        :author:        baoruobing
        :date  :        2018.07.28
        :description:   获取节点某个进程的pid
        :param node_ip: 节点ip
        :param process: 进程标志
        :return:
        """
        ps_cmd = ('ps -ef | grep %s | grep -v grep' % process)
        rc, stdout = common.run_command_shot_time(ps_cmd, node_ip, print_flag=False)
        if rc != 0:
            return None
        pid = stdout.splitlines()[0].split()[1]
        return pid

    def scp_all_log(self):
        """拷贝所有log"""
        log.info("******************************")
        for key in self.all_log_dir:
            log_info_list = []
            for mem in self.all_log_dir[key]:
                if mem not in log_info_list:
                    log_info_list.append(mem)
            self.all_log_dir[key] = log_info_list[:]

            log_lst = []
            for log_info in self.all_log_dir[key]:
                log_lst.append(log_info['log'])
            info_str = 'node %s: %s will scp' % (key, log_lst)
            log.info(info_str)
        log.info("******************************")

        def _scp_all_log(self, key, col_log_lst):
            """创建日志存放路径"""
            log_put_dir = os.path.join(self.dest_path, key)
            common.mkdir_path(self.dest_ip, log_put_dir)
            self.scp_log(col_log_lst, key, self.dest_ip, log_put_dir)

        thread_lst = []
        for key in self.all_log_dir:
            th = threading.Thread(target=_scp_all_log, args=(self, key, self.all_log_dir[key]))
            thread_lst.append(th)

        for th in thread_lst:
            th.daemon = True
            th.start()

        while True:
            time.sleep(2)
            for th in thread_lst:
                if th.is_alive():
                    break
            else:
                break

    @staticmethod
    def scp_log(log_lst, src_node_ip, dest_node_ip, dest_dir):
        """
        :author:             baoruobing
        :date  :             2018.07.28
        :description:        拷贝log
        :param log_lst:      日志列表
        :param src_node_ip:  源节点
        :param dest_node_ip: 日志存放节点
        :param dest_dir:     日志存放目录
        :return:
        """
        for log_info in log_lst:
            if src_node_ip != 'test' and common.check_file_exist(src_node_ip, log_info['log']) is False:
                continue
            if log_info['path']:
                true_dest_dir = os.path.join(dest_dir, log_info['path'])
                common.mkdir_path(dest_node_ip, true_dest_dir)
            else:
                true_dest_dir = dest_dir
            if "home_parastor_log" in true_dest_dir:
                cmd_mv = 'mv %s %s' % (get_mount_log_path_dic()[src_node_ip] + "/*", true_dest_dir)
                info_str = "mv %s to %s" % (get_mount_log_path_dic()[src_node_ip] + "/*", true_dest_dir)
                log.info(info_str)
                rc, stdout = common.run_command_shot_time(cmd_mv, dest_node_ip, print_flag=False)
                if rc != 0:
                    log.info("node: %s, cmd: %s" % (dest_node_ip, cmd_mv))
                    log.info(stdout)
                    log.info('mv log failed!!!')
            else:
                cmd = 'scp -rp %s root@%s:%s' % (log_info['log'], dest_node_ip, true_dest_dir)
                info_str = "scp %s:%s to %s:%s" % (src_node_ip, log_info['log'], dest_node_ip, true_dest_dir)
                log.info(info_str)
                if src_node_ip == 'test':
                    rc, stdout = common.run_command_shot_time(cmd, print_flag=False)
                else:
                    rc, stdout = common.run_command_shot_time(cmd, src_node_ip, print_flag=False)
                if rc != 0:
                    log.info("node: %s, cmd: %s" % (src_node_ip, cmd))
                    log.info(stdout)
                    log.info('scp log failed!!!')

    @staticmethod
    def get_current_time():
        """
        :author:        baoruobing
        :date  :        2018.07.28
        :description:   获取当前时间
        :return:
        """
        now_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
        return now_time

    def get_BadFile_log(self, node_ip):
        """收集tools信息"""
        vdbench_path = self.test_log_lst[0]
        bad_file = None
        bad_sector = None
        df_path_dic = {}

        cmd = "cd %s;grep -r 'bad sector' | grep 'errorlog.html' | head -1" % vdbench_path
        rc, stdout = common.run_command_shot_time(cmd, print_flag=False)
        common.judge_rc(rc, 0, "get bad sector error")
        if stdout:
            stdout_info = stdout.strip().split("File name:")[1].strip()
            bad_file = stdout_info.split()[0][:-1]
            bad_sector = stdout_info.split()[-1]

            cmd = "ls %s" % bad_file
            rc, stdout_ls = common.pscli_run_command(cmd, print_flag=False)
            if rc != 0:
                mount_num = stdout.split()[1][:-1].split("=")[0]
                cmd = "cd %s;grep -r '=%s,system=' | grep parmfile.html | head -1" % (vdbench_path, mount_num.split("-")[0])
                rc, stdout_ip = common.run_command_shot_time(cmd, print_flag=False)
                mount_ip = stdout_ip.strip().split("=")[-1]

                rc, stdout = common.run_command_shot_time("df | grep :", mount_ip, print_flag=False)
                for df_info in stdout.split("\n"):
                    if df_info.split()[-1] in bad_file:
                        df_path = df_info.split()[0].split(":")[-1]
                        df_path_dic[df_path] = df_info.split()[-1]
                        bad_file = df_path + bad_file.split(df_path_dic[df_path])[1]
                        break
                    if df_info == stdout.split('\n')[-1]:
                        log.error("find bad file nfs mount path error")

        parastor_tools_path = os.path.join(self.TmpCollectLogPath, "parastor_tools_log")
        common.mkdir_path(node_ip, parastor_tools_path)

        if bad_file:
            getinfo_datacon_log = os.path.join(parastor_tools_path, "getinfo_datacon.log")
            cmd = "sh /home/parastor/tools/getinfo_datacon.sh %s %s | tee %s" % (bad_file, bad_sector, getinfo_datacon_log)
            rc, stdout = common.run_command(cmd=cmd, node_ip=node_ip, timeout=900)
            if rc != 0:
                log.error("getinfo_datacon.sh failed!!!")
            line_lst = stdout.splitlines()
            badfile_ino = ''
            badseg_index = 0
            for line in line_lst:
                if 'badfile ino' in line:
                    badfile_ino = line.split(':')[-1].strip()
                if 'badseg infile' in line:
                    badseg_index = line.split(':')[-1].strip()

            ecode_dump_log = os.path.join(parastor_tools_path, "ecode-dump.log")
            cmd = "cd /home/parastor/tools/ecodecheck;sh ecode-dump.sh %s %s %s > %s" % (node_ip, bad_file, badseg_index,
                                                                                         ecode_dump_log)
            rc, stdout = common.run_command(cmd=cmd, node_ip=node_ip, timeout=900)
            if rc != 0:
                log.error("ecode-dump.sh failed!!!")

            rep_dump_log = os.path.join(parastor_tools_path, "rep-dump.log")
            cmd = "cd /home/parastor/tools/ecodecheck;sh rep-dump.sh %s %s > %s" % (node_ip, bad_file, rep_dump_log)
            rc, stdout = common.run_command(cmd=cmd, node_ip=node_ip, timeout=900)
            if rc != 0:
                log.error("rep-dump.sh failed!!!")

            cmd = "mv /tmp/iNode-%s* %s" % (badfile_ino, parastor_tools_path)
            common.run_command(cmd=cmd, node_ip=node_ip, timeout=900)
        return parastor_tools_path
