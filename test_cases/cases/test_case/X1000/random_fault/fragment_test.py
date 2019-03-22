#!/usr/bin/python
# -*- encoding=utf8 -*-
"""
 author 鲍若冰
 date 2018-07-28
 @summary：
    碎片文件整理。
 @changelog：
"""

import os
import time
import shutil
import random
from multiprocessing import Pool, Process


Test_Path = '/mnt/volume5'
Process_Num = 100       # 进程个数
File_Size = '100k'      # 文件大小
File_Num_A_Set = 100    # 一组中的文件数
Set_Num = 100           # 文件组数
Xfersize = 4            # 一次写入的大小，单位:K
Cycles_Num = 10         # 循环的次数


def get_file_size(file_size_str):
    """
    转换文件大小
    """
    if 'm' in file_size_str or 'M' in file_size_str:
        file_size = int(file_size_str.strip('mM'))*1024*1024
    elif 'k' in file_size_str or 'K' in file_size_str:
        file_size = int(file_size_str.strip('kK'))*1024
    else:
        file_size = int(file_size_str)
    return file_size


def get_one_write_context():
    """
    获取单次写入的内容
    """
    write_str = 'all or nothing, now or never!!!!'
    context = Xfersize*1024/len(write_str)*write_str
    return context


def write_one_file(file_name, file_size):
    """
    写文件
    :param file_name: 文件全路径
    :param file_size: 文件大小, int
    :return: 
    """
    context_one = get_one_write_context()
    write_nums = file_size/len(context_one)
    fd = os.open(file_name, os.O_RDWR | os.O_CREAT)
    for i in range(write_nums):
        os.write(fd, context_one)
        os.fsync(fd)
    os.close(fd)
    print "%s write finished" % file_name


def write_some_files(file_lst, file_size):
    """
    每个进程创建一些文件
    :param file_lst: 文件列表[[一组文件], [一组文件]] 
    :return: 
    """
    for set_file_lst in file_lst:
        for file_name in set_file_lst:
            write_one_file(file_name, file_size)


def del_most_file(file_lst):
    """
    删除100个文件的随机99个
    :param file_lst: 文件列表
    :return: 
    """
    del_file_lst = random.sample(file_lst, len(file_lst)-1)
    for file_name in del_file_lst:
        os.remove(file_name)
        print "%s delete finished" % file_name


def main():
    """
    主函数
    """
    """获取文件大小"""
    file_size = get_file_size(File_Size)

    for i in range(Cycles_Num):
        """创建子目录"""
        path_name = os.path.join(Test_Path, 'fragment_test_%s' % i)
        if os.path.exists(path_name):
            shutil.rmtree(path_name)
        os.mkdir(path_name)

        print "\n******************** %s create file begin ********************\n" % path_name

        """多进程创建文件,文件名的组成是 进程标号_组数_组内文件号_test"""
        all_file_lst = []
        for pro_id in range(Process_Num):
            """创建子目录"""
            dir_path_name = os.path.join(path_name, 'dir_%02d' % pro_id)
            os.mkdir(dir_path_name)
            pro_file_lst = []
            for set_id in range(Set_Num):
                set_file_lst = []
                for file_id in range(File_Num_A_Set):
                    file_name = "%03d_%02d_test" % (set_id, file_id)
                    file_name = os.path.join(dir_path_name, file_name)
                    set_file_lst.append(file_name)
                pro_file_lst.append(set_file_lst)
            all_file_lst.append(pro_file_lst)

        pro_lst = []
        for pro_file_lst in all_file_lst:
            p = Process(target=write_some_files, args=(pro_file_lst, file_size))
            pro_lst.append(p)

        for p in pro_lst:
            p.daemon = True
            p.start()
        for p in pro_lst:
            p.join()

        """删除文件"""
        print "\n******************** %s delete file begin ********************\n" % path_name
        for pro_file_lst in all_file_lst:
            for set_file_lst in pro_file_lst:
                del_most_file(set_file_lst)

        print "wait 600s ..."
        time.sleep(600)

        print "%s finish" % path_name


if __name__ == '__main__':
    main()