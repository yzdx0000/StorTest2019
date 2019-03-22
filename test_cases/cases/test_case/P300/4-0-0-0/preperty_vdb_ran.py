# testlink case:3.0-42109,3.0-42112,3.0-42115
# -*-coding:utf-8 -*
from multiprocessing import Process
import subprocess
import os
import time
import random
import sys
import datetime

import utils_path
import common
import log
import shell
import get_config
import prepare_clean
import commands
#################################################################
#
# Author: chenjy1
# Date: 2018-09-03
# @summary：
#    性能测试：集群吞吐量 + 重建（修复）速度
# @steps:
#    1> vdbench创建文件
#    2> 获得性能值
#    3> 修改磁盘重建超时时间为60秒
#    4> 拔一块盘，等被动重建
#    5> 计算被动重建耗时/文件量
#    6> 恢复环境
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]          # 本脚本名字
VDBENCH_PATH1 = os.path.join(prepare_clean.PROPERTY_PATH, FILE_NAME, "vdbench1")
VDBENCH_PATH2 = os.path.join(prepare_clean.PROPERTY_PATH, FILE_NAME, "vdbench2")
VDBENCH_PATH3 = os.path.join(prepare_clean.PROPERTY_PATH, FILE_NAME, "vdbench3")


def command_getinfo(cmd):
    bandwidth_avg = 0
    bandwidth_peak = 0
    resp_avg = 0
    resp_peak = 0

    log.info(cmd)
    avg_times = 0
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        line = process.stdout.readline()
        if '' == line:
            break
        everyline_lst = line.rstrip().split()
        if len(everyline_lst) >= 20 and ('read' not in line.rstrip().split()) and ('resp' not in line.rstrip().split()):
            if float(everyline_lst[13]) > bandwidth_peak:
                bandwidth_peak = float(everyline_lst[13])
            if float(everyline_lst[3]) > resp_peak:
                resp_peak = float(everyline_lst[3])
        if 'avg_' in line.rstrip():
            avg_times += 1
            if avg_times == 2:
                str_lst = line.rstrip().split()
                bandwidth_avg = float(str_lst[13])
                resp_avg = float(str_lst[3])
        log.debug(line.rstrip())
    process.wait()
    if process.returncode == 0:
        return 0, bandwidth_peak, bandwidth_avg, resp_peak, resp_avg
    else:
        return -1, 0, 0, 0, 0


