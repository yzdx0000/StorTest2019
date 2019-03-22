#-*-coding:utf-8 -*
#!/usr/bin/python

'''
节点池和存储池关联后，删除和添加节点池中的节点
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
    '''获取集群节点ip'''
    system_ip = get_config.get_parastor_ip(0)

    '''创建节点池'''
    common.create_nodepool('nodepool1', '1,2,3', 4, 2, 1, 1)
    nodepool_id = common.get_nodepool_id('nodepool1')

    '''创建存储池'''
    common.create_storagepool('storagepool1', 'FILE', nodepool_id)

    '''删除节点池中的一个节点'''
    cmd = ("pscli --command=update_node_pool --node_pool_id=%s --name=nodepool1 --node_ids=1,2" %nodepool_id)
    log.info(cmd)
    rc, stdout, stderr = shell.ssh(system_ip, cmd)
    if 0 == rc:
        log.error("Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))
    else:
        msg = common.json_loads(stdout)
        if msg['err_no'] != 1000 or msg['detail_err_msg'] != 'Node pool nodepool1 is in used, all the nodes in this node pool can not be removed.':
            log.error("Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))
            raise Exception(
                "Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))

    '''添加一个节点到节点池'''
    common.update_nodepool(nodepool_id, 'nodepool1', '1,2,3')

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