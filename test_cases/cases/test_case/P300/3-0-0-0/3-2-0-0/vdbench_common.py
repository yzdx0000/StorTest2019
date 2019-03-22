# -*-coding:utf-8 -*

#
# Author: caizhenxing
# date 2018/11/14
# @summary：
# @steps:
# @changelog：
#

import os
import sys
import csv
import log
import get_config
import common


class Vdbenchrun:
    """
    运行vdbench

    run_write:       生成vdbench配置文件
    """
    def __init__(self,
                 data_error=None,
                 case_id=None,
                 host=None,
                 depth=None,
                 width=None,
                 files=None,
                 size=None,
                 shared=None,
                 openflags=None,
                 threads=None,
                 small_xfersize=None,
                 big_xfersize=None,
                 operation=None,
                 fwdrate=None,
                 warmup=None,
                 pause=None,
                 format=None,
                 elapsed=None,
                 output=None,
                 truncate=None,
                 align=None,
                 validate=None,
                 shared_folder=None,
                 shared_file=None,
                 ln_operation=None,
                 is_windows=False,
                 file_name=None):
        """
        :author:             caizhenxing
        :date  :             2018.11.13
        :description:        初始化各参数
        :param data_error:  vdbench停止运行的error次数，默认为1
        :param host:        运行vdbench节点
        :param depth:       目录深度，默认2
        :param width:       目录宽度，默认2
        :param files:       单个目录中文件数目，默认100
        :param size:        文件大小，默认
        :param shared:      文件是否共享
        :param openflags:   文件打开方式
        :param threads:     线程数，默认100
        :param small_xfersize:   小数据块
        :param big_xfersize:   大数据块
        :param operation:    读写操作
        :param fwdrate:     文件系统每秒操作次数
        :param warmup:      warmup
        :param pause:       pause
        :param format:      格式化目录及文件结构
        :param elapsed:     执行时间
        :param truncate:    是否执行truncate操作
        :param align:       是否对齐
        """

        self.data_error = 1 if data_error is None else data_error
        self.case_id = case_id
        self.host = host
        self.depth = 2 if depth is None else depth
        self.width = 2 if width is None else width
        self.files = 100 if files is None else files
        self.size = "(4k,35,128k,30,1m,20,10m,10,100m,5)" if size is None else size
        self.shared = None if shared is None else shared
        self.openflags = None if openflags is None else openflags
        self.threads = 100 if threads is None else threads
        self.small_xfersize = "(4k,25,16k,25,64k,25,128k,25)" if small_xfersize is None or small_xfersize is '' else small_xfersize
        self.big_xfersize = "(256k,25,512k,25,1024k,25,4096k,25)" if big_xfersize is None or big_xfersize is '' else big_xfersize
        self.fwdrate = "max" if fwdrate is None else fwdrate
        self.warmup = None if warmup is None else warmup
        self.pause = None if pause is None else pause
        self.operation = None if operation is None else operation
        self.format = None if format is None else format
        self.elapsed = 900 if elapsed is None else elapsed
        self.truncate = 'no' if truncate is None else truncate
        self.align = 'yes' if align is None else align
        self.validate = 'yes' if validate is None else validate
        self.shared_folder = 'no' if shared_folder is None else shared_folder
        self.shared_file = 'no' if shared_file is None else shared_file
        self.ln_operation = ln_operation

        self.vdbench_path = get_config.get_vdbench_path()
        self.is_windows = is_windows
        self.tool_path = get_config.get_tools_path()
        self.vdbench_output_path = ''

        self.fsd_lst = []
        self.glb_lst = []
        self.outputpath_tail = output
        self.anchor_path = ''
        self.ln_path = []
        self.all_path = []
        self.system_ips = ''
        self.vdbench_log_path = os.path.join(os.path.dirname(get_config.get_testlog_path()), 'vdbench_log')
        self.client_ip = get_config.get_allclient_ip()
        self.file_name = file_name

        return

    def run_vdb(self, anchor_path, journal_path, client_ip_list, only_create=False, only_clean=False, **args):
        """
        :author:             caizhenxing
        :date  :             2018.11.13
        :description:        生成vdbench配置文件并运行vdbench测试
        :param anchor_path:  数据读写的路径
        :param journal_path: 校验文件创建的路径
        :return:
        """
        self.anchor_path = anchor_path
        self.journal_path = journal_path

        self.system_ips = client_ip_list

        for i in range(len(self.system_ips) - 1):
            self.ln_path.append(os.path.join(anchor_path, 'ln%d' % i))

        self.all_path.append(os.path.join(anchor_path, 'vdbench1'))
        for p in self.ln_path:
            self.all_path.append(os.path.join(p, 'vdbench1'))
        """生成配置create文件"""
        self._set_write_file(only_create, only_clean)

        create_file_name = os.path.join(self.tool_path, 'vdbench_datacheck', '%s_write' % self.file_name)

        vdbench_ex_path = os.path.join(self.vdbench_path, 'vdbench')
        self.base_case_path = os.path.join(self.vdbench_log_path, self.outputpath_tail)
        vdbench_output_path = os.path.join(self.base_case_path, self.case_id)
        cmd = 'mkdir -p %s' % vdbench_output_path
        rc = common.command(cmd)
        self.mk_dir(journal_path)
        # self.mk_journal_dir(journal_path)
        # self.mk_dir(anchor_path)
        common.judge_rc(rc, 0, "cmd:%s failed" % cmd)

        if only_create:
            vdb_output_path = os.path.join(vdbench_output_path, 'create')
        elif only_clean:
            vdb_output_path = os.path.join(vdbench_output_path, 'clean')
        else:
            vdb_output_path = os.path.join(vdbench_output_path, 'read_write')

        self.vdbench_output_path = vdb_output_path

        cmd = "sh %s -f %s -o %s" % (vdbench_ex_path, create_file_name, vdb_output_path)
        if self.truncate == 'yes':
            cmd += " -d86"
        elif self.validate == 'yes':
            cmd += " -v"
        else:
            cmd += ' -d27'
        rc = common.command(cmd)
        return rc

    def get_results(self, currenttime, rc, case_file):
        """
        :author:             caizhenxing
        :date  :             2018.11.13
        :description:
                             1. 在log存放路径生成Excel测试结果，记录case_id，case执行结果，iops，延迟，带宽
                             2. 更新case列表中的Result_Flag标识位
        :param currenttime:
        :param rc:
        :param case_file:
        :return:
        """
        result_line = []
        bflag = True
        if rc == 0:
            log_file = os.path.join(self.vdbench_output_path, 'flatfile.html')
            with open(log_file, 'r') as fh:
                lines = fh.readlines()
                result_line = lines[-1].split()
                bflag = "* rate" in lines[13].lower()
                if bflag:
                    log.info("Case_ID: %s, Avg_IOPS: %s, Avg_resp: %s, Avg_bandwidth: %s" % (self.case_id,
                                                                                             result_line[5],
                                                                                             result_line[6],
                                                                                             result_line[7]))
                else:
                    log.info("Case_ID: %s, Avg_IOPS: %s, Avg_resp: %s, Avg_bandwidth: %s" % (self.case_id,
                                                                                             result_line[7],
                                                                                             result_line[10],
                                                                                             result_line[13]))

        file_name = os.path.join(self.base_case_path, "%s.csv" % currenttime)
        fieldnames = ['Case_ID', 'Result', 'Avg_IOPS', 'Avg_resp', 'Avg_bandwidth']
        if not os.path.exists(file_name):
            with open(file_name, "wb") as fh:
                writer = csv.DictWriter(fh, fieldnames=fieldnames)
                writer.writeheader()
        with open(file_name, "ab") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            if rc == 0:
                if bflag:
                    writer.writerow({'Case_ID': self.case_id, 'Result': 'Pass', 'Avg_IOPS': result_line[5],
                                    'Avg_resp': result_line[6], 'Avg_bandwidth': result_line[7]})
                else:
                    writer.writerow({'Case_ID': self.case_id, 'Result': 'Pass', 'Avg_IOPS': result_line[7],
                                     'Avg_resp': result_line[10], 'Avg_bandwidth': result_line[13]})
            else:
                writer.writerow({'Case_ID': 0, 'Result': 'Failed', 'Avg_IOPS': 0, 'Avg_resp': 0, 'Avg_bandwidth': 0})

        with open('out.csv', 'wb') as out_put, open(case_file, 'rb') as in_put:
            writer = csv.writer(out_put)
            reader = csv.reader(in_put)
            for row in reader:
                if self.case_id == row[0]:
                    if rc == 0:
                        row[1] = 'passed'
                    else:
                        row[1] = 'failed'
                writer.writerow(row)
        os.rename('out.csv', case_file)
    #
    # def init_case_file(self, case_file, bflag):
    #     with open('out.csv', 'wb') as out_put, open(case_file, 'rb') as in_put:
    #         writer = csv.writer(out_put)
    #         reader = csv.reader(in_put)
    #         f_lst = 0
    #         if bflag:
    #             for row in reader:
    #                 if row[1] != 'passed':
    #                     f_lst += 1
    #             if f_lst == 0:
    #                 log.info("The cases have been successfully executed")
    #                 sys.exit(0)
    #         for row in reader:
    #             row[1] = ''
    #             writer.writerow(row)

    def mk_dir(self, file_path):

        if not os.path.exists(file_path):
            os.makedirs(file_path)
        return

    def mk_journal_dir(self, file_path):
        for ip in self.system_ips:
            cmd = 'ls %s' % file_path
            mk_cmd = 'mkdir -p %s' % file_path
            rc, stdout = common.run_command(ip, cmd)
            if rc != 0:
                common.run_command(ip, mk_cmd)

    def _set_write_file(self, only_create, only_clean):
        """
        :author:      caizhenxing
        :date  :      2018.11.14
        :description: 生成vdbench配置文件
        :return:
        """
        file_content_lst = []
        """设置头部分"""
        line_str = "data_errors=1"
        file_content_lst.append(line_str)

        line_str = "create_anchors=y"
        file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)
        """hd部分"""
        if self.is_windows:
            shell_type = 'vdbench'
        else:
            shell_type = 'ssh,user=root'
        line_str = "hd=default,vdbench=%s,shell=%s" % (self.vdbench_path, shell_type)
        file_content_lst.append(line_str)

        if only_create:
            line_str = "hd=h1,system=%s" % self.system_ips[0]
            file_content_lst.append(line_str)
        else:
            i = 0
            for system_ip in self.system_ips:
                i += 1
                line_str = "hd=h%d,system=%s" % (i, system_ip)
                file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        self.create_fsd(file_content_lst, only_create)

        line_str = ""
        file_content_lst.append(line_str)

        self.create_fwd(file_content_lst, only_create)

        line_str = ""
        file_content_lst.append(line_str)

        self.create_rd(file_content_lst, only_create, only_clean)

        """写入配置文件"""
        file_content = '\n'.join(file_content_lst)

        create_file_name = os.path.join(self.tool_path, 'vdbench_datacheck', '%s_write' % self.file_name)
        with open(create_file_name, 'w') as f:
            f.write(file_content)
        return

    def get_xfersize(self, operation):
        if 'big' in operation:
            self.xfersize = self.big_xfersize
        elif 'small' in operation:
            self.xfersize = self.small_xfersize

    def create_fwd(self, file_content_lst, only_create):
        """
        :author:             caizhenxing
        :date  :             2018.11.14
        :description:        拼装fwd
        :param file_content_lst:
        :param only_create:
        :return:
        """
        if '|' in self.operation:
            operations = self.operation.split('|')
            line_str = "fwd=default,threads=%s" % self.threads
            file_content_lst.append(line_str)

            if 'small' not in self.operation or self.align == 'no':
                for operation in operations:
                    self.get_xfersize(operation)
                line_str = "fwd=format,threads=%s,xfersize=%s" % (self.threads, self.xfersize)
                file_content_lst.append(line_str)

            system_ips = []
            if only_create:
                system_ips.append(self.system_ips[0])
            else:
                system_ips = self.system_ips
            h = 1
            for i in range(len(system_ips)):

                i += 1
                for index in range(len(operations)):

                    operation = operations[index].split('-')

                    self.get_xfersize(operation)
                    if self.shared_folder == 'yes':
                        line_str = "fwd=fwd%d,fsd=fsd1," \
                                   "hd=h%d,xfersize=%s,fileio=%s," \
                                   "fileselect=%s,operation=%s" % (h, i, self.xfersize, operation[2], operation[2],
                                                                   operation[1])
                    elif self.shared_file == 'yes':
                        line_str = "fwd=fwd%d,fsd=fsd1," \
                                   "hd=h%d,xfersize=%s,fileio=(%s,shared)," \
                                   "operation=%s" % (h, i, self.xfersize, operation[2], operation[1])
                    else:
                        line_str = "fwd=fwd%d,fsd=fsd%d," \
                                   "hd=h%d,xfersize=%s,fileio=%s," \
                                   "fileselect=%s,operation=%s" % (h, i, i, self.xfersize, operation[2], operation[2],
                                                                   operation[1])

                    file_content_lst.append(line_str)
                    h += 1
            pass
        else:
            operation = self.operation.split('-')
            self.get_xfersize(operation)

            line_str = "fwd=default,threads=%s,xfersize=%s,operation=%s" % (self.threads, self.xfersize, operation[1])
            if self.shared_file == 'yes':
                line_str += ",fileio=(%s,shared)" % operation[2]
            else:
                line_str += ",fileio=%s,fileselect=%s" % (operation[2], operation[2])

            file_content_lst.append(line_str)
            if 'small' not in self.operation or self.align == 'no':
                line_str = "fwd=format,threads=%s,xfersize=%s" % (self.threads, self.xfersize)
                file_content_lst.append(line_str)

            if only_create:
                line_str = "fwd=fwd1,fsd=fsd1,hd=h1"
                file_content_lst.append(line_str)
            else:
                for i in range(len(self.system_ips)):
                    i += 1
                    if self.shared_folder == 'yes' or self.shared_file == 'yes':
                        line_str = "fwd=fwd%d,fsd=fsd1,hd=h%d" % (i, i)
                    else:
                        line_str = "fwd=fwd%d,fsd=fsd%d,hd=h%d" % (i, i, i)
                    file_content_lst.append(line_str)

    def create_rd(self, file_content_lst, only_create, only_clean):
        """
        :author:             caizhenxing
        :date  :             2018.11.13
        :description:        拼装rd
        :param file_content_lst:
        :param only_create:
        :param only_clean:
        :return:
        """
        line_str = "rd=default,fwdrate={},elapsed={},interval=1".format(self.fwdrate, self.elapsed)
        if self.warmup is not None:
            line_str += ",warmup={}".format(self.warmup)
        if self.pause is not None:
            line_str += ",pause={}".format(self.pause)
        file_content_lst.append(line_str)

        if self.shared_folder == 'yes':
            line_str = "rd=rd1,fwd=fwd*,format=(clean,only)"
            file_content_lst.append(line_str)
            line_str = "rd=rd2,fwd=fwd*,format=restart"
            file_content_lst.append(line_str)
        elif only_create:
            line_str = "rd=rd1,fwd=fwd*,format=only"
            file_content_lst.append(line_str)
        elif only_clean:
            line_str = "rd=rd1,fwd=fwd*,format=clean"
            file_content_lst.append(line_str)
        elif self.ln_operation == 'yes':
            line_str = "rd=rd1,fwd=fwd*,format=restart"
            file_content_lst.append(line_str)
        else:
            line_str = "rd=rd1,fwd=fwd*"
            if self.format is not None:
                line_str += ",format={}".format(self.format)

            file_content_lst.append(line_str)

    def create_fsd(self, file_content_lst, only_create):
        """
        :author:             caizhenxing
        :date  :             2018.11.13
        :description:        拼装fsd
        :param file_content_lst:
        :param only_create:
        :return:
        """
        line_str = "fsd=default,depth=%s,width=%s,files=%s,size=%s" \
                   % (self.depth, self.width, self.files, self.size)
        if self.shared_folder == 'yes':
            line_str += ",shared={}".format(self.shared_folder)
        if self.openflags is not None:
            line_str += ",openflags={}".format(self.openflags)
        file_content_lst.append(line_str)

        if self.shared_folder == 'yes' or self.shared_file == 'yes' or only_create:
            self.fsd_lst.append("%s/vdbench1" % self.anchor_path)
            line_str = "fsd=fsd1,anchor=%s/vdbench1" % self.anchor_path
            file_content_lst.append(line_str)
        else:
            for i in range(len(self.system_ips)):
                i += 1
                self.fsd_lst.append("%s/vdbench%d" % (self.anchor_path, i))
                if self.ln_operation == 'yes':
                    line_str = "fsd=fsd%d,anchor=%s" % (i, self.all_path[i])
                else:
                    line_str = "fsd=fsd%d,anchor=%s/vdbench%d" % (i, self.anchor_path, i)
                file_content_lst.append(line_str)

    def traverse(self, f):
        """
        :author:             caizhenxing
        :date  :             2018.11.20
        :description:        遍历目录结构
        :param f:
        :return:
        """
        # fs = os.listdir(f)
        cmd = 'ls %s' % f
        rc, stdout = common.run_command(self.client_ip[0], cmd, print_flag=False)
        fs = stdout.strip("\n").split("\n")
        for f1 in fs:
            if not f1.endswith(".file"):
                tmp_path = os.path.join(f, f1)

                cmd = 'ls -ld %s' % tmp_path
                rc, stdout = common.run_command(self.client_ip[0], cmd, print_flag=False)
                if stdout.startswith("d"):
                    self.traverse(tmp_path)
                # else:
                #     parent_path = os.path.dirname(tmp_path)
                #     if parent_path not in self.glb_lst:
                #         self.glb_lst.append(parent_path)
            else:
                if f not in self.glb_lst:
                    if os.path.dirname(f) != self.anchor_path:
                        self.glb_lst.append(f)
            # if os.path.isdir(tmp_path):
            #     self.traverse(tmp_path)
            # else:
            #     parent_path = os.path.dirname(tmp_path)
            #     if parent_path not in self.glb_lst:
            #         self.glb_lst.append(parent_path)

    def get_dir(self, dir_lst):
        """
        :author:             caizhenxing
        :date  :             2018.11.20
        :description:        获取最终需要硬链接的目录
        :param dir_lst:
        :return:
        """
        dirs = dir_lst
        for i in range(len(dirs)):
            if (i + 1) < len(dirs):
                if len(dirs[i + 1]) > len(dirs[i]):
                    self.glb_lst.remove(dirs[i])

    def ln_file(self):
        """
        :author:             caizhenxing
        :date  :             2018.11.21
        :description:        为待测文件创建硬链接
        :return:
        """
        f_list = []
        for f in self.fsd_lst:
            self.traverse(f)
            self.get_dir(self.glb_lst)
        for i in range(len(self.ln_path)):
            data_lst = []
            for f in self.glb_lst:
                data_lst.append(f.replace(self.anchor_path, self.ln_path[i]))
            cmd = "ls -d %s" % self.ln_path[i]
            rc, stdout = common.run_command(self.client_ip[0], cmd)
            # if os.path.exists(self.ln_path[i]):
            if rc == 0:
                common.run_command(self.client_ip[0], "rm -rf %s" % self.ln_path[i])
            f_list.append(data_lst)
        log.info("************************Begin to execute ln*********************************")
        # for j in range(len(f_list)):
        #     common.command("mkdir -p %s" % f_list[j])
        #     common.command("ln %s/* %s" % (self.glb_lst[j], f_list[j]))

        for d in f_list:
            for j in range(len(d)):
                common.run_command(self.client_ip[0], "mkdir -p %s" % d[j])
                common.run_command(self.client_ip[0], "ln %s/* %s" % (self.glb_lst[j], d[j]))
        log.info("************************End ln*********************************")
