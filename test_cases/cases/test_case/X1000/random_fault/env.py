#!usr/bin/env python  
# -*- coding:utf-8 -*-  
""" 
:author: Liu he
:Description:
@file: test.py 
@time: 2018/12/21 
"""
import os
import re
import sys
import time
import inspect
import random
import datetime
import utils_path
import Lun_managerTest
import common
import common2
import commands
import breakdown
import log
import json
import disk
import prepare_x1000
# import prepare_clean
# import prepare_x1000
import get_config
from get_config import config_parser as cp
import decorator_func
import ReliableTest
import env_manage

# 初始化配置文件
conf_file = get_config.CONFIG_FILE  # 配置文件路径
deploy_ips = get_config.get_env_ip_info(conf_file)  # 获取集群IP列表
client_ips = get_config.get_allclient_ip()  # 获取客户端IP

case_list_path = "/home/StorTest/test_cases/cases/test_case/X1000/random_fault/"
case_list_file = case_list_path + "param"

lib_disk = disk.disk()
osan = Lun_managerTest.oSan()
com2_osan = common2.oSan()
node = common.Node()


def check_ping(ip):
    cmd = 'ping -c 3 %s | grep "0 received" | wc -l' % ip
    rc, stdout = commands.getstatusoutput(cmd)
    if '0' != stdout.strip():
        return False
    else:
        return True


def get_os_type(s_ip=deploy_ips[0]):
    """
    :Auther: Liu he
    :Description: 读取机器类型
    :param s_ip: 测试节点IP地址
    :return: VM虚拟机将返回字符VM，其他类型机器返回"phy"
    ====================================================================================
    :注：该方法适用于多种虚拟机，stdout返回值在其他类型虚拟机上需要验证，物理机返回机器型号（若有）
    ====================================================================================
    """
    if "True" == check_ping(s_ip):
        log.error("Node %s do not get info,Please check IP or the machine status" % (s_ip))
        os._exit(1)
    else:
        cmd = ("ssh %s \" dmidecode -s system-product-name\"" % (s_ip))
        rc, stdout = commands.getstatusoutput(cmd)
        if rc != 0:
            log.info("get  %s system type failed.\n Error Info : \n %s" % (s_ip, stdout))
            os._exit(1)
        else:
            if "VMware" in stdout:
                log.info("check %s the system is %s " % (s_ip, stdout))
                return "VM"
            else:
                log.info("Get The test %s machine is %s ,will return\"phy\"" % (s_ip, stdout))
                return "phy"


def get_nodes(s_ip=None):
    '''
    date    :   2018-06-05
    Description :   获取节点ID
    param   :   s_ip : 服务节点IP
    return  :   节点ID
    '''
    nodeids = []
    # if None == s_ip:
    #     pass
    #     # log.error("Please input the corrent ip.")
    # else:
    # s_ip = s_ip.split()
    cmd = ("ssh %s \"pscli --command=get_nodes\"" % (s_ip))
    (res, final) = commands.getstatusoutput(cmd)
    log.info(cmd)
    if res != 0:
        log.error("Get nodes error.")
        exit(1)
    else:
        log.info("Get nodes success.")
        final = json.loads(final)
        for i in range(0, len(final['result']['nodes'])):
            nodeids.append(final['result']['nodes'][i]['data_disks'][0]['nodeId'])
    return nodeids


def ls_scsi_dev(client_ip):
    '''
    date    :   2018-05-16
    Description :  获取scsi设备名
    param   :   client_ip   :   iscsi客户端IP;
    return  :   scsi 设备名列表
    change_log
    Author:wangxiang
    Des:更改了关于iscsi设备的判断
    '''
    cmd = ("ssh %s \"lsscsi | grep Xstor\" | awk '{print $NF}'" % (client_ip))
    (res, final) = commands.getstatusoutput(cmd)
    if res != 0:
        log.error(final)
        log.error("Get scsi devices on %s failed.Error info: \n%s" % (client_ip, final))
        exit(1)
    else:
        log.info("Get scsi devices on %s success. Get Xstor disk : \n%s " % (client_ip, final))
    scsis = []
    scsis = final.split('\n')
    if scsis == ['']:
        scsis = []
    if len(scsis) == 0:
        log.error("There is no scsi devices on %s." % (client_ip))
    log.info("From %s host get iscsi device list : %s" % (client_ip, scsis))
    return scsis


