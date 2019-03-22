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
#    本测试主要测试3节点P300的文件truncate操作。
# @steps:
#    1，添加文件
#    2，truncate文件变大
#    3，truncate文件变小
#    4，删除文件
#
# @changelog：
##########################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                # 本脚本名字
MINI_TRUE_PATH = os.path.join(prepare_clean.MINICASE_PATH, FILE_NAME)      # /mnt/volume1/mini_case/3_0015_truncate_test


def case():
    log.info("----------case----------")
    cli_ip1 = get_config.get_client_ip(0)
    cli_ip2 = get_config.get_client_ip(1)

    '''添加文件'''
    for i in range(0, 100):
        test_file = os.path.join(MINI_TRUE_PATH, 'test%d' % i)
        cmd = ("truncate %s -s 0" % test_file)
        rc, stdout = common.run_command(cli_ip1, cmd)
        common.judge_rc(rc, 0, 'truncate create %s' % test_file)

        '''在另一个节点检查文件是否存在'''
        cmd1 = ("ls %s" % test_file)
        rc, stdout = common.run_command(cli_ip2, cmd1)
        common.judge_rc(rc, 0, '%s is not exist!!!' % test_file)

    '''truncate文件到1M'''
    for i in range(0, 100):
        test_file = os.path.join(MINI_TRUE_PATH, 'test%d' % i)
        cmd = ("truncate %s -s 1M" % test_file)
        rc, stdout = common.run_command(cli_ip1, cmd)
        common.judge_rc(rc, 0, 'truncate 1M %s' % test_file)

        '''在另一个节点检查文件大小'''
        cmd = ("du %s -b" % test_file)
        rc, stdout = common.run_command(cli_ip2, cmd)
        common.judge_rc(rc, 0, 'du %s' % test_file)

        common.judge_rc(stdout.split()[0], str(1048576), "%s size is not correct!!!" % test_file)

    '''truncate文件到100M'''
    for i in range(0, 100):
        test_file = os.path.join(MINI_TRUE_PATH, 'test%d' % i)
        cmd = ("truncate %s -s 100M" % test_file)
        rc, stdout = common.run_command(cli_ip1, cmd)
        common.judge_rc(rc, 0, 'truncate %s 100M' % test_file)

        '''在另一个节点检查文件大小'''
        cmd = ("du %s -b" % test_file)
        rc, stdout = common.run_command(cli_ip2, cmd)
        common.judge_rc(rc, 0, 'du %s' % test_file)

        common.judge_rc(stdout.split()[0], str(104857600), "%s size is not correct!!!" % test_file)

    '''truncate文件到100G'''
    for i in range(0, 100):
        test_file = os.path.join(MINI_TRUE_PATH, 'test%d' % i)
        cmd = ("truncate %s -s 100G" % test_file)
        rc, stdout = common.run_command(cli_ip1, cmd)
        common.judge_rc(rc, 0, 'truncate %s 100G' % test_file)

        '''在另一个节点检查文件大小'''
        cmd = ("du %s -b" % test_file)
        rc, stdout = common.run_command(cli_ip2, cmd)
        common.judge_rc(rc, 0, 'du %s' % test_file)

        common.judge_rc(stdout.split()[0], str(107374182400), "%s size is not correct!!!" % test_file)

    '''truncate文件到1K'''
    for i in range(0, 100):
        test_file = os.path.join(MINI_TRUE_PATH, 'test%d' % i)
        cmd = ("truncate %s -s 1K" % test_file)
        rc, stdout = common.run_command(cli_ip1, cmd)
        common.judge_rc(rc, 0, 'truncate %s 1K' % test_file)

        '''在另一个节点检查文件大小'''
        cmd = ("du %s -b" % test_file)
        rc, stdout = common.run_command(cli_ip2, cmd)
        common.judge_rc(rc, 0, 'du %s' % test_file)

        common.judge_rc(stdout.split()[0], str(1024), "%s size is not correct!!!" % test_file)

    '''truncate文件为空'''
    for i in range(0, 100):
        test_file = os.path.join(MINI_TRUE_PATH, 'test%d' % i)
        cmd = ("truncate %s -s 0" % test_file)
        rc, stdout = common.run_command(cli_ip1, cmd)
        common.judge_rc(rc, 0, 'truncate %s 0' % test_file)

        '''在另一个节点检查文件大小'''
        cmd = ("du %s -b" % test_file)
        rc, stdout = common.run_command(cli_ip2, cmd)
        common.judge_rc(rc, 0, 'du %s' % test_file)

        common.judge_rc(stdout.split()[0], '0', "%s size is not correct!!!" % test_file)

    '''删除文件'''
    for i in range(0, 100):
        test_file = os.path.join(MINI_TRUE_PATH, 'test%d' % i)
        common.rm_exe(cli_ip2, test_file)

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