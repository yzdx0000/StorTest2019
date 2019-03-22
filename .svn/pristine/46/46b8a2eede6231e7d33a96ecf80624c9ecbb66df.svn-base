# -*-coding:utf-8 -*
import os

import utils_path
import common
import log
import get_config
import prepare_clean

##########################################
#
# Author: baorb
# date 2017-08-21
# @summary：
#    本测试主要测试3节点P300的文件操作。
# @steps:
#    1，添加文件
#    2，修改文件
#    3，删除文件
#
# @changelog：
##########################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                # 本脚本名字
MINI_TRUE_PATH = os.path.join(prepare_clean.MINICASE_PATH, FILE_NAME)      # /mnt/volume1/mini_case/3_0014_data_test


def case():
    log.info("----------case----------")
    ip_list = get_config.get_allclient_ip()

    '''创建100个1M文件'''
    for i in range(0, 100):
        test_file = os.path.join(MINI_TRUE_PATH, 'test%d' % i)
        cmd = ("iozone -s 1m -i 0 -f %s -w" % test_file)
        log.info(cmd)
        rc, stdout = common.run_command(ip_list[0], cmd)
        common.judge_rc(rc, 0, "iozone create file %s" % test_file)

    '''修改文件为2M'''
    for i in range(0, 100):
        test_file = os.path.join(MINI_TRUE_PATH, 'test%d' % i)
        cmd1 = ("iozone -s 2m -i 0 -f %s -w" % test_file)
        rc, stdout = common.run_command(ip_list[0], cmd1)
        common.judge_rc(rc, 0, "iozone change file %s" % test_file)

    '''缩减文件为512k'''
    for i in range(0, 100):
        test_file = os.path.join(MINI_TRUE_PATH, 'test%d' % i)
        cmd2 = ("truncate -s 512k %s" % test_file)
        rc, stdout = common.run_command(ip_list[0], cmd2)
        common.judge_rc(rc, 0, 'truncate file %s' % test_file)

    '''查看文件内容'''
    for i in range(0, 100):
        test_file = os.path.join(MINI_TRUE_PATH, 'test%d' % i)
        cmd3 = ("cat %s" % test_file)
        rc, stdout = common.run_command(ip_list[1], cmd3)
        common.judge_rc(rc, 0, 'cat file %s' % test_file)

    '''修改文件内容'''
    file_msg = "'hello world!'"
    for i in range(0, 100):
        test_file = os.path.join(MINI_TRUE_PATH, 'test%d' % i)
        cmd4 = ('echo %s >> %s' % (file_msg, test_file))
        rc, stdout = common.run_command(ip_list[1], cmd4)
        common.judge_rc(rc, 0, 'echo file %s' % test_file)

    '''删除文件'''
    for i in range(0, 100):
        test_file = os.path.join(MINI_TRUE_PATH, 'test%d' % i)
        common.rm_exe(ip_list[1], test_file)

    '''检查系统'''
    common.ckeck_system()

    log.info("case succeed!")
    return


def main():
    prepare_clean.minicase_test_prepare(FILE_NAME)
    case()
    prepare_clean.minicase_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)
    return


if __name__ == '__main__':
    common.case_main(main)