#!/usr/local/bin/python
# -*- coding:utf-8 -*-
import os
import sys
import hashlib
#=================================================================================
#  latest update:2018-06-14                                                    =
#  author:wangguanglin                                                           =
#=================================================================================
# 2018-06-14:
# 修改者：wangguanglin
#@summary：
#   比较文件内容的一致性 可以选择要比较的文件，在什么位置进行比较，比较的块大小，
#   返回所要比较内容的md5值,光标的位置，stat文件的信息
#@steps:
#
#   1、第一个参数是获取外来要打开的文件
#   2、第二个参数获取偏移量
#   3、第三个参数是读/写的块大小
#   4、第四个参数是读写选择


#changelog:
######################################################


hash1 = hashlib.md5()

f = open(sys.argv[1], mode='r+') #获取外来要打开的文件，并打开
"""从文件开头写入4M的字符串a"""
off_set=sys.argv[2] #获取偏移量
offset=int(off_set)
block=sys.argv[3] #读/写的块大小
block_size=int(block)
r_w=sys.argv[4] #读写选择
test_str='z'*block_size
f.seek(offset)
if r_w=='r':
    aa1 = f.read(block_size)
elif r_w=='w':
    f.write(test_str)
    f.seek(offset)
    aa1 = f.read(block_size)
else:
    print "ERROR"
hash1.update(aa1)
file_md5 = hash1.hexdigest()
print  file_md5
print f.tell()
print  os.stat(sys.argv[1])

f.close()