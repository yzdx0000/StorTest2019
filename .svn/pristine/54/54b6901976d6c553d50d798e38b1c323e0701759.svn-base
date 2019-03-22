#!/usr/bin/python
# -*-coding:utf-8 -*

import os
import utils_path
import common2
import log
import get_config
import login
import commands
import re
import datetime
import dpc
import random
import disk
import error
import time

conf_file = common2.CONF_FILE

file_name = os.path.basename(__file__)
file_name = file_name[:-3]
log_file_path = log.get_log_path(file_name)
log.init(log_file_path, True)

deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()
disk = disk.disk()
osan = common2.oSan()
(vip, lun) = login.login()
case_list_path = "/home/StorTest/test_cases/cases/test_case/X1000/additional/"
case_list_file = case_list_path + "param"


def check_core():
    # 检查是否有core
    core_flag = False
    for ip in deploy_ips:
        cmd1 = ("ssh root@%s 'ls /core.* 2> /dev/null'" % (ip,))
        cmd2 = ("ssh root@%s 'ls /home/parastor/log/core.* 2> /dev/null'" % (ip,))
        rc1, stdout1 = commands.getstatusoutput(cmd1)
        rc2, stdout2 = commands.getstatusoutput(cmd2)
        if rc1 == 0 or rc2 == 0:
            core_flag = True
            break
        else:
            core_flag = False
    if core_flag is True:
        exit(1)


def analysis_range(lun_range):
    lun_range = re.sub('\(|\)|[a-zA-Z]', '', lun_range).split(',')
    if int(lun_range[0]) >= int(lun_range[1]):
        print lun_range[0] + ":" + lun_range[1]
        print "Get wrong range,please check your param."
        exit(1)
    return int(lun_range[0]), int(lun_range[1])


def get_lba(cip, c_lun):
    cmd = ("ssh root@%s 'fdisk -l %s'" % (cip, c_lun))
    res, output = commands.getstatusoutput(cmd)
    lba = output.split('\n')[-1].split()[1]
    while 'fdisk' in lba:
        res, output = commands.getstatusoutput(cmd)
        lba = output.split('\n')[-1].split()[1]
        time.sleep(3)
    return lba


