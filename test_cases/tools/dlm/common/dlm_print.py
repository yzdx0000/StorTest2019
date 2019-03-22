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
# Description   : DLM common module for print                                  #
#                                                                              #
# History       :                                                              #
# 1.Date         : 2014/05/05                                                  #
#   Author       : Zhang Jianbin <zhangjb@sugon.com>                           #
#   Modification : Creating file                                               #
#                                                                              #
################################################################################

beauty_len = 100

#print like this
#######################
def print_a_hash_line():
    str_tmp = ''
    print str_tmp.center(beauty_len,'#')

#print like this
#         str         #
def print_beauty(fmt):
    str_tmp = str(fmt)
    for line in str_tmp.split('\n'):
        line_tmp = line.center(beauty_len-2)
        print line_tmp.center(beauty_len, '#')
