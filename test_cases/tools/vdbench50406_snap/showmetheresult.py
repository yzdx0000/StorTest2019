#!/usr/bin/python
# -*- coding: utf-8 -*-
# ===============================================================================================
# What this can do?
# Print Vdbench frequent perform results in terminal.
# ===============================================================================================
# Why use this script?
# Vdbench504 will not print MAX RESP in filesystem testing what is the main purpose by this script,
# addtionally it can also show perform result with graphic print.
# ===============================================================================================
# Created by lukexing @ 2016.10.7
# version = 0.1
import os
import sys
import commands
import string
import re
import matplotlib.pyplot as plt


def _get_section():
    section_list, row_list = [], []
    cmd_left_section = 'sed -n \'/<a/,$p\' ' + sys.argv[1]
    cmd_get_section = 'sed -n \'/<a/,/avg/p\' ' + sys.argv[1]
    left_section = commands.getoutput(cmd_left_section).split("\n")  # type(left_section) = list
    for row in left_section: #row type is str
        if re.search("^<a", row):
            row_list.append(row)
        elif re.search("^[0-9]", row) and not re.search("avg", row):
            row_list.append(row)
        elif re.search("avg", row):
            row = _clean_avg(row)
            row_list.append(row)
            section_list.append(row_list)
            row_list = []
        else:
            pass
    return section_list


def _clean_avg(str):
    clean_list = str.split()
    for i in range(len(clean_list)):
        if clean_list[i] == '\xef\xbf\xbd':
            clean_list[i] = '0'
        else:
            pass
    clean_str = ' '.join(clean_list)
    return clean_str


def _get_resp(list):
    return float(list[10]), float(list[8])


def _get_draw_list(list):
    w_resp, r_resp, w_bw, r_bw, w_ops, r_ops = list[10], list[8], list[12], list[11], list[9], list[7]
    draw_list = [w_resp, r_resp, w_bw, r_bw, w_ops, r_ops]
    return draw_list


def _draw_dis(ylist):
    plt.figure(figsize=(12, 8), dpi=80)
    ytext = ['write resp: ms','read resp: ms','write bandwidth: MB/s','read bandwidth: MB/s','write IOPS','read IOPS']
    for y, t in zip(range(len(ylist)), ytext):
        plt.subplot(3, 2, y + 1)
        plt.plot(ylist[y])
        plt.ylabel(t)
    plt.show()


def _get_title(list):
    title_list = list[0].split()
    tmp_title = title_list[-1]
    title = tmp_title.split('<')[0]
    return title


def get_result(list):
    title = _get_title(list)
    avg_list = list[-1].split()
    avg_w_resp = float(avg_list[10])
    avg_r_resp = float(avg_list[8])
    avg_w_bandwidth = float(avg_list[12])
    avg_r_bandwidth = float(avg_list[11])
    avg_ops = float(avg_list[2])
    avg_ops_resp = float(avg_list[3])
    avg_sum = [avg_w_resp, avg_r_resp, avg_w_bandwidth, avg_r_bandwidth, avg_ops, avg_ops_resp]
    avg_sum_result = 0
    max_w_resp, max_r_resp = 0, 0
    d_w_resp, d_r_resp, d_w_bw, d_r_bw, d_w_ops, d_r_ops = [], [], [], [], [], []
    draw_type = [d_w_resp, d_r_resp, d_w_bw, d_r_bw, d_w_ops, d_r_ops]
    list.pop()
    list.pop(0)
    for i in list:
        tmp_list = i.split()
        tmp_resp = _get_resp(tmp_list)
        if tmp_resp[0] > max_w_resp:
            max_w_resp = tmp_resp[0]
        if tmp_resp[1] > max_r_resp:
            max_r_resp = tmp_resp[1]
        tmp_draw_list = _get_draw_list(tmp_list)
        for j in range(len(tmp_draw_list)):
            draw_type[j].append(tmp_draw_list[j])
    print "======================================"
    print "%s" % title
    print "======================================"
    print "max_write_resp      = %.3f ms" % max_w_resp
    print "avg_write_bandwidth = %.3f MB/s" % avg_w_bandwidth
    print "avg_write_resp      = %.3f ms" % avg_w_resp
    print "max_read_resp       = %.3f ms" % max_r_resp
    print "avg_read_bandwidth  = %.3f MB/s" % avg_r_bandwidth
    print "avg_read_resp       = %.3f ms" % avg_r_resp
    print "avg_ops             = %.3f " % avg_ops
    print "avg_ops_resp        = %.3f ms" % avg_ops_resp
    print "======================================"
    print "\n"
    for i in avg_sum:
        avg_sum_result += int(i*1000)
    if avg_sum_result:
        _draw_dis(draw_type)


def main():
    sections = _get_section()
    for i in sections:
        get_result(i)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Please input the vdbench summary.html fullpath." 
        print "exp: ./showmetheresult.py /home/vdbench504/output/summary.html"
        exit(-1)
    main()

