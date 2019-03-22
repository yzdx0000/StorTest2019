# -*- coding:utf-8 -*-

import os

import utils_path
import log
import common
import remote
import nas_common

# 当前脚本名称
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]


def nas_main():     # todo: 脚本调试中
    """
    类中函数：def func(self, a, b, c=4, d=3):
    调用方式：rc = a.run_keyword('func', [1, 2], {'c': 3, 'd': 4})
    :return:
    """
    # for windows端smb挂载
    uri = nas_common.SMB_CLIENT_IP_AND_PORT_250
    disk_symbol = 'x:\\'
    mount_path = '\\\\10.2.40.49\\smb_export_name'
    password = '111111'
    user = 'adtest\\smb_auth_user_name'

    nas_common.create_file_by_smb_client(disk_symbol, 'file1')

    return


if __name__ == '__main__':
    # 初始化日志
    nas_common.nas_log_init(FILE_NAME)
    common.case_main(nas_main)
