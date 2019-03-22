# -*-coding:utf-8 -*
from multiprocessing import Lock, Value
import multiprocessing
import os
import time
import sys

import log

#
# Author: caizhenxing
# date 2018/10/5
# @summary：
#   每个CPU核心一个进程，以固定速率追加写，块大小为1MB+1KB
# @steps:
# @changelog：
#

# 当前脚本名称
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]


lock = Lock()
# 设置多进程全局变量
counter = Value('i', 0)


def case(filesize, runtime, speed):
    global lock, counter
    filename = "test_" + str(os.getpid())
    ds = 0
    ts = int(round(time.time() * 1000))
    ts1 = 0

    with open(filename, "a+") as f:
        while ds < filesize*1024*1024 and (ts1 - ts) < runtime:
            ts1 = int(round(time.time() * 1000))
            t_1 = int(round(time.time() * 1000))
            for i in range(0, int(speed)):
                t1 = int(round(time.time() * 1000))
                f.write(str(0)*1024*1025)
                f.flush()
                t2 = int(round(time.time() * 1000))
                if (t2 - t1) > 100:
                    with lock:
                        counter.value += 1
            t_2 = int(round(time.time() * 1000))
            # 当连续写10次后，如果时长小于1秒，则等待一会
            if (t_2 - t_1) < 1000:
                time.sleep((t_2 - t_1)/1000)
                # print "sleep time: {} ms".format(t_2 - t_1)
            # 获取文件大小
            ds = os.path.getsize(filename)
            # 如果文件大小大于指定size，则清空文件内容
            if ds > filesize*1024*1024:
                # print "max 100ms: {}, PID: {}".format(counter.value, os.getpid())
                os.system(">" + filename)
                ds = 0
            # 如果到达指定运行时长，则退出
            if (ts1 - ts) > runtime:
                print "max 100ms: {}".format(counter.value)
                log.info("max 100ms: {}".format(counter.value))
                os.system("rm -rf " + filename)
                sys.exit(0)


if __name__ == "__main__":
    for process_idx in range(multiprocessing.cpu_count()):
        p = multiprocessing.Process(target=case, args=(500, 3600000, 10))
        # 使进程再指定CPU上运行
        os.system("taskset -p -c %d %d" % (process_idx % multiprocessing.cpu_count(), os.getpid()))
        p.start()
