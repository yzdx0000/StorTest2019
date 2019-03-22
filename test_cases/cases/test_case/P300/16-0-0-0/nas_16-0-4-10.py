#-*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-4-10 目录权限rwxrwxrwx
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
        1、在根目录下创建目录a，目录权限为rwxrwxrwx；
        pscli --command=create_file --path=volume:/a --posix_permission=rwxrwxrwx
    :return:
    """
    log.info("（2）executing_case")

    dir_name = "nas_16-0-4-10_dir"
    create_file_path = nas_common.ROOT_DIR + dir_name
    get_file_list_path = nas_common.ROOT_DIR

    check_result1 = nas_common.create_file(path=create_file_path, posix_permission="rwxrwxrwx")
    if check_result1["detail_err_msg"] != "":
        log.info("%s" % check_result1["detail_err_msg"])

    check_result2 = nas_common.get_file_list(path=get_file_list_path, display_details="true")
    if check_result2["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    files = check_result2["result"]["detail_files"]
    for file in files:
        if file["path"] == create_file_path:
            if file["name"] != "%s" % dir_name \
                    or file["path"] != "%s" % create_file_path \
                    or file["posix_permission"] != "rwxrwxrwx" \
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

class Nas_Class_16_0_4_10():
    def nas_method_16_0_4_10(self):
        nas_main()

if __name__ == '__main__':
    nas_main()