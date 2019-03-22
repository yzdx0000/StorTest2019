#!/usr/bin/python
# -*- encoding=utf8 -*-

#######################################################
# 脚本作者：鲍若冰
# 脚本说明：工具使用脚本
#######################################################

import os
import re
import log
import sys
import datetime

import common
import get_config
import time


class Vdbenchrun():
    """
    运行vdbench

    run_create:      创建文件，并生成校验文件
    run_write:       修改文件
    run_write_jn:    修改文件，并生成校验文件
    run_check:       校验数据正确性
    run_check_write: 校验数据正确性，然后跑一定时间的读写
    """

    def __init__(
            self,
            depth=None,
            width=None,
            files=None,
            size=None,
            threads=None,
            xfersize=None,
            elapsed=None,
            output_path=None,
            operations=None,
            format=None):
        """
        :author:         baoruobing
        :date  :         2018.04.17
        :description:    创建vdbench对象
        :param depth:    目录深度，默认2
        :param width:    目录宽度，默认2
        :param files:    单个目录中文件数目，默认100
        :param size:     文件大小，默认(512k,30,2m,35,4m,30,32m,5)
        :param threads:  线程数，默认100
        :param xfersize: 单次读取大小，默认(4k,50,64k,30,1m,20)
        :param elapsed:  写的时间，默认240s
        :param operations:  rd的操作，默认是write。非默认以'(read,write)'的方式传入
        :param format: rd的format值
        """
        self.depth = 2 if depth is None else depth
        self.width = 2 if width is None else width
        self.files = 100 if files is None else files
        self.size = "(1m,30,4m,35,8m,30,32m,5)" if size is None else size
        # self.size = "(64k,30,128k,35,256k,30,1m,5)" if size == None else size
        self.threads = 100 if threads is None else threads
        self.xfersize = "(4k,50,64k,30,1m,20)" if xfersize is None else xfersize
        self.elapsed = 240 if elapsed is None else elapsed
        self.openflags = None

        print 'init self.depth is %s' % self.depth
        print 'init self.width is %s' % self.width
        print 'init self.files is %s' % self.files

        self.vdbench_path = get_config.get_snap_vdbench_path()
        self.tool_path = get_config.get_tools_path()
        current_time = datetime.datetime.now()
        currenttime = current_time.strftime('%y-%m-%d-%H-%M-%S')
        # self.outputpath_tail = currenttime + '_' + os.path.splitext(os.path.basename(sys.argv[0]))[0]
        # self.vdbench_log_path = os.path.join(os.path.dirname(get_config.get_testlog_path()), 'vdbench_log')
        if output_path is None:
            self.vdbench_log_path = os.path.join(
                log.log_file_dir, 'vdbench_log')
        else:
            self.vdbench_log_path = output_path

        if operations is None:
            self.operations = 'write'
        else:
            '''
            operationstr = '( '
            for operation in operations:
                operationstr = operationstr + operation
            operationstr = operationstr +')'
            self.operations = operationstr
            print 'self.operations is %s' % self.operations
           '''
            self.operations = operations
        if format is None:
            self.format = 'no'
        else:
            self.format = format
        print 'format is %s' % self.format
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
        self.system_ips = args
        """生成配置create文件"""
        self._set_create_file()

        create_file_name = os.path.join(
            self.tool_path, 'vdbench_datacheck', 'create')
        vdbench_ex_path = os.path.join(self.vdbench_path, 'vdbench')
        vdbench_output_path = os.path.join(self.vdbench_log_path, 'create')
        cmd = 'mkdir -p %s' % vdbench_output_path
        rc = common.command(cmd)
        common.judge_rc(rc, 0, "cmd:%s failed" % cmd)
        cmd = "sh %s -f %s -o %s -jn" % (vdbench_ex_path,
                                         create_file_name, vdbench_output_path)
        rc = common.command(cmd)
        return rc

    def run_create_nv(self, anchor_path, *args):
        """
        :author:             wanggl
        :date  :             2018.07.28
        :description:        运行vdbench_create_nv 创建文件,不带校验
        :param anchor_path:  数据读写的路径
        :param journal_path: 校验文件创建的路径
        :param args:         运行vdbench的ip
        :return:
        """
        self.anchor_path = anchor_path
        if 0 == len(args):
            raise Exception("please input client ip")
        self.system_ips = args
        """生成配置create文件"""
        self._set_create_file_mul()

        create_file_name = os.path.join(
            self.tool_path, 'vdbench_datacheck', 'create')
        vdbench_ex_path = os.path.join(self.vdbench_path, 'vdbench')
        vdbench_output_path = os.path.join(self.vdbench_log_path, 'create')
        cmd = 'mkdir -p %s' % vdbench_output_path
        rc = common.command(cmd)
        common.judge_rc(rc, 0, "cmd:%s failed" % cmd)
        cmd = "sh %s -f %s -o %s " % (vdbench_ex_path,
                                      create_file_name, vdbench_output_path)
        rc = common.command(cmd)
        return rc

    def run_write(self, anchor_path, *args):
        """
        :author:             baoruobing
        :date  :             2018.04.17
        :description:        运行vdbench_write修改文件
        :param anchor_path:  数据读写的路径
        :param args:         运行vdbench的ip
        :return:
        """
        self.anchor_path = anchor_path
        if 0 == len(args):
            raise Exception("please input client ip")
        self.system_ips = args
        self.openflags = None
        """生成配置write文件"""
        self._set_write_file()

        write_file_name = os.path.join(
            self.tool_path, 'vdbench_datacheck', 'write')
        vdbench_ex_path = os.path.join(self.vdbench_path, 'vdbench')
        vdbench_output_path = os.path.join(self.vdbench_log_path, 'write')
        cmd = 'mkdir -p %s' % vdbench_output_path
        rc = common.command(cmd)
        common.judge_rc(rc, 0, "cmd:%s failed" % cmd)
        cmd = "sh %s -f %s -o %s" % (vdbench_ex_path,
                                     write_file_name, vdbench_output_path)
        rc = common.command(cmd)
        return rc

    def run_write_jn(self, anchor_path, journal_path, *args):
        """
        :author:             baoruobing
        :date  :             2018.04.17
        :description:        运行vdbench_write_jn修改文件
        :param anchor_path:  数据读写的路径
        :param journal_path: 校验文件创建的路径
        :param args:         运行vdbench的ip
        :return:
        """
        self.anchor_path = anchor_path
        self.journal_path = journal_path
        print 'anchor in jn is %s' % self.anchor_path
        print 'journal_path in jn is %s' % self.journal_path
        if 0 == len(args):
            raise Exception("please input client ip")
        self.system_ips = args
        """生成配置write_jn文件"""
        self._set_write_jn_file()

       # print 'self.system_ips in jn is %s' %ip
        write_file_name = os.path.join(
            self.tool_path, 'vdbench_datacheck', 'write_jn')
        vdbench_ex_path = os.path.join(self.vdbench_path, 'vdbench')
        vdbench_output_path = os.path.join(self.vdbench_log_path, 'write_jn')
        cmd = 'mkdir -p %s' % vdbench_output_path
        rc = common.command(cmd)
        common.judge_rc(rc, 0, "cmd:%s failed" % cmd)
        cmd = "sh %s -f %s -o %s -jn" % (vdbench_ex_path,
                                         write_file_name, vdbench_output_path)
        rc = common.command(cmd)
        return rc

    def run_write_dio(self, anchor_path, *args):
        """
        :author:             baoruobing
        :date  :             2018.04.17
        :description:        运行vdbench_write修改文件
        :param anchor_path:  数据读写的路径
        :param args:         运行vdbench的ip
        :return:
        """
        self.anchor_path = anchor_path
        if 0 == len(args):
            raise Exception("please input client ip")
        self.system_ips = args
        self.openflags = 'o_direct'
        """生成配置write文件"""
        self._set_write_file()

        write_file_name = os.path.join(
            self.tool_path, 'vdbench_datacheck', 'write')
        vdbench_ex_path = os.path.join(self.vdbench_path, 'vdbench')
        vdbench_output_path = os.path.join(self.vdbench_log_path, 'write')
        cmd = 'mkdir -p %s' % vdbench_output_path
        rc = common.command(cmd)
        common.judge_rc(rc, 0, "cmd:%s failed" % cmd)
        cmd = "sh %s -f %s -o %s" % (vdbench_ex_path,
                                     write_file_name, vdbench_output_path)
        rc = common.command(cmd)
        return rc

    def run_check(self, anchor_path, journal_path, *args):
        """
        :author:             baoruobing
        :date  :             2018.04.17
        :description:        运行vdbench_check校验文件
        :param anchor_path:  数据读写的路径
        :param journal_path: 校验文件创建的路径
        :param args:         运行vdbench的ip
        :return:
        """
        self.anchor_path = anchor_path
        self.journal_path = journal_path
        if 0 == len(args):
            raise Exception("please input client ip")
        self.system_ips = args
        """生成配置check文件"""
        self._set_check_file()

        check_file_name = os.path.join(
            self.tool_path, 'vdbench_datacheck', 'check')
        vdbench_ex_path = os.path.join(self.vdbench_path, 'vdbench')
        vdbench_output_path = os.path.join(self.vdbench_log_path, 'check')
        cmd = 'mkdir -p %s' % vdbench_output_path
        rc = common.command(cmd)
        common.judge_rc(rc, 0, "cmd:%s failed" % cmd)
        cmd = "sh %s -f %s -o %s -jro" % (vdbench_ex_path,
                                          check_file_name, vdbench_output_path)
        rc = common.command(cmd)
        return rc

    def run_check_write(self, anchor_path, journal_path, *args):
        """
        :author:             baoruobing
        :date  :             2018.04.17
        :description:        运行vdbench_check_write校验文件然后跑压力
        :param anchor_path:  数据读写的路径
        :param journal_path: 校验文件创建的路径
        :param args:         运行vdbench的ip
        :return:
        """
        self.anchor_path = anchor_path
        self.journal_path = journal_path
        if 0 == len(args):
            raise Exception("please input client ip")
        self.system_ips = args
        """生成配置check_write文件"""
        self._set_check_write_file()

        check_write_file_name = os.path.join(
            self.tool_path, 'vdbench_datacheck', 'check_write')
        vdbench_ex_path = os.path.join(self.vdbench_path, 'vdbench')
        vdbench_output_path = os.path.join(
            self.vdbench_log_path, 'check_write')
        cmd = 'mkdir -p %s' % vdbench_output_path
        rc = common.command(cmd)
        common.judge_rc(rc, 0, "cmd:%s failed" % cmd)
        cmd = "sh %s -f %s -o %s -jr" % (vdbench_ex_path,
                                         check_write_file_name, vdbench_output_path)
        rc = common.command(cmd)
        return rc

    def run_stress_no_jnl(self, anchor_path, *args):
        """
        :author:             baoruobing
        :date  :             2018.04.17
        :description:        运行run_stress_no_jnl跑压力
        :param anchor_path:  数据读写的路径
        :param args:         运行vdbench的ip
        :return:
        """
        self.anchor_path = anchor_path
        if 0 == len(args):
            raise Exception("please input client ip")
        self.system_ips = args
        """生成配置stress_no_jnl文件"""
        self._set_stress_no_jnl()

        check_write_file_name = os.path.join(
            self.tool_path, 'vdbench_datacheck', 'stress_no_jnl')
        vdbench_ex_path = os.path.join(self.vdbench_path, 'vdbench')
        vdbench_output_path = os.path.join(
            self.vdbench_log_path, 'stress_no_jnl')
        cmd = 'mkdir -p %s' % vdbench_output_path
        rc = common.command(cmd)
        common.judge_rc(rc, 0, "cmd:%s failed" % cmd)
        cmd = "sh %s -f %s -o %s" % (vdbench_ex_path,
                                     check_write_file_name,
                                     vdbench_output_path)
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
        self.system_ips = args
        """生成配置clean文件"""
        self._set_clean_file()

        clean_file_name = os.path.join(
            self.tool_path, 'vdbench_datacheck', 'clean')
        vdbench_ex_path = os.path.join(self.vdbench_path, 'vdbench')
        vdbench_output_path = os.path.join(self.vdbench_log_path, 'clean')
        cmd = 'mkdir -p %s' % vdbench_output_path
        rc = common.command(cmd)
        common.judge_rc(rc, 0, "cmd:%s failed" % cmd)
        cmd = "sh %s -f %s -o %s" % (vdbench_ex_path,
                                     clean_file_name, vdbench_output_path)
        rc = common.command(cmd)
        return rc

    def run_create_mulpath_diff(
            self,
            anchor_path_lst,
            journal_path_lst,
            client_lst,
            file_struct_lst,
            fsd_index=None):
        """
        :author:             chenjy1
        :date  :             2018.08.31
        :description:        运行vdbench_create创建文件 对多个路径创建，且每个路径文件结构不一样
        :param anchor_path:  数据读写的路径
        :param journal_path: 校验文件创建的路径
        :param file_struct_lst: 文件结构列表 形式: [[深度,宽度,文件数,大小],[深度,宽度,文件数,大小]......]
        :param args:         运行vdbench的ip
        :return:
        """

        common.judge_rc_unequal(len(client_lst), 0, "please input client ip")
        common.judge_rc_unequal(
            len(anchor_path_lst),
            0,
            "please input anchor path")
        common.judge_rc_unequal(
            len(journal_path_lst),
            0,
            "please input journal path")
        common.judge_rc_unequal(
            len(file_struct_lst),
            0,
            "please input file_struct_lst path")

        self.anchor_path = anchor_path_lst
        self.journal_path = journal_path_lst
        self.system_ips = client_lst
        self.file_struct = file_struct_lst
        """生成配置create文件"""
        self._set_create_mulpath_diff_file(fsd_index=fsd_index)

        create_file_name = os.path.join(
            self.tool_path,
            'vdbench_datacheck',
            'create_mulpath_diff')
        vdbench_ex_path = os.path.join(self.vdbench_path, 'vdbench')
        vdbench_output_path = os.path.join(
            self.vdbench_log_path, 'create_mulpath_diff')
        cmd = 'mkdir -p %s' % vdbench_output_path
        rc = common.command(cmd)
        common.judge_rc(rc, 0, "cmd:%s failed" % cmd)
        cmd = "sh %s -f %s -o %s" % (vdbench_ex_path,
                                     create_file_name, vdbench_output_path)
        rc = common.command(cmd)
        return rc

    def run_create_mulpath(
            self,
            anchor_path_lst,
            journal_path_lst,
            client_lst):
        """
        :author:             chenjy1
        :date  :             2018.08.22
        :description:        运行vdbench_create创建文件 对多个路径创建
        :param anchor_path:  数据读写的路径
        :param journal_path: 校验文件创建的路径
        :param args:         运行vdbench的ip
        :return:
        """

        common.judge_rc_unequal(len(client_lst), 0, "please input client ip")
        common.judge_rc_unequal(
            len(anchor_path_lst),
            0,
            "please input anchor path")
        common.judge_rc_unequal(
            len(journal_path_lst),
            0,
            "please input journal path")

        self.anchor_path = anchor_path_lst
        self.journal_path = journal_path_lst
        self.system_ips = client_lst
        """生成配置create文件"""
        self._set_create_mulpath_file()

        create_file_name = os.path.join(
            self.tool_path, 'vdbench_datacheck', 'create_mulpath')
        vdbench_ex_path = os.path.join(self.vdbench_path, 'vdbench')
        vdbench_output_path = os.path.join(
            self.vdbench_log_path, 'create_mulpath')
        cmd = 'mkdir -p %s' % vdbench_output_path
        rc = common.command(cmd)
        common.judge_rc(rc, 0, "cmd:%s failed" % cmd)
        cmd = "sh %s -f %s -o %s -jn" % (vdbench_ex_path,
                                         create_file_name, vdbench_output_path)
        rc = common.command(cmd)
        return rc

    def run_change_one_fsd(
            self,
            anchor_path_lst,
            journal_path_lst,
            client_lst,
            file_struct_lst,
            fsd_index):
        """
        :author:             chenjy1
        :date  :             2018.08.31
        :description:        运行vdbench_create创建文件 对多个路径创建，且每个路径文件结构不一样
        :param anchor_path:  数据读写的路径
        :param journal_path: 校验文件创建的路径
        :param file_struct_lst: 文件结构列表 形式: [[深度,宽度,文件数,大小],[深度,宽度,文件数,大小]......]
        :param args:         运行vdbench的ip
        :return:
        """

        common.judge_rc_unequal(len(client_lst), 0, "please input client ip")
        common.judge_rc_unequal(
            len(anchor_path_lst),
            0,
            "please input anchor path")
        common.judge_rc_unequal(
            len(journal_path_lst),
            0,
            "please input journal path")
        common.judge_rc_unequal(
            len(file_struct_lst),
            0,
            "please input file_struct_lst path")

        self.anchor_path = anchor_path_lst
        self.journal_path = journal_path_lst
        self.system_ips = client_lst
        self.file_struct = file_struct_lst
        self.fsd_index = fsd_index
        """生成配置create文件"""
        self._set_change_one_fsd()

        create_file_name = os.path.join(
            self.tool_path, 'vdbench_datacheck', 'change_one_fsd')
        vdbench_ex_path = os.path.join(self.vdbench_path, 'vdbench')
        vdbench_output_path = os.path.join(
            self.vdbench_log_path, 'change_one_fsd')
        cmd = 'mkdir -p %s' % vdbench_output_path
        rc = common.command(cmd)
        common.judge_rc(rc, 0, "cmd:%s failed" % cmd)
        cmd = "sh %s -f %s -o %s" % (vdbench_ex_path,
                                     create_file_name, vdbench_output_path)
        rc = common.command(cmd)
        return rc

    def run_check_write_mulpath(
            self,
            anchor_path_lst,
            journal_path_lst,
            client_lst):
        """
        :author:             chenjy1
        :date  :             2018.08.22
        :description:        运行vdbench_check_write校验文件然后跑压力
        :param anchor_path:  数据读写的路径
        :param journal_path: 校验文件创建的路径
        :param args:         运行vdbench的ip
        :return:
        """
        common.judge_rc_unequal(len(client_lst), 0, "please input client ip")
        common.judge_rc_unequal(
            len(anchor_path_lst),
            0,
            "please input anchor path")
        common.judge_rc_unequal(
            len(journal_path_lst),
            0,
            "please input journal path")

        self.anchor_path = anchor_path_lst
        self.journal_path = journal_path_lst
        self.system_ips = client_lst
        """生成配置check_write文件"""
        self._set_check_write_mulpath_file()

        check_write_file_name = os.path.join(
            self.tool_path, 'vdbench_datacheck', 'check_write_mulpath')
        vdbench_ex_path = os.path.join(self.vdbench_path, 'vdbench')
        vdbench_output_path = os.path.join(
            self.vdbench_log_path, 'check_write_mulpath')
        cmd = 'mkdir -p %s' % vdbench_output_path
        rc = common.command(cmd)
        common.judge_rc(rc, 0, "cmd:%s failed" % cmd)
        cmd = "sh %s -f %s -o %s -jn" % (vdbench_ex_path,
                                         check_write_file_name, vdbench_output_path)
        rc = common.command(cmd)
        return rc

    def run_create_mulpath_diff_snap_size(
            self,
            anchor_path_lst,
            journal_path_lst,
            client_lst,
            file_struct_lst):
        """
        :author:             chenjy1
        :date  :             2018.08.31
        :description:        运行vdbench_create创建文件 对多个路径创建，且每个路径文件结构不一样
        :param anchor_path:  数据读写的路径
        :param journal_path: 校验文件创建的路径
        :param file_struct_lst: 文件结构列表 形式: [[深度,宽度,文件数,大小],[深度,宽度,文件数,大小]......]
        :param args:         运行vdbench的ip
        :return:
        """

        common.judge_rc_unequal(len(client_lst), 0, "please input client ip")
        common.judge_rc_unequal(
            len(anchor_path_lst),
            0,
            "please input anchor path")
        common.judge_rc_unequal(
            len(journal_path_lst),
            0,
            "please input journal path")
        common.judge_rc_unequal(
            len(file_struct_lst),
            0,
            "please input file_struct_lst path")

        self.anchor_path = anchor_path_lst
        self.journal_path = journal_path_lst
        self.system_ips = client_lst
        self.file_struct = file_struct_lst
        """生成配置create文件"""
        self._set_create_mulpath_diff_file_snap_size()

        create_file_name = os.path.join(
            self.tool_path,
            'vdbench_datacheck',
            'create_mulpath_diff')
        vdbench_ex_path = os.path.join(self.vdbench_path, 'vdbench')
        vdbench_output_path = os.path.join(
            self.vdbench_log_path, 'create_mulpath_diff')
        cmd = 'mkdir -p %s' % vdbench_output_path
        rc = common.command(cmd)
        common.judge_rc(rc, 0, "cmd:%s failed" % cmd)
        cmd = "sh %s -f %s -o %s" % (vdbench_ex_path,
                                     create_file_name, vdbench_output_path)
        rc = common.command(cmd)
        return rc

    def run_clean_one_fsd_snapsize(
            self,
            anchor_path_lst,
            journal_path_lst,
            client_lst,
            file_struct_lst,
            fsd_index):
        """
        :author:             chenjy1
        :date  :             2018.08.31
        :description:        运行vdbench_create创建文件 对多个路径创建，且每个路径文件结构不一样
        :param anchor_path:  数据读写的路径
        :param journal_path: 校验文件创建的路径
        :param file_struct_lst: 文件结构列表 形式: [[深度,宽度,文件数,大小],[深度,宽度,文件数,大小]......]
        :param args:         运行vdbench的ip
        :return:
        """

        common.judge_rc_unequal(len(client_lst), 0, "please input client ip")
        common.judge_rc_unequal(
            len(anchor_path_lst),
            0,
            "please input anchor path")
        common.judge_rc_unequal(
            len(journal_path_lst),
            0,
            "please input journal path")
        common.judge_rc_unequal(
            len(file_struct_lst),
            0,
            "please input file_struct_lst path")

        self.anchor_path = anchor_path_lst
        self.journal_path = journal_path_lst
        self.system_ips = client_lst
        self.file_struct = file_struct_lst
        self.fsd_index = fsd_index
        """生成配置create文件"""
        self._set_clean_one_fsd_snapsize()

        create_file_name = os.path.join(
            self.tool_path,
            'vdbench_datacheck',
            'clean_one_fsd_snapsize')
        vdbench_ex_path = os.path.join(self.vdbench_path, 'vdbench')
        vdbench_output_path = os.path.join(
            self.vdbench_log_path, 'clean_one_fsd_snapsize')
        cmd = 'mkdir -p %s' % vdbench_output_path
        rc = common.command(cmd)
        common.judge_rc(rc, 0, "cmd:%s failed" % cmd)
        cmd = "sh %s -f %s -o %s" % (vdbench_ex_path,
                                     create_file_name, vdbench_output_path)
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

        line_str = "fsd=fsd1,anchor=%s,journal=%s" % (
            self.anchor_path, self.journal_path)
        file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """fwd部分"""
        line_str = "fwd=default,threads=%d,xfersize=%s" % (
            self.threads, self.xfersize)
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

        create_file_name = os.path.join(
            self.tool_path, 'vdbench_datacheck', 'create')
        with open(create_file_name, 'w') as f:
            f.write(file_content)
        return

    def _set_create_file_mul(self):
        """
        :author:      wanggl
        :date  :      2018.04.17
        :description: 生成create配置文件,fsd部分不要shared，fwd部分增加fileio使得多线程操作一个文件不冲突
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
        line_str = "fsd=default,depth=%d,width=%d,files=%d,size=%s" \
                   % (self.depth, self.width, self.files, self.size)
        file_content_lst.append(line_str)

        line_str = "fsd=fsd1,anchor=%s,journal=%s" % (
            self.anchor_path, self.journal_path)
        file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """fwd部分"""
        line_str = "fwd=default,threads=%d,xfersize=%s,fileio=(random,shared)" % (
            self.threads, self.xfersize)
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
        line_str = "rd=rd2,fwd=fwd*,format=(restart,only)"
        file_content_lst.append(line_str)

        """写入配置文件"""
        file_content = '\n'.join(file_content_lst)

        create_file_name = os.path.join(
            self.tool_path, 'vdbench_datacheck', 'create')
        with open(create_file_name, 'w') as f:
            f.write(file_content)
        return

    def _set_write_file(self):
        """
        :author:      baoruobing
        :date  :      2018.04.17
        :description: 生成write配置文件
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
        line_str = "fwd=default,threads=%d,xfersize=%s" % (
            self.threads, self.xfersize)
        file_content_lst.append(line_str)

        for i in range(len(self.system_ips)):
            i += 1
            line_str = "fwd=fwd%d,fsd=fsd1,hd=h%d,operation=write" % (i, i)
            file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """rd部分"""
        line_str = "rd=default,fwdrate=max,elapsed=%d,interval=1,warmup=1,pause=2" % self.elapsed
        file_content_lst.append(line_str)
        if self.openflags is None:
            line_str = "rd=rd1,fwd=fwd*,format=no"
        else:
            line_str = "rd=rd1,fwd=fwd*,format=no,openflags=o_direct"
        file_content_lst.append(line_str)

        """写入配置文件"""
        file_content = '\n'.join(file_content_lst)

        create_file_name = os.path.join(
            self.tool_path, 'vdbench_datacheck', 'write')
        with open(create_file_name, 'w') as f:
            f.write(file_content)
        return

    def _set_write_jn_file(self):
        """
        :author:      baoruobing
        :date  :      2018.04.17
        :description: 生成write_jn配置文件
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

        line_str = "fsd=fsd1,anchor=%s,journal=%s" % (
            self.anchor_path, self.journal_path)
        file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """fwd部分"""
        line_str = "fwd=default,threads=%d,xfersize=%s" % (
            self.threads, self.xfersize)
        file_content_lst.append(line_str)

        for i in range(len(self.system_ips)):
            i += 1
            line_str = "fwd=fwd%d,fsd=fsd1,hd=h%d,operation=write" % (i, i)
            file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """rd部分"""
        line_str = "rd=default,fwdrate=max,elapsed=%d,interval=1,warmup=10,pause=50" % self.elapsed
        file_content_lst.append(line_str)
        line_str = "rd=rd1,fwd=fwd*,format=no"
        file_content_lst.append(line_str)

        """写入配置文件"""
        file_content = '\n'.join(file_content_lst)

        create_file_name = os.path.join(
            self.tool_path, 'vdbench_datacheck', 'write_jn')
        with open(create_file_name, 'w') as f:
            f.write(file_content)
        return

    def _set_check_file(self):
        """
        :author:      baoruobing
        :date  :      2018.04.17
        :description: 生成check配置文件
        :return:
        """
        file_content_lst = []

        """data_errors部分"""
        line_str = "data_errors=1"
        file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

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

        line_str = "fsd=fsd1,anchor=%s,journal=%s" % (
            self.anchor_path, self.journal_path)
        file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """fwd部分"""
        line_str = "fwd=default,threads=%d,xfersize=%s" % (
            self.threads, self.xfersize)
        file_content_lst.append(line_str)

        for i in range(len(self.system_ips)):
            i += 1
            line_str = "fwd=fwd%d,fsd=fsd1,hd=h%d" % (i, i)
            file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """rd部分"""
        line_str = "rd=default,fwdrate=max,elapsed=30,interval=1,warmup=10,pause=5"
        file_content_lst.append(line_str)
        line_str = "rd=rd1,fwd=fwd*,format=no"
        file_content_lst.append(line_str)

        """写入配置文件"""
        file_content = '\n'.join(file_content_lst)

        create_file_name = os.path.join(
            self.tool_path, 'vdbench_datacheck', 'check')
        with open(create_file_name, 'w') as f:
            f.write(file_content)
        return

    def _set_check_write_file(self):
        """
        :author:      baoruobing
        :date  :      2018.04.17
        :description: 生成check_write配置文件
        :return:
        """
        file_content_lst = []
        """data_errors部分"""
        line_str = "data_errors=1"
        file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)
        
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

        line_str = "fsd=fsd1,anchor=%s,journal=%s" % (
            self.anchor_path, self.journal_path)
        file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """fwd部分"""
        line_str = "fwd=default,threads=%d,xfersize=%s" % (
            self.threads, self.xfersize)
        file_content_lst.append(line_str)

        for i in range(len(self.system_ips)):
            i += 1
            line_str = "fwd=fwd%d,fsd=fsd1,hd=h%d" % (i, i)
            file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """rd部分"""
        line_str = "rd=default,fwdrate=max,elapsed=%d,maxdata=20g,interval=1,warmup=10,pause=5" % self.elapsed
        file_content_lst.append(line_str)
        line_str = "rd=rd1,fwd=fwd*,format=no,forrdpct=50,forseekpct=50,foroperations=(getattr)"
        file_content_lst.append(line_str)
        line_str = "rd=rd2,fwd=fwd*,format=no,forrdpct=50,forseekpct=50,openflags=o_sync,foroperations=(setattr)"
        file_content_lst.append(line_str)
        line_str = "rd=rd3,fwd=fwd*,format=no,forrdpct=50,forseekpct=50,openflags=o_direct,foroperations=(getattr)"
        file_content_lst.append(line_str)

        """写入配置文件"""
        file_content = '\n'.join(file_content_lst)

        create_file_name = os.path.join(
            self.tool_path, 'vdbench_datacheck', 'check_write')
        with open(create_file_name, 'w') as f:
            f.write(file_content)
        return

    def _set_stress_no_jnl(self):
        """
        :author:      baoruobing
        :date  :      2018.04.17
        :description: 生成stress_no_jnl配置文件
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
        line_str = "fsd=default,depth=%d,width=%d,files=%d,size=%s" \
                   % (self.depth, self.width, self.files, self.size)
        file_content_lst.append(line_str)

        for i in range(len(self.system_ips)):
            i += 1
            line_str = "fsd=fsd%d,anchor=%s" % (i, self.anchor_path)
            file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """fwd部分"""
        line_str = "fwd=default,threads=%d,xfersize=%s" % (
            self.threads, self.xfersize)
        file_content_lst.append(line_str)

        for i in range(len(self.system_ips)):
            i += 1
            line_str = "fwd=fwd%d,fsd=fsd%d,hd=h%d" % (i, i, i)
            file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """rd部分"""
        line_str = "rd=default,fwdrate=max,elapsed=%d,interval=1,warmup=20,pause=20" % self.elapsed
        file_content_lst.append(line_str)
        line_str = "rd=rd1,fwd=fwd*,format=only"
        file_content_lst.append(line_str)
        line_str = "rd=rd2,fwd=fwd*,format=no,forrdpct=50,forseekpct=50,foroperations=(getattr)"
        file_content_lst.append(line_str)
        line_str = "rd=rd3,fwd=fwd*,format=no,forrdpct=50,forseekpct=50,openflags=o_sync,foroperations=(setattr)"
        file_content_lst.append(line_str)
        line_str = "rd=rd4,fwd=fwd*,format=no,forrdpct=50,forseekpct=50,openflags=o_direct,foroperations=(getattr)"
        file_content_lst.append(line_str)
        line_str = "rd=rd5,fwd=fwd*,format=clean"
        file_content_lst.append(line_str)

        """写入配置文件"""
        file_content = '\n'.join(file_content_lst)

        create_file_name = os.path.join(
            self.tool_path, 'vdbench_datacheck', 'stress_no_jnl')
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
        line_str = "fwd=default,threads=%d,xfersize=%s" % (
            self.threads, self.xfersize)
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

        clean_file_name = os.path.join(
            self.tool_path, 'vdbench_datacheck', 'clean')
        with open(clean_file_name, 'w') as f:
            f.write(file_content)
        return

    def _set_create_mulpath_file(self):
        """
        :author:      chenjy1
        :date  :      2018.08.22
        :description: 生成create配置文件
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
        line_str = "fsd=default,depth=%d,width=%d,files=%d,size=%s" \
                   % (self.depth, self.width, self.files, self.size)
        file_content_lst.append(line_str)

        for i, anchor_path in enumerate(self.anchor_path):
            line_str = "fsd=fsd%d,anchor=%s,journal=%s" % (
                i + 1, anchor_path, self.journal_path[i])
            file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """fwd部分"""
        line_str = "fwd=default,threads=%d,xfersize=%s" % (
            self.threads, self.xfersize)
        file_content_lst.append(line_str)

        for i in range(len(self.system_ips)):
            i += 1
            line_str = "fwd=fwd%d,fsd=fsd%d,hd=h%d" % (i, i, i)
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

        create_file_name = os.path.join(
            self.tool_path, 'vdbench_datacheck', 'create_mulpath')
        with open(create_file_name, 'w') as f:
            f.write(file_content)
        return

    def _set_check_write_mulpath_file(self):
        """
        :author:      chenjy1
        :date  :      2018.08.23
        :description: 生成check_write配置文件
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
        line_str = "fsd=default,depth=%d,width=%d,files=%d,size=%s" \
                   % (self.depth, self.width, self.files, self.size)
        file_content_lst.append(line_str)

        for i, anchor_path in enumerate(self.anchor_path):
            line_str = "fsd=fsd%d,anchor=%s,journal=%s" % (
                i + 1, anchor_path, self.journal_path[i])
            file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """fwd部分"""
        line_str = "fwd=default,threads=%d,xfersize=%s" % (
            self.threads, self.xfersize)
        file_content_lst.append(line_str)

        for i in range(len(self.system_ips)):
            i += 1
            line_str = "fwd=fwd%d,fsd=fsd%d,hd=h%d" % (i, i, i)
            file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """rd部分"""
        line_str = "rd=default,fwdrate=max,elapsed=%d,maxdata=20g,interval=1,warmup=10,pause=5" % self.elapsed
        file_content_lst.append(line_str)
        line_str = "rd=rd1,fwd=fwd*,format=no,forrdpct=50,forseekpct=50,foroperations=(getattr)"
        file_content_lst.append(line_str)
        line_str = "rd=rd2,fwd=fwd*,format=no,forrdpct=50,forseekpct=50,openflags=o_sync,foroperations=(setattr)"
        file_content_lst.append(line_str)
        line_str = "rd=rd3,fwd=fwd*,format=no,forrdpct=50,forseekpct=50,openflags=o_direct,foroperations=(getattr)"
        file_content_lst.append(line_str)

        """写入配置文件"""
        file_content = '\n'.join(file_content_lst)

        create_file_name = os.path.join(
            self.tool_path,
            'vdbench_datacheck',
            'check_write_mulpath')
        with open(create_file_name, 'w') as f:
            f.write(file_content)
        return

    def _set_create_mulpath_diff_file(self, fsd_index=None):
        """
        :author:      chenjy1
        :date  :      2018.08.31
        :description: 生成create配置文件
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

        for i, anchor_path in enumerate(self.anchor_path):
            line_str = "fsd=fsd%d,anchor=%s,depth=%d,width=%d,files=%d,size=%s" \
                       % (i + 1, anchor_path,
                          self.file_struct[i][0],
                          self.file_struct[i][1], self.file_struct[i][2], self.file_struct[i][3])
            file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """fwd部分"""
        line_str = "fwd=default,threads=%d,xfersize=%s" % (
            self.threads, self.xfersize)
        file_content_lst.append(line_str)

        for i in range(len(self.anchor_path)):
            i += 1
            index = (i - 1) % len(self.system_ips)
            line_str = "fwd=fwd%d,fsd=fsd%d,hd=h%s" % (i, i, index + 1)
            file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """rd部分"""
        line_str = "rd=default,fwdrate=max,elapsed=%d,interval=1,warmup=10,pause=5" % self.elapsed
        file_content_lst.append(line_str)
        if fsd_index is None:
            line_str = "rd=rd1,fwd=fwd*,format=(restart, only)"
        else:
            line_str = "rd=rd1,fwd=fwd%s,format=(restart, only)" % fsd_index
        file_content_lst.append(line_str)

        """写入配置文件"""
        file_content = '\n'.join(file_content_lst)

        create_file_name = os.path.join(
            self.tool_path,
            'vdbench_datacheck',
            'create_mulpath_diff')
        with open(create_file_name, 'w') as f:
            f.write(file_content)
        return

    def _set_change_one_fsd(self):
        """
        :author:      chenjy1
        :date  :      2018.08.31
        :description: 改变某个fsd中的文件内容
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

        for i, anchor_path in enumerate(self.anchor_path):
            line_str = "fsd=fsd%d,anchor=%s,depth=%d,width=%d,files=%d,size=%s" \
                       % (i + 1, anchor_path, self.file_struct[i][0],
                          self.file_struct[i][1], self.file_struct[i][2], self.file_struct[i][3])
            file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """fwd部分"""
        line_str = "fwd=default,threads=%d,xfersize=%s" % (
            self.threads, self.xfersize)
        file_content_lst.append(line_str)

        for i in range(len(self.anchor_path)):
            i += 1
            index = (i - 1) % len(self.system_ips)
            line_str = "fwd=fwd%d,fsd=fsd%d,hd=h%s" % (i, i, index + 1)
            file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """rd部分"""
        line_str = "rd=default,fwdrate=max,elapsed=%d,interval=1,warmup=10,pause=5" % self.elapsed
        file_content_lst.append(line_str)
        line_str = "rd=rd1,fwd=fwd%d,format=no,forrdpct=0" % self.fsd_index
        file_content_lst.append(line_str)

        """写入配置文件"""
        file_content = '\n'.join(file_content_lst)

        create_file_name = os.path.join(
            self.tool_path, 'vdbench_datacheck', 'change_one_fsd')
        with open(create_file_name, 'w') as f:
            f.write(file_content)
        return

    def _set_create_mulpath_diff_file_snap_size(self):
        """
        :author:      chenjy1
        :date  :      2018.08.31
        :description: 生成create配置文件
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

        for i, anchor_path in enumerate(self.anchor_path):
            line_str = "fsd=fsd%d,anchor=%s,depth=%d,width=%d,files=%d,size=%s" \
                       % (i + 1, anchor_path,
                          self.file_struct[i][0],
                          self.file_struct[i][1], self.file_struct[i][2], self.file_struct[i][3])
            file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """fwd部分"""
        line_str = "fwd=default,threads=%d,xfersize=%s" % (
            self.threads, self.xfersize)
        file_content_lst.append(line_str)

        for i in range(len(self.anchor_path)):
            i += 1
            index = (i - 1) % len(self.system_ips)
            line_str = "fwd=fwd%d,fsd=fsd%d,hd=h%s" % (i, i, index + 1)
            file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """rd部分"""
        line_str = "rd=default,fwdrate=max,elapsed=%d,interval=1,warmup=10,pause=5" % self.elapsed
        file_content_lst.append(line_str)
        line_str = "rd=rd1,fwd=fwd*,format=yes"
        file_content_lst.append(line_str)

        """写入配置文件"""
        file_content = '\n'.join(file_content_lst)

        create_file_name = os.path.join(
            self.tool_path,
            'vdbench_datacheck',
            'create_mulpath_diff')
        with open(create_file_name, 'w') as f:
            f.write(file_content)
        return

    def _set_clean_one_fsd_snapsize(self):
        """
        :author:      chenjy1
        :date  :      2018.08.31
        :description: 改变某个fsd中的文件内容
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

        for i, anchor_path in enumerate(self.anchor_path):
            line_str = "fsd=fsd%d,anchor=%s,depth=%d,width=%d,files=%d,size=%s" \
                       % (i + 1, anchor_path, self.file_struct[i][0],
                          self.file_struct[i][1], self.file_struct[i][2], self.file_struct[i][3])
            file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """fwd部分"""
        line_str = "fwd=default,threads=%d,xfersize=%s" % (
            self.threads, self.xfersize)
        file_content_lst.append(line_str)

        for i in range(len(self.anchor_path)):
            i += 1
            index = (i - 1) % len(self.system_ips)
            line_str = "fwd=fwd%d,fsd=fsd%d,hd=h%s" % (i, i, index + 1)
            file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """rd部分"""
        line_str = "rd=default,fwdrate=max,elapsed=%d,interval=1,warmup=10,pause=5" % self.elapsed
        file_content_lst.append(line_str)
        line_str = "rd=rd1,fwd=fwd%d,format=clean,forrdpct=0" % self.fsd_index
        file_content_lst.append(line_str)

        """写入配置文件"""
        file_content = '\n'.join(file_content_lst)

        create_file_name = os.path.join(
            self.tool_path,
            'vdbench_datacheck',
            'clean_one_fsd_snapsize')
        with open(create_file_name, 'w') as f:
            f.write(file_content)
        return

    def _set_create_and_check_file(self, vdbflagname, casename):
        """
        :author:      liuyzhb
        :date  :      2019.01.15
        :description: 生成一个vdbench配置文件，此配置文件可以直接用-jn执行，他会直接创建文件创建完了不断的读写校验
        param: vdbflagname :vdbench生成的配置文件的名称
        :return: 将vdbench生成的配置文件全路径返回
        """
        file_content_lst = []
        first_line = "data_errors=1"
        file_content_lst.append(first_line)
        """hd部分"""
        vdbench_path = os.path.join(self.tool_path, 'vdbench50406')
        line_str = "hd=default,vdbench=%s,shell=ssh,user=root" % vdbench_path
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

        '''
        print 'self.depth in fsd is %s' %self.depth
        print 'self.width in fsd is %s' %self.width
        print 'self.files in fsd is %s' %self.files

        """fsd部分"""
        if not isinstance(self.depth, int):
            print 'aaa self.depth is not int'
            print 'aaa self.depth in fsd is %s' % self.depth
            self.depth = int(self.depth)
        if not isinstance(self.width, int):
            self.width = int(self.width)
        if not isinstance(self.files, int):
            self.files = int(self.files)
        '''
        line_str = "fsd=default,depth=%d,width=%d,files=%d,size=%s" \
                   % (self.depth, self.width, self.files, self.size)
        file_content_lst.append(line_str)

        anchor_path = os.path.join(self.anchor_path, casename)
        line_str = "fsd=fsd1,anchor=%s,journal=%s" % (
            anchor_path, self.journal_path)
        file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """fwd部分"""
        line_str = "fwd=default,threads=%d,xfersize=%s" % (
            self.threads, self.xfersize)
        file_content_lst.append(line_str)

        if self.system_ips == ():
            line_str = "fwd=fwd1,fsd=fsd1,hd=h1，operations=%s" % self.operations
            file_content_lst.append(line_str)
        else:
            for i in range(len(self.system_ips)):
                i += 1
                line_str = "fwd=fwd%d,fsd=fsd1,hd=h%d, operations=%s" % (
                    i, i, self.operations)
                file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """rd部分"""
        line_str = "rd=default,fwdrate=max,elapsed=%d,interval=1,warmup=10,pause=5" % self.elapsed
        file_content_lst.append(line_str)
        line_str = "rd=rd1,fwd=fwd*,format=%s" % (self.format)
        file_content_lst.append(line_str)

        """写入配置文件"""
        file_content = '\n'.join(file_content_lst)

        vdb_file_name = vdbflagname + casename
        create_file_name = os.path.join(
            self.tool_path, 'vdbench_datacheck', vdb_file_name)
        with open(create_file_name, 'w') as f:
            f.write(file_content)
        return create_file_name

    def run_create_and_operations_jn(
            self,
            casename,
            anchor_path,
            journal_path,
            vdbflagname,
            jn_check_internal_step,
            jn_map_storage_time,
            *args):
        """
        :author:             lyzhb
        :date  :             2018.01.15
        :description:        把_set_create_and_check_file生成的文件进行vdbench运行
        :param anchor_path:  数据读写的路径
        :param journal_path: 校验文件创建的路径
        :ip:                 运行vdbench的ip
        :jn_check_internal_step: vdbench校验的时间间隔
        :jn_map_storage_time: vdbench的map中存储多长时间段的IO
        :return:
        """
        self.anchor_path = anchor_path
        journalname = casename + '_' + vdbflagname + 'jnl'
        current_path = os.path.dirname(
            os.path.dirname(os.path.realpath(__file__)))
        self.journal_path = os.path.join(journal_path, journalname)

        print ' run_create_and_operations_jn anchor in jn is %s' % self.anchor_path
        print ' run_create_and_operations_jn in jn is %s' % self.journal_path

        if len(args) == 0:
            raise Exception("please input client ip")
        self.system_ips = args

        """到每一个hd里面去创建所需的journal文件夹"""
        cmd = 'ls %s' % self.journal_path
        for node_ip in self.system_ips:
            rc, stdout = common.run_command(
                node_ip, cmd, print_flag=True, timeout=120)
            if rc != 0:
                cmd1 = 'mkdir %s' % self.journal_path
                rc, stdout = common.run_command(
                    node_ip, cmd1, print_flag=True, timeout=120)
        print ' run_create_and_operations_jn  self.depth in jn is %s' % self.depth
        print ' run_create_and_operations_jn  self.width in jn is %s' % self.width
        """生成配置create_and_check_file文件"""
        write_file_name = self._set_create_and_check_file(
            vdbflagname, casename)

        vdbench_ex_path = os.path.join(
            self.tool_path, 'vdbench50406', 'vdbench')
        #vdbench_ex_path = os.path.join(self.vdbench_path, 'vdbench')
        outputname = casename + '_' + vdbflagname + 'output'
        current_path = os.path.dirname(
            os.path.dirname(os.path.realpath(__file__)))

        vdbench_output_path = os.path.join(
            current_path, 'log', 'vdbench_log', outputname)
        #vdbench_output_path = os.path.join(self.vdbench_log_path, outputname)
        cmd = 'mkdir -p %s' % vdbench_output_path
        rc = common.command(cmd)
        common.judge_rc(rc, 0, "cmd:%s failed" % cmd)
        print 'output of %s' % vdbench_output_path
        cmd = "sh %s -f %s -o %s -jn -d 27 -d 134 -g %s -h %s" % (
            vdbench_ex_path, write_file_name, vdbench_output_path, jn_check_internal_step, jn_map_storage_time)
        print 'run_create_cmd_operations_jn cmd of %s is %s ' % (vdbflagname, cmd)
        rc = common.command(cmd)
        print 'vdbench -jn is running'
        return rc


