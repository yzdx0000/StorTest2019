#-*-coding:utf-8 -*

import os

import utils_path
import common
import log
import get_config
import shell
import json

##########################################
#
# Author: baorb
# date 2017-08-21
#@summary：
#    本测试主要测试P300节点池名字的规范。
#@steps:
#    1，配置节点池
#    2，修改节点池名字加入违规字符
#
#@changelog：
##########################################

def case():
    log.info("----------case begin----------")
    '''获取系统节点ip'''
    system_ip = get_config.get_parastor_ip(0)

    '''创建节点池'''
    common.create_nodepool('nodepool1', '1', 1, 0, 0, 1)
    nodepool_id = common.get_nodepool_id('nodepool1')

    '''修改节点池'''
    cmd = "pscli --command=update_node_pool --node_pool_id=%s --name=%s --node_ids=%s" % (nodepool_id, 'nodepool*', '1')
    cmd1 = ("ssh %s %s" % (system_ip, cmd))
    log.info(cmd)
    rc, stdout, stderr = shell.ssh(system_ip, cmd)
    if 0 == rc:
        log.error("Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))
    else:
        result = common.json_loads(stdout)
        if result['err_no'] != 1000 or result['err_msg'] != 'ILLEGAL_ARGUMENT':
            log.error("Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))
            raise Exception(
                "Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))

    '''检查系统状态'''
    common.ckeck_system()

    '''清除所有资源'''
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