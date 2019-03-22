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

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
MINI_TRUE_PATH = os.path.join(prepare_clean.MINICASE_PATH, FILE_NAME)       # /mnt/volume1/mini_case/3_0013_file_config


def case():
    log.info('-----------case----------')
    cli_ip1 = get_config.get_client_ip(0)
    cli_ip2 = get_config.get_client_ip(1)

    '''添加文件'''
    for i in range(0, 100):
        test_file = os.path.join(MINI_TRUE_PATH, 'test%d.txt' % i)
        cmd = ("touch %s" % test_file)
        rc, stdout = common.run_command(cli_ip1, cmd)
        common.judge_rc(rc, 0, 'touch file %s' % test_file)

        '''在另一个节点检查文件是否存在'''
        cmd1 = ("ls %s" % test_file)
        rc, stdout = common.run_command(cli_ip2, cmd1)
        common.judge_rc(rc, 0, '%s is not exist!!!' % test_file)

    '''修改文件'''
    for i in range(0, 100):
        old_test_file = os.path.join(MINI_TRUE_PATH, 'test%d.txt' % i)
        new_test_file = os.path.join(MINI_TRUE_PATH, 'test_new%d.txt' % i)
        cmd2 = ("mv %s %s" % (old_test_file, new_test_file))
        rc, stdout = common.run_command(cli_ip1, cmd2)
        common.judge_rc(rc, 0, 'mv %s %s' % (old_test_file, new_test_file))

        '''在另一个节点检查文件是否修改'''
        cmd3 = ("ls %s" % old_test_file)
        rc, stdout = common.run_command(cli_ip2, cmd3)
        common.judge_rc_unequal(rc, 0, '%s is exist!!!' % old_test_file)

        cmd4 = ("ls %s" % new_test_file)
        rc, stdout = common.run_command(cli_ip2, cmd4)
        common.judge_rc(rc, 0, '%s is not exist!!!' % new_test_file)

    '''删除文件'''
    for i in range(0, 100):
        new_test_file = os.path.join(MINI_TRUE_PATH, 'test_new%d.txt' % i)
        common.rm_exe(cli_ip1, new_test_file)

        '''在另一个节点检查文件是否删除'''
        cmd6 = "ls %s" % new_test_file
        rc, stdout = common.run_command(cli_ip2, cmd6)
        common.judge_rc_unequal(rc, 0, '%s is exist!!!' % new_test_file)

    '''检查系统'''
    common.ckeck_system()

    log.info("case succeed!")
    return


def main():
    prepare_clean.minicase_test_prepare(FILE_NAME)
    case()
    prepare_clean.minicase_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)