##############################################################################
# ##name  :      vdbench_run
# ##parameter:   node1_ip:客户端节点1的ip node2_ip:客户端节点2的ip
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 运行vdbench进行文件创建和数据校验
##############################################################################
def vdbench_run(
        anchor_path,
        node1_ip,
        node2_ip,
        run_create=False,
        run_check_write=False,
        run_write=False,
        run_write_dio=False,
        run_check=False):
    """
    :author:                baoruobing
    :date  :                2018.04.17
    :Description:           获取集群中的core文件信息
    :param anchor_path:     vdbench运行路径
    :param node1_ip:        节点1的ip
    :param node2_ip:        节点2的ip
    :param run_create:      是否跑create,默认:不跑
    :param run_check_write: 是否跑check_write,默认:不跑
    :param run_write:       是否跑write,默认:不跑
    :param run_write_dio:   是否跑write_dio,默认:不跑
    :param run_check:       是否跑check,默认:不跑
    :return:
    """
    obj_vdbench = Vdbenchrun()
    if run_create is True:
        rc = obj_vdbench.run_create(anchor_path, '/tmp', node1_ip, node2_ip)
        if rc != 0:
            log.error('rc = %d' % rc)
            raise Exception("vdbench create failed!!!!!!")

    if run_check_write is True:
        rc = obj_vdbench.run_check_write(
            anchor_path, '/tmp', node1_ip, node2_ip)
        if rc != 0:
            raise Exception("vdbench check_write failed!!!!!!")

    if run_write is True:
        rc = obj_vdbench.run_write(anchor_path, node1_ip, node2_ip)
        if rc != 0:
            raise Exception("vdbench write failed!!!!!!")

    if run_write_dio is True:
        rc = obj_vdbench.run_write_dio(anchor_path, node1_ip, node2_ip)
        if rc != 0:
            raise Exception("vdbench write_dio failed!!!!!!")

    if run_check is True:
        rc = obj_vdbench.run_check(anchor_path, '/tmp', node1_ip, node2_ip)
        if rc != 0:
            raise Exception("vdbench check failed!!!!!!")
    return


