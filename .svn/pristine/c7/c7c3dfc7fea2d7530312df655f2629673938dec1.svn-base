#!/usr/bin/python
#-*-coding:utf-8 -*
"""
:Date: 2019-01-28
:Author: wuyq
:Description:
function: Try to find the best performance configuration.
:Changerlog:
"""
import os
import commands
import time
import xml
import ConfigParser
import datetime
import threading
import utils_path
import common2
import common
import log
import get_config
import breakdown

# 参数实例化
conf_file = common2.CONF_FILE
osan = common2.oSan()
reliable = breakdown.Os_Reliable()
disk = breakdown.disk()
node = common.Node()
conf = ConfigParser.ConfigParser()

# 初始化日志文件
file_name = os.path.basename(__file__)
file_name = file_name[:-3]
log_file_path = log.get_log_path(file_name)
log.init(log_file_path, True)

# 获取集群节点信息
deploy_ips = get_config.get_env_ip_info(conf_file)
client_ips = get_config.get_allclient_ip()

config_info = xml.dom.minidom.parse(conf_file)
replica = config_info.getElementsByTagName('replica')[0].firstChild.nodeValue
strip_width = config_info.getElementsByTagName('stripwidth')[0].firstChild.nodeValue
node_parity = int(replica) - 1
# lun_nums = osan.get_lun_nums(deploy_ips[0])

now_path = os.path.dirname(os.path.abspath(__file__))
per_result_path = os.path.join(now_path, 'per_result')
if os.path.exists(per_result_path) is False:
    os.mkdir(per_result_path)
per_conf_path = os.path.join(now_path, 'perf_test.conf')
if os.path.exists(per_result_path) is False:
    log.error("There is not exists perf_test.conf...will exit.")
    os._exit(1)
per_hardware_path = os.path.join(now_path, 'hardware_result')
if os.path.exists(per_result_path) is False:
    os.mkdir(per_hardware_path)

conf.read('perf_test.conf')
iorate = conf.get('vdbench-conf', 'iorate')
threads = conf.get('vdbench-conf', 'threads')
luns = conf.get('vdbench-conf', 'luns')

# 解析性能配置文件
conf.read(per_conf_path)
io_model_list = conf.sections()
for parm in io_model_list:
    if parm == 'vdbench-conf':
        io_model_list.remove(parm)

current_time = datetime.datetime.now()
now_time = current_time.strftime('%Y-%m-%d_%H-%M-%S')
per_log = per_result_path + '/perf_res_' + now_time + '.log'
per_write = open(per_log, 'a+')
per_write.write("============================\n")
per_write.write("The Performance Test Result.\nTime:%s.\nReplications:%s.\nStrip_Width:%s.\nLun_Nums:%s\n"
                % (now_time, replica, strip_width, luns))
per_write.write("============================\n\n")
per_write.close()

def collect_cpu(host_ip=None, interval=10, time=300):
    list1 = []
    list2 = []
    list3 = []
    list4 = []
    list5 = []
    list6 = []
    for count in range(time):
        cmd = ("ssh %s 'iostat -c | sed -n 4p'" % host_ip)
        final = commands.getoutput(cmd)
        parm_list = final.split()
        list1.append(float(parm_list[0]))
        list2.append(float(parm_list[1]))
        list3.append(float(parm_list[2]))
        list4.append(float(parm_list[3]))
        list5.append(float(parm_list[4]))
        list6.append(float(parm_list[5]))
        time.sleep(interval)
        count += interval
    avg1 = sum(list1) / len(list1)
    avg2 = sum(list2) / len(list2)
    avg3 = sum(list3) / len(list3)
    avg4 = sum(list4) / len(list4)
    avg5 = sum(list5) / len(list5)
    avg6 = sum(list6) / len(list6)
    info_name = ('cpu_info_of_%s' % host_ip)
    with open(info_name, 'w') as cpu_write:
        cpu_write.write("\nCPU info, mechine ip : %s\n" % host_ip)
        cpu_write.write("------------------------------------------------------\n")
        cpu_write.write("| %user | %nice | %system | %iowait | %steal | %idle |\n")
        cpu_write.write("------------------------------------------------------\n")
        cpu_write.write("| %-5s | %-5s | %-7s | %-7s | %-6s | %-5s |" %
                        (str(avg1), str(avg2), str(avg3), str(avg4), str(avg5), str(avg6)))
        cpu_write.write("------------------------------------------------------\n")

