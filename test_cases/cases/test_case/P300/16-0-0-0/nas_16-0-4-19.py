# -*- coding:utf-8 -*-

######################################################
# Author: jiangxiaoguang
# Date: 2018-08-23
# @summary：
#   删除空目录（未使用）
# @steps:
#   1、在根目录下创建目录a；
#   pscli --command=create_file --path=volume:/a
#   2、删除刚创建的目录a；
#   pscli --command=delete_file --path=volume:/a
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
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]


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
    dir_name = "nas_16-0-4-19_dir"
    create_file_path = '%s:/' % nas_common.VOLUME_NAME + dir_name
    # for get_file_list
    get_file_list_path = '%s:/' % nas_common.VOLUME_NAME

    msg = nas_common.create_file(path=create_file_path)
    if msg["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)

    msg = nas_common.get_file_list(path=get_file_list_path)
    if msg["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)
    files = msg["result"]["files"]
    for f in files:
        if f["path"] == create_file_path:
            if cmp(f, {
                    "auth_provider_id": 0,
                    "name": "%s" % dir_name,
                    "path": "%s" % create_file_path,
                    "type": "DIR"
                    }):
                raise Exception("%s Failed" % FILE_NAME)

    # 通过客户端查看目录存在，且权限正确
    cmd = 'ls -l /mnt/%s | grep %s' % (nas_common.VOLUME_NAME, dir_name)
    rc, stdout = common.run_command(nas_common.RANDOM_NODE_IP, cmd)
    common.judge_rc(rc, 0, "ls -l failed")
    if stdout.split()[0] != 'drwxr-xr-x' or stdout.split()[2] != 'root' or stdout.split()[3] != 'root':
        raise Exception("%s Failed" % FILE_NAME)

    msg = nas_common.delete_file(path=create_file_path)
    if msg["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)

    # 通过客户端查看是否删除成功
    cmd = 'ls -l /mnt/%s/%s' % (nas_common.VOLUME_NAME, dir_name)
    rc, stdout = common.run_command(nas_common.RANDOM_NODE_IP, cmd)
    common.judge_rc(rc, 2, "ls -l failed")  # 文件不存在，ls的返回值为2

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