##############################################################################
# ##name  :      iozone_run
# ##parameter:   node_count：对几个节点运行
#                line_per_node：每个node有line_per_node行
#                运行命令：iozone -t [run_thread] -s [size] -r [xfersize] -+m [这个参数在函数内部]  -w
#                path参数为对哪个目录iozone
# ##author:      chenjinyu
# ##date  :      2018.07.12
# ##Description: 集群运行iozone
##############################################################################
def iozone_run(node_count, line_per_node, path, run_thread, size, xfersize):
    log.info("\t[ iozone_run ]")
    log.info("prepare iozone config file")
    tools_path = get_config.get_tools_path()
    iozone_file_path = tools_path + '/iozone/iozonetest'

    # 清除旧的iozone配置文件
    if iozone_file_path == '' or re.match(
            r'[/\*]*$', iozone_file_path) is not None:
        log.warn('-----There is a dangerous command!!!-----')
        return -1, None
    else:
        cmd = 'rm -rf %s' % iozone_file_path
        rc = common.command(cmd)
        if rc != 0:
            log.info("rm -rf iozonefile failed!!!!!!")

    # 开始按设定的参数写入配置文件
    file_object = open(iozone_file_path, 'w')
    for i in range(node_count):
        for j in range(line_per_node):
            node_ip_tmp = get_config.get_client_ip(i)
            file_object.write(node_ip_tmp + '   ')
            file_object.write(path + '   ' + 'iozone' + '\n')
    file_object.close()
    # 执行iozone
    cmd = 'iozone -t %d -s %s -r %s -+m %s -+d -w' % (
        run_thread, size, xfersize, iozone_file_path)
    log.info("start run iozone")
    rc = common.command(cmd)
    return rc