def analysis_xml_file():
    cmd = 'ls %s' % case_list_file
    rc, stdout = commands.getstatusoutput(cmd)
    if 0 != rc:
        print '%s is not exist!!!' % case_list_file
        return
    with open(case_list_file, 'r') as f:
        for (num, line) in enumerate(f, 1):
            if line == '\r\n':
                continue
            new_line = get_config.get_processd_single_line(line)
            if 0 == len(new_line):
                continue
            print "line:" + str(num) + ",param:" + new_line
            new_line = new_line.split("/")
            # parameters of vdbench
            # 偏移量
            align = int(new_line[0]) / 512 * 512
            offset = int(new_line[1]) / 512 * 512
            # 读写比例
            rdpct = new_line[2]
            # 随机比例
            seekpct = new_line[3]
            # io大小
            iosize = new_line[4]
            # 进程数
            threads = new_line[5]
            # 是否开启校验
            jn_jro = new_line[6]
            # io速率
            io_rate = new_line[7]
            # 最大数据量
            maxdata = new_line[8]
            # range区间
            range_expand = int(new_line[9])
            # unmappct
            if len(new_line) == 11:
                unmappct = int(new_line[10])
            lun_range = []
            ranges1 = [0, 4, 16384, 32768, 65536, 262144]
            j = 0
            for i in ranges1:
                if i == 0:
                    continue
                else:
                    low_size = random.randint(ranges1[j], i)
                    tmp = '(%d,%d)' % (low_size, low_size + range_expand)
                    lun_range.append(tmp)
                    j += 1
            for i in ranges1:
                if i == 0:
                    continue
                else:
                    low_size = i - 1
                    tmp = '(%d,%d)' % (low_size, low_size + range_expand)
                    lun_range.append(tmp)
            luns = []
            sd_num = 1
            for p_lun in lun:
                range_num = sd_num % len(lun_range)
                min_size, max_size = analysis_range(lun_range[range_num])
                res = disk.parted_lun(c_ip=client_ips[0], lun=p_lun, min_size=min_size, max_size=max_size)
                luns.append(res)
                sd_num += 1
            # Create configuration file of vdbench
            vdb_file = case_list_path + str(num) + ".vdb"
            w_file = open(vdb_file, "w+")
            data_errors = ("data_errors=3\n")
            w_file.write(data_errors)
            # Write sd default
            if jn_jro == "yes":
                sd_default = "sd=default,journal=/root/vdbench/journal/%s,openflags=o_direct\n" \
                             % (str(deploy_ips[0]),)
            else:
                sd_default = "sd=default,journal=/root/vdbench/journal/%s,openflags=o_direct,align=%s,offset=%s\n" \
                             % (str(deploy_ips[0]), str(align), str(offset))
            w_file.write(sd_default)
            # Write sd
            sd_num = 1
            for dev_name in luns:
                # range_num = sd_num%4
                sd = ("sd=sd%d,lun=%s\n"
                      % (sd_num, dev_name))
                w_file.write(sd)
                sd_num += 1
                # maxdata = maxdata+analysis_range(lun_range[range_num])
            # Write wd default
            if len(new_line) == 11:
                wd_default = "wd=default,xfersize=%s,rdpct=%s,seekpct=%s,unmappct=%s\n" \
                             % (iosize, str(rdpct), str(seekpct), str(unmappct))
            else:
                wd_default = "wd=default,xfersize=%s,rdpct=%s,seekpct=%s\n" \
                             % (iosize, str(rdpct), str(seekpct))
            w_file.write(wd_default)
            # Write wd
            wd_num = 1
            if len(new_line) == 11:
                for dev_name in lun:
                    lba = get_lba(client_ips[0], dev_name)
                    wd = "wd=wd%d,sd=sd%d,startlba=%s\n" % (wd_num, wd_num, str(lba))
                    wd_num += 1
                    w_file.write(wd)
            else:
                for dev_name in lun:
                    wd = "wd=wd%d,sd=sd%d\n" % (wd_num, wd_num)
                    wd_num += 1
                    w_file.write(wd)
            # Write rd
            # maxdata = maxdata+3
            rd_default = "rd=rd1,wd=wd*,iorate=%s,elapsed=600h,maxdata=%sG,threads=%s,interval=1\n" \
                         % (io_rate, maxdata, str(threads))
            w_file.write(rd_default)
            w_file.close()
            # case 执行后注释掉
            cmd = ("sed -r -i '%ss/^/#run_/' %s" % (str(num), case_list_file))
            commands.getstatusoutput(cmd)
            vdb_sum_name = str(num) + ".vdb_" + str(datetime.datetime.now().microsecond)
            log.info(vdb_sum_name)
            error.rel_check_before_run(file_name)
            for cip in client_ips:
                cmd = ("ssh root%s 'killall -9 vdbench'" % (cip,))
                commands.getstatusoutput(cmd)
            if len(new_line) == 11:
                lun_num = len(luns)
                time_to_run = lun_num * int(range_expand) * 1024 / 45 * 1.2
                cmd = ("cp %s %s_bak" % (vdb_file, vdb_file))
                commands.getstatusoutput(cmd)
                cmd = ("sed -i 's/,unmappct.*//g' %s_bak" % (vdb_file,))
                commands.getstatusoutput(cmd)
                cmd = ("sed -i 's/rdpct=[0-9]+/rdpct=0/g' %s_bak" % (vdb_file,))
                commands.getstatusoutput(cmd)
                cmd = ("sed -i 's/seekpct=[0-9]+/seekpct=0/g' %s_bak" % (vdb_file,))
                commands.getstatusoutput(cmd)
                cmd = ("sed -r -i 's/xfersize=\(.*\)/xfersize=(8M)/g' %s_bak" % (vdb_file,))
                commands.getstatusoutput(cmd)
                init_file = vdb_file + '_bak'
                osan.run_vdb(client_ips[0], init_file, output=deploy_ips[0], time=int(time_to_run))
            if jn_jro == "yes":
                # vdb_sum_name1 = vdb_sum_name + ".jn"
                osan.run_vdb(client_ips[0], vdb_file, output=deploy_ips[0], jn_jro="jn")
                check_core()
                # osan.save_vdb_log(c_ip=client_ips[0], f_name=vdb_sum_name, out=deploy_ips[0])
                # vdb_sum_name2 = vdb_sum_name + ".jro"
                osan.run_vdb(client_ips[0], vdb_file, output=deploy_ips[0], jn_jro="jro")
                check_core()
                osan.save_vdb_log(c_ip=client_ips[0], f_name=vdb_sum_name, out=deploy_ips[0])
            else:
                osan.run_vdb(client_ips[0], vdb_file, jn_jro=jn_jro, output=deploy_ips[0], time=1800)
                check_core()
                osan.save_vdb_log(c_ip=client_ips[0], f_name=vdb_sum_name, out=deploy_ips[0])
            for p_lun in lun:
                disk.del_lun_part(c_ip=client_ips[0], lun=p_lun)
            # case 执行后注释掉
            cmd = ("sed -r -i '%ss/^#run_/#pass_/' %s" % (str(num), case_list_file))
            commands.getstatusoutput(cmd)
            dpc.dpc_wb_bw(deploy_ips[0], client_ips[0], vdb_sum_name)
            dpc.dpc_stats(deploy_ips[0], client_ips[0], vdb_sum_name)
            dpc.dpc_concur_stats(deploy_ips[0], client_ips[0], vdb_sum_name)
            dpc.dpc_io_stats(deploy_ips[0], client_ips[0], vdb_sum_name)
        exit(1)


def main():
    analysis_xml_file()


if __name__ == '__main__':
    main()
