#!usr/bin/env python  
# -*- coding:utf-8 _*-
""" 
@author: Liu he
@file: env_manage.py 
@time: 2018/11/01 
"""

import os
import re
import sys
import time
import inspect
import random
import utils_path
import Lun_managerTest
import disk
import common
import common2
import commands
import breakdown
import log
import json
import prepare_x1000
import datetime
import env_manage
# import prepare_x1000
import get_config
from get_config import config_parser as cp
import decorator_func
import ReliableTest

# 初始化配置文件
conf_file = get_config.CONFIG_FILE  # 配置文件路径
deploy_ips = get_config.get_env_ip_info(conf_file)  # 获取集群IP列表
client_ips = get_config.get_allclient_ip()  # 获取客户端IP

case_list_path = "/home/StorTest/test_cases/cases/test_case/X1000/read_ahead/"
case_list_file = case_list_path + "param"

# 类实例化
osan = Lun_managerTest.oSan()
com_bk_os = breakdown.Os_Reliable()
com_bd_disk = breakdown.disk()
com_disk = common.Disk()
com_node = common.Node()
com2_osan = common2.oSan()
c_disk = disk.disk()


def get_osan_los_master(id):
    for ip in deploy_ips:
        node_id = com_node.get_node_id_by_ip(ip)
        cmd = ("ssh %(node_ip)s \"/home/parastor/tools/nWatch -t oSan -i %(id)s -c oSan#get_lcache\"" % {'node_ip': ip,
                                                                                                         'id': node_id})
        rc, output = commands.getstatusoutput(cmd)
        log.info(cmd)
        lun_infos_list = output.split("\n")
        lun_id_list = []
        for out in lun_infos_list:
            if "LUN ID" in out:
                lun_id = out.split(":")[-1].strip()
                lun_id_list.append(lun_id)
        chk_id_list = list(set(lun_id_list))
        for chk_id in chk_id_list:
            if int(chk_id) == id:
                log.info("Get the lun in node %s. need set read ahead lun ID is %s" % (ip, id))
                return node_id


def set_cache(id, mode, size=0, s_ip=deploy_ips[0], stype="dpc_lun_ra"):
    mode_status = {"0": "down", "1": "auto", "2": "manual", }
    node_id = com_bk_os.get_node_id_by_ip(s_ip)
    # if set_lun_node_id is None:
    for i in range(4):
        set_lun_node_id = get_osan_los_master(id)
        if set_lun_node_id is not None:
            # set_lun_node_id = get_osan_los_master(id)
            set_lun_node_ip = com_node.get_node_ip_by_id(set_lun_node_id)
            break
        if i == 3:
            log.error("get set lun node ID is :%s " % (set_lun_node_id))
            os._exit(1)
        time.sleep(60)
    if mode == "2":
        size = str(3 * 1) + "M"  # 如果mode=2 需要设置size为条带宽度*1M大小
    log.info("set read ahead osan node id: %s , node ip: %s" % (set_lun_node_id, set_lun_node_ip))
    cmd = ("ssh {} \"/home/parastor/tools/nWatch -t oSan -i {} -c oSan#{} -a \\\"{} {} {}\\\"\"".format(set_lun_node_ip,
                                                                                                        set_lun_node_id,
                                                                                                        stype, id, mode,
                                                                                                        size))
    log.info(cmd)
    res, output = commands.getstatusoutput(cmd)
    log.info(output)
    if res != 0 or "can not find lunsb" in output:
        log.info(output)
        log.error("The node %s set %s is failed, please check" % (node_id, stype))
        os._exit(1)
    else:
        time.sleep(2)
        '''验证是否生效'''
        cmd = ("ssh %s \"/home/parastor/tools/nWatch -t oSan -i %s -c oSan#dpc_lun_status -a \"%s\"\"" % (
            set_lun_node_ip, set_lun_node_id, id))
        log.info(cmd)
        rc, output = commands.getstatusoutput(cmd)
        if rc != 0:
            log.error("get lun read ahead status failed")
        elif "can not find lunsb for " in output:
            log.info("The lun have node set read ahead")
        else:
            lun_status = output.split(", ")[3].split(':')[-1].strip()
            log.info("get lun %(lunid)s lun read head status: %(status)s" % {'lunid': id, 'status': lun_status})
            if int(lun_status) == int(mode):
                log.info("The node %s set %s success.\nGet oSan#dpc_lun_status:%s " % (node_id, stype, output))
            else:
                log.error("The node %s set %s failed.\n%s " % (node_id, stype, output))
                os._exit(1)


