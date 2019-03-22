#-*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-x-x 修改目录权限到---------
#######################################################

import os

import utils_path
import log
import nas_common
import shell
import prepare_clean
import common
import get_config

# 当前脚本名称
VOLUME_NAME = get_config.get_one_volume_name()
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0].replace('-', '_')                 # 本脚本名字
NAS_PATH = get_config.get_one_nas_test_path()                            # /mnt/volume/nas_test_dir
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)             # /mnt/volume/nas_test_dir/nas_16_6_0_16
BASE_NAS_PATH = os.path.dirname(NAS_PATH)                                # /mnt/volume
NAS_PATH_BASENAME = os.path.basename(NAS_PATH)                           # nas_test_dir
SYSTEM_IP_0 = get_config.get_parastor_ip(0)
SYSTEM_IP_1 = get_config.get_parastor_ip(1)
SYSTEM_IP_2 = get_config.get_parastor_ip(2)

#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def executing_case():
    """
        1、3节点集群，通过命令行创建目录；
        pscli --command=create_file --path=volume:/nas/dir_test
        2、通过命令行查看目录列表中创建的目录；
        pscli --command=get_file_list --path:volume:/nas/
        3、通过客户端查看目录存在，且权限正确；
        4、通过命令行修改目录权限到000；
        pscli --command=update_file --path=volume:/nas/dir_test --posix_permission=---------
        5、通过客户端查看目录权限修改是否正确；
    :return:
    """
    log.info("（2）executing_case")

    # 创建目录，查看目录
    dir_name1 = "nas_16-0-4-17_dir"
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

        check_result2 = nas_common.get_file_list(path=get_file_list_path_list[i], display_details="true")
        if check_result2["detail_err_msg"] != "":
            log.error(("%s Failed") % FILE_NAME)
            raise Exception(("%s Failed") % FILE_NAME)
        files = check_result2["result"]["detail_files"]
        for file in files:
            if file["path"] == create_file_path_list[i]:
                if file["name"] != "%s" % dir_name_list[i] \
                        or file["path"] != "%s" % create_file_path_list[i] \
                        or file["posix_permission"] != "rwxr-xr-x" \
                        or file["type"] != "DIR":
                    log.error(("%s Failed") % FILE_NAME)
                    raise Exception(("%s Failed") % FILE_NAME)

    # 通过客户端查看目录权限
    base_obj_path = os.path.join(NAS_PATH, dir_name1)
    cmd = "ls -l %s | grep %s | cut -d \" \" -f 1" % (base_obj_path, dir_name2)
    rc, stdout = common.run_command(SYSTEM_IP_2, cmd)
    print stdout
    if rc != 0 or stdout.split()[0] != 'drwxr-xr-x':
        common.except_exit('there is no correct file info !!!')

    # update_file
    check_result3 = nas_common.update_file(path=create_file_path2, posix_permission="---------")
    if check_result3["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)

    check_result4 = nas_common.get_file_list(path=get_file_list_path2, display_details="true")
    if check_result4["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    files = check_result4["result"]["detail_files"]
    for file in files:
        if file["path"] == create_file_path2:
            if file["name"] != "%s" % dir_name2 \
                    or file["path"] != "%s" % create_file_path2 \
                    or file["posix_permission"] != "---------" \
                    or file["type"] != "DIR":
                log.error(("%s Failed") % FILE_NAME)
                raise Exception(("%s Failed") % FILE_NAME)

    # 通过客户端查看目录权限
    cmd = "ls -l %s | grep %s | cut -d \" \" -f 1" % (base_obj_path, dir_name2)
    rc, stdout = common.run_command(SYSTEM_IP_2, cmd)
    if rc != 0 or stdout.split()[0] != 'd---------':
        common.except_exit('there is no correct file info !!!')
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
