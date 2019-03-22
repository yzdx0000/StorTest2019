#-*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-4-9 目录配额阈值硬阈值下创建目录
#######################################################

import os

import utils_path
import log
import common
import nas_common
import quota_common
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
        1、对根目录做配额，其硬阈值为1；
        2、尝试在根目录下创建两个目录；
    :return:
    """
    log.info("（2）executing_case")

    dir_name1 = "nas_16-0-4-9_dir"
    dir_name2 = "dir1"
    dir_name3 = "dir2"
    create_file_path1 = nas_common.ROOT_DIR + dir_name1
    create_file_path2 = create_file_path1 + "/" + dir_name2
    create_file_path3 = create_file_path1 + "/" + dir_name3
    get_file_list_path1 = nas_common.ROOT_DIR

    check_result1 = nas_common.create_file(path=create_file_path1)
    if check_result1["detail_err_msg"] != "":
        log.info("%s" % check_result1["detail_err_msg"])

    check_result2 = nas_common.get_file_list(path=get_file_list_path1)
    if check_result2["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    files = check_result2["result"]["files"]
    for file in files:
        if file["path"] == create_file_path1:
            if cmp(file, {
                "auth_provider_id": 0,
                "name": "%s" % dir_name1,
                "path": "%s" % create_file_path1,
                "type": "DIR"
            }) != 0:
                log.error(("%s Failed") % FILE_NAME)
                raise Exception(("%s Failed") % FILE_NAME)

    rc, pscli_info = quota_common.create_one_quota(path=create_file_path1,
                                                   filenr_quota_cal_type='QUOTA_LIMIT',
                                                   filenr_hard_threshold=1)
    common.judge_rc(rc, 0, "create  quota failed")
    if check_result1["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)

    check_result3 = nas_common.create_file(path=create_file_path2)
    if check_result3["detail_err_msg"] != "":
        log.info("%s" % check_result3["detail_err_msg"])

    check_result4 = nas_common.create_file(path=create_file_path3)
    if check_result4["detail_err_msg"] == "" \
            or check_result4["err_msg"] != "IO_EXCEPTION":
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
        prepare_clean.nas_test_prepare(FILE_NAME)
    return


class Nas_Class_16_0_4_9():
    def nas_method_16_0_4_9(self):
        nas_main()


if __name__ == '__main__':
    nas_main()