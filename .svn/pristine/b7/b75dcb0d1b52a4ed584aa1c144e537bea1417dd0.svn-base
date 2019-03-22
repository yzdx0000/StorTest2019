#-*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-x-x 允许匿名修改到false
#######################################################

import os

import utils_path
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
        1、创建一个允许匿名登录的FTP共享；
        pscli --command=create_ftp_export --access_zone_id=1 --export_name=ftp_export_name --export_path=volume:/export/dir --allow_anonymous=true
        2、修改上述FTP共享为不允许匿名登录；
        pscli --command=update_ftp_export --id=x --allow_anonymous=false
    :return:
    """
    log.info("（2）executing_case")

    # create_file
    dir_name1 = "nas_16-0-4-147_dir"
    dir_name2 = "dir"
    dir_name_list = [dir_name1, dir_name2]
    create_file_path1 = nas_common.ROOT_DIR + dir_name1
    create_file_path2 = create_file_path1 + "/" + dir_name2
    create_file_path_list = [create_file_path1, create_file_path2]
    get_file_list_path1 = nas_common.ROOT_DIR
    get_file_list_path2 = create_file_path1
    get_file_list_path_list = [get_file_list_path1, get_file_list_path2]
    # create_ftp_export
    access_zone_id = 1
    export_name = "nas_16_0_4_147_ftp_export_name"

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
                    "name": "%s" % dir_name_list[i],
                    "path": "%s" % create_file_path_list[i],
                    "type": "DIR"
                }) != 0:
                    log.error(("%s Failed") % FILE_NAME)
                    raise Exception(("%s Failed") % FILE_NAME)

    check_result3 = nas_common.create_ftp_export(access_zone_id=access_zone_id,
                                                 export_name=export_name,
                                                 export_path=create_file_path2,
                                                 allow_anonymous="true")
    if check_result3["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    result = check_result3["result"]

    check_result4 = nas_common.get_ftp_exports(ids=result)
    if check_result4["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    exports = check_result4["result"]["exports"]
    for export in exports:
        if cmp(export, {
            "access_zone_id": int("%s" % access_zone_id),
            "allow_anonymous": True,
            "bandwidth_limit": 0,
            "export_name": "%s" % export_name,
            "export_path": "%s" % create_file_path2,
            "id": int("%s" % result),
            "key": int("%s" % result),
            "version": 0
        }) != 0:
            log.error(("%s Failed") % FILE_NAME)
            raise Exception(("%s Failed") % FILE_NAME)

    check_result5 = nas_common.update_ftp_export(id=result,
                                                 allow_anonymous="false")
    if check_result5["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)

    check_result6 = nas_common.get_ftp_exports(ids=result)
    if check_result6["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    exports = check_result6["result"]["exports"]
    for export in exports:
        if cmp(export, {
            "access_zone_id": int("%s" % access_zone_id),
            "allow_anonymous": False,
            "bandwidth_limit": 0,
            "export_name": "%s" % export_name,
            "export_path": "%s" % create_file_path2,
            "id": int("%s" % result),
            "key": int("%s" % result),
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
