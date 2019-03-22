#-*-coding:utf-8 -*
#!/usr/bin/python

'''
部署一个5节点集群，后续脚本测试资源池
'''

import os
import utils_path
import common
import log


def main():
    file_name = os.path.basename(__file__)
    file_name = file_name[:-3]
    log_file_path = log.get_log_path(file_name)
    stream = log.init(log_file_path, True)
    '''安装系统'''
    common.install_parastor(5)
    log.info('succeed!')

if __name__ == '__main__':
    main()
