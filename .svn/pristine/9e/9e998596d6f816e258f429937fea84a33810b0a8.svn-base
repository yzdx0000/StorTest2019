#-*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-4-3 同时嵌套创建多层目录
#######################################################

import os
import time
import random
import commands

import utils_path
import common
import nas_common
import log
import shell
import get_config
import json
import prepare_clean

# 当前脚本名称
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0].replace('-', '_')
SYSTEM_IP_0 = get_config.get_parastor_ip(0)
SYSTEM_IP_1 = get_config.get_parastor_ip(1)
SYSTEM_IP_2 = get_config.get_parastor_ip(2)

#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def executing_case():
    """
        1、依次创建多层嵌套目录；
        pscli --command=create_file --path=volume:/a
        pscli --command=create_file --path=volume:/a/b
        pscli --command=create_file --path=volume:/a/b/c
        pscli --command=create_file --path=volume:/a/b/c/d
        pscli --command=create_file --path=volume:/a/b/c/d/e
        2、在父目录不存在的情况下一次创建多层嵌套目录；
        比如：在/a/b/c/d四个目录都不存在的情况下，一次创建a、b、c、d、e五个嵌套目录
        pscli --command=create_file --path=volume:/a/b/c/d/e
    :return:
    """
    log.info("（2）executing_case")

    abs_dir_name = '/mnt/' + nas_common.VOLUME_NAME + '/' + os.path.join(nas_common.LAST_PART, FILE_NAME)
    check_dir_name = nas_common.ROOT_DIR + FILE_NAME
    print check_dir_name
    cmd = 'mkdir -p %s' % abs_dir_name
    common.run_command(SYSTEM_IP_0, cmd)

    """循环创建嵌套目录"""
    dir_num = 5
    dir_list = [check_dir_name]
    for i in range(dir_num):
        check_dir_name = check_dir_name + '/dir_' + str(i)
        exe_info = nas_common.create_file(check_dir_name)
        if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
            common.except_exit('create path %s failed !!!' % check_dir_name)
        dir_list.append(check_dir_name)

    print dir_list

    """循环检查嵌套目录信息"""
    for i in range(dir_num):
        expect_path = dir_list[i]
        exe_info = nas_common.get_file_list(expect_path)
        actual_path = exe_info['result']['files'][0]['path']
        if actual_path != dir_list[i+1]:
            log.error('check file info %s wrong !!!' % expect_path)
            raise Exception('check file info %s wrong !!!' % expect_path)

    return

#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def preparing_environment():
    log.info("（1）preparing_environment")

    '''
    1、下发nas相关的配置
    2、创建nas测试相关的目录和文件
    '''

    return

#######################################################
# 函数功能：本用例入口函数
# 函数入参：无
# 函数返回值：无
#######################################################
def nas_main():
    file_name = os.path.basename(__file__)
    file_name = os.path.splitext(file_name)[0]
    log_file_path = log.get_log_path(file_name)
    stream = log.init(log_file_path, True)

    prepare_clean.nas_test_prepare(FILE_NAME)
    preparing_environment()
    executing_case()
    if nas_common.DEBUG != "on":
        prepare_clean.nas_test_clean()
    log.info('%s succeed !' % FILE_NAME)

    return

class Nas_Class_16_0_4_3():
    def nas_method_16_0_4_3(self):
        nas_main()

if __name__ == '__main__':
    nas_main()