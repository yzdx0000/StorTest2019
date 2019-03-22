#-*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-4-8 创建目录长度达到极限
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
        1、在根目录下创建目录dir，使其名称长度为255；
        2、在根目录下创建目录dir1，使其名称长度为256；
    :return:
    """
    log.info("（2）executing_case")

    dir_name_255 = "nas_16-0-4-8_" + "x" * (255 - len("nas_16-0-4-8_"))
    dir_name_256 = "nas_16-0-4-8_" + "x" * (256 - len("nas_16-0-4-8_"))
    create_file_path_255 = nas_common.ROOT_DIR + dir_name_255
    create_file_path_256 = nas_common.ROOT_DIR + dir_name_256
    get_file_list_path = nas_common.ROOT_DIR

    chinese_dir_name_85 = "姜" * 85
    chinese_dir_name_86 = "姜" * 86
    chinese_create_file_path_85 = nas_common.ROOT_DIR + chinese_dir_name_85
    chinese_create_file_path_86 = nas_common.ROOT_DIR + chinese_dir_name_86

    # 英文长度校验
    check_result1 = nas_common.create_file(path=create_file_path_255)
    if check_result1["detail_err_msg"] != "":
        log.info("%s" % check_result1["detail_err_msg"])

    check_result2 = nas_common.get_file_list(path=get_file_list_path)
    if check_result2["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    files = check_result2["result"]["files"]
    for file in files:
        if file["path"] == create_file_path_255:
            if cmp(file, {
                "auth_provider_id": 0,
                "name": "%s" % dir_name_255,
                "path": "%s" % create_file_path_255,
                "type": "DIR"
            }) != 0:
                log.error(("%s Failed") % FILE_NAME)
                raise Exception(("%s Failed") % FILE_NAME)

    check_result3 = nas_common.create_file(path=create_file_path_256)
    if check_result3["detail_err_msg"].find("file name is longer than 255") == -1:
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)

    # 中文长度校验
    check_result4 = nas_common.create_file(path=chinese_create_file_path_85)
    if check_result4["detail_err_msg"] != "":
        log.info("%s" % check_result4["detail_err_msg"])

    check_result5 = nas_common.get_file_list(path=chinese_create_file_path_85)
    if check_result5["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    files = check_result5["result"]["files"]
    for file in files:
        if file["path"] == chinese_create_file_path_85:
            if cmp(file, {
                "name": "%s" % chinese_dir_name_85,
                "path": "%s" % chinese_create_file_path_85,
                "type": "DIR"
            }) != 0:
                log.error(("%s Failed") % FILE_NAME)
                raise Exception(("%s Failed") % FILE_NAME)

    check_result6 = nas_common.create_file(path=chinese_create_file_path_86)
    if check_result6["detail_err_msg"].find("file name is longer than 255") == -1:
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    else:
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
        prepare_clean.nas_test_prepare(FILE_NAME)

    return

class Nas_Class_16_0_4_8():
    def nas_method_16_0_4_8(self):
        nas_main()

if __name__ == '__main__':
    nas_main()