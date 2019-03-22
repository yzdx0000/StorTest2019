#-*-coding:utf-8 -*

'''
修改节点池名称
'''

import os

import utils_path
import common
import log


def case():
    log.info("----------case begin----------")
    '''创建节点池'''
    common.create_nodepool('nodepool1', '1', 1, 0, 0, 1)
    nodepool_id = common.get_nodepool_id('nodepool1')

    '''修改节点池'''
    common.update_nodepool(nodepool_id, 'nodepool_1', 1)

    common.update_nodepool(nodepool_id, 'nodepool1', 1)

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