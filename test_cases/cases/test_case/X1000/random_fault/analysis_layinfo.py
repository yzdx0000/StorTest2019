#!/usr/bin/python
# -*-coding:utf-8 -*
import os
import sys

lmosid_lst = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
result_lst = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


def traverse(f):
    fs = os.listdir(f)

    for f1 in fs:
        tmp_path = os.path.join(f, f1)
        cmd = "/home/parastor/tools/para_layinfo %s | grep lmosid" % tmp_path
        lmosid = int(os.popen(cmd).readlines()[0].strip().split(":")[-1])
        if lmosid in lmosid_lst:
            index = lmosid_lst.index(lmosid)
            result_lst[index] += 1
        if os.path.isdir(tmp_path):
            traverse(tmp_path)


def log_result(fh, str):
    fh.write(str)
    print str.replace("\n", "")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Please input the path: python xxx.py \033[1;31;40m/your/path\033[0m"
        sys.exit(1)
    path = sys.argv[1]
    traverse(path)
    log_name = "data_result"
    if os.path.exists(log_name):
        os.remove(log_name)
    with open(log_name, "a+") as fh:
        log_result(fh, "lmosid    count\n")
        for i in lmosid_lst:
            log_result(fh, "%-10d%d\n" % (i, result_lst[i - 1]))
