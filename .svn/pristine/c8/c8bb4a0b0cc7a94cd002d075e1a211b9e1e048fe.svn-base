#-*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-x-x 删除非空子目录
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
        1、在根目录下创建嵌套目录/a/b/c/d/e；
        2、删除目录c；
        pscli --command=delete_file --path=volume:/a/b/c
    :return:
    """
    log.info("（2）executing_case")

    dir_name1 = "nas_16-0-4-21_dir"
    dir_name2 = "dir"
    dir_name_list = [dir_name1, dir_name2]
    create_file_path1 = nas_common.ROOT_DIR + dir_name1
    create_file_path2 = create_file_path1 + "/" + dir_name2
    create_file_path_list = [create_file_path1, create_file_path2]
    get_file_list_path1 = nas_common.ROOT_DIR
    get_file_list_path2 = create_file_path1
    get_file_list_path_list = [get_file_list_path1, get_file_list_path2]

    for i in range(len(dir_name_list)):
        check_result1 = nas_common.create_file(path=create_file_path_list[i])
        if check_result1["detail_err_msg"] != "":
            log.info("%s" % check_result1["detail_err_msg"])

        check_result2 = nas_common.get_file_list(path=get_file_list_path_list[i])
        if check_result2["detail_err_msg"] != "":
            log.error(("%s Failed") % FILE_NAME)
            raise Exception(("%s Failed") % FILE_NAME)
        files = check_result2["result"]["files"]
        for file in files:
            if file["path"] == create_file_path_list[i]:
                if cmp(file, {
                    "auth_provider_id": 0,
                    "name": "%s" % dir_name_list[i],
                    "path": "%s" % create_file_path_list[i],
                    "type": "DIR"
                }) != 0:
                    log.error(("%s Failed") % FILE_NAME)
                    raise Exception(("%s Failed") % FILE_NAME)

    check_result3 = nas_common.delete_file(path=create_file_path1)
    if check_result3["detail_err_msg"].find("is not empty") == -1:
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
        prepare_clean.nas_test_clean()

    return

class Nas_Class_16_0_x_x():
    def nas_method_16_0_x_x(self):
        nas_main()

if __name__ == '__main__':
    nas_main()
