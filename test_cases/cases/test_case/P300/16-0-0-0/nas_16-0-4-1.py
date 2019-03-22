# -*- coding:utf-8 -*-

######################################################
# Author: jiangxiaoguang
# Date: 2018-08-23
# @summary：
#   显示信息正确性测试
# @steps:
#   1、浏览文件系统详细信息；
#   pscli --command=get_file_list --path=volume:/dir --display_details=true
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
    dir_name = "nas_16-0-4-1_dir"
    create_file_path = nas_common.ROOT_DIR + dir_name
    # for get_file_list
    get_file_list_path = nas_common.ROOT_DIR

    msg = nas_common.create_file(path=create_file_path)
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
                    "posix_permission": "rwxr-xr-x",
                    "size": 4096,
                    "type": "DIR"
                    }):
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
