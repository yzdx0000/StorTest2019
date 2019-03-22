#-*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-4-6 创建边界深度层数的目录
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
        1、创建255层嵌套深度的目录（含/mnt/volume/）；
        注：去掉前两层目录/mnt/a，还有253层可以创建(real_max_depth=253)；
    :return:
    """
    log.info("（2）executing_case")

    max_depth = 256     # 支持任意数字大小测试
    real_max_depth = max_depth - 2  # real_max_depth = 254，即最大可以创建253层，尝试创建254层
    dir_name_list = [FILE_NAME]
    init_dir = nas_common.VOLUME_NAME + ':/'
    get_file_list_path_list = [init_dir]
    create_file_path = nas_common.VOLUME_NAME + ':/' + FILE_NAME
    create_file_path_list = [create_file_path]

    for i in range(real_max_depth):
        print "count = %s" % (i+1)
        if i < real_max_depth-1:    # 少循环一次，因为列表初始化已经包含一个元素；
            dir_name = "d"
            dir_name_list.append(dir_name)

            get_file_list_path = create_file_path
            get_file_list_path_list.append(get_file_list_path)

            create_file_path = create_file_path + "/" + dir_name
            create_file_path_list.append(create_file_path)

        if i < 253:     # 循环253次（i=0~252），创建的目录都是合法的
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
        else:      # 循环>253次，无法再创建目录
            check_result3 = nas_common.create_file(path=create_file_path_list[i])
            if check_result3["detail_err_msg"].find("depth of absolute path is deeper than 255") == -1:
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

class Nas_Class_16_0_4_6():
    def nas_method_16_0_4_6(self):
        nas_main()

if __name__ == '__main__':
    nas_main()