#-*-coding:utf-8 -*
from multiprocessing import Process
import os
import time

import utils_path
import common
import snap_common
import log
import shell
import get_config
import prepare_clean
import json
import random

#############################################################
#test
#############################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]        # 本脚本名字


SYSTEM_IP = get_config.get_parastor_ip()

NODE_IP_1 = get_config.get_parastor_ip(0)
NODE_IP_2 = get_config.get_parastor_ip(1)
NODE_IP_3 = get_config.get_parastor_ip(2)

'''客户端节点ip'''
CLIENT_IP_1 = get_config.get_client_ip()
CLIENT_IP_2 = get_config.get_client_ip(1)
CLIENT_IP_3 = get_config.get_client_ip(2)



##############################################################################
# ##name  :      run_command
# ##parameter:   node_ip:节点ip, cmd:命令
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 执行命令
##############################################################################
def run_command(node_ip, cmd, flag=True):
    log.info(cmd)
    if node_ip == None:
        node_ip = SYSTEM_IP
    rc, stdout, stderr = shell.ssh(node_ip, cmd)
    if 0 != rc:
        log.info("Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))
    elif '' != stdout and flag == True:
        log.info(stdout)
    return rc, stdout


##############################################################################
# ##name  :      run_pscli_command
# ##parameter:   cmd:命令
# ##author:      baoruobing
# ##date  :      2018.01.19
# ##Description: 执行spcli命令
##############################################################################
def run_pscli_command(cmd, ext_node_ip=None):
    rc, stdout = run_command(ext_node_ip, cmd)
    if 0 != rc:
        log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        stdout = common.json_loads(stdout)
        return stdout


package_name = 'parastor-3.0.0-centos7.5-ofs3.0_be06fa1_20180725_094220-2-1.tar.xz'


def get_version_baseon_package_name(package_name):
    version = int(package_name[-10])
    min_version = int(package_name[-8])

    return version, min_version


def main():
    version, minversion = get_version_baseon_package_name(package_name)
    print type(version)
    print version


if __name__ == '__main__':
    common.case_main(main)
