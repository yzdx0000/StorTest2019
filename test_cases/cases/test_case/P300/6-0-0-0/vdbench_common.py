# -*-coding:utf-8 -*

#
# Author: caizhenxing
# date 2018/9/29
# @summary：
# @steps:
# @changelog：
#

import os
import log
import get_config
import common
import re
import sys
import datetime


class Vdbenchrun():
    """
    运行vdbench

    run_create:      创建文件，并生成校验文件
    run_write:       修改文件
    run_write_jn:    修改文件，并生成校验文件
    run_check:       校验数据正确性
    run_check_write: 校验数据正确性，然后跑一定时间的读写
    """
    def __init__(self, depth=None,
                 width=None,
                 files=None,
                 size=None,
                 shared=None,
                 openflags=None,
                 threads=None,
                 xfersize=None,
                 fileio=None,
                 fwdrate=None,
                 warmup=None,
                 pause=None,
                 format=None,
                 forrdpct=None,
                 forseekpct=None,
                 elapsed=None):
        """

        :param depth:      目录深度，默认2
        :param width:      目录宽度，默认2
        :param files:      单个目录中文件数目，默认100
        :param size:       文件大小，默认
        :param shared:     文件是否共享
        :param openflags:  文件打开方式
        :param threads:    线程数，默认100
        :param xfersize:   单次读取大小，默认
        :param fileio:     文件IO方式
        :param fwdrate:    文件系统每秒操作次数
        :param warmup:     warmup
        :param pause:      pause
        :param format:     格式化目录及文件结构
        :param forrdpct:   读写比例
        :param forseekpct: 寻道比例
        :param elapsed:    执行时间
        """

        self.depth = 2 if depth is None else depth
        self.width = 2 if width is None else width
        self.files = 100 if files is None else files
        self.size = "(4k,45,128k,15,256k,20,1m,10,10m,10)" if size is None else size
        self.shared = None if shared is None else shared
        self.openflags = "o_direct" if openflags is None else openflags
        self.threads = 100 if threads is None else threads
        self.xfersize = "(4k,50,64k,30,1m,20)" if xfersize is None else xfersize
        self.fileio = None if fileio is None else fileio
        self.fwdrate = "max" if fwdrate is None else fwdrate
        self.warmup = None if warmup is None else warmup
        self.pause = None if pause is None else pause
        self.format = None if format is None else format
        self.forrdpct = None if forrdpct is None else forrdpct
        self.forseekpct = None if forseekpct is None else forseekpct
        self.elapsed = 240 if elapsed is None else elapsed

        self.vdbench_path = get_config.get_snap_vdbench_path()
        self.tool_path = get_config.get_tools_path()
        current_time = datetime.datetime.now()
        currenttime = current_time.strftime('%y-%m-%d-%H-%M-%S')
        self.outputpath_tail = currenttime + '_' + os.path.splitext(os.path.basename(sys.argv[0]))[0]
        self.vdbench_log_path = os.path.join(os.path.dirname(get_config.get_testlog_path()), 'vdbench_log')

        return

    def run_create(self, anchor_path, journal_path, *args):
        """
        :author:             baoruobing
        :date  :             2018.04.17
        :description:        运行vdbench_create创建文件
        :param anchor_path:  数据读写的路径
        :param journal_path: 校验文件创建的路径
        :param args:         运行vdbench的ip
        :return:
        """
        self.anchor_path = anchor_path
        self.journal_path = journal_path
        """
        if 0 == len(args):
            raise Exception("please input client ip")
        """
        self.system_ips = args[0]
        """生成配置create文件"""
        self._set_create_file()

        create_file_name = os.path.join(self.tool_path, 'vdbench_datacheck', 'create')
        vdbench_ex_path = os.path.join(self.vdbench_path, 'vdbench')
        vdbench_output_path = os.path.join(self.vdbench_log_path, self.outputpath_tail, 'create')
        cmd = 'mkdir -p %s' % vdbench_output_path
        rc = common.command(cmd)
        common.judge_rc(rc, 0, "cmd:%s failed" % cmd)
        cmd = "sh %s -f %s -o %s -jn" % (vdbench_ex_path, create_file_name, vdbench_output_path)
        rc = common.command(cmd)
        return rc

    def run_write(self, anchor_path, journal_path, *args):
        """
        :author:             caizhenxing
        :date  :             2018.09.30
        :description:        运行vdbench_create创建文件
        :param anchor_path:  数据读写的路径
        :param journal_path: 校验文件创建的路径
        :param args:         运行vdbench的ip
        :return:
        """
        self.anchor_path = anchor_path
        self.journal_path = journal_path
        """
        if 0 == len(args):
            raise Exception("please input client ip")
        """
        self.system_ips = args[0]
        """生成配置create文件"""
        self._set_write_file()

        create_file_name = os.path.join(self.tool_path, 'vdbench_datacheck', 'write')
        vdbench_ex_path = os.path.join(self.vdbench_path, 'vdbench')
        vdbench_output_path = os.path.join(self.vdbench_log_path, self.outputpath_tail, 'write')
        cmd = 'mkdir -p %s' % vdbench_output_path
        rc = common.command(cmd)
        common.judge_rc(rc, 0, "cmd:%s failed" % cmd)
        cmd = "sh %s -f %s -o %s" % (vdbench_ex_path, create_file_name, vdbench_output_path)
        rc = common.command(cmd)
        return rc

    def run_clean(self, anchor_path, *args):
        """
        :author:              chenjy1
        :date  :              2018.08.15
        :description:         运行vdbench删除文件
        :param anchor_path:  数据读写的路径
        :param args:         运行vdbench的ip
        :return:
        """
        self.anchor_path = anchor_path
        if 0 == len(args):
            raise Exception("please input client ip")
        self.system_ips = args[1]
        """生成配置clean文件"""
        self._set_clean_file()

        clean_file_name = os.path.join(self.tool_path, 'vdbench_datacheck', 'clean')
        vdbench_ex_path = os.path.join(self.vdbench_path, 'vdbench')
        vdbench_output_path = os.path.join(self.vdbench_log_path, self.outputpath_tail, 'clean')
        cmd = 'mkdir -p %s' % vdbench_output_path
        rc = common.command(cmd)
        common.judge_rc(rc, 0, "cmd:%s failed" % cmd)
        cmd = "sh %s -f %s -o %s" % (vdbench_ex_path, clean_file_name, vdbench_output_path)
        rc = common.command(cmd)
        return rc

    def _set_create_file(self):
        """
        :author:      baoruobing
        :date  :      2018.04.17
        :description: 生成create配置文件
        :return:
        """
        file_content_lst = []
        """hd部分"""
        line_str = "hd=default,vdbench=%s,shell=ssh,user=root" % self.vdbench_path
        file_content_lst.append(line_str)

        if self.system_ips == ():
            line_str = "hd=h1,system=localhost"
            file_content_lst.append(line_str)
        else:
            i = 0
            for system_ip in self.system_ips:
                i += 1
                line_str = "hd=h%d,system=%s" % (i, system_ip)
                file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """fsd部分"""
        line_str = "fsd=default,depth=%d,width=%d,files=%d,size=%s,shared=yes" \
                   % (self.depth, self.width, self.files, self.size)
        file_content_lst.append(line_str)

        line_str = "fsd=fsd1,anchor=%s" % (self.anchor_path)
        file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """fwd部分"""
        line_str = "fwd=default,threads=%d,xfersize=%s" % (self.threads, self.xfersize)
        file_content_lst.append(line_str)

        if self.system_ips == ():
            line_str = "fwd=fwd1,fsd=fsd1,hd=h1"
            file_content_lst.append(line_str)
        else:
            for i in range(len(self.system_ips)):
                i += 1
                line_str = "fwd=fwd%d,fsd=fsd1,hd=h%d" % (i, i)
                file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """rd部分"""
        line_str = "rd=default,fwdrate=max,elapsed=%d,interval=1,warmup=10,pause=5" % self.elapsed
        file_content_lst.append(line_str)
        line_str = "rd=rd1,fwd=fwd*,format=(clean)"
        file_content_lst.append(line_str)
        line_str = "rd=rd2,fwd=fwd*,format=(restart,only)"
        file_content_lst.append(line_str)

        """写入配置文件"""
        file_content = '\n'.join(file_content_lst)

        create_file_name = os.path.join(self.tool_path, 'vdbench_datacheck', 'create')
        with open(create_file_name, 'w') as f:
            f.write(file_content)
        return

    def _set_write_file(self):
        """
        :author:      caizhenxing
        :date  :      2018.09.29
        :description: 生成create配置文件
        :return:
        """
        file_content_lst = []
        """设置头部分"""
        line_str = "data_errors=1"
        file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)
        """hd部分"""
        line_str = "hd=default,vdbench=%s,shell=ssh,user=root" % self.vdbench_path
        file_content_lst.append(line_str)

        if self.system_ips == ():
            line_str = "hd=h1,system=localhost"
            file_content_lst.append(line_str)
        else:
            i = 0
            for system_ip in self.system_ips:
                i += 1
                line_str = "hd=h%d,system=%s" % (i, system_ip)
                file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """fsd部分"""
        line_str = "fsd=default,depth=%d,width=%d,files=%d,size=%s" \
                   % (self.depth, self.width, self.files, self.size)
        if self.shared is not None:
            line_str += ",shared={}".format(self.shared)
        if self.openflags is not None:
            line_str += ",openflags={}".format(self.openflags)
        file_content_lst.append(line_str)

        line_str = "fsd=fsd1,anchor={}".format(self.anchor_path)
        file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """fwd部分"""
        line_str = "fwd=default,threads=%d,xfersize=%s" % (self.threads, self.xfersize)
        if self.fileio is not None:
            line_str += ",fileio={}".format(self.fileio)
        file_content_lst.append(line_str)

        if self.system_ips == ():
            line_str = "fwd=fwd1,fsd=fsd1,hd=h1"
            file_content_lst.append(line_str)
        else:
            for i in range(len(self.system_ips)):
                i += 1
                line_str = "fwd=fwd%d,fsd=fsd1,hd=h%d" % (i, i)
                file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """rd部分"""
        line_str = "rd=default,fwdrate={},elapsed={},interval=1".format(self.fwdrate, self.elapsed)
        if self.warmup is not None:
            line_str += ",warmup={}".format(self.warmup)
        if self.pause is not None:
            line_str += ",pause={}".format(self.pause)
        file_content_lst.append(line_str)
        line_str = "rd=rd1,fwd=fwd*"
        if self.format is not None:
            line_str += ",format={}".format(self.format)
        if self.forrdpct is not None:
            line_str += ",forrdpct={}".format(self.forrdpct)
        if self.forseekpct is not None:
            line_str += ",forseekpct={}".format(self.forseekpct)
        file_content_lst.append(line_str)

        """写入配置文件"""
        file_content = '\n'.join(file_content_lst)

        create_file_name = os.path.join(self.tool_path, 'vdbench_datacheck', 'write')
        with open(create_file_name, 'w') as f:
            f.write(file_content)
        return

    def _set_clean_file(self):
        """
        :author:      chenjy1
        :date  :      2018.08.15
        :description: 生成clean配置文件
        :return:
        """
        file_content_lst = []
        """hd部分"""
        line_str = "hd=default,vdbench=%s,shell=ssh,user=root" % self.vdbench_path
        file_content_lst.append(line_str)

        i = 0
        for system_ip in self.system_ips:
            i += 1
            line_str = "hd=h%d,system=%s" % (i, system_ip)
            file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """fsd部分"""
        line_str = "fsd=default,depth=%d,width=%d,files=%d,size=%s,shared=yes" \
                   % (self.depth, self.width, self.files, self.size)
        file_content_lst.append(line_str)

        line_str = "fsd=fsd1,anchor=%s" % (self.anchor_path)
        file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """fwd部分"""
        line_str = "fwd=default,threads=%d,xfersize=%s" % (self.threads, self.xfersize)
        file_content_lst.append(line_str)

        for i in range(len(self.system_ips)):
            i += 1
            line_str = "fwd=fwd%d,fsd=fsd1,hd=h%d" % (i, i)
            file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """rd部分"""
        line_str = "rd=default,fwdrate=max,elapsed=%d,interval=1,warmup=10,pause=5" % self.elapsed
        file_content_lst.append(line_str)
        line_str = "rd=rd1,fwd=fwd*,format=(clean)"
        file_content_lst.append(line_str)

        """写入配置文件"""
        file_content = '\n'.join(file_content_lst)

        clean_file_name = os.path.join(self.tool_path, 'vdbench_datacheck', 'clean')
        with open(clean_file_name, 'w') as f:
            f.write(file_content)
        return
