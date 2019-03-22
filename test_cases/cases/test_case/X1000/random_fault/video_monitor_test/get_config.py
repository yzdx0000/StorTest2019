#!/usr/bin/python
# -*- encoding=utf8 -*-

'''

'''
import sys,os,time,re
import datetime
from optparse import OptionParser
import random
import re

# 获取当前路径
cur_dir = os.path.dirname(os.path.realpath(__file__))
#parser = OptionParser()
#parser.add_option("-f",
#                  dest="paramfile",
#                  help="get paramfile.")
#(options,args) = parser.parse_args()
#if None != options.paramfile:
#    p_file = options.paramfile
#else:
#    print "Please input paramfile."
#    exit(1)
conf_file = cur_dir+'/'+'conf'
f = open(conf_file,'r+')

lines = f.readlines()
for line in lines:
    if 'big_file_write_threads' in line:
        big_file_write_threads_val = int(re.sub(' ','',line).split('#')[0].split('=')[-1])
#        print big_file_write_threads_val
    elif 'lit_file_write_threads' in line:
        lit_file_write_threads_val = int(re.sub(' ','',line).split('#')[0].split('=')[-1])
#        print lit_file_write_threads_val
    elif 'rm_file_threads' in line:
        rm_file_threads_val = int(re.sub(' ','',line).split('#')[0].split('=')[-1])
#        print rm_file_threads_val
    elif 'b_file_nums' in line:
        b_file_nums_val = int(re.sub(' ','',line).split('#')[0].split('=')[-1])
#        print b_file_nums_val
    elif 'l_file_nums' in line:
        l_file_nums_val = int(re.sub(' ','',line).split('#')[0].split('=')[-1])
#        print l_file_nums_val
    elif 'b_file_size' in line:
        b_file_size_val = re.sub(' |\[|\]','',line).split('#')[0].split('=')[-1].split(',')
#        print b_file_size_val
    elif 'l_file_size' in line:
        l_file_size_val = re.sub(' |\[|\]','',line).split('#')[0].split('=')[-1].split(',')
#        print l_file_size_val
    elif 'b_iorate' in line:
        b_iorate_val = int(re.sub(' ','',line).split('#')[0].split('=')[-1])
#        print b_iorate_val
    elif 'l_iorate' in line:
        l_iorate_val = int(re.sub(' ','',line).split('#')[0].split('=')[-1])
#        print l_iorate_val
    elif 'file_path' in line:
        file_path_val = re.sub(' ','',line).split('#')[0].split('=')[-1]
#        print file_path_val
    elif 'b_frame_size' in line:
        b_frame_size_val = int(re.sub(' ','',line).split('#')[0].split('=')[-1])
#        print b_frame_size_val
    elif 'l_frame_size' in line:
        l_frame_size_val = int(re.sub(' ','',line).split('#')[0].split('=')[-1])
#        print l_frame_size_val
    elif 'timeout' in line:
        timeout_val =  int(re.sub(' ','',line).split('#')[0].split('=')[-1])
#        print timeout_val
    elif 'path_size' in line:
        path_size_val = int(re.sub(' ','',line).split('#')[0].split('=')[-1])
#        print path_size_val
    elif 'test_path_nums' in line:
        test_path_nums = int(re.sub(' ','',line).split('#')[0].split('=')[-1])