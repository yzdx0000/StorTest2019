#-*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-x-x 本地用户授权smb权限
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
        1、创建3节点访问分区az1，启动nas服务；
        2、创建共享路径volume:/nas/smb_dir
        3、在az1上创建smb共享，输入正确的名称和共享路径；
        4、查看smb共享路径配置成功，信息是否与配置信息匹配；
        5、添加本地用户user1
        6、授权本地用户user1的smb 权限
        pscli --command=add_smb_export_auth_clients --export_id=x --name=user1 --type=USER --run_as_root=ture
        7、查看user1授权信息是否匹配
        pscli --command=get_smb_export_auth_clients
    :return:
    """
    log.info("（2）executing_case")

    '''1> 创建3节点访问分区az1，启动nas服务'''
    """创建访问分区"""
    obj_node = common.Node()
    nodes_id_list = obj_node.get_nodes_id()
    nodes_id_str = ','.join(str(p) for p in nodes_id_list)
    access_zone_name = 'az_' + FILE_NAME
    exe_info = nas_common.create_access_zone(nodes_id_str, access_zone_name)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('create access zone %s failed !!!' % access_zone_name)
        raise Exception('create access zone %s failed !!!' % access_zone_name)
    access_zone_id = exe_info['result']

    """启动nas服务"""
    exe_info = nas_common.enable_nas(access_zone_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('enable nas failed !!!')
        raise Exception('enable nas failed !!!')

    # create_file
    dir_name1 = "nas_16-0-4-155_dir"
    dir_name2 = "dir"
    dir_name_list = [dir_name1, dir_name2]
    create_file_path1 = nas_common.ROOT_DIR + dir_name1
    create_file_path2 = create_file_path1 + "/" + dir_name2
    create_file_path_list = [create_file_path1, create_file_path2]
    get_file_list_path1 = nas_common.ROOT_DIR
    get_file_list_path2 = create_file_path1
    get_file_list_path_list = [get_file_list_path1, get_file_list_path2]
    # create_smb_export
    smb_export_name = "nas_16_0_4_155_smb_export_name"
    # for user and group

    """获取本地认证服务器id"""
    exe_info = nas_common.get_auth_providers_local()
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        common.except_exit("get auth providers local failed !!!")
    local_auth_provider_id = exe_info['result']['auth_providers'][0]['id']
    auth_group_name = "nas_4_155_auth_group_name"
    smb_auth_user_name = "nas_4_155_smb_auth_user_name"
    password = "111111"
    # for export_auth_clients
    smb_export_auth_clients_name = "nas_4_155_smb_auth_user_name"   # The authorization user/group name
    smb_run_as_root = "true"
    smb_type = "USER"

    for i in range(len(dir_name_list)):
        check_result1 = nas_common.create_file(path=create_file_path_list[i])
        if check_result1["detail_err_msg"] != "":
            log.info("%s" % check_result1["detail_err_msg"])

        check_result2 = nas_common.get_file_list(path=get_file_list_path_list[i])
        if check_result2["detail_err_msg"] != "":
            raise Exception("%s Failed" % FILE_NAME)
        files = check_result2["result"]["files"]
        for f in files:
            if f["path"] == create_file_path_list[i]:
                if cmp(f, {
                    "auth_provider_id": f['auth_provider_id'],
                    "name": "%s" % dir_name_list[i],
                    "path": "%s" % create_file_path_list[i],
                    "type": "DIR"
                }) != 0:
                    raise Exception("%s Failed" % FILE_NAME)

    check_result3 = nas_common.create_smb_export(access_zone_id=access_zone_id,
                                                 export_name=smb_export_name,
                                                 export_path=create_file_path2)
    if check_result3["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)
    smb_result = check_result3["result"]

    check_result4 = nas_common.create_auth_group(auth_provider_id=local_auth_provider_id,
                                                 name=auth_group_name)
    if check_result4["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)
    group_id = check_result4["result"]

    check_result5 = nas_common.create_auth_user(auth_provider_id=local_auth_provider_id,
                                                name=smb_auth_user_name,
                                                password=password,
                                                primary_group_id=group_id)
    if check_result5["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)

    check_result6 = nas_common.add_smb_export_auth_clients(export_id=smb_result,
                                                           name=smb_export_auth_clients_name,
                                                           user_type=smb_type,
                                                           run_as_root=smb_run_as_root)
    if check_result6["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)
    export_ids = check_result6["result"][0]

    check_result7 = nas_common.get_smb_export_auth_clients(export_ids=smb_result)
    if check_result7["detail_err_msg"] != "":
        raise Exception("%s Failed" % FILE_NAME)
    smb_export_auth_clients = check_result7["result"]["smb_export_auth_clients"]
    for smb_export_auth_client in smb_export_auth_clients:
        if smb_export_auth_client != {
                "export_id": int(smb_result),
                "id": int(export_ids),
                "key": int(export_ids),
                "name": smb_export_auth_clients_name,
                "permission_level": "full_control",
                "run_as_root": True,
                "type": "USER",
                "version": 0
                }:
            raise Exception("%s Failed" % FILE_NAME)

    return


def nas_main():
    """脚本入口函数
    :return:无
    """
    prepare_clean.nas_test_prepare(FILE_NAME)
    executing_case()
    if nas_common.DEBUG != 'on':
        prepare_clean.nas_test_clean()
    log.info('%s succeed !' % FILE_NAME)
    return


if __name__ == '__main__':
    common.case_main(nas_main)
