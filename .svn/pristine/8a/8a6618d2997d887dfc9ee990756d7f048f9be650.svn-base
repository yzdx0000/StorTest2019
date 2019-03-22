# -*- coding:utf-8 -*-

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-x-x 批量创建1000万目录
#######################################################

import os

import utils_path
import log
import common
import nas_common
import prepare_clean

# 当前脚本名称
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]


def executing_case():
    """
        1、通过脚本批量创建1000万个目录；
    :return:
    """
    log.info("（2）executing_case")

    count = 10000000
    base_dir_name = "nas_16-0-4-23_dir"

    create_file_path = nas_common.ROOT_DIR + base_dir_name
    check_result = nas_common.create_file(path=create_file_path)
    if check_result["detail_err_msg"] != "":
        log.info("%s" % check_result["detail_err_msg"])

    for i in range(count):
        log.info("count = %s" % (i+1))
        dir_name = base_dir_name + "_%s" % (i+1)
        create_file_path = nas_common.ROOT_DIR + base_dir_name + '/' + dir_name
        check_result = nas_common.create_file(path=create_file_path)
        if check_result["detail_err_msg"] != "":
            raise Exception("%s Failed" % FILE_NAME)

    return


def nas_main():
    """脚本入口函数
    :return:无
    """
    # prepare_clean.nas_test_prepare(FILE_NAME)
    file_name = os.path.basename(__file__)
    file_name = os.path.splitext(file_name)[0]
    log_file_path = log.get_log_path(file_name)
    stream = log.init(log_file_path, True)

    prepare_clean.nas_test_prepare(FILE_NAME)
    if nas_common.DEBUG != 'on':
        prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)
