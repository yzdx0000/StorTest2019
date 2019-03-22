#-*-coding:utf-8 -*
#!/usr/bin/python

'''
存储池名字冲突
'''
import os
import json

import utils_path
import common
import log
import shell
import get_config

def case():
    log.info("----------case begin----------")
    '''获取系统节点ip'''
    system_ip = get_config.get_parastor_ip(0)

    '''创建节点池'''
    common.create_nodepool('nodepool1', '1', 1, 0, 0, 1)
    common.create_nodepool('nodepool2', '2', 1, 0, 0, 1)
    common.create_nodepool('nodepool3', '3', 1, 0, 0, 1)
    nodepool1_id = common.get_nodepool_id('nodepool1')
    nodepool2_id = common.get_nodepool_id('nodepool2')
    nodepool3_id = common.get_nodepool_id('nodepool3')

    '''创建存储池'''
    common.create_storagepool('storagepool1', 'FILE', nodepool1_id)

    '''创建一个名字相同的存储池'''
    nodepool_ids_str = (nodepool2_id + ',' + nodepool3_id)
    cmd = ("pscli --command=create_storage_pool --name=storagepool1, --type=FILE --node_pool_ids=%s" %(nodepool_ids_str))
    log.info(cmd)
    rc, stdout, stderr = shell.ssh(system_ip, cmd)
    if 0 == rc:
        log.error("Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))
    else:
        msg = common.json_loads(stdout)
        if msg['err_no'] != 1000 or msg['detail_err_msg'] != 'Storage pool name storagepool1 exists':
            log.error("Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))
            raise Exception(
                "Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))

    '''创建一个名字不同的存储池'''
    common.create_storagepool('storagepool3', 'FILE', nodepool_ids_str)

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