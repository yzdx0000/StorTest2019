#-*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import json
import random

import utils_path
import common
import log
import shell
import get_config

#################################################################
#
# Author: baorb
# date 2017-08-21
#@summary：
#    本测试主要测试5节点无效的授权ip。
#@steps:
#    1，创建节点池
#    2，创建存储池
#    3，穿件卷
#    4，创建无效ip的客户端授权
#
#@changelog：
#################################################################

def case():
    log.info("----------case begin----------")
    '''获取系统节点ip'''
    system_ip = get_config.get_parastor_ip(0)

    '''创建节点池'''
    common.create_nodepool('nodepool1', '1,2,3,4,5', 4, 2, 1, 1)
    nodepool_id = common.get_nodepool_id('nodepool1')

    '''创建存储池'''
    common.create_storagepool('stor1', 'FILE', nodepool_id)
    storage_pool_id = common.get_storagepool_id('stor1')

    '''创建卷'''
    rc, json_info = common.create_volume('volume1', storage_pool_id, 4, 2, 1, 1)
    common.judge_rc(rc, "create volume failed")
    volume_id = common.get_volume_id('volume1')

    '''创建无效ip的客户端授权'''
    cmd = ("pscli --command=create_client_auth --auth_info=\'{\"ip\":\"1.256.0.10\",\"volume_ids\":[%s]}\'" % volume_id)
    log.info(cmd)
    rc, stdout, stderr = shell.ssh(system_ip, cmd)
    if 0 == rc:
        log.error("Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))
    else:
        msg = common.json_loads(stdout)
        if msg['err_no'] != 7009 or msg['err_msg'] != 'CLIENT_AUTH_IP_ILLEGAL':
            log.error("Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))
            raise Exception(
                "Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))

    '''检查系统状态'''
    common.ckeck_system()

    '''清除资源'''
    common.clear_test_env()

    return


def main():
    file_name = os.path.basename(__file__)
    file_name = file_name[:-3]
    log_file_path = log.get_log_path(file_name)
    stream = log.init(log_file_path, True)
    case()
    log.info('succeed!')
    return


if __name__ == '__main__':
    main()
