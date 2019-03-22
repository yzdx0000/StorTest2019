#!/usr/bin/python
# -*- encoding=utf8 -*-

import os
import sys
import json
import subprocess


global Xml_File
global Account_Name
global Parastor_Ip
global Cli_Path


def arg_analysis():
    global Xml_File
    global Account_Name
    global Parastor_Ip
    global Cli_Path
    if len(sys.argv) != 5:
        print "Usage:create_s3_xml.py xml_to_change account_name parastor_ip cli.sh_path"
    Xml_File = sys.argv[1]
    Account_Name = sys.argv[2]
    Parastor_Ip = sys.argv[3]
    Cli_Path = sys.argv[4]
    return


def command(cmd, node_ip=None):
    """
    :author:        baoruobing
    :date  :        2018.08.15
    :description:   执行shell命令
    :param cmd:     (str)要执行的命令
    :param node_ip: (str)节点ip,不输入时为本节点
    :return:
    """
    if node_ip:
        cmd1 = 'ssh %s "%s"' % (node_ip, cmd)
    else:
        cmd1 = cmd
    process = subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output, unused_err = process.communicate()
    retcode = process.poll()
    return retcode, output


def add_account(name, email, quota):
    """
    :author:      baourobing
    :date:        2018.08.29
    :description: 创建s3账户
    :param name:  (str)账户名字
    :param email: (str)邮箱
    :param quota: (int)配额，byte
    :return:
    """
    cmd = "pscli --command=add_account --account_name=%s --account_email=%s --account_quota=%s" % (name, email, quota)
    rc, stdout = command(cmd, Parastor_Ip)
    if rc != 0:
        print stdout
        return rc, stdout
    else:
        print stdout
        stdout = json.loads(stdout)
        account_id = stdout['result']['account_id']
        return rc, account_id


def add_certificate(account_id):
    """
    :author:           baourobing
    :date:             2018.08.29
    :description:      创建s3证书
    :param account_id: (str)账户id
    :return:
    """
    cmd = "pscli --command=add_certificate --account_id=%s" % account_id
    rc, stdout = command(cmd, Parastor_Ip)
    if rc != 0:
        return rc, None, None
    else:
        stdout = json.loads(stdout)
        certificate_id = stdout['result']['certificate_id']
        certificate = stdout['result']['secret_key']
        return rc, certificate_id, certificate




def case():
    """创建账户"""
    account_email = Account_Name + "@sugon.com"
    rc, account_id = add_account(Account_Name, account_email, 0)
    if rc != 0:
        print "account exist"
        print account_id
        sys.exit(1)

    """创建证书"""
    rc, new_ak, new_sk = add_certificate(account_id)
    if rc != 0:
        print "create certificate failed!!!"
        sys.exit(1)

    new_prefix = "zh%s" % Account_Name
    cmd1 = "grep accesskey %s | sed -n 1p | awk -F '[=|;]' '{print $4}'" % Xml_File
    cmd2 = "grep accesskey %s | sed -n 1p | awk -F '[=|;]' '{print $6}'" % Xml_File
    cmd3 = "grep cprefix %s | sed -n 1p | awk -F '[=|;|\"]' '{print $10}'" % Xml_File
    rc, stdout = command(cmd1)
    old_ak = stdout.strip()
    rc, stdout = command(cmd2)
    old_sk = stdout.strip()
    rc, stdout = command(cmd3)
    old_prefix = stdout.strip()

    cmd4 = 'sed -i "s/%s/%s/g" %s' % (old_ak, new_ak, Xml_File)
    cmd5 = 'sed -i "s/%s/%s/g" %s' % (old_sk, new_sk, Xml_File)
    cmd6 = 'sed -i "s/%s/%s/g" %s' % (old_prefix, new_prefix, Xml_File)
    command(cmd4)
    command(cmd5)
    command(cmd6)

    cmd = "sh %s submit %s" % (Cli_Path, Xml_File)
    rc = os.system(cmd)
    if rc != 0:
        print "cmd: %s  failed!!!" % cmd
        sys.exit(1)


def main():
    arg_analysis()
    case()


if __name__ == '__main__':
    main()