def update_osan_params(mode):
    cmd = ("pscli --command=update_param --section=oSan --name=ldpc_ra_mode --current=%s" % (mode))
    rc, output = com2_osan.run_pscli_cmd(pscli_cmd=cmd, time_out=120, times=1)
    log.info(cmd)
    if rc != 0:
        log.info("set lun read head mode :%s failed" % (mode))
    else:
        cmd = ("pscli --command=get_params --section=oSan --name=ldpc_ra_mode")
        log.info(cmd)
        rc, output = com2_osan.run_pscli_cmd(cmd)
        if rc != 0:
            log.error("get ldpc_ra_mode failed")
        else:
            output = json.loads(output)
            mode_type = output["result"]["parameters"][0]["current"]
            log.info("check The mode :%s" % (mode))
            if int(mode) == int(mode_type):
                return mode
            else:
                log.error("get mode type:%(get_mode)s is node equal to set mode:%(set_mode)s" % {'get_mode': mode_type,
                                                                                                 'set_mode': mode})
                os._exit(1)


def gen_vdb_xml(thread=8, offset=None, align=None, lun=None, xfersize=None, rdpct=None, seekpct=None, interval=1,
                rhpct=0, startlba=0):
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
        commands.getstatusoutput(cmd)
    cmd = ("cp %s %s" % (template_file, vdb_xml))
    commands.getstatusoutput(cmd)
    if None == lun or len(lun) == 0:
        log.error("Found no scsi devices.")
        exit(1)
    if None != offset:
        cmd = ("sed -i '1s/$/,offset=%s/g' %s" % (str(offset), vdb_xml))  # 修改前偏移量
        log.info("Modify vdb_xml cmd %s" % (cmd))
        commands.getstatusoutput(cmd)
    if None != align:
        cmd = ("sed -i '1s/$/,align=%s/g' %s" % (str(align), vdb_xml))  # 修改后偏移量
        log.info("Modify vdb_xml cmd %s" % (cmd))
        commands.getstatusoutput(cmd)
    if None != rdpct:
        cmd = ("sed -i '2s/$/,rdpct=%s/g' %s" % (str(rdpct), vdb_xml))  # 修改读写占比
        log.info("Modify vdb_xml cmd %s" % (cmd))
        commands.getstatusoutput(cmd)
    if None != seekpct:
        cmd = ("sed -i '2s/$/,seekpct=%s/g' %s" % (str(seekpct), vdb_xml))  # 修改读写占比
        log.info("Modify vdb_xml cmd %s" % (cmd))
        commands.getstatusoutput(cmd)
    if None != xfersize:
        cmd = ("sed -i -r 's/xfersizes.*?\)/xfersize=%s/g' %s" % (xfersize, vdb_xml))  # 修改xferrsize
        log.info("Modify vdb_xml cmd %s" % (cmd))
        commands.getstatusoutput(cmd)
    for dev_name in lun:
        sd_xml = ("sd=sd%d,lun=%s" % (sd_num, dev_name))
        wd_xml = ("wd=wd%d,sd=sd%d,rhpct=%s" % (sd_num, sd_num, rhpct))
        cmd = ("sed -i '%da\%s' %s" % (sd_num, sd_xml, vdb_xml))  # 插入rd
        commands.getstatusoutput(cmd)
        cmd = ("sed -i '$i\%s' %s" % (wd_xml, vdb_xml))  # 插入wd
        commands.getstatusoutput(cmd)
        sd_num = sd_num + 1
        # threads.append("10")
    # threads = "3"
    # maxdata = len(lun) * 9
    cmd = ("sed -i -r 's/iorate=[0-9]+/iorate=max/g' %s" % (vdb_xml))  # 修改iorate为max
    commands.getstatusoutput(cmd)
    cmd = ("sed -i -r 's/thread.*?/threads=%s/g' %s" % (thread, vdb_xml))  # 修改每个wd的进程数
    commands.getstatusoutput(cmd)
    cmd = ("sed -i -r 's/interval.*?/interval=%s/g' %s" % (interval, vdb_xml))  # 修改每个wd的interval
    commands.getstatusoutput(cmd)
    cmd = ("sed -r -i '1idata_errors=3' %s" % (vdb_xml))
    commands.getstatusoutput(cmd)
    cmd = ("sed -r -i '1idebug=27' %s" % (vdb_xml))
    commands.getstatusoutput(cmd)
    log.info(vdb_xml)
    return vdb_xml