def collect_mem(host_ip=None, interval=10, time=300):
    list1 = []
    list2 = []
    list3 = []
    list4 = []
    list5 = []
    list6 = []
    for count in range(time):
        cmd = ("ssh %s 'free | grep Mem'" % host_ip)
        final = commands.getoutput(cmd)
        parm_list = final.split()
        list1.append(float(parm_list[1]))
        list2.append(float(parm_list[2]))
        list3.append(float(parm_list[3]))
        list4.append(float(parm_list[4]))
        list5.append(float(parm_list[5]))
        list6.append(float(parm_list[6]))
        time.sleep(interval)
        count += interval
    avg1 = str((sum(list1) / len(list1)) / (1024 ** 2)) + 'G'
    avg2 = str((sum(list2) / len(list2)) / (1024 ** 2)) + 'G'
    avg3 = str((sum(list3) / len(list3)) / (1024 ** 2)) + 'G'
    avg4 = str((sum(list4) / len(list4)) / (1024 ** 2)) + 'G'
    avg5 = str((sum(list5) / len(list5)) / (1024 ** 2)) + 'G'
    avg6 = str((sum(list6) / len(list6)) / (1024 ** 2)) + 'G'
    info_name = ('mem_info_of_%s' % host_ip)
    with open(info_name, 'w') as cpu_write:
        cpu_write.write("\nMem info, mechine ip : %s\n" % host_ip)
        cpu_write.write("---------------------------------------------------------\n")
        cpu_write.write("| total | used | free | shared | buff/cache | available |\n")
        cpu_write.write("---------------------------------------------------------\n")
        cpu_write.write("| %-5s | %-4s | %-4s | %-6s | %-10s | %-9s |" %
                        (avg1, avg2, avg3, avg4, avg5, avg6))
        cpu_write.write("------------------------------------------------------\n")

def collect_hdw(host_ip=None, interval=10, time=300):
    thread_list = []
    thread_list.append(threading.Thread(target=collect_cpu, args=(host_ip, interval, time)))
    thread_list.append(threading.Thread(target=collect_mem, args=(host_ip, interval, time)))
    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()