def gen_vdb_xml(max_range='100M', maxdata='1G', thread=32, offset=None, align=None, lun=None, xfersize=None, rdpct=None,
                seekpct=None, interval=1):
    '''
    date    :   2018-05-17
    Description :   生成vdbench配置文件
    param   :  vdbench标准配置参数
    return  :   vdbench xml file path
    '''
    t1 = datetime.datetime.now()
    template_file = get_config.get_tools_path() + "/osan/template"  # 获取配置文件模板路径
    vdb_xml = get_config.get_tools_path() + "/osan/vdb_xml." + str(t1.microsecond)  # vdbench测试所用的文件
    sd_num = 1  # 初始化sd数量
    threads = []
    # vdb_path = get_config.get_vdbench_path()        #获取vdbench路径
    if True == os.path.exists(vdb_xml):
        cmd = ("rm -rf %s" % (vdb_xml))
        log.info(cmd)
        commands.getstatusoutput(cmd)
    cmd = ("cp %s %s" % (template_file, vdb_xml))
    log.info(cmd)
    commands.getstatusoutput(cmd)
    if None == lun or len(lun) == 0:
        log.error("Found no scsi devices.")
        os._exit(1)
    if None != offset:
        cmd = ("sed -i '1s/$/,offset=%s/g' %s" % (str(offset), vdb_xml))  # 修改前偏移量
        #            log.info("Modify vdb_xml cmd %s" % (cmd))
        log.info(cmd)
        commands.getstatusoutput(cmd)
    if None != align:
        cmd = ("sed -i '1s/$/,align=%s/g' %s" % (str(align), vdb_xml))  # 修改后偏移量
        #            log.info("Modify vdb_xml cmd %s" % (cmd))
        log.info(cmd)
        commands.getstatusoutput(cmd)
    if None != rdpct:
        cmd = ("sed -i '2s/$/,rdpct=%s/g' %s" % (str(rdpct), vdb_xml))  # 修改读写占比
        log.info(cmd)
        commands.getstatusoutput(cmd)
    if None != seekpct:
        cmd = ("sed -i '2s/$/,seekpct=%s/g' %s" % (str(seekpct), vdb_xml))  # 修改读写占比
        #            log.info("Modify vdb_xml cmd %s" % (cmd))
        log.info(cmd)
        commands.getstatusoutput(cmd)
    if None != xfersize:
        cmd = ("sed -i -r 's/xfersize.*?\)/xfersize=%s/g' %s" % (xfersize, vdb_xml))  # 修改xferrsize
        #            log.info("Modify vdb_xml cmd %s" % (cmd))
        log.info(cmd)
        commands.getstatusoutput(cmd)
    for dev_name in lun:
        if max_range:
            sd_xml = ("sd=sd%d,lun=%s,range=(0,%s)" % (sd_num, dev_name, max_range))
        else:
            sd_xml = ("sd=sd%d,lun=%s" % (sd_num, dev_name))
        wd_xml = ("wd=wd%d,sd=sd%d" % (sd_num, sd_num))
        cmd = ("sed -i '%da\%s' %s" % (sd_num, sd_xml, vdb_xml))  # 插入rd
        log.info(cmd)
        commands.getstatusoutput(cmd)
        cmd = ("sed -i '$i\%s' %s" % (wd_xml, vdb_xml))  # 插入wd
        log.info(cmd)
        commands.getstatusoutput(cmd)
        sd_num = sd_num + 1
        # threads.append("10")
    # threads = "3"
    if max_range:
        max = len(lun) * int(max_range[:-1]) * 2
        if max_range[-1] == 'G':
            maxdata = str(max) + 'G'
        elif max_range[-1] == 'M':
            maxdata = str(max / 1000 + 1) + 'G'
    cmd = ("sed -i -r 's/thread.*?\)/threads=%s/g' %s" % (thread, vdb_xml))  # 修改每个wd的进程数
    log.info(cmd)
    commands.getstatusoutput(cmd)
    cmd = ("sed -i -r 's/interval.*?/interval=%s/g' %s" % (interval, vdb_xml))  # 修改每个wd的interval
    log.info(cmd)
    commands.getstatusoutput(cmd)
    cmd = ("sed -r -i 's/maxdata=[0-9]+[a-zA-Z]+,/maxdata=%s,/g' %s" % (str(maxdata), vdb_xml))  # 修改每个wd的maxdata
    log.info(cmd)
    commands.getstatusoutput(cmd)
    cmd = ("sed -r -i '1idata_errors=3' %s" % (vdb_xml))
    log.info(cmd)
    commands.getstatusoutput(cmd)
    log.info(vdb_xml)
    return vdb_xml


