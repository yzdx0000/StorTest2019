#!/usr/bin/python
# -*- encoding=utf8 -*-

import os
import sys
import json
import subprocess
from optparse import OptionParser


global Xml_File
global Account_Name
global Parastor_Ip
global Domain_Name
global Cli_Path

'''
def arg_analysis():
    global Xml_File
    global Account_Name
    global Parastor_Ip
    global Domain_Name
    global Cli_Path
    if len(sys.argv) != 6:
        print "Usage:create_s3_xml.py xml_to_change account_name parastor_ip domain_name cli.sh_path"
    Xml_File = sys.argv[1]
    Account_Name = sys.argv[2]
    Parastor_Ip = sys.argv[3]
    Domain_Name = sys.argv[4]
    Cli_Path = sys.argv[5]
    return
'''


def arg_analysis():
    """
       :author:      lichengxu
       :date:        2019.01.14
       :description: 获取并解析参数
       :return:
       """
    global Xml_File
    global Account_Name
    global Parastor_Ip
    global Domain_Name
    global Cli_Path

    usage = "usage: %prog [options] arg1 arg2 arg3"
    parser = OptionParser(usage)

    parser.add_option("-f", "--conf_path",
                      type="str",
                      dest="config_path",
                      default=None,
                      help='Required:True   Type:str   Help:Nodes that need to choose which xml file.'
                           'e.g. "/home/aaa_xml"')

    parser.add_option("-a", "--account_name",
                      type="str",
                      dest="account_name",
                      default=None,
                      help='Required:True   Type:str   Help:Nodes that need to input account name.'
                           'e.g. "aaa"')

    parser.add_option("-i", "--ip",
                      type="str",
                      dest="parastor_ip",
                      default=None,
                      help='Required:True   Type:str   Help:Nodes that need to send massage to parastor.'
                           'e.g. "20.2.42.71"')

    parser.add_option("-d", "--domain_name",
                      type="str",
                      dest="domain_name",
                      default=None,
                      help='Required:True   Type:str   Help:Nodes that need to change domain name.'
                           'e.g. "www.aaa.com"')

    parser.add_option("-p", "--cli_path",
                      type="str",
                      dest="cli_path",
                      default=None,
                      help='Required:True   Type:str   Help:Nodes that need to input cli.sh path.'
                           'e.g. "/home/Cosbench/0.4.2.c4/cli.sh"')

    options, args = parser.parse_args()
    """检查-f参数"""
    if options.config_path is None:
        parser.error("please input -f or --conf_path, xml file path")
    else:
        Xml_File = options.config_path

    """检查-a参数"""
    if options.account_name is None:
        parser.error("please input -a or --account_name, account name")
    else:
        Account_Name = options.account_name

    """检查-i参数"""
    if options.parastor_ip is None:
        parser.error("please input -i or --parastor_ip, parastor ip")
    else:
        Parastor_Ip = options.parastor_ip

    """检查-d参数"""
    if options.domain_name is None:
        parser.error("please input -d or --domain_name, domain name")
    else:
        Domain_Name = options.domain_name

    """检查-p参数"""
    if options.cli_path is None:
        parser.error("please input -p or --cli_path, cli.sh path")
    else:
        Cli_Path = options.cli_path

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


def find_account(account_email):
    """
    :author:           baourobing
    :date:             2018.08.29
    :description:      根据账户，返回sk
    :param account_id: (str)账户邮箱
    :return:
    """
    cmd = "pscli --command=find_account --account_email=%s" % account_email
    rc, stdout = command(cmd, Parastor_Ip)
    if rc != 0:
        return rc, None
    else:
        stdout = json.loads(stdout)
        account_id = stdout['result']['account_id']
        return rc, account_id


def list_certificates(account_id):
    """
    :author:           lichengxu
    :date:             2019.01.15
    :description:      根据账户id，返回ak,sk
    :param account_id: (str)账户id
    :return:
    """
    cmd = "pscli --command=list_certificates --account_id=%s" % account_id
    rc, stdout = command(cmd, Parastor_Ip)
    if rc != 0:
        return rc, None, None
    else:
        stdout = json.loads(stdout)
        certificate_id = stdout['result']['certificate_info'][0]['certificate_id']
        secret_key = stdout['result']['certificate_info'][0]['secret_key']
        return rc, certificate_id, secret_key


def change_xml(new_ak, new_sk):
    """
    :author:           modify by lichengxu
    :date:             2019.01.15
    :description:      修改XML文件
    :return:
    """
    new_prefix = "bucket%s" % Account_Name
    new_domainName = "http://%s:20480" % Domain_Name
    cmd1 = "grep accesskey %s | sed -n 1p | awk -F '[=|;]' '{print $4}'" % Xml_File
    cmd2 = "grep accesskey %s | sed -n 1p | awk -F '[=|;]' '{print $6}'" % Xml_File
    cmd3 = "grep endpoint %s | sed -n 1p | awk -F '[=|;]' '{print $8}'" % Xml_File
    cmd4 = "grep cprefix %s | sed -n 1p | awk -F '[=|;|\"]' '{print $10}'" % Xml_File

    rc, stdout = command(cmd1)
    old_ak = stdout.strip()
    rc, stdout = command(cmd2)
    old_sk = stdout.strip()
    rc, stdout = command(cmd3)
    old_name = stdout.strip()
    rc, stdout = command(cmd4)
    old_prefix = stdout.strip()

    cmd5 = 'sed -i "s/%s/%s/g" %s' % (old_ak, new_ak, Xml_File)
    cmd6 = 'sed -i "s/%s/%s/g" %s' % (old_sk, new_sk, Xml_File)
    cmd7 = 'sed -i "s?%s?%s?g" %s' % (old_name, new_domainName, Xml_File)
    cmd8 = 'sed -i "s/%s/%s/g" %s' % (old_prefix, new_prefix, Xml_File)
    command(cmd5)
    command(cmd6)
    command(cmd7)
    command(cmd8)
    return


def case():
    """判断账户是否存在"""
    account_email = Account_Name + "@sugon.com"
    rc, account_id = find_account(account_email)
    if rc != 0:
        """账户不存在，先创建账户"""
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
    else:
        """账户已存在，根据账户id获取ak,sk"""
        rc, new_ak, new_sk = list_certificates(account_id)

    """修改xml文件"""
    change_xml(new_ak, new_sk)

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