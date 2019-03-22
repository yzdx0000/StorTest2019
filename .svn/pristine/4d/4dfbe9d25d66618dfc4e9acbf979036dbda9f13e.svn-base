#-*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-x-x 批量删除FTP共享ID
#######################################################

import os

import utils_path
import log
import nas_common
import common
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

#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def executing_case():
    """
        1、删除正在使用的FTP共享目录；
        pscli --command=delete_ftp_exports --ids=x
    :return:
    """
    log.info("（2）executing_case")

    """1> 创建3节点访问分区"""
    obj_node = common.Node()
    nodes_id_list = obj_node.get_nodes_id()
    nodes_id_str = ','.join(str(p) for p in nodes_id_list)
    access_zone_name = 'az_' + FILE_NAME
    exe_info = nas_common.create_access_zone(nodes_id_str, access_zone_name)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('create access zone %s failed !!!' % access_zone_name)
        raise Exception('create access zone %s failed !!!' % access_zone_name)
    access_zone_id = exe_info['result']

    """2> 创建本地用户组"""
    exe_info = nas_common.get_auth_providers_local()
    auth_provider_id = exe_info['result']['auth_providers'][0]['id']

    exe_info = nas_common.create_auth_group(auth_provider_id=auth_provider_id, name='local_group')
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit('create auth group failed !!!')

    exe_info = nas_common.get_auth_groups(auth_provider_id=auth_provider_id)
    group_id = exe_info['result']['auth_groups'][0]['id']

    """3> 创建多个本地用户"""
    user_ftp_num = 100
    user_name_list = []
    for i in range(user_ftp_num):
        user_name = 'local_user_' + str(i)
        exe_info = nas_common.create_auth_user(auth_provider_id=auth_provider_id, name=user_name,
                                               password='111111', primary_group_id=group_id)
        if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
            common.except_exit('create auth user %s failed !!!' % user_name)

    for i in range(user_ftp_num):
        rc, exe_info = nas_common.get_auth_users(auth_provider_id=auth_provider_id)
        tmp_user_name = exe_info['result']['auth_users'][i]['name']
        user_name_list.append(tmp_user_name)

    # create_ftp_export
    ids_lst = []
    for i in range(user_ftp_num):
        count = i + 1
        dir_name = "nas_16-0-4-153_dir" + "_%s" % count
        create_file_path = nas_common.ROOT_DIR + dir_name

        export_name = "nas_16_0_4_153_ftp_export_name" + "_%s" % count

        check_result1 = nas_common.create_file(path=create_file_path)
        if check_result1["detail_err_msg"] != "":
            log.info("%s" % check_result1["detail_err_msg"])

        check_result2 = nas_common.create_ftp_export(access_zone_id=access_zone_id,
                                                     user_name=user_name_list[i],
                                                     export_path=create_file_path)
        if check_result2["detail_err_msg"] != "":
            log.error(("%s Failed") % FILE_NAME)
            raise Exception(("%s Failed") % FILE_NAME)
        result = check_result2["result"]
        ids_lst.append(result)

    ids_str = ','.join(str(i) for i in ids_lst)
    check_result3 = nas_common.delete_ftp_exports(ids=ids_str)
    if check_result3["detail_err_msg"] != "":
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