def change_xml(s_ip=deploy_ips[0], jn_on=None, vdb_xml=None, whether_change="Y"):
    if whether_change == "Y":
        type_info = get_os_type()
        node_num = len(get_nodes(s_ip))
        if node_num == 5:
            if type_info == "phy":
                if jn_on != None:
                    # 修改xfersize
                    # cmd = ("sed -i -r 's/xfersize.*?\)/xfersize=(1k,10,4k,25,15k,20,128k,20,213k,25)/g' %s"
                    #        % (vdb_xml))
                    # commands.getstatusoutput(cmd)
                    # # 修改range
                    # cmd = ("sed -r -i 's/range=.*\)/range=(0,3G)/g' %s" % (vdb_xml,))
                    # commands.getstatusoutput(cmd)
                    # # 修改iorate
                    # cmd = ("sed -r -i 's/iorate=[0-9]+/iorate=1000/g' %s" % (vdb_xml,))
                    # commands.getstatusoutput(cmd)

                    cmd = ("sed -i -r 's/xfersize.*?\)/xfersize=(3k)/g' %s" % (vdb_xml))
                    commands.getstatusoutput(cmd)
                    # 修改range
                    cmd = ("sed -r -i 's/range=.*\)/range=(0,100M)/g' %s" % (vdb_xml,))
                    commands.getstatusoutput(cmd)
                    # 修改iorate
                    cmd = ("sed -r -i 's/iorate=[0-9]+/iorate=400/g' %s" % (vdb_xml,))
                    commands.getstatusoutput(cmd)
                    # 修改threads
                    cmd = ("sed -r -i 's/threads=[0-9]+/threads=8/g' %s" % (vdb_xml,))
                    commands.getstatusoutput(cmd)
                    # 修改maxdata
                    cmd = ('grep -c lun %s' % (vdb_xml,))
                    res, lun_num = commands.getstatusoutput(cmd)
                    maxdata = int(lun_num) * 3 + 4
                    cmd = ("sed -r -i 's/maxdata=[0-9]+[a-zA-Z]+,/maxdata=%sG,/g' %s" % (str(maxdata), vdb_xml,))
                    commands.getstatusoutput(cmd)
                else:
                    # # 修改xfersize
                    # cmd = ("sed -i -r 's/xfersize.*?\)/xfersize=(4k,30,15k,20,127k,20,213k,30)/g' %s"
                    #        % (vdb_xml,))
                    # commands.getstatusoutput(cmd)
                    # # 修改range
                    # cmd = ("sed -r -i 's/range=.*\)/range=(0,5G)/g' %s" % (vdb_xml,))
                    # commands.getstatusoutput(cmd)
                    # # 修改iorate
                    # cmd = ("sed -r -i 's/iorate=[0-9]+/iorate=1000/g' %s" % (vdb_xml,))
                    # commands.getstatusoutput(cmd)

                    # 修改xfersize
                    cmd = ("sed -i -r 's/xfersize.*?\)/xfersize=(3k)/g' %s" % (vdb_xml,))
                    commands.getstatusoutput(cmd)
                    # 修改range
                    cmd = ("sed -r -i 's/range=.*\)/range=(0,100M)/g' %s" % (vdb_xml,))
                    commands.getstatusoutput(cmd)
                    # 修改iorate
                    cmd = ("sed -r -i 's/iorate=[0-9]+/iorate=400/g' %s" % (vdb_xml,))
                    commands.getstatusoutput(cmd)
                    # 修改threads
                    cmd = ("sed -r -i 's/threads=[0-9]+/threads=8/g' %s" % (vdb_xml,))
                    commands.getstatusoutput(cmd)
                    # 修改maxdata
                    cmd = ('grep -c lun %s' % (vdb_xml,))
                    res, lun_num = commands.getstatusoutput(cmd)
                    maxdata = int(lun_num) * 5 + 4
                    cmd = ("sed -r -i 's/maxdata=[0-9]+[a-zA-Z]+,/maxdata=%sG,/g' %s" % (str(maxdata), vdb_xml))
                    commands.getstatusoutput(cmd)
        elif node_num == 3:
            if type_info == "phy":
                if jn_on != None:
                    # # 修改xfersize
                    # cmd = ("sed -i -r 's/xfersize.*?\)/xfersize=(1k,20,3k,35,16k,20,127k,10,212k,15)/g' %s"
                    #        % (vdb_xml))
                    # commands.getstatusoutput(cmd)
                    # # 修改range
                    # cmd = ("sed -r -i 's/range=.*\)/range=(0,2G)/g' %s" % (vdb_xml,))
                    # commands.getstatusoutput(cmd)
                    # # 修改iorate
                    # cmd = ("sed -r -i 's/iorate=[0-9]+/iorate=1000/g' %s" % (vdb_xml,))
                    # commands.getstatusoutput(cmd)

                    # 修改xfersize
                    cmd = ("sed -i -r 's/xfersize.*?\)/xfersize=(3k)/g' %s" % (vdb_xml))
                    commands.getstatusoutput(cmd)
                    # 修改range
                    cmd = ("sed -r -i 's/range=.*\)/range=(0,100M)/g' %s" % (vdb_xml,))
                    commands.getstatusoutput(cmd)
                    # 修改iorate
                    cmd = ("sed -r -i 's/iorate=[0-9]+/iorate=400/g' %s" % (vdb_xml,))
                    commands.getstatusoutput(cmd)

                    # 修改threads
                    cmd = ("sed -r -i 's/threads=[0-9]+/threads=8/g' %s" % (vdb_xml,))
                    commands.getstatusoutput(cmd)
                    # 修改maxdata
                    cmd = ('grep -c lun %s' % (vdb_xml,))
                    res, lun_num = commands.getstatusoutput(cmd)
                    maxdata = int(lun_num) * 3 + 4
                    cmd = ("sed -r -i 's/maxdata=[0-9]+[a-zA-Z]+,/maxdata=%sG,/g' %s" % (str(maxdata), vdb_xml,))
                    commands.getstatusoutput(cmd)
                else:
                    # # 修改xfersize
                    # cmd = ("sed -i -r 's/xfersize.*?\)/xfersize=(1k,20,4k,30,15k,20,127k,10,213k,20)/g' %s"
                    #        % (vdb_xml,))
                    # commands.getstatusoutput(cmd)
                    # # 修改range
                    # cmd = ("sed -r -i 's/range=.*\)/range=(0,4G)/g' %s" % (vdb_xml,))
                    # commands.getstatusoutput(cmd)
                    # # 修改iorate
                    # cmd = ("sed -r -i 's/iorate=[0-9]+/iorate=1000/g' %s" % (vdb_xml,))
                    # commands.getstatusoutput(cmd)

                    # 修改xfersize
                    cmd = ("sed -i -r 's/xfersize.*?\)/xfersize=(3k)/g' %s" % (vdb_xml,))
                    commands.getstatusoutput(cmd)
                    # 修改range
                    cmd = ("sed -r -i 's/range=.*\)/range=(0,100M)/g' %s" % (vdb_xml,))
                    commands.getstatusoutput(cmd)
                    # 修改iorate
                    cmd = ("sed -r -i 's/iorate=[0-9]+/iorate=400/g' %s" % (vdb_xml,))
                    commands.getstatusoutput(cmd)

                    # 修改threads
                    cmd = ("sed -r -i 's/threads=[0-9]+/threads=8/g' %s" % (vdb_xml,))
                    commands.getstatusoutput(cmd)
                    # 修改maxdata
                    cmd = ('grep -c lun %s' % (vdb_xml,))
                    res, lun_num = commands.getstatusoutput(cmd)
                    maxdata = int(lun_num) * 5 + 4
                    cmd = ("sed -r -i 's/maxdata=[0-9]+[a-zA-Z]+,/maxdata=%sG,/g' %s" % (str(maxdata), vdb_xml))
                    commands.getstatusoutput(cmd)


