#!/usr/bin/python
# -*- encoding=utf8 -*-
import commands, json, re
from optparse import OptionParser

global MGRIP
global START_MODEL


def get_nodes_ip(node_ip=None):
    if None == node_ip:
        cmd = "pscli --command=get_nodes"
    else:
        cmd = 'ssh %s "pscli --command=get_nodes"' % node_ip
    nodes_ips = []
    rc, stdout = commands.getstatusoutput(cmd)
    if 0 != rc:
        raise Exception("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        node_info = json.loads(stdout)
        nodes = node_info['result']['nodes']
        for node in nodes:
            nodes_ips.append(node['ctl_ips'][0]['ip_address'])

    return nodes_ips


def get_local_node_ip():
    node_ips = get_nodes_ip()
    cmd = 'ip addr | grep "inet "'
    rc, stdout = commands.getstatusoutput(cmd)
    if 0 != rc:
        raise Exception("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    lines = stdout.split('\n')
    for line in lines:
        ip = line.split()[1].split('/')[0]
        if ip in node_ips:
            return ip
    return None


def check_ip(ip):
    pattern = re.compile(r'((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    match = pattern.match(ip)
    if match:
        return True
    else:
        return False


def check_local_node():
    cmd = "ls /home/parastor/bin"
    rc, stdout = commands.getstatusoutput(cmd)
    if 0 != rc:
        return False
    return True


def stop_process(node_ip, process):
    pid_cmd = 'ssh root@%s \"pidof %s\"' % (node_ip, process)
    rc, stdout = commands.getstatusoutput(pid_cmd)
    if 0 != rc:
        print "node %s %s is not exist!!!" % (node_ip, process)
        return
    stop_cmd = 'ssh root@%s \"kill -SIGSTOP %s\"' % (node_ip, stdout)
    rc, stdout = commands.getstatusoutput(stop_cmd)
    if 0 != rc:
        print "node %s %s stop failed!!!" % (node_ip, process)
    return


def start_process(node_ip, process):
    pid_cmd = 'ssh root@%s \"pidof %s\"' % (node_ip, process)
    rc, stdout = commands.getstatusoutput(pid_cmd)
    if 0 != rc:
        print "node %s %s is not exist!!!" % (node_ip, process)
        return
    start_cmd = 'ssh root@%s \"kill -SIGCONT %s\"' % (node_ip, stdout)
    rc, stdout = commands.getstatusoutput(start_cmd)
    if 0 != rc:
        print "node %s %s stop failed!!!" % (node_ip, process)
    return


def stop_all_process():
    global MGRIP
    nodes_ips = get_nodes_ip(MGRIP)
    process_lst = ['oStor', 'oPara', 'oMgcd', 'oJob', 'oRole']
    for node_ip in nodes_ips:
        for process in process_lst:
            stop_process(node_ip, process)

    return


def start_all_process():
    global MGRIP
    nodes_ips = get_nodes_ip(MGRIP)
    process_lst = ['oStor', 'oPara', 'oMgcd', 'oJob', 'oRole']
    for node_ip in nodes_ips:
        for process in process_lst:
            start_process(node_ip, process)

    return


##############################################################################
###name  :      arg_analysis
###parameter:
###author:      baoruobing
###date  :      2017.11.02
###Description: 参数解析
##############################################################################
def arg_analysis():
    global MGRIP
    global START_MODEL

    parser = OptionParser()
    parser.add_option("-i", "--ip", type="string", dest="mgrip", help="mgr node ip")

    parser.add_option("-s", "--start", action="store_true", dest="start",
                      help="When you want to start the process, configure this parameter")

    options, args = parser.parse_args()
    if options.mgrip != None:
        # 检查输入的ip格式
        if False == check_ip(options.mgrip):
            parser.error("-i the ip format is incorrent!!!")
        MGRIP = options.mgrip
    else:
        # 如果没有输入-i，则认为本节点为管理节点
        if False == check_local_node():
            parser.error("local node isn't a parastor node, please use -i or --ip input mgrnode ip")
        MGRIP = get_local_node_ip()

    if True == options.start:
        START_MODEL = True
    else:
        START_MODEL = False

    return


def main():
    global START_MODEL
    arg_analysis()
    if True == START_MODEL:
        start_all_process()
    else:
        stop_all_process()


if __name__ == '__main__':
    main()