##############################################################################
# ##name  :      iozone_run_faultrun
# ##parameter:   node_count：对几个节点运行
#                line_per_node：每个node有line_per_node行
#                运行命令：iozone -t [run_thread] -s [size] -r [xfersize] -+m [这个参数在函数内部]  -w
#                path参数为对哪个目录iozone
#                ips:执行iozone的节点ip列表
#                flag:iozone配置文件的名称标志
#                num:iozone命令执行的次数
# ##author:      liuyzhb
# ##date  :      2019.02.17
# ##Description: 集群运行iozone,iozone配置文件中的节点ip来自于p300_s3_config.xml文件的nas和私有客户端ip
##############################################################################


def iozone_run_faultrun(
        node_count,
        line_per_node,
        path,
        run_thread,
        size,
        xfersize,
        ips,
        flag,
        num):
    log.info("\t[ iozone_run ]")
    log.info("prepare iozone config file")
    tools_path = get_config.get_tools_path()
    iozone_file_path = tools_path + '/iozone/iozonetest' + flag

    # 清除旧的iozone配置文件
    if iozone_file_path == '' or re.match(
            r'[/\*]*$', iozone_file_path) is not None:
        log.warn('-----There is a dangerous command!!!-----')
        return -1, None
    else:
        cmd = 'rm -rf %s' % iozone_file_path
        rc = common.command(cmd)
        if rc != 0:
            log.info("rm -rf iozonefile failed!!!!!!")

    # 开始按设定的参数写入配置文件
    file_object = open(iozone_file_path, 'w')
    for i in range(len(ips)):
        for j in range(line_per_node):
            node_ip_tmp = ips[i]
            file_object.write(node_ip_tmp + '   ')
            file_object.write(path + '   ' + 'iozone' + '\n')
    file_object.close()
    # 执行iozone
    cmd = 'iozone -t %d -s %s -r %s -+m %s -i 0 -w' % (
        run_thread, size, xfersize, iozone_file_path)
    print cmd
    for i in range(num):
        print "start run iozone num %d " % i
        rc = common.command(cmd)
    return rc


