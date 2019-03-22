#-*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-x-x 无效的访问区ID
#######################################################

import os

import utils_path
import log
import common
import nas_common
import prepare_clean
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


def executing_case():
    """
        1、创建一个访问区ID不存在的FTP共享；
        pscli --command=create_ftp_export --access_zone_id=2 --export_name=ftp_export_name --export_path=volume:/export/dir --description=export_description --allow_anonymous=true --bandwidth_limit=10
        注：访问区id 2不存在；
    :return:
    """
    log.info("（2）executing_case")

    # create_file
    dir_name1 = "nas_16-0-4-145_dir"
    dir_name2 = "dir"
    dir_name_list = [dir_name1, dir_name2]
    create_file_path1 = nas_common.ROOT_DIR + dir_name1
    create_file_path2 = create_file_path1 + "/" + dir_name2
    create_file_path_list = [create_file_path1, create_file_path2]
    get_file_list_path1 = nas_common.ROOT_DIR
    get_file_list_path2 = create_file_path1
    get_file_list_path_list = [get_file_list_path1, get_file_list_path2]
    # create_ftp_export
    not_exist_access_zone_id = 250
    export_name = "nas_16_0_4_145_ftp_export_name"

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

    check_result3 = nas_common.create_ftp_export(access_zone_id=not_exist_access_zone_id,
                                                 user_name=nas_common.AD_USER_1,
                                                 export_path=create_file_path2)
    if check_result3["detail_err_msg"].find("Can not find the access zone by id") == -1:
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    else:
        log.info(("%s Succeed") % FILE_NAME)

    return


def nas_main():
    """脚本入口函数
    :return:无
    """
    prepare_clean.nas_test_prepare(FILE_NAME)
    executing_case()
    if nas_common.DEBUG != 'on':
        prepare_clean.nas_test_clean()
    return


if __name__ == '__main__':
    common.case_main(nas_main)
