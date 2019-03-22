#!/usr/bin/python
#-*-coding:utf-8-*-

import commands, os, sys, string, getopt, ConfigParser, time

def main():
    time.sleep(3)
    os.system("echo b > /proc/sysrq-trigger")

if __name__ == '__main__':
    main()
