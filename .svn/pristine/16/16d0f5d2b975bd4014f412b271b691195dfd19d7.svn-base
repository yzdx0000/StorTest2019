#!/usr/bin/python
# -*- encoding=utf8 -*-

'''

'''
import os
from multiprocessing import Process
import log
import functions
import get_config


# 删除文件的进程数
rm_file_threads = functions.rm_file_threads

# 测试的挂载点
file_path = functions.file_path
psize = functions.path_size

def main():
    psize_num = 0
    #遍历所有测试目录
    for fpath in file_path:
        b_file_size = get_config.b_file_size_val  # 每个大文件大小，单位：M或G
        l_file_size = get_config.l_file_size_val  # 每个小文件大小，单位：M或K
        log.info("Change path to :%s" %(fpath))
        b_pool = []
        #定义匿名管道，容量监控进程通过该管道向主进程发送消息
        pipein, pipeout = os.pipe()
        #判断测试项是否有大文件
        if b_file_size[0] != '0':
            #遍历大文件配置数组，给每个大小分配不同的进程数
            for bs in b_file_size:
                for bwthread in range(int(b_file_size[1])):
                    b_child = Process(target=functions.big_file_write,
                                      args=(fpath, b_file_size[0], bwthread, functions.b_iorate))
                    b_pool.append(b_child)
                b_file_size = b_file_size[2:]
                if len(b_file_size) == 0:
                    break
        #判断是否有小文件读写
        elif l_file_size[0] != '0':
            #遍历小文件配置数组，给每个大小分配不同的进程数
            for ls in l_file_size:
                for lwthread in range(int(l_file_size[1])):
                    l_child = Process(target=functions.lit_file_write,args=(fpath,l_file_size[0],lwthread,functions.l_iorate))
                    b_pool.append(l_child)
                l_file_size = l_file_size[2:]
                if len(l_file_size) == 0:
                    break
        #删除文件的进程
        for rmthread in range(rm_file_threads):
            rm_child = Process(target=functions.remove_files,args=(fpath,))
            b_pool.append(rm_child)
        #监控被测试目录已用容量的进程
        psize_child = Process(target=functions.check_path_size,args=(fpath,psize,pipeout))
        b_pool.append(psize_child)
        psize_num += 1
        for p in b_pool:
            p.start()
        suc_num = 0
        #死循环，读取匿名管道的内容，如果收到check_path_size发来的‘break’信号，则杀死所有子进程，同时退出当前测试
        # 目录，进入下一个目录测试
        while True:
            line = os.read(pipein, 7)
            if 'break' in line:
                break_flag = 1
                for p in b_pool:
                    p.terminate()
                break
#        if break_flag == 1:
#            continue
        for p in b_pool:
            p.join()
#        for p in b_pool:
#            p.terminate()
if __name__ == '__main__':
    main()
