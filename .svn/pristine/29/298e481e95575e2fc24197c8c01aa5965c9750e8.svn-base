# -*- coding:utf-8 -*-

######################################################
# Author: jiangxiaoguang
# Date: 2018-08-23
# @summary：
#   卷根目录下创建目录
# @steps:
#   1、3节点集群，通过命令行创建目录；
#   pscli --command=create_file --path=volume:/nas/dir_test
#   2、通过命令行查看目录列表中创建的文件；
#   pscli --command=get_file_list --path:volume:/nas/
#   3、通过客户端查看目录存在，且权限正确；
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
    dir_name1 = "nas_16-0-4-2_dir"
    dir_name2 = "dir"
    dir_name_list = [dir_name1, dir_name2]
    root_dir = "%s:/" % nas_common.VOLUME_NAME
    create_file_path1 = root_dir + dir_name1
    create_file_path2 = create_file_path1 + "/" + dir_name2
    create_file_path_list = [create_file_path1, create_file_path2]
    # for get_file_list
    get_file_list_path1 = root_dir
    get_file_list_path2 = create_file_path1
    get_file_list_path_list = [get_file_list_path1, get_file_list_path2]

    for i in range(len(dir_name_list)):
        msg = nas_common.create_file(path=create_file_path_list[i])
        if msg["detail_err_msg"] != "":
            raise Exception("%s Failed" % FILE_NAME)

        msg = nas_common.get_file_list(path=get_file_list_path_list[i])
        if msg["detail_err_msg"] != "":
            raise Exception("%s Failed" % FILE_NAME)
        files = msg["result"]["files"]
        for f in files:
            if f["path"] == create_file_path_list[i]:
                if cmp(f, {
                        "auth_provider_id": 0,
                        "name": "%s" % dir_name_list[i],
                        "path": "%s" % create_file_path_list[i],
                        "type": "DIR"
                        }):
                    raise Exception("%s Failed" % FILE_NAME)

    # 通过客户端查看目录存在，且权限正确
    cmd = 'ls -l /mnt/%s | grep %s' % (nas_common.VOLUME_NAME, dir_name1)
    rc, stdout = common.run_command(nas_common.RANDOM_NODE_IP, cmd)
    common.judge_rc(rc, 0, "ls -l failed")
    if stdout.split()[0] != 'drwxr-xr-x' or stdout.split()[2] != 'root' or stdout.split()[3] != 'root':
        raise Exception("%s Failed" % FILE_NAME)

    cmd = 'ls -l /mnt/%s/%s | grep %s' % (nas_common.VOLUME_NAME, dir_name1, dir_name2)
    rc, stdout = common.run_command(nas_common.RANDOM_NODE_IP, cmd)
    common.judge_rc(rc, 0, "ls -l failed")
    if stdout.split()[0] != 'drwxr-xr-x' or stdout.split()[2] != 'root' or stdout.split()[3] != 'root':
        raise Exception("%s Failed" % FILE_NAME)

    # 根目录，需自己清理环境
    msg = nas_common.delete_file(path=create_file_path_list[1])
    if msg["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)
    msg = nas_common.delete_file(path=create_file_path_list[0])
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