class Testlink:
    """
    :author:      baorb
    :date  :      2018.12.11
    :description: testlink接口
    """
    server_url = get_config.get_tl_url()
    devkey = get_config.get_tl_devkey()

    def __init__(self):
        import testlink

        tlh = testlink.TestLinkHelper(
            server_url=self.server_url,
            devkey=self.devkey)
        self.tlserver = tlh.connect(testlink.TestlinkAPIClient)

    def reportTCResult(
            self,
            testplanid,
            testcaseexternalid,
            buildid,
            status,
            execduration,
            platformname,
            notes=None):
        """上报执行结果"""
        return self.tlserver.reportTCResult(
            testplanid=testplanid,
            testcaseexternalid=testcaseexternalid,
            buildid=buildid,
            status=status,
            execduration=execduration,
            platformname=platformname,
            notes=notes)

    def listProjects(self):
        """列举项目"""
        return self.tlserver.listProjects()

    def getProjects(self):
        """获取项目"""
        return self.tlserver.getProjects()

    def getTestProjectByName(self, testprojectname):
        return self.tlserver.getTestProjectByName(
            testprojectname=testprojectname)

    def getinfo(self):
        return self.tlserver.about()

    def getProjectTestPlans(self, testprojectid):
        """获取项目中的测试计划"""
        return self.tlserver.getProjectTestPlans(testprojectid=testprojectid)

    def getTestPlanIdByName(self, testprojectname, testplanname):
        """通过名字获取测试计划的id"""
        return self.tlserver.getTestPlanByName(
            testprojectname=testprojectname,
            testplanname=testplanname)[0]['id']

    def getTestSuitesForTestPlan(self, testplanid):
        """获取测试计划中的测试用例集"""
        return self.tlserver.getTestSuitesForTestPlan(testplanid=testplanid)

    def getTestCasesForTestPlan(self, testplanid, details='simple'):
        return self.tlserver.getTestCasesForTestPlan(
            testplanid=testplanid, details=details)

    def getLatestBuildIdForTestPlan(self, testplanid):
        return self.tlserver.getLatestBuildForTestPlan(
            testplanid=testplanid)['id']

    def getTestSuite_id(self, testsuitename, prefix):
        """通过测试用例集的名字获取id"""
        testsuite_info = self.tlserver.getTestSuite(testsuitename, prefix)
        for mem, mem1 in testsuite_info[0].items():
            print mem, mem1
        return testsuite_info[0]['id']

    def getTestCasesForTestSuite(self, testsuiteid):
        """获取测试用例集中的用例"""
        return self.tlserver.getTestCasesForTestSuite(testsuiteid=testsuiteid)

    def getTestCase(self, testcaseexternalid=None):
        """通过id获取测试用例"""
        return self.tlserver.getTestCase(testcaseexternalid=testcaseexternalid)

    def getTestCaseIDByName(self, testcasename):
        """通过名字获取测试用例id"""
        return self.tlserver.getTestCaseIDByName(testcasename)

    def getLastExecutionResult(self, testplanid, testcaseexternalid):
        return self.tlserver.getLastExecutionResult(
            testplanid=testplanid, testcaseexternalid=testcaseexternalid)

    def report_tl_result(
            self,
            project_name,
            testplan_name,
            case_ext_id,
            result,
            execduration,
            platformname,
            notes=None):
        """
        :description:         上传结果到testlink
        :param project_name:  项目名字
        :param testplan_name: 测试计划名字
        :param case_ext_id:   用例id
        :param result:        结果
        :param execduration:  执行时间
        """
        testplan_id = self.getTestPlanIdByName(
            testprojectname=project_name, testplanname=testplan_name)
        build_id = self.getLatestBuildIdForTestPlan(testplan_id)
        self.reportTCResult(
            testplan_id,
            case_ext_id,
            build_id,
            result,
            execduration,
            platformname,
            notes=notes)

    def get_tc_external_id_in_testplan(
            self,
            project_name,
            testplan_name,
            details='simple'):
        """获取testplan下的所有用例的外部id"""
        testplan_id = self.getTestPlanIdByName(
            testprojectname=project_name, testplanname=testplan_name)
        all_testcase_info_dic = self.getTestCasesForTestPlan(
            testplanid=testplan_id, details=details)
        tc_external_id_lst = []
        for tc_lst in all_testcase_info_dic.values():
            for testcase in tc_lst:
                tc_external_id_lst.append(testcase['full_external_id'])
        return tc_external_id_lst