def get_vdbech_res(output, c_ip=client_ips[0], jn_stat=None):
    if jn_stat is None:
        output = output + "_nor"
    else:
        output = output + "_" + jn_stat
    cmd = ("ssh %s \"cd /root/output/%s;cat summary.html  |grep avg\"" % (c_ip, output))
    res, output = commands.getstatusoutput(cmd)
    if res != 0:
        log.info("get vdbench result failed")
        os._exit(1)
    else:
        result = output.split(" ")
        while '' in result:
            result.remove('')
        res_dict = {"iops": result[2], "bw": result[3], "resp": result[5]}
        return res_dict


def run_vdb(vdb_file=None, c_ip=client_ips[0], x_size="4k", rd="100", ths=1, run_time=100, file="result_file", rhpct=0):
    """
    :Auther: Liuhe
    :param x_size: 块大小
    :param rd: 100全读
    :return:
    """

    if rd == "100":
        log.info("vdbench 进行读业务:xfersize=%s" % (x_size))
        com2_osan.run_vdb(client_ip=c_ip, vdb_xml=vdb_file, output=file, time=run_time)
        value = get_vdbech_res(c_ip=c_ip, output=file)
        log.info("get performance %s" % (value))
    elif rd == "0":
        log.info("vdbench 进行写业务:xfersize=%s" % (x_size))
        com2_osan.run_vdb(client_ip=c_ip, vdb_xml=vdb_file, output=file, jn_jro="jn", time=run_time)
        com2_osan.run_vdb(client_ip=c_ip, vdb_xml=vdb_file, output=file, jn_jro="jro")
        value = get_vdbech_res(c_ip=c_ip, output=file, jn_stat="jn")
        log.info("get performance %s" % (value))
    else:
        log.info("vdbench 进行混合业务:xfersize=%s ,rdpct=%s" % (x_size, rd))
        com2_osan.run_vdb(client_ip=c_ip, vdb_xml=vdb_file, output=file, jn_jro="jn", time=run_time)
        com2_osan.run_vdb(client_ip=c_ip, vdb_xml=vdb_file, output=file, jn_jro="jro")
        value = get_vdbech_res(c_ip=c_ip, output=file, jn_stat="jn")
        log.info("get performance %s" % (value))
    return value


def get_lun_size(c_ip=None, lun=None):
    '''
    :Usage : get lun's size
    :param c_ip:
    :param lun:
    :return: int,unit:GB
    '''
    cmd = ("ssh %s \"fdisk -l %s 2> /dev/null | grep '%s' | awk -F ',| ' '{print \$3}'\"" % (c_ip, lun, lun))
    (res, output) = commands.getstatusoutput(cmd)
    if res != 0:
        log.error("Get %s size failed." % (lun))
        exit(1)
    else:
        return output


