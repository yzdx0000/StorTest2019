#-*-coding:utf-8 -*
#!/usr/bin/python

import os
import time
import commands
import json
import hashlib

import utils_path
import common
import snap_common
import nas_common

import random
import log
import shell
import get_config
import tool_use
import prepare_clean

#=================================================================================
#  latest update:2018-08-17                                                    =
#  author:wangguanglin                                                           =
#=================================================================================
# 2018-08-17:
# Author：wangguanglin
#@summary：
#   私有客户端大文件操作控制
#@steps:
#   1、部署大容量存储集群；
#   2、挂载2个私有客户端；
#   3、通过私有客户端创建256T的大文件（可通过python语言或c语言中的truncate函数进行创建）；
#   4、第一个客户端从offset:0的位置每次间隔50T对文件写入4M的数据；
#   5、第二个客户端读写所有写入的4M数据是否正确；
#   6、第二个客户端删除该大文件。
#
   #changelog:
######################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
vdb_path = os.path.join(nas_common.BASE_NAS_PATH, FILE_NAME)             # /mnt/wangguanglin/cus_6_1_0_27
create_file_path = os.path.join(nas_common.ROOT_DIR, FILE_NAME)         # wangguanglin:/cus_6_1_0_27
PRIVATE_CLIENT_IP1 = get_config.get_client_ip(0)
PRIVATE_CLIENT_IP2 = get_config.get_client_ip(1)
PRIVATE_CLIENT_IP3 = get_config.get_client_ip(2)


def case():
    log.info('3> 通过私有客户端创建256T的大文件（可通过python语言或c语言中的truncate函数进行创建）')
    cmd = "mkdir %s"% vdb_path
    rc, stdout = common.run_command(PRIVATE_CLIENT_IP1, cmd)
    common.judge_rc(rc, 0, 'create path')

    test_file1=os.path.join(vdb_path,'test_file1')
    cmd = "ssh %s truncate -s 256T %s" %(PRIVATE_CLIENT_IP1,test_file1)
    rc, stdout = common.run_command(PRIVATE_CLIENT_IP1, cmd)
    common.judge_rc(rc, 0, 'truncate 256T file')

    log.info('4> 第一个客户端从offset:0的位置每次间隔50T对文件写入4M的数据')
    offset1 = 54975581388800 #500T=500*1024*1024*1024*1024
    block_size = 4194304 #块大小为4M
    r_w = 'w'

    '''校验工具'''
    tools_path = get_config.get_tools_path()
    VERIFY_TOOL = os.path.join(tools_path,'verify')
    verify_file=os.path.join(VERIFY_TOOL,'verify_common.py')

    log.info(' 第一个客户端读写所有写入的4M数据是否正确')
    cmd21 = "ssh %s python %s %s %s %s %s" \
           % (PRIVATE_CLIENT_IP1,verify_file, test_file1,offset1,block_size,r_w)
    rc, stdout = common.run_command(PRIVATE_CLIENT_IP1, cmd21)
    common.judge_rc(rc, 0, 'the first private client %s get offset %s data '%(PRIVATE_CLIENT_IP1,offset1))
    file21_md5=str(stdout.strip().split()[0])
    print("The %s md5 value of the first private client %s " %(offset1, file21_md5))

    log.info('5> 第二个客户端读写所有写入的4M数据是否正确')
    cmd1 = "ssh %s python %s %s %s %s %s" \
           % (PRIVATE_CLIENT_IP2,verify_file, test_file1,offset1,block_size,r_w)
    rc, stdout = common.run_command(PRIVATE_CLIENT_IP2, cmd1)
    common.judge_rc(rc, 0, 'the second private client %s get offset %s data '%(PRIVATE_CLIENT_IP2,offset1))
    file1_md5=str(stdout.strip().split()[0])
    print("The %s md5 value of nfs client %s " %(offset1, file1_md5))
    if file21_md5 != file1_md5:
        log.error('The file was read successfully but the data of %s offset was not correct!!!'% offset1 )
        raise Exception('The file was read successfully but the data of %s offset was not correct!!!'% offset1)

    log.info('6> 第二个客户端删除该大文件')
    cmd = "rm -rf %s"% test_file1
    rc, stdout = common.run_command(PRIVATE_CLIENT_IP2, cmd1)
    common.judge_rc(rc, 0, 'the second private client %s remove %s '%(PRIVATE_CLIENT_IP2,test_file1))


def main():
    prepare_clean.test_prepare(FILE_NAME)
    case()
    prepare_clean.test_clean(FILE_NAME)
    log.info('succeed!')


if __name__ == '__main__':
    common.case_main(main)