def get_tl_case(script_name):
    """
    :author:            baorb
    :date  :            2018.12.11
    :description:       检查脚本是否和testlink用例关联,用例中需要用以下格式, # testlink case: 3.0-342~356,3.0-1243,3.0-235
    :param script_name: 脚本名称
    """
    tl_case_lst = []
    with open(script_name, 'r') as f:
        for line in f.readlines():
            if '# testlink case:' in line:
                tl_case_str = line.split(':', 1)[-1]
                tl_case_tmp_lst = tl_case_str.split(',')
                for tl_case in tl_case_tmp_lst:
                    if '~' in tl_case:
                        case_full_begin = tl_case.split('~')[0]
                        case_full_end = tl_case.split('~')[-1]
                        if '-' not in case_full_begin:
                            continue
                        else:
                            case_prefix = case_full_begin.split('-')[0]
                            case_begin = case_full_begin.split('-')[-1]
                            case_end = case_full_end.split('-')[-1]
                            for i in range(int(case_begin), int(case_end) + 1):
                                case_full_name = '%s-%s' % (case_prefix, i)
                                tl_case_lst.append(case_full_name.strip())
                    else:
                        tl_case_lst.append(tl_case.strip())
                break
    tl_case_lst = sorted(set(tl_case_lst))
    return tl_case_lst


def report_tl_case_result(script_name, result, exetime, notes=None):
    """
    :author:             baorb
    :date  :             2018.12.11
    :description:        上传脚本执行结果到testlink
    :param script_name:  脚本名
    :param result:       脚本执行结果
    :param exetime:      脚本执行时间, s
    """
    tl_case_script_lst = get_tl_case(script_name)
    if len(tl_case_script_lst) == 0:
        return
    execduration = round(float(exetime) / 60, 2)
    tl_project_name = get_config.get_tl_projectname()
    tl_testplan_name = get_config.get_tl_planname()
    tl_platform_name = get_config.get_tl_platformname()

    tl = Testlink()
    tc_external_id_lst = tl.get_tc_external_id_in_testplan(
        tl_project_name, tl_testplan_name)
    for case_id in tl_case_script_lst:
        if case_id not in tc_external_id_lst:
            continue
        else:
            tl.report_tl_result(
                project_name=tl_project_name,
                testplan_name=tl_testplan_name,
                case_ext_id=case_id,
                result=result,
                execduration=execduration,
                platformname=tl_platform_name,
                notes=notes)


if __name__ == "__main__":
    vdb = Vdbenchrun(operations=['read', 'write'], format='yes')
    vdb._set_create_and_check_file()