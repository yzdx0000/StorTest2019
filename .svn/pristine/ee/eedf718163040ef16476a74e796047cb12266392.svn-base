#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import sys
import time
import subprocess

# =========================
# 创建属性文件，记录编译打包路径和开发用例列表路径
# The Author:duyuli
# Create Date:2019/03/05
# =========================
job_name = sys.argv[1]
parastor_tar_dir = "/var/ftp/%s" % sys.argv[1]
file_path = "/home/jenkins/scripts/propfile"
develop_tar_path = "/home/jenkins/scripts/develop_list.tar.gz"

def run_command(cmd, node_ip=None, timeout=None):
    if node_ip:
        cmd1 = 'ssh %s "%s"' % (node_ip, cmd)
    else:
        cmd1 = cmd

    if timeout:
        cmd1 = "timeout %s %s" % (timeout, cmd1)
    process = subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output, unused_err = process.communicate()
    retcode = process.poll()
    return retcode, output

def find_latest_tar():
    cmd = "ls %s" % parastor_tar_dir
    rc, stdout = run_command(cmd)
    stdout = stdout.strip()
    tar_time_max = 0
    for dir_tar in stdout.split("\n"):
        tar_time = int(''.join(dir_tar.split('_')))
        if tar_time > tar_time_max:
            tar_time_max = tar_time

    for dir_tar in stdout.split("\n"):
        tar_time_match = int(''.join(dir_tar.split('_')))
        if tar_time_max == tar_time_match:
            dir_tar_path = os.path.join(parastor_tar_dir, dir_tar)
            cmd = "ls %s" % dir_tar_path
            rc, stdout = run_command(cmd)
            tar_path = os.path.join(dir_tar_path, stdout.strip())
            return tar_path

    raise Exception("get tar path error")

def find_develop_list():
    develop_dir_new_path = None
    develop_list_str = None
    if os.path.exists(develop_tar_path):
        current_time = time.strftime("%y_%m_%d_%H_%M_%S")
        develop_dir_new_path = os.path.join(os.path.dirname(develop_tar_path), current_time)
        develop_tar_new_path = os.path.join(develop_dir_new_path, 'develop_list.tar.gz')
        cmd = "mkdir -p %s;mv %s %s;tar -xf %s -C %s" % (develop_dir_new_path,
                                                         develop_tar_path,
                                                         develop_dir_new_path,
                                                         develop_tar_new_path,
                                                         develop_dir_new_path)
        run_command(cmd)

        cmd_develop_list = "ls %s" % develop_dir_new_path + '/*/'
        rc, stdout = run_command(cmd_develop_list)
        stdout = stdout.strip()
        develop_list_str = ','.join(stdout.split('\n'))

    return develop_dir_new_path, develop_list_str

def create_propfile():
    parastor_tar_path = find_latest_tar()
    develop_dir_new_path, develop_list_str = find_develop_list()
    if develop_dir_new_path is not None:
        data1 = "tar_path=%s\n" % parastor_tar_path
        data2 = "develop_list_dir=%s\n" % develop_dir_new_path
        data3 = "develop_list_str=%s" % develop_list_str
        with open(file_path, 'w') as fd:
            fd.writelines([data1, data2, data3])
    else:
        data1 = "tar_path=%s" % parastor_tar_path
        with open(file_path, 'w') as fd:
            fd.write(data1)
    return


if __name__ == '__main__':
    create_propfile()
