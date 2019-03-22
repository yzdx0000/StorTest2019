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
g_opara_log_path = '/home/parastor/log/'
g_ostor_log_path = '/home/parastor/log/'
g_oapp_log_path = '/var/log/'
g_oapp_log_lists =  ['parastor_1.log_0', 'parastor_1.log_1', 'parastor.log_0', \
                     'parastor.log_1', 'mgcdcli.log_0', 'mgcdcli.log_1']
g_opara_log_lists = ['dlm_stats.log_1', 'jnl.log_0', 'mgcdmos.log_0', 'mgcdtool.log_0', 	\
                     'mgrha.log_0', 'mgrha.pid', 'mgs.log_0', 'mtools.log_0', 'ofsha.log_0',	\
                     'ofsha.pid', 'oPara.log_1', 'paratrans.log_0', 'start.log', 'jnl.log_1',	\
                     'mgcdmos.log_1', 'mgcdtool.log_1', 'mgrha.log_1', 'mgrha_start.log', 	\
                     'mgs.log_1', 'mtools.log_1', 'ofsha.log_1', 'oPara.log_0', 		\
                     'oPara_opstat.log', 'paratrans.log_1']
g_ostor_log_lists =  ['dlm_stats.log_0', 'mgcdds.log_0', 'mgcdds.log_1', 'mgcdtool.log_0', 	\
                      'mgcdtool.log_1', 'oStor.log_0', 'oStor.log_1']

g_oapp_lists = []
g_opara_lists = []
g_ostor_lists = []

def dlm_read_config(filename):
    cf = ConfigParser.ConfigParser()
    try:
        cf.read(filename)
    except:
        print("Read config file %s FAILED" %(filename))
    return cf

def dlm_get_opara_lists(cf):
    global g_opara_lists

    for section in cf.sections():
        if section.find('oPara') >= 0:
            g_opara_lists.append(cf.get(section, 'ha_ip_0'))

def dlm_get_oapp_lists(cf):
    global g_oapp_lists

    for section in cf.sections():
        if section.find('oApp') >= 0:
            g_oapp_lists.append(cf.get(section, 'ha_ip_0'))

def dlm_get_ostor_lists(cf):
    global g_ostor_lists

    for section in cf.sections():
        if section.find('oStor') >= 0:
            g_ostor_lists.append(cf.get(section, 'ha_ip_0'))

def dlm_do_clean_opara_log(ip):
    global g_opara_log_lists
    #cmd = 'ssh ' + ip + ' ls ' + g_opara_log_path
    #(ret, output) = commands.getstatusoutput(cmd)
    #if ret != 0:
    #    print("Failed to get log files, err%d" %ret)
    #    sys.exit(-1)

    #list = output.split()
    #for l in list:
    cmd = 'ssh ' + ip + ' "'
    for l in g_opara_log_lists:
        cmd += 'echo > ' + g_opara_log_path + l + ';'
    cmd += '"'
    os.system(cmd)

    cmd = 'ssh ' + ip + ' "'
    for l in g_oapp_log_lists:
        cmd += 'echo > ' + g_oapp_log_path + l + ';'
    cmd += '"'
    os.system(cmd)

    cmd = 'ssh ' + ip + ' rm -rf /core.*'
    os.system(cmd)

def dlm_do_clean_oapp_log(ip):
    global g_oapp_log_lists

    cmd = 'ssh ' + ip + ' "'
    for l in g_oapp_log_lists:
        cmd += 'echo > ' + g_oapp_log_path + l + ';'
    cmd += '"'
    os.system(cmd)

def dlm_do_clean_ostor_log(ip):
    global g_ostor_log_lists

    cmd = 'ssh ' + ip + ' "'
    for l in g_ostor_log_lists:
        cmd += 'echo > ' + g_ostor_log_path + l + ';'
    cmd += '"'
    os.system(cmd)

def dlm_clean_opara_log():
    global g_opara_lists

    for l in g_opara_lists:
        dlm_do_clean_opara_log(l)
    
def dlm_clean_oapp_log():
    global g_oapp_lists

    for l in g_oapp_lists:
        dlm_do_clean_oapp_log(l)

def dlm_clean_ostor_log():
    global g_ostor_lists

    for l in g_ostor_lists:
        dlm_do_clean_ostor_log(l)

def main():
    cf = dlm_read_config(g_node_config)
    dlm_get_opara_lists(cf)
    dlm_get_oapp_lists(cf)
    dlm_get_ostor_lists(cf)
    dlm_clean_opara_log()
    dlm_clean_oapp_log()
    dlm_clean_ostor_log()
    
if __name__ == '__main__':
    main()
