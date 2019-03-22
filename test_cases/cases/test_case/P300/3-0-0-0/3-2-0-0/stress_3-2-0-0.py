# -*-coding:utf-8 -*
import os
import time
import datetime
import sys
import csv
from optparse import OptionParser

import utils_path
import common
import log
import get_config
import prepare_clean
import vdbench_common as vdbench

#
# Author: caizhenxing
# date 2018/11/14
# @summary：
#           稳定性测试，包括：多客户端多目录不同文件（带校验）、
#                            多客户端同目录不同文件（带校验）、
#                            多客户端同目录同文件（不带校验）
# @steps:
# @changelog：
#


Case_Result = []
Case_File = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'stress.csv')        # 用例表文件名
# 当前脚本名称
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
# VOLUME = os.path.join(prepare_clean.MOUNT_PAHT, FILE_NAME)

current_time = datetime.datetime.now()
currenttime = current_time.strftime('%y-%m-%d-%H-%M-%S')
OUTPUT_PATH = currenttime + '_' + os.path.splitext(os.path.basename(sys.argv[0]))[0]
global FAILEDFLAG
global WINDOWSFLAG


def vdbench_run(test_case, client_ip_list, **args):

    global WINDOWSFLAG

    if WINDOWSFLAG:
        volume = os.path.join(get_config.get_one_windows_path(), FILE_NAME)
    else:
        volume = os.path.join(prepare_clean.MOUNT_PAHT, FILE_NAME)

    journal = '/tmp/vdbench/journal'

    case_id = test_case['Case_ID']
    data_error = test_case['Data_Error']
    depth = test_case['Depth']
    width = test_case['Width']
    files = test_case['Files']
    size = test_case['Size'].replace('-', ',').replace('|', ',')
    threads = test_case['Threads']

    small_xfersize = test_case['Small_Xfersize'].replace('-', ',').replace('|', ',')
    big_xfersize = test_case['Big_Xfersize'].replace('-', ',').replace('|', ',')
    operation = test_case['Operation']
    format = test_case['Format']
    elapsed = test_case['Elapsed']
    truncate = test_case['Truncate']
    align = test_case['Align']
    validate = test_case['Validate']
    shared_folder = test_case['Shared_Folder']
    shared_file = test_case['Shared_File']
    ln_operation = test_case['LN']

    vdb = vdbench.Vdbenchrun(data_error=data_error,
                             case_id=case_id,
                             depth=depth,
                             width=width,
                             files=files,
                             size=size,
                             threads=threads,
                             small_xfersize=small_xfersize,
                             big_xfersize=big_xfersize,
                             operation=operation,
                             format=format,
                             elapsed=elapsed,
                             output=OUTPUT_PATH,
                             truncate=truncate,
                             align=align,
                             validate=validate,
                             shared_folder=shared_folder,
                             shared_file=shared_file,
                             ln_operation=ln_operation,
                             is_windows=WINDOWSFLAG,
                             file_name=FILE_NAME)

    if ln_operation == 'yes':
        vdb.run_vdb(os.path.join(volume, case_id), journal, client_ip_list, only_create=True, only_clean=False, **args)
        vdb.ln_file()
    rc = vdb.run_vdb(os.path.join(volume, case_id), journal, client_ip_list, only_create=False, only_clean=False, **args)
    vdb.get_results(currenttime, rc, Case_File)
    if ln_operation == 'yes':
        vdb.run_vdb(os.path.join(volume, case_id), journal, client_ip_list, only_create=False, only_clean=True, **args)
    """当case失败后，将失败case_id记录到Case_Result"""
    if rc != 0:
        log.info('vdbench run_write failed!!!!!!')
        Case_Result.append(case_id)
        return

    time.sleep(10)

    return


def case(test_case):
    log.info("case begin")
    """获取客户端节点"""
    client_ip_list = get_config.get_allclient_ip()
    log.info("1> vdbench读写")
    vdbench_run(test_case, client_ip_list)
    """如当前case失败，则直接返回"""
    if Case_Result:
        pass
        return
    log.info("case succeed!")
    return


def main():
    """初始化日志"""
    filename = os.path.splitext(os.path.basename(__file__))[0]
    log_file_path = log.get_log_path(filename)
    log.init(log_file_path, True)
    with open(Case_File) as csvfile:
        """
        以字典形式读取csv文件内容；逐行读取，每行一个case
        """
        read_results = csv.DictReader(csvfile)
        for row in read_results:
            if WINDOWSFLAG and row['LN'] == 'yes':
                continue
            else:
                if FAILEDFLAG:
                    if row['Result_Flag'] != 'passed':
                        # prepare_clean.defect_test_prepare(FILE_NAME, env_check=False)
                        case(row)
                else:
                    # prepare_clean.defect_test_prepare(FILE_NAME, env_check=False)
                    case(row)
            # prepare_clean.defect_test_clean(FILE_NAME)
            """
            当前case失败后，继续执行下一case
            """
            if Case_Result:
                continue
            log.info('%s succeed!' % FILE_NAME)

    if Case_Result:
        log.info("case: %s failed" % ", ".join(Case_Result))
        sys.exit(1)


def arg_options():
    """
    :author:             caizhenxing
    :date  :             2018.11.22
    :description:
                         判断是否只重新执行失败和未执行过的case，
                         当有-F时，只运行失败和未执行的case，没有-F，则重新执行全部case
    :return:
    """
    global FAILEDFLAG
    global WINDOWSFLAG

    parser = OptionParser()

    parser.add_option("-F", "--failed",
                      action="store_true",
                      dest="failed",
                      help="If you only want to run the failed or never executed case, configure this parameter")

    parser.add_option("-W", "--windows",
                      action='store_true',
                      dest='iswindows',
                      help="vdbench slave is windows")

    options, args = parser.parse_args()

    if options.failed:
        FAILEDFLAG = True
    else:
        FAILEDFLAG = False

    if options.iswindows:
        WINDOWSFLAG = True
    else:
        WINDOWSFLAG = False


def init_case_file(case_file, bflag):
    """
    :author:             caizhenxing
    :date  :             2018.11.22
    :description:
                         当有-F时，首先判断是否所有case都已执行过且都为passed，如果是，则终止测试
                         当没有-F时，则重新执行所有case，首先初始化所有case的Resul_Flag为空
    :param case_file:   case列表
    :param bflag:       是否只重新执行失败的和未执行过的case
    :return:
    """
    with open('out.csv', 'wb') as out_put, open(case_file, 'rb') as in_put:
        writer = csv.writer(out_put)
        reader = csv.reader(in_put)
        f_lst = 0

        if bflag:
            for row in reader:
                if row[1] != 'passed' and row[1] != 'Result_Flag':
                    f_lst += 1
            if f_lst == 0:
                print "\n"
                print "* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *"
                print "*********************The cases have already been successfully executed*********************"
                print "* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *"
                print "\n"
                sys.exit(0)
        else:
            for row in reader:
                if row[1] != 'Result_Flag':
                    row[1] = ''
                writer.writerow(row)
            os.rename('out.csv', case_file)


if __name__ == '__main__':

    arg_options()
    init_case_file(Case_File, FAILEDFLAG)
    common.case_main(main)