def analysis_range(lun_range):
    lun_range = re.sub('\(|\)|[a-zA-Z]', '', lun_range).split(',')
    if int(lun_range[0]) >= int(lun_range[1]):
        print lun_range[0] + ":" + lun_range[1]
        print "Get wrong range,please check your param."
        exit(1)
    return int(lun_range[0]), int(lun_range[1])


def get_lba(cip, c_lun):
    cmd = ("ssh root@%s 'fdisk -l %s'" % (cip, c_lun))
    res, output = commands.getstatusoutput(cmd)
    lba = output.split('\n')[-1].split()[1]
    while 'fdisk' in lba:
        res, output = commands.getstatusoutput(cmd)
        lba = output.split('\n')[-1].split()[1]
        time.sleep(3)
    return lba


def analysis_xml_file(lun_list):
    cmd = 'ls %s' % case_list_file
    rc, stdout = commands.getstatusoutput(cmd)
    if 0 != rc:
        print '%s is not exist!!!' % case_list_file
        return
    with open(case_list_file, 'r') as f:
        for (num, line) in enumerate(f, 1):
            if line == '\r\n':
                continue
            new_line = get_config.get_processd_single_line(line)
            if 0 == len(new_line):
                continue
            print "line:" + str(num) + ",param:" + new_line
            new_line = new_line.split("/")
            # parameters of vdbench
            # 偏移量
            align = int(new_line[0]) / 512 * 512
            offset = int(new_line[1]) / 512 * 512
            # 读写比例
            rdpct = new_line[2]
            # 随机比例
            seekpct = new_line[3]
            # io大小
            iosize = new_line[4]
            # 进程数
            threads = new_line[5]
            # 是否开启校验
            jn_jro = new_line[6]
            # io速率
            io_rate = new_line[7]
            # 最大数据量
            maxdata = new_line[8]
            # range区间
            range_expand = int(new_line[9])
            # unmappct
            if len(new_line) == 11:
                unmappct = int(new_line[10])
            lun_range = []
            ranges1 = [0, 4, 16, 32, 99]
            j = 0
            for i in ranges1:
                if i == 0:
                    continue
                else:
                    low_size = random.randint(ranges1[j], i)
                    tmp = '(%d,%d)' % (low_size, low_size + range_expand)
                    lun_range.append(tmp)
                    j += 1
            for i in ranges1:
                if i == 0:
                    continue
                else:
                    low_size = i - 1
                    tmp = '(%d,%d)' % (low_size, low_size + range_expand)
                    lun_range.append(tmp)
            luns = []
            sd_num = 1
            for p_lun in lun_list:
                range_num = sd_num % len(lun_range)
                min_size, max_size = analysis_range(lun_range[range_num])
                res = lib_disk.parted_lun(c_ip=client_ips[0], lun=p_lun, min_size=min_size * 1024,
                                          max_size=max_size * 1024)
                luns.append(res)
                sd_num += 1
            # Create configuration file of vdbench
            vdb_file = case_list_path + str(num) + ".vdb"
            w_file = open(vdb_file, "w+")
            data_errors = ("data_errors=3\n")
            w_file.write(data_errors)
            # Write sd default
            if jn_jro == "yes":
                sd_default = "sd=default,journal=/root/vdbench/journal/%s,openflags=o_direct\n" % (str(deploy_ips[0]),)
            else:
                sd_default = "sd=default,journal=/root/vdbench/journal/%s,openflags=o_direct,align=%s,offset=%s\n" % (
                    str(deploy_ips[0]), str(align), str(offset))
            w_file.write(sd_default)
            # Write sd
            sd_num = 1
            for dev_name in luns:
                # range_num = sd_num%4
                sd = ("sd=sd%d,lun=%s\n" % (sd_num, dev_name))
                w_file.write(sd)
                sd_num += 1
                # maxdata = maxdata+analysis_range(lun_range[range_num])
            # Write wd default
            if len(new_line) == 11:
                wd_default = "wd=default,xfersize=%s,rdpct=%s,seekpct=%s,unmappct=%s\n" % (
                    iosize, str(rdpct), str(seekpct), str(unmappct))
            else:
                wd_default = "wd=default,xfersize=%s,rdpct=%s,seekpct=%s\n" % (iosize, str(rdpct), str(seekpct))
            w_file.write(wd_default)
            # Write wd
            wd_num = 1
            if len(new_line) == 11:
                for dev_name in lun_list:
                    lba = get_lba(client_ips[0], dev_name)
                    wd = "wd=wd%d,sd=sd%d,startlba=%s\n" % (wd_num, wd_num, str(lba))
                    wd_num += 1
                    w_file.write(wd)
            else:
                for dev_name in lun_list:
                    wd = "wd=wd%d,sd=sd%d\n" % (wd_num, wd_num)
                    wd_num += 1
                    w_file.write(wd)
            # Write rd
            # maxdata = maxdata+3
            rd_default = "rd=rd1,wd=wd*,iorate=%s,elapsed=600h,maxdata=%sG,threads=%s,interval=1\n" % (
                io_rate, maxdata, str(threads))
            w_file.write(rd_default)
            w_file.close()
            log.info("xml create finished")
            return vdb_file


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
    print output
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
            change_xml(vdb_xml=vdb_xml, whether_change=whether_change_xml)
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
                os._exit(1)
            else:
                pass
        elif jn_jro == "jn":
            change_xml(jn_on="yes", vdb_xml=vdb_xml, whether_change=whether_change_xml)
            ch_cmd = ("sed -r -i 's/,offset=[0-9]+//g' %s" % (vdb_xml))
            commands.getstatusoutput(ch_cmd)
            ch_cmd = ("sed -r -i 's/,align=[0-9]+//g' %s" % (vdb_xml))
            commands.getstatusoutput(ch_cmd)
            cmd = ("scp %s root@%s:/home/vdbench/vdb_xml" % (vdb_xml, client_ip,))
            log.info(cmd)
            res, final = commands.getstatusoutput(cmd)
            if res != 0:
                print final
                os._exit(1)
            log.info(cmd1)
            res, out = commands.getstatusoutput(cmd1)
            if res != 0:
                if need_judge:
                    pass
                else:
                    log.error("Error! Run vdbench with 'jn' error.Vdbench log path is /root/output/%s." % (str(output)))
                    os._exit(1)
            else:
                log.info("Vdbench jn log path is /root/output.")
        elif jn_jro == "jro":
            log.info(cmd2)
            res, out = commands.getstatusoutput(cmd2)
            if res != 0:
                log.error("Error! Run vdbench with 'jro' error.Vdbench log path is /root/output/%s." % (str(output)))
                os._exit(1)
            else:
                log.info("Vdbench jro log path is /root/output.")
        else:
            ch_cmd = ("sed -r -i 's/,offset=[0-9]+//g' %s" % (vdb_xml))
            commands.getstatusoutput(ch_cmd)
            ch_cmd = ("sed -r -i 's/,align=[0-9]+//g' %s" % (vdb_xml))
            commands.getstatusoutput(ch_cmd)
            change_xml(jn_on="yes", vdb_xml=vdb_xml, whether_change=whether_change_xml)
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


