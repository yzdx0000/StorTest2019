#-*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-4-7 创建边界深度长度的目录
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
        1、创建多层嵌套目录，使路径总长度为1018（含/mnt/volume/）；
        2、创建多层嵌套目录，使路径总长度为1019（含/mnt/volume/）；
    :return:
    """
    log.info("（2）executing_case")

    # 测试路径最大长度1018
    # 按/mnt/volume/dir...计算路径长度
    # 路径总长度 = 5 + len("nas_common.VOLUME_NAME") + 1 + 待构造的路径长度

    dir_name = ""
    get_file_list_path = ""
    dir_name_list = ["nas_16-0-4-7_dir"]
    get_file_list_path_list = [nas_common.ROOT_DIR]
    create_file_path = nas_common.ROOT_DIR + "nas_16-0-4-7_dir"
    create_file_path_list = [create_file_path]

    for i in range(17): # 构造create_file_path_list 16次：前15次是256*15，最后一次是bbb和ccc；循环创建、查询17次
        print "count = %s" % (i + 1)
        if i < 15:      # 循环前15次
            # 前15次是65*15
            dir_name = "a" * 60
            dir_name_list.append(dir_name)

            get_file_list_path = create_file_path
            get_file_list_path_list.append(get_file_list_path)

            create_file_path = create_file_path + "/" + dir_name
            create_file_path_list.append(create_file_path)

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
        elif i == 15:   # 循环第16次
            # 构造供第17次使用的create_file_path_list，先构造bbb，再构造ccc
            # 先构造bbb：1019 - 5 - len(nas_common.VOLUME_NAME) - 1，预期创建失败
            dir_name = "b" * (1019 - len(("/mnt/%s/nas_16-0-4-7_dir") % nas_common.VOLUME_NAME) - 60*15 - len("/"))
            dir_name_list.append(dir_name)

            create_file_path_old = create_file_path
            get_file_list_path = create_file_path_old
            get_file_list_path_list.append(get_file_list_path)

            create_file_path = create_file_path_old + "/" + dir_name
            create_file_path_list.append(create_file_path)

            # 创建、查询第16次
            check_result3 = nas_common.create_file(path=create_file_path_list[i])
            if check_result3["detail_err_msg"] != "":
                log.info("%s" % check_result3["detail_err_msg"])

            check_result4 = nas_common.get_file_list(path=get_file_list_path_list[i])
            if check_result4["detail_err_msg"] != "":
                log.error(("%s Failed") % FILE_NAME)
                raise Exception(("%s Failed") % FILE_NAME)
            files = check_result4["result"]["files"]
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

        else:   # 循环第17次，只创建、查询，不构造dir_name_list[],get_file_list_path_list[],create_file_path_list[]
            check_result5 = nas_common.create_file(path=create_file_path_list[i])
            if check_result5["detail_err_msg"].find("length:1043 exceed the max length:1019") == -1:
                log.error(("%s Failed") % FILE_NAME)
                raise Exception(("%s Failed") % FILE_NAME)

            # 构造完删除dir_name_list[],get_file_list_path_list[],create_file_path_list[]最后一个元素
            dir_name_list.remove(dir_name)
            get_file_list_path_list.remove(get_file_list_path)
            create_file_path_list.remove(create_file_path)

            # 再构造ccc：1018 - 5 - len(nas_common.VOLUME_NAME) - 1，预期创建成功
            dir_name = "c" * (1018 - len(("/mnt/%s/nas_16-0-4-7_dir") % nas_common.VOLUME_NAME) - 60*15 - len("/"))
            dir_name_list.append(dir_name)

            get_file_list_path = create_file_path_old
            get_file_list_path_list.append(get_file_list_path)

            create_file_path = create_file_path_old + "/" + dir_name
            create_file_path_list.append(create_file_path)

            check_result4 = nas_common.create_file(path=create_file_path_list[i])
            if check_result4["detail_err_msg"] != "":
                log.info("%s" % check_result4["detail_err_msg"])

            check_result5 = nas_common.get_file_list(path=get_file_list_path_list[i])
            if check_result5["detail_err_msg"] != "":
                log.error(("%s Failed") % FILE_NAME)
                raise Exception(("%s Failed") % FILE_NAME)
            files = check_result5["result"]["files"]
            for file in files:
                if file["path"] == create_file_path_list[i]:
                    if cmp(file, {
                        "name": "%s" % dir_name_list[i],
                        "path": "%s" % create_file_path_list[i],
                        "type": "DIR"
                    }) != 0:
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

class Nas_Class_16_0_4_7():
    def nas_method_16_0_4_7(self):
        nas_main()

if __name__ == '__main__':
    nas_main()