#-*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-x-x 描述信息特殊字符测试
#######################################################

import os

import log
import nas_common

# 当前脚本名称
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]

#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def executing_case():
    """
        1、创建一个描述信息中含有特殊字符（比如：@#￥%……&*），长度在1-255之间（含1和255）的FTP共享；
    :return:
    """
    log.info("（2）executing_case")

    dir_name = "nas_16-0-4-141_dir"
    create_file_path = nas_common.ROOT_DIR + dir_name
    get_file_list_path = nas_common.ROOT_DIR
    description = "\"@#￥%……&*\""
    export_name = "nas_16_0_4_141_ftp_export_name"

    check_result1 = nas_common.create_file(path=create_file_path)
    if check_result1["detail_err_msg"] != "":
        log.info("%s" % check_result1["detail_err_msg"])

    check_result2 = nas_common.get_file_list(path=get_file_list_path)
    if check_result2["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    files = check_result2["result"]["files"]
    for file in files:
        if file["path"] == create_file_path:
            if cmp(file, {
                "name": "%s" % dir_name,
                "path": "%s" % create_file_path,
                "type": "DIR"
            }) != 0:
                log.error(("%s Failed") % FILE_NAME)
                raise Exception(("%s Failed") % FILE_NAME)

    result = 1
    check_result3 = nas_common.create_ftp_export(access_zone_id=result,
                                                 export_name=export_name,
                                                 export_path=create_file_path,
                                                 description=description)
    if check_result3["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    result1 = check_result3["result"]

    check_result4 = nas_common.get_ftp_exports(ids=result1)
    if check_result4["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    exports = check_result4["result"]["exports"]
    for export in exports:
        if cmp(export, {
                "access_zone_id": int("%s" % result),
                "allow_anonymous": False,
                "bandwidth_limit": 0,
                "description": "@#￥%……&*",
                "export_name": "%s" % export_name,
                "export_path": "%s" % create_file_path,
                "id": int("%s" % result1),
                "key": int("%s" % result1),
                "version": 0
                }) != 0:
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

    nas_common.cleaning_environment()
    preparing_environment()
    executing_case()
    if nas_common.DEBUG != "on":
        nas_common.cleaning_environment()

    return

class Nas_Class_16_0_x_x():
    def nas_method_16_0_x_x(self):
        nas_main()

if __name__ == '__main__':
    nas_main()