def process():
    maxdata = 0
    for client_ip in client_ips:
        cmd = ("ssh %s 'free -h' | sed -n '2p' | awk '{print $4}' | sed 's/[A-Z]//g'" % client_ip)
        res = commands.getoutput(cmd)
        maxdata += int(res)
    data_conf = osan.gen_stress_vdb(xfersize='(4k,30,16k,30,64k,20,256k,20)',
                                    rdpct=0,
                                    seekpct=0,
                                    iorate=iorate,
                                    maxdata=maxdata,
                                    threads=threads,
                                    lun_nums=int(luns))
    log.info("↓↓↓↓↓ Steps in advance:Embedded data, full memory. ↓↓↓↓↓")
    osan.run_vdb(client_ips[0], data_conf, output=client_ips[0], time=300)
    time.sleep(30)

    total_lines = []
    for io_model in io_model_list:
        log.info("Start to performance test...")
        log.info("=========================================")
        log.info("IO model: %s" % io_model)
        log.info("=========================================")
        log.info("Step1:Generate vdbench performance test parameters.")
        xfersize = conf.get(io_model, 'xfersize')
        rdpct = conf.get(io_model, 'rdpct')
        seekpct = conf.get(io_model, 'seekpct')
        # Generate the vdbench configuration file
        perf_io = osan.gen_stress_vdb(xfersize=xfersize,
                                      rdpct=rdpct,
                                      seekpct=seekpct,
                                      iorate=iorate,
                                      lun_nums=int(luns),
                                      model='forthreads=(1-64,d)')

        log.info("Step2:Begin performance testing...")
        # output = xfersize + rppct + seekpct model
        out_name = str(xfersize) + '_' + str(rdpct) + '_' + str(seekpct)
        osan.run_vdb(client_ips[0], perf_io, output=out_name, time=600)
        time.sleep(10)
        log.info("Step3:Statistical test results.")
        result_path = '/root/output/' + out_name + '_nor'
        cmd1 = ("ssh %s 'cat %s/summary.html' | grep 'avg' | awk -F 'avg' '{print $2}'" % (client_ips[0], result_path))
        rc1, result = commands.getstatusoutput(cmd1)
        cmd2 = ("ssh %s 'cat %s/totals.html' | grep 'Starting.*threads' | awk -F 'threads=' '{print $2}' | awk -F '</b>' '{print $1}'"
                % (client_ips[0], result_path))
        rc2, final = commands.getstatusoutput(cmd2)
        if rc1 != 0 or rc2 != 0:
            log.error("Can't view the output of vdbench in %s" % client_ips[0])
            os._exit(1)
        else:
            iops_list = []
            res_line_list = []
            result_list = result.split('\n')
            threads_list = final.split('\n')
            io_model_info = ('>>>>>>>>>> xfersize:%s. rdpct:%s. seekpct:%s. <<<<<<<<<<' % (xfersize, rdpct, seekpct))
            split_line = "---------------------------------------------------------------------"
            title_line = "|  iops  | bandwidth | resp_time | resp_max | queue_depth | threads |"
            per_write = open(per_log, 'a+')
            per_write.write(io_model_info + '\n')
            per_write.write(split_line + '\n')
            per_write.write(title_line + '\n')
            per_write.write(split_line + '\n')
            for each_res in result_list:
                res_info = each_res.split()
                res_line = ("| %-6s | %-9s | %-9s | %-8s | %-11s | %-7s |"
                            % (res_info[1], res_info[2], res_info[5], res_info[8], res_info[10], threads_list[result_list.index(each_res)]))
                res_line_list.append(res_line)
                per_write.write(res_line + '\n')
                per_write.write(split_line + '\n')
                iops_list.append(float(res_info[1]))
            per_write.write('\n')
            per_write.close()
            max_iops = max(iops_list)
            max_line = res_line_list[iops_list.index(max_iops)]
            model_info = ('%s,%s,%s' % (xfersize, rdpct, seekpct))
            echo_total = ('| %-12s ' % model_info) + max_line
            total_lines.append(echo_total)

    title_split = "===================================================================================="
    total_title = "| xfer,rpt,spt |  iops  | bandwidth | resp_time | resp_max | queue_depth | threads |"
    split_lines = "------------------------------------------------------------------------------------"
    note_info = "The following is the statistical result of all models...\n"
    pro_info = ("Cluster: %s\nHost: %s\nLuns: %s\n" % (','.join(deploy_ips), ','.join(client_ips), luns))
    with open(per_log, 'a+') as per_write:
        per_write.write(note_info)
        per_write.write(pro_info + '\n')
        per_write.write(title_split + '\n')
        per_write.write(total_title + '\n')
        per_write.write(title_split + '\n')
        for total in total_lines:
            per_write.write(total + '\n')
            per_write.write(split_lines + '\n')

    for host_ip in client_ips:
        cmd1 = ("cat cpu_info_of_%s >> %s" % (host_ip, per_log))
        cmd2 = ("cat mem_info_of_%s >> %s" % (host_ip, per_log))
        os.system(cmd1)
        os.system(cmd2)
    for node_ip in deploy_ips:
        cmd1 = ("cat cpu_info_of_%s >> %s" % (node_ip, per_log))
        cmd2 = ("cat mem_info_of_%s >> %s" % (node_ip, per_log))
        os.system(cmd1)
        os.system(cmd2)

    log.info("Congratulations! All performance tests have been completed...")
    log.info("↓↓↓↓↓ If you want to see the test results.Please go to the directory and check it ↓↓↓↓↓\n%s" % per_log)

if __name__ == '__main__':
    thread_list = []
    thread_list.append(threading.Thread(target=process))
    for host_ip in client_ips:
        thread_list.append(threading.Thread(target=collect_hdw, args=(host_ip, 10, 300)))
    for node_ip in deploy_ips:
        thread_list.append(threading.Thread(target=collect_hdw, args=(node_ip, 10, 300)))
    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()
