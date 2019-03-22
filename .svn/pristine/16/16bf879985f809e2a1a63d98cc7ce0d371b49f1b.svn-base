# -*- coding:utf-8 -*-

##################################################
# author 姜晓光
# date 2018-08-01
# @summary：
#   类中实现功能函数，比如：挂载，去挂载，查询
# @steps:
#   1、
# @changelog：
##################################################

import utils_path_win
import common
import os
import time
import log
import shutil


class Smb():
    def smb_mount(self, disk_symbol, mount_path, password, user):
        """smb挂载
        :Author: jiangxiaoguang
        :Date: 2018-08-06
        :param disk_symbol: 盘符，类似:'x:'
        :param mount_path: 挂载路径
        :param password: 用户登录密码
        :param user: 用户登录名称
        :return: retcode:命令返回码， output:命令执行结果
        """

        cmd = 'net use %s /del /y' % disk_symbol
        rc, stdout = common.run_command_shot_time(cmd)

        cmd = 'net use %s %s %s /user:%s' % (disk_symbol, mount_path, password, user)
        log.info('cmd = %s' % cmd)
        retcode, output = common.run_command_shot_time(cmd)

        return retcode, output

    def smb_umount(self, disk_symbol):
        """smb去挂载
        :param disk_symbol: 盘符，类似:'x:'
        :return: retcode:命令返回码， output:命令执行结果
        """

        cmd = 'net use %s /del /y' % disk_symbol
        log.info('cmd = %s' % cmd)
        retcode, output = common.run_command_shot_time(cmd)
        log.info("output=%s" % output)

        return retcode, output

    def net_use(self):
        """列出本机网络连接
        :return: retcode:命令返回码， output:命令执行结果
        """
        log.info("\t[ net_use ]")

        cmd = 'net use'
        log.info('cmd = %s' % cmd)
        retcode, output = common.run_command_shot_time(cmd)
        log.info("output=%s" % output)

        return retcode, output

    def create_file(self, disk_symbol, filename):
        """通过smb挂载写入数据
        :param disk_symbol: 盘符，类似:'x:'
        :param filename: 写入文件的名称
        :return:
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        try:
            retval = os.getcwd()
            log.info('retval = %s ' % retval)

            os.chdir('E:\\jiangxg')
            retval = os.getcwd()
            log.info('retval = %s' % retval)

            path = 'E:\\jiangxg\\dir'
            log.info('path = %s' % path)

            if 'dir' not in os.listdir('.'):
                log.info('##########')
                os.mkdir(path)

            filename1 = 'E:\\jiangxg\\filename1'
            with open(filename1, 'w') as f:
                pass
        finally:
            os.chdir(current_dir)

    def create_dir_file(self, disk_symbol, dir_num=None, file_num=None):
        """
        author: liyao
        date: 2018-11-27
        :param disk_symbol: smb端挂载的盘符
        :return:
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        log.info("current_dir=%s" % current_dir)
        try:
            root_path = '%s\\' % disk_symbol
            dir_base = os.path.join(root_path, 'test_dir')
            os.chdir(root_path)

            if dir_num is None:
                dir_num = 5
            dir_lst = []   # 将已创建的目录存到列表中
            for i in range(dir_num):
                dir = dir_base + '_%s' % i
                os.mkdir(dir)
                dir_lst.append(dir)

            if file_num is None:
                file_num = 3
            file_lst = []   # 保存已创建的文件
            for mem in dir_lst:
                file_base = os.path.join(mem, 'test_file')
                for i in range(file_num):
                    file = file_base + '_%s' % i
                    file_lst.append(file)
                    with open(file, 'w') as f:
                        f.write('hello world')
                        f.close()
        finally:
            os.chdir(current_dir)
        return dir_lst, file_lst

    def delete_dir_file(self, dir_lst, file_lst):
        """
        author: liyao
        date: 2018-11-28
        :param disk_symbol:smb端挂载的盘符
        :return:
        """
        for file in file_lst:
            os.remove(file)

        log.info('waiting for 10s')
        time.sleep(10)
        for dir in dir_lst:
            os.rmdir(dir)

    def count_file_num(self, disk_symbol):
        """
        author: liyao
        date: 2018-11-29
        :param disk_symbol:挂载的盘符
        :affect: 统计目录下的所有文件数（包含子目录下的文件数）
        :return:
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        log.info("current_dir = %s" % current_dir)
        try:
            count = 0
            file_lst = []
            root_path = '%s\\' % disk_symbol
            for dirpath, dirnames, filenames in os.walk(root_path):
                for file in filenames:
                    file_lst.append(os.path.join(dirpath, file))
                    count = count + 1
            log.info('waiting for 10s')
            time.sleep(10)
        finally:
            os.chdir(current_dir)
        return count, file_lst


    def create_move_delete(self, disk_symbol):
        '''
        author: liujx
        date: 2019-13-16
        :param disk_symbol:
        :return:
        ：description：移动集采用例
        '''
        current_dir = os.path.dirname(os.path.abspath(__file__))
        log.info("current_dir=%s" % current_dir)
        try:
            root_path = '%s\\' % disk_symbol
            dir_base = os.path.join(root_path, 'test_dir')
            os.chdir(root_path)
            os.mkdir(dir_base)
            dir_path = root_path
            for i in range(1, 9):
                dir_path = os.path.join(dir_path, '%s' % i)
                os.mkdir(dir_path)
            dir_base_new = os.path.join(root_path, 'test_dir1')
            os.rename(dir_base, dir_base_new)
            os.rmdir(dir_base_new)
            os.mkdir(dir_base)
            test_file = os.path.join(dir_base, 'testfile')
            with open(test_file, 'w') as f:
                f.write('hello, world')
                f.close()
            test_file_new = os.path.join(root_path, 'testfile')
            shutil.move(test_file, test_file_new)
            test_file_new_new = os.path.join(root_path, 'testfile1')
            os.renames(test_file_new, test_file_new_new)
            os.remove(test_file_new_new)

        finally:
            os.chdir(current_dir)

class Ftp():
    def test2_1(self):

        return

    def test2_2(self):

        return

    def test2_3(self):

        return


if __name__ == '__main__':
    a = Smb()
    a.smb_umount('X:')