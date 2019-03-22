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
#    本测试主要测试P300卸载功能。
#@steps:
#    1，卸载Parastor300
#
#@changelog：
##########################################

def case():
    log.info("----------case begin----------")
    '''获取系统节点ip'''
    system_ip = get_config.get_parastor_ip(0)

    '''创建节点池'''
    common.create_nodepool('nodepool1', '1,2,3', 1, 0, 2, 3)
    common.create_nodepool('nodepool2', '4,5', 1, 0, 1, 2)
    nodepool1_id = common.get_nodepool_id('nodepool1')
    nodepool2_id = common.get_nodepool_id('nodepool2')

    '''修改节点池'''
    common.create_storagepool('stor1', 'FILE', nodepool1_id)
    storage_pool_id = common.get_storagepool_id('stor1')

    cmd = "ssh %s pscli --command=expand_storage_pool --storage_pool_id=%s --node_pool_ids=%s" %(system_ip, storage_pool_id, nodepool2_id)
    if True != common.command(cmd):
        raise Exception("expand storage pool error")

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