def parted_lun(c_ip=None, lun=None, min_size=None, max_size=None):
    '''
    :Usage : make a part for the disk by parted tool
    :param c_ip: host ip
    :param lun: lun to make part
    :param min_size: range
    :param max_size: range
    :return: part name
    '''
    # range_1 : min:0G,max:4G
    # range_2 : min:4G,max:16384G(16T)
    # range_3 : min:16384G,max:65536G(64T)
    # range_4 : min:65536G,max:262144G(256T)

    # Judge if the lun is exist
    cmd = ("ssh %s 'ls %s1'" % (c_ip, lun))
    (res, output) = commands.getstatusoutput(cmd)
    if res != 0:
        lun_size = get_lun_size(c_ip=c_ip, lun=lun)
        lun_size = int(lun_size.split('.')[0])
        if min_size == None or max_size == None:
            if lun_size <= 4:
                return lun
            elif lun_size <= 16384 and lun_size > 4:
                range_num = random.randint(0, 1)
                if range_num == 0:
                    min_size = random.randint(0, 4)
                    max_size = min_size + 2
                else:
                    min_size = random.randint(0, lun_size - 2)
                    max_size = min_size + 2
            elif lun_size > 16384 and lun_size <= 65536:
                range_num = random.randint(0, 2)
                if range_num == 0:
                    min_size = random.randint(0, 4)
                    max_size = min_size + 2
                elif range_num == 1:
                    min_size = random.randint(4, 16384)
                    max_size = min_size + 2
                else:
                    min_size = random.randint(16384, lun_size - 2)
                    max_size = min_size + 2
            else:
                range_num = random.randint(0, 3)
                if range_num == 0:
                    min_size = random.randint(0, 4)
                    max_size = min_size + 2
                elif range_num == 1:
                    min_size = random.randint(4, 16384)
                    max_size = min_size + 2
                elif range_num == 2:
                    min_size = random.randint(16384, 65536)
                    max_size = min_size + 2
                else:
                    min_size = random.randint(65536, lun_size - 2)
                    max_size = min_size + 2

        cmd = ("ssh %s 'parted -s %s mklabel gpt mkpart primary %sG %sG'" % (c_ip, lun, str(min_size), str(max_size)))
        (res, output) = commands.getstatusoutput(cmd)
        if res != 0:
            log.error("Parted %s and mkpart %s to %s on %s failed." % (lun, str(min_size), str(max_size), c_ip))
            exit(1)
        else:
            return lun + '1'
    else:
        return lun + '1'


