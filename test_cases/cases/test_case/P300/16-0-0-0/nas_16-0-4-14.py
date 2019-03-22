# -*- coding:utf-8 -*-

######################################################
# Author: jiangxiaoguang
# Date: 2018-08-23
# @summary：
#   修改权限到rwxrwxrwx
# @steps:
#   1、在根目录下创建目录a，目录权限为---------；
#   pscli --command=create_file --path=volume:/a --posix_permission=---------
#   2、修改a权限为rwxrwxrwx；
#   pscli --command=update_file --path=volume:/a --posix_permission=rwxrwxrwx
# @changelog：
#   None
######################################################

import os

import utils_path
import log
import common
import nas_common
import prepare_clean

# 当前脚本名称
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0].replace('-', '_')


#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def executing_case():
    """测试执行
    :return:无
    """
    log.info("（2）executing_case")

    # for create_file
    dir_name = FILE_NAME
    create_file_path = '%s:/' % nas_common.VOLUME_NAME + dir_name
    # for get_file_list
    get_file_list_path = '%s:/' % nas_common.VOLUME_NAME

    msg = nas_common.create_file(path=create_file_path,
                                 posix_permission="---------")
    if msg["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)

    msg = nas_common.get_file_list(path=get_file_list_path,
                                   display_details="true")
    if msg["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)
    detail_files = msg["result"]["detail_files"]
    for detail_file in detail_files:
        if detail_file["path"] == create_file_path:
            if cmp(detail_file, {
                    "access_time": detail_file['access_time'],
                    "auth_provider_id": 0,
                    "create_time": detail_file['create_time'],
                    "modify_time": detail_file['modify_time'],
                    "name": dir_name,
                    "owner_group_name": "root",
                    "owner_user_name": "root",
                    "path": create_file_path,
                    "posix_permission": "---------",
                    "size": 4096,
                    "type": "DIR"
                    }):
                raise Exception("%s Failed" % FILE_NAME)

    # 通过客户端查看目录存在，且权限正确
    cmd = 'ls -l /mnt/%s | grep %s' % (nas_common.VOLUME_NAME, dir_name)
    rc, stdout = common.run_command(nas_common.RANDOM_NODE_IP, cmd)
    common.judge_rc(rc, 0, "ls -l failed")
    if stdout.split()[0] != 'd---------' or stdout.split()[2] != 'root' or stdout.split()[3] != 'root':
        raise Exception("%s Failed" % FILE_NAME)

    msg = nas_common.update_file(path=create_file_path,
                                 posix_permission="rwxrwxrwx")
    if msg["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)

    msg = nas_common.get_file_list(path=get_file_list_path,
                                   display_details="true")
    if msg["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)
    detail_files = msg["result"]["detail_files"]
    for detail_file in detail_files:
        if detail_file["path"] == create_file_path:
            if cmp(detail_file, {
                    "access_time": detail_file['access_time'],
                    "auth_provider_id": 0,
                    "create_time": detail_file['create_time'],
                    "modify_time": detail_file['modify_time'],
                    "name": dir_name,
                    "owner_group_name": "root",
                    "owner_user_name": "root",
                    "path": create_file_path,
                    "posix_permission": "rwxrwxrwx",
                    "size": 4096,
                    "type": "DIR"
                    }):
                raise Exception("%s Failed" % FILE_NAME)

    # 通过客户端查看目录存在，且权限正确
    cmd = 'ls -l /mnt/%s | grep %s' % (nas_common.VOLUME_NAME, dir_name)
    rc, stdout = common.run_command(nas_common.RANDOM_NODE_IP, cmd)
    common.judge_rc(rc, 0, "ls -l failed")
    if stdout.split()[0] != 'drwxrwxrwx' or stdout.split()[2] != 'root' or stdout.split()[3] != 'root':
        raise Exception("%s Failed" % FILE_NAME)

    # 根目录，需自己清理环境
    msg = nas_common.delete_file(path=create_file_path)
    if msg["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)

    return


def nas_main():
    """脚本入口函数
    :return:无
    """
    prepare_clean.nas_test_prepare(FILE_NAME)
    executing_case()
    if nas_common.DEBUG != 'on':
        prepare_clean.nas_test_clean()

    log.info('%s succeed !' % FILE_NAME)
    return


if __name__ == '__main__':
    common.case_main(nas_main)