class Vdbenchrun():
    """
    运行vdbench

    run_create:      创建文件，并生成校验文件
    run_write:       修改文件
    run_write_jn:    修改文件，并生成校验文件
    run_check:       校验数据正确性
    run_check_write: 校验数据正确性，然后跑一定时间的读写
    """
    def __init__(self, depth=None, width=None, files=None, size=None, threads=None, xfersize=None, elapsed=None,
                 fileio=None, fileselect=None, rdinfo=None):
        """
        :author:          baoruobing
        :date  :          2018.04.17
        :description:     创建vdbench对象
        :param depth:    (int)目录深度，默认2
        :param width:    (int)目录宽度，默认2
        :param files:    (int)单个目录中文件数目，默认100
        :param size:     (str)文件大小，默认(512k,30,2m,35,4m,30,32m,5)
        :param threads:  (int)线程数，默认100
        :param xfersize: (str)单次读取大小，默认(4k,50,64k,30,1m,20)
        :param elapsed:  (int)写的时间，默认240s
        :param rdinfo:   (dict)写的时间，默认240s
        """
        self.depth = 2 if depth is None else depth
        self.width = 2 if width is None else width
        self.files = 100 if files is None else files
        self.size = "(1m,30,4m,35,8m,30,32m,5)" if size is None else size
        # self.size = "(64k,30,128k,35,256k,30,1m,5)" if size == None else size
        self.threads = 100 if threads is None else threads
        self.xfersize = "(4k,50,64k,30,1m,20)" if xfersize is None else xfersize
        self.elapsed = 240 if elapsed is None else elapsed
        self.fileio = 'sequential' if fileio is None else fileio
        self.fileselect = 'sequential' if fileselect is None else fileselect
        self.rdinfo = rdinfo

        self.openflags = None

        self.vdbench_path = get_config.get_snap_vdbench_path()
        self.tool_path = get_config.get_tools_path()
        current_time = datetime.datetime.now()
        currenttime = current_time.strftime('%y-%m-%d-%H-%M-%S')
        self.outputpath_tail = currenttime + '_' + os.path.splitext(os.path.basename(sys.argv[0]))[0]
        self.vdbench_log_path = os.path.join(os.path.dirname(get_config.get_testlog_path()), 'vdbench_log')

        return

    def run_write_preperty(self, anchor_path_lst, journal_path_lst, client_lst):
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
        common.judge_rc_unequal(len(anchor_path_lst), 0, "please input anchor path")

        self.anchor_path = anchor_path_lst
        self.journal_path = journal_path_lst
        self.system_ips = client_lst
        """生成配置check_write文件"""
        self._set_write_preperty_file()

        check_write_file_name = os.path.join(self.tool_path, 'vdbench_datacheck', 'check_write_preperty')
        vdbench_ex_path = os.path.join(self.vdbench_path, 'vdbench')
        vdbench_output_path = os.path.join(self.vdbench_log_path, self.outputpath_tail, 'check_write_preperty')
        cmd = 'mkdir -p %s' % vdbench_output_path
        rc = common.command(cmd)
        common.judge_rc(rc, 0, "cmd:%s failed" % cmd)
        cmd = "sh %s -f %s -o %s" % (vdbench_ex_path, check_write_file_name, vdbench_output_path)
        rc, a, b, c, d = command_getinfo(cmd)
        return rc, a, b, c, d

    def _set_write_preperty_file(self):
        """
        :author:      chenjy1
        :date  :      2018.08.23
        :description: 生成check_write配置文件
        :return:
        """
        file_content_lst = []
        """hd部分"""
        line_str = "messagescan=no "
        file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

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
            line_str = "fsd=fsd%d,anchor=%s,journal=%s" % (i+1, anchor_path, self.journal_path[i])
            file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """fwd部分"""
        line_str = "fwd=format,threads=%d,xfersize=%s" % (self.threads, self.xfersize)
        file_content_lst.append(line_str)
        line_str = "fwd=default,threads=%d,xfersize=%s,fileio=%s,fileselect=%s" % (self.threads, self.xfersize,
                                                                                   self.fileio, self.fileselect)
        file_content_lst.append(line_str)

        for i in range(len(self.system_ips)):
            i += 1
            line_str = "fwd=fwd%d,fsd=fsd%d,hd=h%d" % (i, i, i)
            file_content_lst.append(line_str)

        line_str = ""
        file_content_lst.append(line_str)

        """rd部分"""
        line_str = "rd=default,fwdrate=max,elapsed=%d,maxdata=2t,interval=1,warmup=10,pause=5" % self.elapsed
        file_content_lst.append(line_str)
        line_str = ''
        rdn = 0
        for rd in self.rdinfo:
            rdn += 1
            line_str += 'rd=rd%s,' % rdn
            for x in rd:
                line_str += '%s=%s,' % (x, rd[x])
            file_content_lst.append(line_str)

        """写入配置文件"""
        file_content = '\n'.join(file_content_lst)

        create_file_name = os.path.join(self.tool_path, 'vdbench_datacheck', 'check_write_preperty')
        with open(create_file_name, 'w') as f:
            f.write(file_content)
        return


def vdbench_test(runtype):
    rdinfo = []
    tmplst = {}
    tmplst['format'] = 'yes'
    if runtype == 'read':
        tmplst['forrdpct'] = 100
    elif runtype == 'write':
        tmplst['forrdpct'] = 0
    else:
        tmplst['forrdpct'] = 70
    tmplst['fwd'] = 'fwd*'
    rdinfo.append(tmplst)
    client_lst = get_config.get_allclient_ip()
    anchor_path_lst = [VDBENCH_PATH1, VDBENCH_PATH2, VDBENCH_PATH3]
    journal_path_lst = []
    for i in anchor_path_lst:
        journal_path_lst.append('/tmp')
    ob_vdb = Vdbenchrun(depth=1, width=10, files=100, size='100m', threads=100, xfersize='16k', elapsed=1200,
                        fileio='random',  fileselect='random', rdinfo=rdinfo)
    rc, a, b, c, d = ob_vdb.run_write_preperty(anchor_path_lst, journal_path_lst, client_lst)
    if rc != 0:
        common.except_exit('run_write_preperty failed')
    else:
        return rc, a, b, c, d


def case():
    log.info("case begin")
    rc, a1, b1, c1, d1 = vdbench_test('write')
    rc, a2, b2, c2, d2 = vdbench_test('read')
    rc, a3, b3, c3, d3 = vdbench_test('r70w30')
    log.info(
        'winfo : 随机写带宽峰值:%s mb/s   随机写带宽均值:%s mb/s   随机写响应峰值:%sms  随机写响应均值:%sms '
        % (a1, b1, c1, d1))
    log.info(
        'rinfo : 随机读带宽峰值:%s mb/s  随机读带宽均值:%s mb/s   随机读响应峰值:%sms  随机读响应均值:%sms '
        % (a2, b2, c2, d2))
    log.info(
        'r70w30info : 随机写70读30带宽峰值:%s mb/s  随机写70读30带宽均值:%s mb/s   随机写70读30响应峰值:%sms  '
        '随机写70读30响应均值:%sms ' % (a3, b3, c3, d3))
    return


def main():
    prepare_clean.preperty_test_prepare(FILE_NAME)
    case()
    prepare_clean.preperty_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)
    return


if __name__ == '__main__':
    common.case_main(main)