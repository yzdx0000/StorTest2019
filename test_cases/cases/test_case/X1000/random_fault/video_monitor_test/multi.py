import sys,os,time,re
from multiprocessing import Process,Pipe,Pool
import logging
import commands

paths = ['a/1','b/1','c/1']
def print_hello(fpath):
    print "hello"+fpath
    time.sleep(20)
    print "world"+fpath
def breakpoint(pipeout):
    i = 0
    while True:
        i += 1
        if i == 7:
            os.write(pipeout, 'break')
        time.sleep(1)
        print "waiting"
def main():
    for fpath in paths:
        cmd = ("du -sh /mnt/ | awk '{print $1}'")
        res,output = commands.getstatusoutput(cmd)
        print output.split('G')[0]
        exit(1)
        break_flag = 0
        pipein,pipeout = os.pipe()
        b_pool = []
        b_child = Process(target=print_hello,args=(fpath,))
        b_pool.append(b_child)
        b_child = Process(target=breakpoint,args=(pipeout,))
        b_pool.append(b_child)
        for p in b_pool:
            p.start()
        while True:
            line = os.read(pipein,7)
            if 'break' in line:
                break_flag = 1
                for p in b_pool:
                    p.terminate()
                break
        if break_flag == 1:
            continue
        for p in b_pool:
            p.join()
if __name__ == '__main__':
    main()
