#-*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-4-11 目录权限rw-rw-rw-
#######################################################

import os

import utils_path
import log
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
    """
        1、在a目录下创建目录b，目录权限为rw-rw-rw-；
        pscli --command=create_file --path=volume:/a/b --posix_permission=rw-rw-rw-
    :return:
    """
    log.info("（2）executing_case")

    dir_name1 = "nas_16-0-4-11_dir"
    dir_name2 = "dir"
    create_file_path1 = nas_common.ROOT_DIR + dir_name1
    create_file_path2 = create_file_path1 + "/" + dir_name2
    get_file_list_path1 = nas_common.ROOT_DIR
    get_file_list_path2 = create_file_path1

    check_result1 = nas_common.create_file(path=create_file_path1)
    if check_result1["detail_err_msg"] != "":
        log.info("%s" % check_result1["detail_err_msg"])

    check_result2 = nas_common.get_file_list(path=get_file_list_path1, display_details="true")
    if check_result2["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    files = check_result2["result"]["detail_files"]
    for file in files:
        if file["path"] == create_file_path1:
            if file["name"] != "%s" % dir_name1 \
                    or file["path"] != "%s" % create_file_path1 \
                    or file["posix_permission"] != "rwxr-xr-x" \
                    or file["type"] != "DIR":
                log.error(("%s Failed") % FILE_NAME)
                raise Exception(("%s Failed") % FILE_NAME)

    check_result3 = nas_common.create_file(path=create_file_path2, posix_permission="rw-rw-rw-")
    if check_result3["detail_err_msg"] != "":
        log.info("%s" % check_result3["detail_err_msg"])

    check_result4 = nas_common.get_file_list(path=get_file_list_path2, display_details="true")
    if check_result4["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    files = check_result4["result"]["detail_files"]
    for file in files:
        if file["path"] == create_file_path2:
            if file["name"] != "%s" % dir_name2 \
                    or file["path"] != "%s" % create_file_path2 \
                    or file["posix_permission"] != "rw-rw-rw-" \
                    or file["type"] != "DIR":
                log.error(("%s Failed") % FILE_NAME)
                raise Exception(("%s Failed") % FILE_NAME)

    log.info(("%s Succeed") % FILE_NAME)

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

    return

class Nas_Class_16_0_4_11():
    def nas_method_16_0_4_11(self):
        nas_main()

if __name__ == '__main__':
    nas_main()