def pre_run_vdb():
    lun_name = osan.ls_scsi_dev(client_ip=client_ips[0])
    vdb_file = gen_vdb_xml(lun=lun_name, xfersize="1M", rdpct="0", thread=8, rhpct=0, seekpct=0)
    run_vdb(vdb_file=vdb_file, c_ip=client_ips[0], x_size="1M", run_time=200)


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
                res = c_disk.parted_lun(c_ip=client_ips[0], lun=p_lun, min_size=min_size * 1024,
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


def run_vdb_hole(client_ip, vdb_xml, jn_jro=None, output=None, time=1200, execute="Y"):
    """
    执行vdbench
    :param client_ip:主机端IP
    :param vdb_xml:
    :param jn_jro:
    :param output:
    :param time:   执行时间
    :param execute: 是否执行vdbench，N 为不执行，非N就会执行
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
        unmap_vdb_path = os.path.dirname(vdb_path)
        vdb_hole_path = os.path.join(unmap_vdb_path, 'vdbench_unmap')  # 打洞写vdbench工具所在路径
        cmd = ("ssh %s 'mkdir -p /root/output/;mkdir -p /root/vdbench/journal/%s'" % (client_ip, str(output)))
        log.info(cmd)
        commands.getstatusoutput(cmd)
        if time != None:
            cmd1 = ("ssh %s '%s/vdbench -f %s -jn -e %s -o /root/output/%s_jn'" % (
                client_ip, vdb_hole_path, vdb_xml1, str(time), str(output)))
            cmd2 = ("ssh %s '%s/vdbench -f %s -jro -e %s -o /root/output/%s_jro'" % (
                client_ip, vdb_hole_path, vdb_xml1, str(time), str(output)))
        else:
            cmd1 = ("ssh %s '%s/vdbench -f %s -jn  -o /root/output/%s_jn'" % (
                client_ip, vdb_hole_path, vdb_xml1, str(output)))
            cmd2 = (
                    "ssh %s '%s/vdbench -f %s -jro -o /root/output/%s_jro'" % (
                client_ip, vdb_hole_path, vdb_xml1, str(output)))
        if None == jn_jro or jn_jro == "no":
            # osan.change_xml(vdb_xml=vdb_xml)
            cmd = ("scp %s root@%s:/home/vdbench/vdb_xml" % (vdb_xml, client_ip,))
            log.info(cmd)
            res, final = commands.getstatusoutput(cmd)
            if res != 0:
                print final
                os._exit(1)
            cmd = ("ssh %s '%s/vdbench -f %s -e %s -o /root/output/%s_nor'" % (
                client_ip, vdb_hole_path, vdb_xml1, str(time), str(output)))
            log.info(cmd)
            res, out = commands.getstatusoutput(cmd)
            if res != 0:
                log.error("Error! Run vdbench without data check error.")
                os._exit(1)
            else:
                pass
        elif jn_jro == "jn":
            # osan.change_xml(jn_on="yes", vdb_xml=vdb_xml)
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
            # osan.change_xml(jn_on="yes", vdb_xml=vdb_xml)
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


def clean_lun_map(ips=deploy_ips[0]):
    """
    2018-09
    :param ips: 节点IP，默认为第一个节点，忽略预设的lun map
    :return: 无
    """
    lun_map_ids = osan.get_lun_maps(ips)
    log.info("LUN map will be cleaned up. be cleaned lun map ID is %s" % (lun_map_ids))
    for lun_map_id in lun_map_ids:
        log.info("在节点 %s 删除LUN MAP ，映射ID: %s" % (ips, lun_map_id))
        osan.delete_lun_map(s_ip=ips, map_id=lun_map_id)


def clean_lun(ips=deploy_ips[0]):
    """
    删除lun ，忽略预设的lun
    :param ips:节点IP
    :return:
    """
    lun_ids = osan.get_lun(s_ip=ips)
    log.info("Get Info:\nGet lun ids:%s" % (lun_ids))
    if len(lun_ids) is None:
        log.error("Do not find the system luns, lun_ids is None")
    else:
        for lun_id in lun_ids:
            log.info("Remove the lun: %s from node:%s" % (lun_id, ips))
            osan.delete_lun(s_ip=ips, lun_id=lun_id)


def check_cache_env(disk_num=None):
    '''
    :param disk_num: 预设硬盘个数，不符合预期直接退出
    :pre_lun: 测试环境预先配置lun数量
    :return: 每个节点硬盘数组成一个列表
    '''
    log.info("Check Xstor LUN test environment")
    env_manage.check_lun_env()
    log.info("Check Node Network device")
    env_manage.check_eth()  # 检查存储端网卡
    log.info("Check Node Disk Device")
    disks = env_manage.check_disk(disk_num)  # 检查各个节点硬盘，不设置预期值将不进行对比
    log.info("Check xStor vip status")
    env_manage.check_vip_status()  # 检查VIP是否都能ping通。不通则退出
    log.info("Check Host Device")
    env_manage.check_host()  # 检查主机端scsi
    log.info("Check lun map ,if found it, will clean up")
    lun_map_ids = osan.get_lun_maps(deploy_ips[0])
    if len(lun_map_ids) > 0:
        log.info("if The system have lun maping ,will clean up")
        clean_lun_map(deploy_ips[0])
    log.info("5.Check lun ,if found it, clean up")
    lun_ids = osan.get_lun(s_ip=deploy_ips[0])
    log.info(lun_ids)
    if len(lun_ids) > 0:
        log.info("The system have lun, will clean other luns")
        clean_lun(deploy_ips[0])  # 删除多余lun
    log.info("check test environment finished")
    return disks


def re_cache_run_vdb(re_num):
    log.info("step:使用新创建的lun 写入刷新缓存")
    names = "LUN" + str(re_num)
    env_manage.create_lun(name=names, size="99999999999", type="THIN")
    log.info("step:2.create lun map")
    env_manage.create_lun_map()
    env_manage.create_iscsi_login()
    lun_name = osan.ls_scsi_dev(client_ip=client_ips[0])
    vdb_file = gen_vdb_xml(lun=lun_name[2:3], xfersize="4k", rdpct="0", thread=8, rhpct=0, seekpct=0)
    res = run_vdb(vdb_file=vdb_file, c_ip=client_ips[0], x_size="4k", run_time=100)
    return res
