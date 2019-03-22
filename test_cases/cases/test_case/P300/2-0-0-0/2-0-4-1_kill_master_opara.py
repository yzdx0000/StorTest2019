#-*-coding:utf-8 -*
#!/usr/bin/python

'''
kill主oPara进程
'''

import os
import time

import utils_path
from utils import common
from utils import log
from utils import shell
from utils import get_config


def main():
    file_name = os.path.basename(__file__)
    file_name = file_name[:-3]
    log_file_path = common.get_log_path(file_name)
    stream = log.init(log_file_path, True)
    case()
    log.info('succeed!')
    return

if __name__ == '__main__':
    main()