def get_dataip_info(node_id=None):
    ctl_ips = ReliableTest.get_ctl_ips(node_ip=deploy_ips[0], node_id=node_id)
    data_ips = ReliableTest.get_data_ips(node_ip=deploy_ips[0], node_id=node_id)
    data_eths = ReliableTest.get_eth(node_ip=ctl_ips[0], test_ip=data_ips)
    extra_ips = ReliableTest.get_extra_ips(node_ip=ctl_ips[0], node_id=node_id, vip=vip, svip=svip)
    return data_eths, extra_ips


def get_ioip_info(node_id=None):
    ctl_ips = ReliableTest.get_ctl_ips(node_ip=deploy_ips[0], node_id=node_id)
    data_ips = ReliableTest.get_data_ips(node_ip=deploy_ips[0], node_id=node_id)
    io_eths = ReliableTest.get_eth(node_ip=ctl_ips[0], test_ip=vip)
    extra_ips = ReliableTest.get_extra_ips(node_ip=ctl_ips[0], node_id=node_id, vip=vip, svip=svip)
    return io_eths, extra_ips


def prepare():
    """
    :Usage:检查集群环境
    :return: None
    """
    nodes = osan.get_nodes(s_ip=deploy_ips[0])
    # 检查所有节点IP是否正常
    # log.info("检查所有节点IP是否正常.")
    for ip in deploy_ips:
        common.check_ip(ip)
    # 检查所有节点状态是否为HEALTHY
    # log.info("检查所有节点状态是否为HEALTHY.")
    for id in nodes:
        while 'HEALTHY' not in node.get_node_state(id):
            time.sleep(20)
            log.info("等待nodeid: %s 数据修复ing" % (str(id)))
    # 检查所有磁盘状态是否为HEALTHY
    # log.info("检查所有磁盘状态是否为HEALTHY.")
    for id in nodes:
        cmd = ("ssh %s ' pscli --command=get_disks --node_ids=%s | grep DISK_STATE '" % (deploy_ips[0], str(id)))
        res, output = commands.getstatusoutput(cmd)
        # log.info(cmd)
        if res != 0:
            log.error("Get nodes failed.")
            os._exit(1)
        else:
            if 'DISK_STATE_REBUILDING_ACTIVE' in output or 'ISOLATE' in output:
                env_manage.com_bd_disk.set_rcvr(val=0)
                while 'DISK_STATE_REBUILDING_ACTIVE' in output or 'ISOLATE' in output:
                    time.sleep(10)
                    log.info("磁盘状态是: ISOLATE or DISK_STATE_REBUILDING_ACTIVE，位于节点:nodeid  %s" % (str(id)))
                    cmd = (
                        "ssh %s ' pscli --command=get_disks --node_ids=%s | grep DISK_STATE '" % (deploy_ips[0], str(id)))
                    res, output = commands.getstatusoutput(cmd)
                else:
                    env_manage.com_bd_disk.set_rcvr(val=1)


def main():
    file_name = os.path.basename(__file__)
    file_name = file_name[:-3]  # 获取本脚本名，去掉.py后缀
    log_file_path = log.get_log_path(file_name)  # 获取日志目录，即test_cases/Log/Case_log
    log.init(log_file_path, True)
    env_manage.clean_test_env()


if __name__ == '__main__':
    main()
