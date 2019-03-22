#!/usr/bin/python
#-*-coding:utf-8-*-

################################################################################
#                                                                              #
#        Copyright (C), 1995-2014, Sugon Information Industry Co., Ltd.        #
#                                                                              #
################################################################################
# File Name     : tc_run.py                                                    #
# Module Name   : Testing Framework                                            #
# Version       : 1.0.0                                                        #
# Author        : Zhang Jianbin <zhangjb@sugon.com>                            #
# Created Date  : 2014/05/05                                                   #
# Description   : Run testcases of DLM                                         #
#                                                                              #
# History       :                                                              #
# 1.Date         : 2014/05/05                                                  #
#   Author       : Zhang Jianbin <zhangjb@sugon.com>                           #
#   Modification : Creating file                                               #
#                                                                              #
################################################################################
import commands, os, sys, string, getopt, ConfigParser, time

ROOT_DIR = '/mnt/parastor/'
g_node_config = ROOT_DIR + 'bin/nodes_config'
g_st_config = ROOT_DIR + 'bin/st_config'

g_opara_lists = []
g_ostor_lists = []

'''************************* P200 functions *************************'''

def dlm_get_opara_lists_P200(cf):
    global g_opara_lists

    for section in cf.sections():
        if section.find('oPara') >= 0:
            g_opara_lists.append(cf.get(section, 'ha_ip_0'))

def dlm_get_ostor_lists_P200(cf):
    global g_ostor_lists

    for section in cf.sections():
        if section.find('oStor') >= 0:
            g_ostor_lists.append(cf.get(section, 'ha_ip_0'))

def dlm_check_cores_P200():
    global g_opara_lists
    global g_ostor_lists

    for opara in g_opara_lists:
        rc = dlm_do_check_core(opara)
        if rc == 1:
            sys.exit(-1)

    for ostor in g_ostor_lists:
        rc = dlm_do_check_core(ostor)
        if rc == 1:
            sys.exit(-1)

'''************************* P300 functions *************************'''

def dlm_get_parastor_nodeip(cf):
    ctl_ip_list = []
    for section in cf.sections():
        if section.find('node') != -1:
            ctl_ip_list.append(cf.get(section, 'ctl_ip_0'))

    return ctl_ip_list

def dlm_check_cores_P300(ip_list):
    for ip in ip_list:
        rc = dlm_do_check_core(ip)
        if rc == 1:
            sys.exit(-1)
    return

'''************************* common functions *************************'''

def dlm_do_check_core(ip):
    cmd = 'ssh ' + ip + ' ls /home/parastor/log/core*'
    (ret, output) = commands.getstatusoutput(cmd)
    if ret == 0:
        return 1
    else:
        return 0

def dlm_read_config(filename):
    cf = ConfigParser.ConfigParser()
    try:
        cf.read(filename)
    except:
        print("Read config file %s FAILED" %(filename))
    return cf

def dlm_get_parastor_version():
    cf = dlm_read_config(g_st_config)
    sections = cf.sections()
    for section in sections:
        if section == 'parastor':
            VERSION = cf.get(section, 'version')
            return VERSION
    return None

def main():
    version = dlm_get_parastor_version()
    cf = dlm_read_config(g_node_config)
    if 'P200' == version:
        dlm_get_opara_lists_P200(cf)
        dlm_get_ostor_lists_P200(cf)
        dlm_check_cores_P200()
    elif 'P300' == version:
        ctl_ip_list = dlm_get_parastor_nodeip(cf)
        dlm_check_cores_P300(ctl_ip_list)
    else:
        print("the st_config's version is error!!!")

    
if __name__ == '__main__':
    main()
