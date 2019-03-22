# -*- coding:utf-8 -*-

##################################################
# author zhanghan
# date 2018-12-03
# @summary：
#   类中实现功能函数，比如：执行指定perl脚本，复制文件，删除文件，执行bat脚本
# @steps:
#   1、
# @changelog：
##################################################

import utils_path_win
import common
import os
import time


class Dac():

    def excute_perl_script(self, scripts_pwd, u1_addr, u2_addr, u3_addr, u4_addr, win_test_dir):
        """
        author: zhanghan
        date: 2018-12-3
        :param scripts_pwd:脚本位置
        :param u1_addr: 用户1的挂载路径
        :param u2_addr: 用户2的挂载路径
        :param u3_addr: 用户3的挂载路径
        :param u4_addr: 用户4的挂载路径
        :win_test_dir: 测试目录名称
        :return:
        """
        print "\t[ /excute_perl_script ]"

        cmd = 'perl %s\win.pl %s %s %s %s %s %s' % (scripts_pwd, scripts_pwd, u1_addr, u2_addr, u3_addr, u4_addr, win_test_dir)
        print 'cmd = %s' % cmd
        retcode, output = common.run_command_shot_time(cmd)
        print output

        return retcode, output

    def copy_file(self, origin_path, destination_path):
        """
        author: zhanghan
        date: 2018-12-3
        :param origin_path:文件原始位置
        :param destination_path:文件目标位置
        :return: retcode:命令返回码， output:命令执行结果
        """
        print "\t[ copy from %s to %s ]" % (origin_path, destination_path)
        cmd = 'powershell;Copy-Item %s %s -Recurse' % (origin_path, destination_path)
        print 'cmd = %s' % cmd
        retcode, output = common.run_command_shot_time(cmd)

        return retcode, output

    def rm_win_file(self, file_location):
        """
        author: zhanghan
        date: 2018-12-3
        :param file_location:待删除文件位置
        :return: retcode:命令返回码， output:命令执行结果
        """
        print "\t[ del %s ]" % file_location
        cmd = 'powershell;del %s -Recurse' % file_location
        print 'cmd = %s' % cmd
        retcode, output = common.run_command_shot_time(cmd)

        return retcode, output

    def excute_acl_bat(self, file_dir, file_name):
        """
        author: zhanghan
        date: 2018-12-3
        :param file_dir:待执行bat文件所在路径
        :param file_name:待执行bat文件名称
        :return: retcode:命令返回码， output:命令执行结果
        """
        print "\t[ excute %s\%s ]" % (file_dir, file_name)
        cmd = 'powershell;cd %s;.\%s' % (file_dir, file_name)
        print 'cmd = %s' % cmd
        retcode, output = common.run_command_shot_time(cmd)

        return retcode, output



if __name__ == '__main__':
    a = Dac()
    cmd = 'cp E:\\testcopy_e C:\\'
    print os.system(cmd)
