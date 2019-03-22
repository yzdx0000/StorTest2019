#-*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-4-12 目录权限r--r--r--
#######################################################

import os

import utils_path
import log
import nas_common
import prepare_clean

# 当前脚本名称
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0].replace('-', '_')

#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def executing_case():
    """
        1、在254层目录下创建目录名称长度为255的目录a...a，目录权限为r--r--r--；
        pscli --command=create_file --path=volume:/dir1/dir2/.../a...a --posix_permission=r--r--r--
    :return:
    """
    log.info("（2）executing_case")

    max_depth = 255     # 支持任意数字大小测试
    real_max_depth = max_depth - 2  # 最大可以创建253层
    dir_name_list = ["nas_16-0-4-12_dir"]
    file_list_init = nas_common.VOLUME_NAME + ':/'
    get_file_list_path_list = [file_list_init]
    create_file_path = nas_common.VOLUME_NAME + ':/' + FILE_NAME
    create_file_path_list = [create_file_path]

    for i in range(real_max_depth):
        print "count = %s" % (i+1)
        if i < real_max_depth-1 and (i+2) != 253:    # 少循环一次，因为列表初始化已经包含一个元素；
            dir_name = "d"
            dir_name_list.append(dir_name)

            get_file_list_path = create_file_path
            get_file_list_path_list.append(get_file_list_path)

            create_file_path = create_file_path + "/" + dir_name
            create_file_path_list.append(create_file_path)
        else:
            dir_name = "a" * 255
            dir_name_list.append(dir_name)

            get_file_list_path = create_file_path
            get_file_list_path_list.append(get_file_list_path)

            create_file_path = create_file_path + "/" + dir_name
            create_file_path_list.append(create_file_path)

        if i < 252:     # 循环<=252次（i=0~251），创建的目录都是合法的
            check_result1 = nas_common.create_file(path=create_file_path_list[i])
            if check_result1["detail_err_msg"] != "":
                log.info("%s" % check_result1["detail_err_msg"])

            check_result2 = nas_common.get_file_list(path=get_file_list_path_list[i], display_details="true")
            if check_result2["detail_err_msg"] != "":
                log.error(("%s Failed") % FILE_NAME)
                raise Exception(("%s Failed") % FILE_NAME)
            files = check_result2["result"]["detail_files"]
            for file in files:
                if file["path"] == create_file_path_list[i]:
                    if file["posix_permission"] != "rwxr-xr-x":
                        log.error(("%s Failed") % FILE_NAME)
                        raise Exception(("%s Failed") % FILE_NAME)
        elif i == 252:  # 循环=253次，创建的目录也是合法的，且权限设为"r--r--r--"
            check_result3 = nas_common.create_file(path=create_file_path_list[i], posix_permission="r--r--r--")
            if check_result3["detail_err_msg"] != "":
                log.info("%s" % check_result3["detail_err_msg"])

            check_result4 = nas_common.get_file_list(path=get_file_list_path_list[i], display_details="true")
            if check_result4["detail_err_msg"] != "":
                log.error(("%s Failed") % FILE_NAME)
                raise Exception(("%s Failed") % FILE_NAME)
            files = check_result4["result"]["detail_files"]
            for file in files:
                if file["path"] == create_file_path_list[i]:
                    if file["posix_permission"] != "r--r--r--":
                        log.error(("%s Failed") % FILE_NAME)
                        raise Exception(("%s Failed") % FILE_NAME)
        else:      # 循环>253次，无法再创建目录
            check_result5 = nas_common.create_file(path=create_file_path_list[i])
            if check_result5["detail_err_msg"].find("depth of absolute path is deeper than 255") == -1:
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

class Nas_Class_16_0_4_12():
    def nas_method_16_0_4_12(self):
        nas_main()

if __name__ == '__main__':
    nas_main()