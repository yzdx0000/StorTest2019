# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time

import utils_path
import common
import log
import shell
import make_fault
import prepare_clean
import commands
#################################################################
#
# Author: chenjy1
# Date: 2018-07-14
# @summary：
#    物理机3节点集群，部署集群后，killoStor和oPara进程后，客户端数据不一致
# @steps:
#    1.kill3个节点oStor进程和oPara进程
#    2.nodeid1上创建一个目录iozone，nodeid2和nodeid3上ls可查看iozone目录；
#    3.nodeid2和nodeid3上分别创建一个文件后，nodeid1上可以观察到两个文件，且nodeid2和nodeid3也可以观察到iozone目录。
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字

session_list = ['oPara', 'oStor']


def kill_process(ip_list):
    """
    :author :             chenjy1
    :date:                2018.07.30
    :description:         进行kill 进程故障
    :param ip_list:       要进程的节点列表
    :return:
    """
    for node_ip in ip_list:
        """杀所有节点的oStor和oPara进程"""
        make_fault.kill_process(node_ip, session_list[0])
        time.sleep(5)
        make_fault.kill_process(node_ip, session_list[1])
        time.sleep(5)


def check_process(node_ip, process):
    """
    :author :             chenjy1
    :date:                2018.07.30
    :description:         检查node_ip的process进程是否起来
    :param node_ip:      要检查的节点
    :param process:      要检查的进程
    :return:             布尔值
    """
    ps_cmd = ('ssh %s \"ps -ef | grep %s | grep -v grep\"' % (node_ip, process))
    rc, stdout = commands.getstatusoutput(ps_cmd)
    if 0 == rc:
        return True
    else:
        return False


def wait_process(node_ip_list):
    """
    :author :             chenjy1
    :date:                2018.07.30
    :description:         等待节点的session_list进程起来
    :param node_ip_list:  检查的节点列表
    :return:
    """
    log.info("wait 60 s")
    time.sleep(60)
    process_status_list = []
    for i in range(len(node_ip_list)):
        single_node = [node_ip_list[i], False, False]
        process_status_list.append(single_node)
    for i in range(len(node_ip_list)):
        log.info('wait 10s')
        time.sleep(10)
        for j in range(2):
            if process_status_list[i][j+1] == False:
                process_status_list[i][j+1] == check_process(node_ip_list[i],session_list[j])
    return


def create_one_file(node_ip, path, filename):
    """
    :author :             chenjy1
    :date:                2018.07.30
    :description:         创建一个文件
    :param node_ip:      创建文件的IP
    :param path:         创建文件的路径
    :param filename:     文件名
    :return:
    """
    cmd = ("cd %s; dd if=/dev/zero of=%s bs=1M count=1") % (path, filename)
    rc, stdout, stderr = shell.ssh(node_ip, cmd)
    if rc != 0:
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))
    return


def create_one_catalog(node_ip,path,catalogname):
    """
    :author :             chenjy1
    :date:                2018.07.30
    :description:         创建一个目录
    :param node_ip:      创建目录的IP
    :param path:         创建目录的路径
    :param catalogname:  目录名
    :return:
    """
    cmd = ("cd %s; mkdir %s") % (path, catalogname)
    rc, stdout, stderr = shell.ssh(node_ip, cmd)
    if rc != 0:
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))
    return


def check_dentry(node_ip, path, name):
    """
    :author :             chenjy1
    :date:                2018.07.30
    :description:         检查文件或目录存不存在
    :param node_ip:      执行命令的IP
    :param path:         检查的路径
    :param name:         检测的目录或文件名
    :return:
    """
    cmd = ("cd %s; ls %s") % (path, name)
    rc, stdout, stderr = shell.ssh(node_ip, cmd)
    if rc != 0:
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))


def case():
    log.info("case begin")

    """获取集群信息"""
    ob_node = common.Node()
    node_ip_list = ob_node.get_nodes_ip()

    log.info("1> kill3个节点oStor进程和oPara进程")
    """杀进程，并等待恢复"""
    kill_process(node_ip_list)
    wait_process(node_ip_list)
    log.info("oPara and oStor ok ")

    log.info("2> nodeid1上创建一个目录iozone，nodeid2和nodeid3上ls可查看iozone目录")
    create_check_path = os.path.join(prepare_clean.DEFECT_PATH, FILE_NAME)

    log.info("node1 create catalog")
    create_one_catalog(node_ip_list[0], create_check_path, 'iozone')

    log.info("node2,3 check catalog")
    for i in range(1, 3):
        check_dentry(node_ip_list[i], create_check_path, 'iozone')

    log.info('wait 60s')
    log.info("3> nodeid2和nodeid3上分别创建一个文件后，nodeid1上可以观察到两个文件，"
             "且nodeid2和nodeid3也可以观察到iozone目录")
    log.info("node2,3 create file")
    create_one_file(node_ip_list[1], create_check_path, 'testfile0')
    create_one_file(node_ip_list[2], create_check_path, 'testfile1')

    log.info("node1 check file")
    check_dentry(node_ip_list[0], create_check_path, 'testfile0')
    check_dentry(node_ip_list[0], create_check_path, 'testfile1')

    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)